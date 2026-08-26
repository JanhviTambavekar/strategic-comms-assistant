"""Streamlit demo: AI-Driven Strategic Communications Assistant.

Implements the linear pipeline from the project architecture diagram:
  UI -> Input Collector -> [Persona Classifier + Document Extractor]
     -> Knowledge Tree -> Prompt Builder -> LLM -> Output Formatter
     -> [Strategy Report + Evaluation Dashboard]
"""
import csv
import importlib
import io
import json
import os
import inspect
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from src.config_loader import load_personas
from src import (
    document_extractor,
    persona_classifier,
    knowledge_tree,
    prompt_builder,
    llm_client,
    output_formatter,
    evaluator,
    cost,
    report_exporter,
)
from src.questionnaire_parser import parse_questionnaire_file
from src.likert_scale import get_likert_scale, get_likert_value, get_likert_label

# override=True so the project's .env is authoritative for the app and is not
# silently overridden by globally-set environment variables (e.g. an
# ANTHROPIC_API_KEY exported for the Claude Code CLI / a gateway).
load_dotenv(override=True)

st.set_page_config(page_title="Strategic Comms Assistant", page_icon="📣", layout="wide")

PERSONAS = load_personas()

PERSONA_BY_RESPONDENT_TYPE = {
    "University / Research Institute STEM-led Spin-out": "university_spinout",
    "SME / Start-up": "sme_innovator",
    "Research Project Team": "research_project",
}

CRITERION_GUIDANCE = {
    "clarity": "Use plain language, remove duplicated material and state recommendations directly.",
    "relevance": "Connect recommendations to named client facts, audiences, objectives and constraints.",
    "actionability": "Give each immediate action an owner, deadline, effort/budget and success measure.",
    "resource_appropriateness": "Show a realistic budget/effort allocation and what will be de-prioritised.",
    "coherence": "Align objectives, messages, channels, timeline, KPIs and next steps around one strategic choice.",
    "strategic_value": "Prioritise one or two high-value activities instead of listing every possible channel.",
    "data_integrity": "Label unsupported facts as assumptions and cite the client input behind material claims.",
    "persona_quality": "Add audience-specific information sources, touchpoints, decision influencers and geography.",
    "timeline_quality": "Use Task + AIDA + Channel/message in every Month 1-36 timeline cell.",
    "kpi_quality": "Add measurable KPI targets with audience, baseline/source, timeframe, owner and measurement tool.",
}

# Kept in the UI layer as well as llm_client so a long-lived Streamlit process
# cannot fail while a module reload is catching up after an application update.
NVIDIA_MODEL_OPTIONS = {
    "Meta Llama 3.1 8B Instruct": "meta/llama-3.1-8b-instruct",
    "Google DiffusionGemma 26B A4B IT": "google/diffusiongemma-26b-a4b-it",
    "NVIDIA Nemotron Mini 4B Instruct": "nvidia/nemotron-mini-4b-instruct",
}

GEMINI_MODEL_OPTIONS = {
    "Gemini 3.5 Flash-Lite": "gemini-3.5-flash-lite",
    "Gemini 3.1 Flash-Lite": "gemini-3.1-flash-lite",
    "Gemini 2.5 Flash-Lite": "gemini-2.5-flash-lite",
}


def sidebar():
    st.sidebar.title("📣 Strategic Comms Assistant")
    st.sidebar.caption("AI-Driven Strategic Communications Assistant")
    provider = llm_client.get_provider()
    model_selection = {
        "strategy_model": None,
        "judge_model": None,
        "strategy_max_tokens": 3000,
        "judge_max_tokens": 500,
    }
    badge = {"gemini": "🟢 Google Gemini", "anthropic": "🟢 Anthropic", "openai": "🟢 OpenAI", "mock": "🟡 Mock (no API key)"}
    st.sidebar.markdown(f"**LLM provider:** {badge.get(provider, provider)}")
    if provider == "mock":
        st.sidebar.info("Running in MOCK mode — add an API key to `.env` for tailored output.")
    if provider == "gemini":
        st.sidebar.markdown("---")
        st.sidebar.subheader("Google Gemini models")
        labels = list(GEMINI_MODEL_OPTIONS)
        configured = os.getenv("GOOGLE_MODEL", "")
        configured_index = next(
            (index for index, label in enumerate(labels)
             if GEMINI_MODEL_OPTIONS[label] == configured),
            0,
        )
        strategy_label = st.sidebar.selectbox(
            "Strategy generation model", labels, index=configured_index,
            help="Model used to generate the communication strategy.",
        )
        judge_label = st.sidebar.selectbox(
            "Independent evaluation model", labels, index=1,
            help="A separate Gemini model used to judge the completed strategy.",
        )
        quality = st.sidebar.radio(
            "Generation mode",
            ["Fast draft", "Full quality"],
            horizontal=True,
            help="Fast draft is recommended on free hosting. Full quality produces a longer report.",
        )
        model_selection = {
            "strategy_model": GEMINI_MODEL_OPTIONS[strategy_label],
            "judge_model": GEMINI_MODEL_OPTIONS[judge_label],
            "strategy_max_tokens": 3000 if quality == "Fast draft" else 5000,
            "judge_max_tokens": 500 if quality == "Fast draft" else 800,
        }
        if model_selection["strategy_model"] == model_selection["judge_model"]:
            st.sidebar.warning("Choose a different evaluation model for an independent comparison.")
        else:
            st.sidebar.caption("Generation and evaluation use separate Gemini models.")
    if provider == "openai" and "nvidia" in (os.getenv("OPENAI_BASE_URL") or "").lower():
        st.sidebar.markdown("---")
        st.sidebar.subheader("NVIDIA NIM models")
        labels = list(NVIDIA_MODEL_OPTIONS)
        configured = os.getenv("OPENAI_MODEL", "")
        configured_index = next(
            (index for index, label in enumerate(labels)
             if NVIDIA_MODEL_OPTIONS[label] == configured),
            0,
        )
        strategy_label = st.sidebar.selectbox(
            "Strategy generation model", labels, index=configured_index,
            help="Model used to generate the communication strategy.",
        )
        judge_label = st.sidebar.selectbox(
            "Independent evaluation model",
            labels,
            index=labels.index("Google DiffusionGemma 26B A4B IT"),
            help="Model used only to judge the completed strategy.",
        )
        quality = st.sidebar.radio(
            "Generation mode",
            ["Fast draft", "Full quality"],
            horizontal=True,
            help="Fast draft reduces response length. Full quality is better for the final dissertation output but can take several minutes on large models.",
        )
        model_selection = {
            "strategy_model": NVIDIA_MODEL_OPTIONS[strategy_label],
            "judge_model": NVIDIA_MODEL_OPTIONS[judge_label],
            "strategy_max_tokens": 3000 if quality == "Fast draft" else 5000,
            "judge_max_tokens": 500 if quality == "Fast draft" else 800,
        }
        # NVIDIA documents a 4,096-token output ceiling for DiffusionGemma.
        if model_selection["strategy_model"] == "google/diffusiongemma-26b-a4b-it":
            model_selection["strategy_max_tokens"] = min(
                model_selection["strategy_max_tokens"], 4096
            )
        if model_selection["strategy_model"] == "google/diffusiongemma-26b-a4b-it":
            st.sidebar.info(
                "DiffusionGemma is larger than Llama and may queue on NVIDIA's shared hosted service. "
                "Use Llama 3.1 8B for reliable quick tests."
            )
        if model_selection["strategy_model"] == model_selection["judge_model"]:
            st.sidebar.warning("Choose a different evaluation model for an independent comparison.")
        else:
            st.sidebar.caption("Generation and evaluation use separate models.")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Pipeline**\n\n"
        "1. Persona selection\n2. Questionnaire + upload\n3. Knowledge-tree routing\n"
        "4. Prompt build → LLM\n5. Strategy + evaluation"
    )
    return model_selection


def reset_below(step: int):
    """Clear downstream state when an earlier step changes."""
    for key in ["strategy", "scores", "route_trace", "doc_text", "human_eval"]:
        if step <= 2 and key in st.session_state:
            del st.session_state[key]


def suggested_persona_key(answers: dict, document_text: str = "") -> str:
    """Prefer the explicit respondent type, then fall back to keyword routing."""
    explicit = PERSONA_BY_RESPONDENT_TYPE.get(answers.get("completing_on_behalf", ""))
    if explicit:
        return explicit
    context = "\n".join(str(value) for value in answers.values()) + "\n" + document_text
    return persona_classifier.suggest_persona(context)


def experiment_csv(records: list[dict]) -> str:
    """Create a flat, spreadsheet-ready experiment export."""
    fields = [
        "timestamp_utc", "strategy_hash", "evaluator_version", "persona", "objective",
        "provider", "model", "judge_model", "prompt_template", "total_tokens", "total_cost_usd",
        "average", "verdict", "timeline_coverage", "timeline_valid", "kpi_valid",
        *evaluator.CRITERIA,
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return buffer.getvalue()


def top_fixes(scores: dict, maximum: int = 3) -> list[str]:
    """Turn validation output and weak rubric criteria into client-facing actions."""
    fixes = list(scores.get("validation_issues", []))
    for criterion in sorted(evaluator.CRITERIA, key=lambda item: scores.get(item, 0)):
        if scores.get(criterion, 0) < 4:
            guidance = CRITERION_GUIDANCE[criterion]
            if guidance not in fixes:
                fixes.append(guidance)
        if len(fixes) >= maximum:
            break
    return fixes[:maximum]


def ensure_current_modules() -> None:
    """Reload stale modules after Streamlit hot-reloads this app file.

    Streamlit can retain an imported module while re-executing app.py. Model
    selection was added to generate_with_usage(), so ensure that signature is
    available before the sidebar or generation path uses it.
    """
    global llm_client, evaluator
    if "model" not in inspect.signature(llm_client.generate_with_usage).parameters:
        llm_client = importlib.reload(llm_client)
    if "max_tokens" not in inspect.signature(evaluator.evaluate).parameters:
        evaluator = importlib.reload(evaluator)


def main():
    ensure_current_modules()
    model_selection = sidebar()
    st.title("AI-Driven Strategic Communications Assistant")
    st.caption("Generate a tailored communication & engagement plan in a few steps.")

    # ---- Step 1: Persona selection ----
    st.header("1. Select your persona")
    persona_keys = list(PERSONAS.keys())
    persona_key = st.radio(
        "Which best describes you?",
        persona_keys,
        format_func=lambda k: f"{PERSONAS[k]['label']} — {PERSONAS[k]['description']}",
    )
    persona = PERSONAS[persona_key]

    # ---- Step 2: Questionnaire + document upload ----
    st.header("2. Tell us about your project")

    # --- Option A: Upload a completed Q&A file (auto-fill) ---
    st.markdown("#### Option A: Upload a completed Q&A file (recommended)")
    st.caption(
        "Upload a Word (.docx), PDF, or text file containing the questionnaire "
        "answers. The system will automatically extract and populate all matching "
        "fields. You can review/edit them before generating."
    )
    answers_file = st.file_uploader(
        "Upload questionnaire answers (.txt, .md, .pdf, or .docx)",
        type=["txt", "md", "pdf", "docx"],
        key="answers_uploader",
    )

    # Parse answers file if uploaded
    file_answers = {}
    if answers_file is not None:
        try:
            file_text = document_extractor.extract_text(answers_file.name, answers_file.getvalue())
            file_answers = parse_questionnaire_file(file_text, persona["questionnaire"])
            if file_answers:
                n_found = len(file_answers)
                n_total = len(persona["questionnaire"])

                # Detect if this is a newly uploaded file (vs a rerun after editing).
                # Only populate session state when a NEW file is uploaded, so user
                # edits are preserved on subsequent reruns.
                file_sig = hash(answers_file.getvalue())
                if st.session_state.get("_answers_file_sig") != file_sig:
                    st.session_state["_answers_file_sig"] = file_sig
                    # Directly set session state for each form widget key so the
                    # form fields in Option B pick up the extracted answers.
                    for q in persona["questionnaire"]:
                        qid = q["id"]
                        if qid in file_answers:
                            st.session_state[qid] = file_answers[qid]

                st.success(
                    f"✅ Auto-populated **{n_found} of {n_total}** questions from "
                    f"`{answers_file.name}`. The answers are now in the form below — "
                    f"review/edit and click **Generate Strategy**."
                )
                missing = [q for q in persona["questionnaire"] if not file_answers.get(q["id"])]
                if missing:
                    st.warning(
                        f"⚠️ **{len(missing)} question(s)** could not be found in the file. "
                        "They are highlighted below — please complete them manually."
                    )
                else:
                    st.info("🎉 All questions populated! Review and edit them in the form below, then click **Generate Strategy**.")
            else:
                st.warning(
                    "⚠️ No answers could be parsed from the file. Please check the format "
                    "or use Option B to fill in manually."
                )
        except Exception as exc:
            st.error(f"Could not parse the answers file: {exc}")

    st.markdown("---")
    st.markdown("#### Option B: Review & edit questionnaire")
    st.caption(
        "The form below is pre-filled with answers from your uploaded file (if any). "
        "You can edit any field before generating."
    )

    # Build the questionnaire form
    answers = {}
    with st.form("intake"):
        cols = st.columns(2)
        for i, q in enumerate(persona["questionnaire"]):
            target = cols[i % 2]
            default_value = file_answers.get(q["id"], "")
            is_missing = not default_value

            # Highlight missing fields with a marker
            label = q["label"]
            if is_missing and file_answers:
                label = f"⚠️ {label}"

            if q["type"] == "textarea":
                answers[q["id"]] = target.text_area(
                    label, value=default_value, key=q["id"]
                )
            elif q["type"] == "select":
                opts = q["options"]
                idx = 0
                if default_value and default_value in opts:
                    idx = opts.index(default_value)
                answers[q["id"]] = target.selectbox(label, opts, index=idx, key=q["id"])
            else:
                answers[q["id"]] = target.text_input(
                    label, value=default_value, key=q["id"]
                )

        st.markdown("#### Evidence and assumptions")
        st.caption(
            "Separate confirmed facts from items that still need validation. This helps "
            "the strategy avoid invented claims and makes its recommendations traceable."
        )
        facts_col, assumptions_col = st.columns(2)
        answers["confirmed_facts"] = facts_col.text_area(
            "Optional information",
            key="confirmed_facts",
            placeholder="e.g. Any additional context, named pilot, funding round, verified figure, or confirmed relationship",
        )
        answers["assumptions_for_review"] = assumptions_col.text_area(
            "Assumptions / facts to validate",
            key="assumptions_for_review",
            placeholder="e.g. baseline still unknown; verify in Months 1–3",
        )

        uploaded = st.file_uploader(
            "Optional: upload a project brief (.txt, .pdf, or .docx)",
            type=["txt", "pdf", "docx"],
            key="brief_uploader",
        )
        submitted = st.form_submit_button("Generate strategy ▶")

    if not submitted:
        st.stop()

    # ---- Document extraction ----
    doc_text = ""
    if uploaded is not None:
        doc_text = document_extractor.extract_text(uploaded.name, uploaded.getvalue())

    suggested_key = suggested_persona_key(answers, doc_text)
    if suggested_key != persona_key:
        st.warning(
            f"Persona check: your answers suggest **{PERSONAS[suggested_key]['label']}**, "
            f"but **{persona['label']}** is selected. The selected persona will be used; "
            "choose the suggested persona and regenerate if that better reflects the organisation."
        )

    # ---- Knowledge-tree routing ----
    objective = answers.get("objective") or persona.get("default_objective", "")
    template_name = knowledge_tree.route(persona_key, objective)
    route_trace = knowledge_tree.explain_route(persona_key, objective)

    # ---- Prompt building ----
    client_inputs = prompt_builder.format_client_inputs(answers, persona["questionnaire"])
    client_inputs += (
        "\n\nCONFIRMED FACTS — use only as evidence:\n"
        f"{answers.get('confirmed_facts') or '(none added)'}\n"
        "\nASSUMPTIONS FOR REVIEW — do not present as established facts:\n"
        f"{answers.get('assumptions_for_review') or '(none added)'}"
    )
    prompt = prompt_builder.build_prompt(
        template_name, persona, objective, client_inputs, doc_text
    )

    # ---- LLM generation ----
    try:
        with st.spinner("Routing through the knowledge tree and generating your strategy…"):
            # The v4 strategy requires a full 10-section plan with a 36-month
            # timeline, personas, and KPIs — needs a larger output budget.
            strategy_md, gen_usage = llm_client.generate_with_usage(
                prompt,
                max_tokens=model_selection["strategy_max_tokens"],
                model=model_selection["strategy_model"],
            )
            if (
                model_selection["strategy_model"]
                and gen_usage.model != model_selection["strategy_model"]
            ):
                st.warning(
                    "The selected strategy model timed out on NVIDIA's hosted service. "
                    f"The strategy was completed using the configured fallback model: `{gen_usage.model}`."
                )
            titled = output_formatter.add_title(
                strategy_md, persona["label"], answers.get("org_name", "")
            )

        # ---- Evaluation ----
        with st.spinner("Evaluating the strategy against the project rubric…"):
            scores, eval_usage = evaluator.evaluate(
                strategy_md,
                client_inputs,
                judge_model=model_selection["judge_model"],
                max_tokens=model_selection["judge_max_tokens"],
            )
            if (
                model_selection["judge_model"]
                and eval_usage.model != model_selection["judge_model"]
            ):
                st.warning(
                    "The selected evaluation model timed out. "
                    f"Evaluation used the fallback model: `{eval_usage.model}`."
                )

        # ---- Token & cost accounting (generation + evaluation = per strategy) ----
        cost_report = cost.summarize(
            [gen_usage, eval_usage], labels=["Strategy generation", "Evaluation"]
        )

        if "experiment_runs" not in st.session_state:
            st.session_state.experiment_runs = []
        run_record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "strategy_hash": scores.get("strategy_hash", ""),
            "evaluator_version": scores.get("evaluator_version", ""),
            "persona": persona["label"],
            "objective": objective,
            "provider": gen_usage.provider,
            "model": gen_usage.model,
            "judge_model": getattr(eval_usage, "model", scores.get("judge_model", "")),
            "prompt_template": template_name,
            "total_tokens": cost_report["total_tokens"],
            "total_cost_usd": round(cost_report["total_cost"], 6),
            "average": scores.get("average", 0),
            "verdict": scores.get("verdict", ""),
            "timeline_coverage": scores.get("timeline_validation", {}).get("timeline_coverage", 0),
            "timeline_valid": scores.get("timeline_validation", {}).get("timeline_valid", False),
            "kpi_valid": scores.get("kpi_validation", {}).get("kpi_valid", False),
            **{criterion: scores.get(criterion, 0) for criterion in evaluator.CRITERIA},
        }
        if not any(run["strategy_hash"] == run_record["strategy_hash"] for run in st.session_state.experiment_runs):
            st.session_state.experiment_runs.append(run_record)
    except llm_client.LLMError as exc:
        st.error(f"⚠️ Could not generate the strategy. {exc}")
        st.info("Tip: set `LLM_PROVIDER=mock` to run the full demo offline with no API key.")
        st.stop()

    # ---- Results ----
    st.success("Strategy generated.")
    st.caption(f"🧭 Routing decision: {route_trace}")
    if uploaded:
        st.caption(f"📎 Document used: {uploaded.name} ({len(doc_text)} chars extracted)")
    if answers_file and file_answers:
        st.caption(f"📋 Answers file used: {answers_file.name} ({len(file_answers)} answers parsed)")

    # Compact token & cost summary line (always visible).
    if gen_usage.provider == "mock":
        model_label = f"Mock (priced as {cost.MOCK_REFERENCE_MODEL})"
    else:
        model_label = gen_usage.model
    cost_word = "est. cost" if cost_report["estimated"] else "cost"
    st.caption(
        f"💰 Model: **{model_label}** · {cost_report['total_tokens']:,} tokens "
        f"({cost_report['total_input_tokens']:,} in / {cost_report['total_output_tokens']:,} out) · "
        f"{cost_word} **${cost_report['total_cost']:.4f}** per strategy"
    )

    tab_strategy, tab_eval, tab_cost, tab_prompt, tab_experiments = st.tabs(
        ["📄 Strategy Report", "📊 Evaluation Dashboard", "💰 Token & Cost",
         "🔍 Prompt (transparency)"]
        + ["Downloads"]
    )

    with tab_strategy:
        st.markdown(titled)
        fname = output_formatter.safe_filename(answers.get("org_name", "strategy"))
        word_data = report_exporter.to_docx(titled)
        pdf_data = report_exporter.to_pdf(titled)
        download_cols = st.columns(2)
        download_cols[0].download_button(
            "⬇ Download Word report", word_data,
            file_name=f"{fname}_strategy.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        download_cols[1].download_button(
            "⬇ Download PDF report", pdf_data,
            file_name=f"{fname}_strategy.pdf",
            mime="application/pdf",
        )

    with tab_eval:
        st.subheader("Strategy readiness")
        timeline_check = scores.get("timeline_validation", {})
        kpi_check = scores.get("kpi_validation", {})
        readiness_ok = (
            scores.get("verdict") == evaluator.VERDICT_USEFUL
            and timeline_check.get("timeline_valid")
            and kpi_check.get("kpi_valid")
            and not scores.get("validation_issues")
        )
        (st.success if readiness_ok else st.warning)(
            "Ready for human review" if readiness_ok else "Needs revision before client use"
        )
        readiness_cols = st.columns(4)
        readiness_cols[0].metric("Timeline coverage", f"{timeline_check.get('timeline_coverage', 0)}%")
        readiness_cols[1].metric("Timeline detail", "Pass" if timeline_check.get("timeline_detail_valid") else "Needs detail")
        readiness_cols[2].metric("KPI checks", "Pass" if kpi_check.get("kpi_valid") else "Needs evidence")
        readiness_cols[3].metric("Validation issues", len(scores.get("validation_issues", [])))
        st.markdown("**Top fixes to make this client-ready**")
        for index, fix in enumerate(top_fixes(scores), start=1):
            st.markdown(f"{index}. {fix}")

        health_col, evidence_col = st.columns(2)
        with health_col:
            with st.expander("Timeline and KPI health", expanded=True):
                st.write(timeline_check.get("timeline_validation_reason", "No timeline validation available."))
                if timeline_check.get("missing_periods"):
                    st.caption(f"Missing months: {', '.join(map(str, timeline_check['missing_periods']))}")
                st.write(kpi_check.get("kpi_validation_reason", "No KPI validation available."))
                st.caption(
                    f"Validated KPI rows: {kpi_check.get('validated_kpi_rows', 0)} · "
                    f"Valid arithmetic blocks: {kpi_check.get('kpi_arithmetic_valid_blocks', 0)}"
                )
        with evidence_col:
            with st.expander("Evidence, assumptions and resources", expanded=True):
                st.markdown("**Confirmed facts**")
                st.write(answers.get("confirmed_facts") or "No additional confirmed facts were added.")
                st.markdown("**Assumptions to validate**")
                st.write(answers.get("assumptions_for_review") or "No additional assumptions were added.")
                st.markdown("**Stated resources**")
                st.write(answers.get("resources") or "No resource information supplied.")

        st.markdown("---")
        st.subheader("LLM-as-judge scores")
        for row_start in range(0, len(evaluator.CRITERIA), 5):
            metric_cols = st.columns(5)
            for col, crit in zip(metric_cols, evaluator.CRITERIA[row_start:row_start + 5]):
                col.metric(crit.replace("_", " ").title(), scores.get(crit, 0))

        with st.expander("What each score means and how to improve it"):
            for criterion in evaluator.CRITERIA:
                score = scores.get(criterion, 0)
                status = "strong" if score >= 4 else "needs improvement"
                st.markdown(
                    f"- **{criterion.replace('_', ' ').title()} ({score}/5 — {status}):** "
                    f"{CRITERION_GUIDANCE[criterion]}"
                )

        avg_col, verdict_col = st.columns(2)
        avg_col.metric("Average", scores.get("average", 0))
        verdict = scores.get("verdict", "")
        verdict_render = {
            evaluator.VERDICT_USEFUL: verdict_col.success,
            evaluator.VERDICT_EDITS: verdict_col.warning,
            evaluator.VERDICT_NOT_USEFUL: verdict_col.error,
        }.get(verdict, verdict_col.info)
        verdict_render(f"Verdict: {verdict}")

        if scores.get("comment"):
            st.info(f"Evaluator comment: {scores['comment']}")
        if scores.get("judge_model"):
            st.caption(f"Independent judge model: `{scores['judge_model']}`")
        if scores.get("validation_issues"):
            st.warning(
                "Completion checks found: " + "; ".join(scores["validation_issues"])
            )
        if scores.get("timeline_validation"):
            timeline_check = scores["timeline_validation"]
            st.caption(
                f"Evaluator {scores.get('evaluator_version', '')} · Strategy {scores.get('strategy_hash', '')} · "
                f"Timeline coverage: {timeline_check['timeline_coverage']}% · "
                f"{timeline_check['timeline_validation_reason']}"
            )
        st.caption(
            "Automated LLM-as-judge assessment against the formal rubric v2.0 (docs/evaluation_rubric.md): "
            "clarity, relevance, actionability, resource-appropriateness, coherence, strategic value, "
            "data integrity, persona quality, timeline quality, KPI quality. Relevance and "
            "resource-appropriateness are MUST-PASS gates. Review the strategy and use the human form below; "
            "the automated score is evidence, not a guarantee of correctness."
        )

        st.markdown("---")
        st.subheader("Human evaluation")
        st.caption(
            "Use the 5-point agreement scale to assess two distinct layers: the "
            "strategy output and your experience of using the service."
        )

        # Keeping the two layers separate prevents a smooth interface from
        # inflating the measured quality of a strategy (or vice versa).
        evaluation_sections = {
            "Strategy output": [
                "The strategy is clearly written and easy to follow.",
                "The strategy is specific to this organisation's context, audiences and objectives.",
                "The recommendations are concrete enough to act on immediately.",
                "The recommendations are realistic for the stated budget, team and timeframe.",
                "The messages and channels are tailored to the priority audiences.",
                "The timeline and KPIs provide a credible way to deliver and measure the strategy.",
                "Overall, this is a useful strategic communications plan for this organisation.",
            ],
            "Service and process experience": [
                "The questionnaire made it clear what information was needed.",
                "The time and effort required to provide the information felt appropriate.",
                "Uploading or entering supporting information was straightforward.",
                "The process made it clear how my inputs informed the generated strategy.",
                "I would feel confident using this service again or recommending it to a colleague.",
            ],
        }

        likert_options = get_likert_scale()

        # Store human evaluation responses in session state
        if "human_eval" not in st.session_state:
            st.session_state.human_eval = {}

        if st.button("Clear human evaluation ratings"):
            for key in list(st.session_state):
                if key.startswith("likert_v2_"):
                    del st.session_state[key]
            st.session_state.human_eval = {}
            st.rerun()

        question_number = 0
        for section, statements in evaluation_sections.items():
            st.markdown(f"#### {section}")
            for statement in statements:
                question_number += 1
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**{question_number}.** {statement}")
                with col2:
                    response = st.selectbox(
                        f"Rating {question_number}",
                        # The blank option is deliberately not a Likert value.
                        # This prevents unanswered questions being recorded as
                        # "Strongly Disagree" and falsely lowering the result.
                        options=[None, *likert_options],
                        format_func=lambda option: "Select a rating…" if option is None else option,
                        key=f"likert_v2_{section}_{question_number}",
                        label_visibility="collapsed",
                    )
                    st.session_state.human_eval[question_number] = {
                        "layer": section,
                        "statement": statement,
                        "response": response,
                        "value": get_likert_value(response),
                    }

        answered_count = sum(
            response["value"] > 0
            for response in st.session_state.human_eval.values()
        )
        if answered_count < question_number:
            st.caption(
                f"{answered_count} of {question_number} ratings completed. "
                "Select a rating for every statement to see the summary."
            )

        # Report averages separately only once every rating is intentional.
        if answered_count == question_number:
            st.markdown("---")
            st.subheader("Evaluation summary")
            summary_cols = st.columns(2)
            for col, section in zip(summary_cols, evaluation_sections):
                values = [
                    response["value"]
                    for response in st.session_state.human_eval.values()
                    if response["layer"] == section and response["value"] > 0
                ]
                if values:
                    col.metric(f"{section} average", f"{sum(values) / len(values):.2f} / 5.00")

            # Distribution across the form, retained as supporting context.
            dist = {}
            for v in st.session_state.human_eval.values():
                label = v["response"]
                dist[label] = dist.get(label, 0) + 1

            st.markdown("**Response distribution:**")
            for option in likert_options:
                count = dist.get(option, 0)
                st.markdown(f"- {option}: {count}")

    with tab_cost:
        st.subheader("Token usage & cost (per strategy)")
        rows = []
        for c in cost_report["calls"]:
            u, cc = c["usage"], c["cost"]
            model_disp = (
                f"{u.model} → priced as {cc['priced_model']}"
                if u.provider == "mock" else u.model
            )
            rows.append({
                "Call": c["label"],
                "Model": model_disp,
                "Input tokens": f"{u.input_tokens:,}",
                "Output tokens": f"{u.output_tokens:,}",
                "Cost (USD)": f"${cc['total_cost']:.5f}",
            })
        rows.append({
            "Call": "TOTAL (per strategy)",
            "Model": "",
            "Input tokens": f"{cost_report['total_input_tokens']:,}",
            "Output tokens": f"{cost_report['total_output_tokens']:,}",
            "Cost (USD)": f"${cost_report['total_cost']:.5f}",
        })
        st.table(rows)

        m1, m2, m3 = st.columns(3)
        m1.metric("Total tokens", f"{cost_report['total_tokens']:,}")
        m2.metric(
            "Est. cost / strategy" if cost_report["estimated"] else "Cost / strategy",
            f"${cost_report['total_cost']:.4f}",
        )
        m3.metric("Provider", gen_usage.provider)

        if cost_report["estimated"]:
            st.info(
                "Running in **mock mode**: token counts are estimated (~4 chars/token) "
                f"and priced as if run on `{cost.MOCK_REFERENCE_MODEL}`. **$0 is actually "
                "charged** — connect a real API key for live token counts and cost."
            )
        if cost_report["has_unknown_price"]:
            st.warning(
                "A model used has no entry in the pricing table — its cost is shown as $0. "
                "Add it to `src/cost.py` → `PRICING`."
            )
        st.caption(
            f"Pricing last updated {cost_report['pricing_last_updated']} "
            "(USD per 1M tokens). A strategy = one generation call + one evaluation call. "
            "See `docs/cost_model.md` for the full cost model."
        )

    with tab_experiments:
        st.subheader("Download report")
        st.caption("Download the completed strategy in an editable Word file or a shareable PDF.")
        export_cols = st.columns(2)
        export_cols[0].download_button(
            "⬇ Download Word report", word_data,
            file_name=f"{fname}_strategy.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="download_word_export_tab",
        )
        export_cols[1].download_button(
            "⬇ Download PDF report", pdf_data,
            file_name=f"{fname}_strategy.pdf",
            mime="application/pdf",
            key="download_pdf_export_tab",
        )

    with tab_prompt:
        st.caption("The exact prompt assembled by the knowledge tree + prompt builder:")
        st.code(prompt, language="text")


if __name__ == "__main__":
    main()
