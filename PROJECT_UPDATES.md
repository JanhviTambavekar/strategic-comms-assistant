# AI-Driven Strategic Communications Assistant — Complete Project Updates

**Project:** MSc Project 06 — Design and Development of an AI-Driven Strategic Communications Assistant  
**Client:** Scientia Scripta  
**Status:** MVP Complete with Multi-Model Evaluation & Dashboard  
**Last Updated:** 2026-09-08

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Core Research Objectives](#core-research-objectives)
3. [System Architecture & Features](#system-architecture--features)
4. [Implemented Strategy Improvements](#implemented-strategy-improvements)
5. [Evaluation Framework](#evaluation-framework)
6. [Dashboard & Experiment Enhancements](#dashboard--experiment-enhancements)
7. [LLM Configuration & Research](#llm-configuration--research)
8. [Deployment & Secrets Management](#deployment--secrets-management)
9. [Automated Testing & Quality Assurance](#automated-testing--quality-assurance)
10. [Remaining Work & Priorities](#remaining-work--priorities)

---

## Project Overview

This project develops an **AI-enabled online system** that produces tailored strategic communication and engagement plans for:
- **Research organizations**
- **University spin-outs**
- **SME innovators**

The system is evaluated as a **structured human-AI workflow**, not merely as a text-generation application.

### What It Demonstrates (maps to proposal)

| Proposal Concept | Implementation Location |
|---|---|
| 3 client personas (research / spin-out / SME) | `config/personas.json` |
| Structured questionnaire + document upload | `app.py`, `src/document_extractor.py` |
| Persona classifier | `src/persona_classifier.py` |
| Knowledge-tree routing mechanism | `src/knowledge_tree.py` |
| Standardised prompt library | `prompts/` |
| Multi-LLM support (Google Gemini + Claude + OpenAI + NVIDIA NIM) | `src/llm_client.py` |
| Strategy report (10-section v4 structure) | `prompts/full_strategy.txt` |
| Evaluation rubric v2.0 (10 criteria + MUST-PASS gates + verdict) | `src/evaluator.py`, `docs/evaluation_rubric.md` |
| Worked ground-truth examples (3 personas) | `ground_truth/` |
| Standardised AISCE prompt template (v4) | `prompts/full_strategy.txt`, `docs/AISCE_prompt_template.md` |
| Human evaluation method (pre-rubric) | `docs/human_evaluation_method.md` |
| Specialist-LLM feasibility note | `docs/specialist_llms.md` |
| Token & cost analysis | `src/cost.py`, `docs/cost_model.md`, 💰 tab in `app.py` |

### System Architecture

```
UI → Input Collector → [Persona Classifier + Document Extractor]
   → Knowledge Tree → Prompt Builder → LLM → Output Formatter
   → [Strategy Report + Evaluation Dashboard]
```

---

## Core Research Objectives

### Primary Research Question

> Can a structured, persona-driven LLM workflow produce strategic communication plans that are more relevant, actionable and resource-appropriate than a generic prompt for small research and innovation-led organisations?

### Supporting Research Questions

1. How does structured prompt design affect strategy quality compared with a generic prompt?
2. How do selected LLMs differ in quality, reliability, cost and consistency?
3. Does the workflow produce useful, credible and usable outputs for the three client personas?
4. Can deterministic validation plus human review catch important LLM failures?

---

## System Architecture & Features

### Input Processing

- **Persona Selection:** Users select from 3 defined personas (Research Project, Spin-out, SME) or receive persona recommendations
- **Questionnaire System:** 31-question structured questionnaires tailored per persona, captured in `config/personas.json`
- **Document Upload & Extraction:** Automatic extraction of client briefs (text, PDF support planned)
- **Evidence & Assumptions Tracking:**
  - **Confirmed facts field:** Reliable, approved information safe to state as evidence
  - **Assumptions field:** Unknown, future, or planned information requiring validation and labelling

### Knowledge Tree & Routing

The knowledge tree mechanism:
- Routes based on: **Persona + Objective + Client Context**
- Selects appropriate: **Prompt Template + LLM Configuration + Output Format**
- Displays routing caption: "Persona X + objective Y → template Z" for transparency

### Standardised Prompt Library

Located in `prompts/`:
- `full_strategy.txt` — AISCE v4 ten-section standardised template
- `messaging_framework.txt` — Message architecture requirements
- `stakeholder_analysis.txt` — Stakeholder mapping & engagement
- `channel_plan.txt` — Channel selection & media strategy
- `evaluation.txt` — LLM-as-judge rubric prompting

### LLM Integration

- **Primary Provider:** Google Gemini (3.5 Flash recommended for cost/quality)
- **Alternatives Supported:**
  - Anthropic Claude (Sonnet 4.6 / Opus 4.8 for quality)
  - OpenAI GPT (GPT-5.5 for structured output)
  - NVIDIA NIM (local inference, Llama 3.1 8B / Nemotron Mini 4B)
- **Mock Mode:** Realistic canned responses (no API key required)
- **Cost Tracking:** Per-strategy token counting and cost estimation

---

## Implemented Strategy Improvements

### 6.1 Clarity and Decision-Readiness

Strategy prompt now mandates:

✅ Plain language for non-specialist founders/clients  
✅ No duplicated headings, tables, or repeated material  
✅ Evidence-led claims; unsupported marketing terms prohibited  
✅ Every recommendation must include:
   - **What to do**
   - **Target audience**
   - **Owner**
   - **Timing**
   - **Cost/trade-off**
   - **Success measure**  
✅ Unknown facts/figures marked as assumptions and converted to validation tasks

### 6.2 Source Integrity

Prompt prohibits treating unconfirmed items as facts:
- ❌ Unconfirmed partnerships
- ❌ Unconfirmed regulatory dialogue
- ❌ Unverified conference/performance claims
- ❌ Unproven pilot results

Such items must be **grounded in client information** or **labelled as assumptions/illustrative examples**.

### 6.3 Complete 36-Month Timeline

- **5,000-token output allowance** (increased from 2,000)
- Mandatory single Month 1-36 table format
- Every audience cell includes:
  ```
  Task: ...
  AIDA: Attention / Interest / Desire / Action
  Channel/message: ...
  ```

### 6.4 KPI Quality Metrics

Requirements:
- ✅ Audience-tagged, measurable KPI targets
- ✅ No invented baselines, markets, or conversion rates
- ✅ Unknown measures recorded as Month 1-3 baseline-setting tasks
- ✅ Reach × conversion arithmetic reconciles with stated absolute target

### 6.5 Resource Allocation Table

New requirement for:
- **Budget allocation** by stream/activity
- **Team requirements** per phase
- **External resource costs** and dependencies
- **Timeline-to-budget reconciliation**

---

## Evaluation Framework

### 7.1 Automated Rubric (LLM-as-Judge)

Scores 10 criteria on a 1–5 scale:

| Criterion | Description |
|---|---|
| 1. **Clarity** | Writing is clear, structured, and easy to follow |
| 2. **Relevance** ⚠️ MUST-PASS | Tailored to organisation's context & objectives |
| 3. **Actionability** | Recommendations are concrete and implementable now |
| 4. **Resource Appropriateness** ⚠️ MUST-PASS | Realistic for stated budget, team, and timeframe |
| 5. **Coherence** | Ideas flow logically; no contradictions |
| 6. **Strategic Value** | Plan creates competitive advantage or mission value |
| 7. **Data Integrity** | Claims supported by evidence; assumptions labelled |
| 8. **Persona Quality** | Tailored to audience (founder/researcher/innovator) |
| 9. **Timeline Quality** | 36-month plan is specific, detailed, and complete |
| 10. **KPI Quality** | KPIs are measurable, realistic, and actionable |

**Must-Pass Gates:** Relevance + Resource Appropriateness = **Useful** verdict only when both pass.

### 7.2 Deterministic Validation (v2.1)

Adds **strategy hash metadata** and checks:

✅ Mandatory output sections and headings present  
✅ Meaningful Month 1-36 coverage (not bare "36 months" claim)  
✅ No gaps in timeline coverage  
✅ AIDA + channel/message detail in timeline periods  
✅ KPI measurability, timeframe, audience link  
✅ KPI reach/conversion arithmetic validation  
✅ Absence of large unstructured/malformed text blocks  

**Key insight:** LLM cannot override deterministic checks. Incomplete timelines or invalid KPIs **cap relevant scores** before final verdict.

### 7.3 Human Evaluation (Two-Layer Likert Scale)

#### Layer A — Strategy Output Quality (7 questions)

Participants rate agreement (1=Strongly Disagree, 5=Strongly Agree):

1. The strategy is clearly written and easy to follow.
2. The strategy is specific to this organisation's context, audiences, and objectives.
3. The recommendations are concrete enough to act on immediately.
4. The recommendations are realistic for the stated budget, team, and timeframe.
5. The messages and channels are tailored to the priority audiences.
6. The timeline and KPIs provide a credible way to deliver and measure the strategy.
7. Overall, this is a useful strategic communications plan for this organisation.

#### Layer B — Service & Process Experience (5 questions)

Participants rate agreement on:

1. The questionnaire made it clear what information was needed.
2. The time and effort required to provide information felt appropriate.
3. Uploading or entering supporting information was straightforward.
4. The process made it clear how my inputs informed the generated strategy.
5. I would feel confident using this service again or recommending it to a colleague.

**Key design choice:** Separate averages reported; never combined into single score.

### Recommended Experimental Table

| Run ID | Persona | Prompt | Model | Cost | LLM Score | Timeline Coverage | KPI Valid | Human Output Rating | Process Rating | Notes |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Example | Spin-out | AISCE v4 | Gemini 3.5 Flash | $0.00 | 0.0 | 100% | Yes | 0.0 | 0.0 | Failure/correction |

---

## Dashboard & Experiment Enhancements

### Dashboard Features Implemented

#### Persona-Mismatch Warning
- App suggests persona from explicit respondent type or questionnaire/document keywords
- Warns if selected persona doesn't match suggestion
- Improves data quality for controlled experiments

#### Strategy Readiness Panel
Pre-LLM-judge assessment displays:
- ✅ Client readiness level
- ✅ Timeline coverage percentage & detail
- ✅ KPI validation status
- ✅ Specific corrective actions if incomplete

#### Experiment & Export Dashboard
- Records each generated strategy with: model, prompt, persona, score, validation, tokens, cost
- **CSV export** for multi-model analysis
- **JSON export** for structured processing
- Browser session persistence

#### Decision-Support View
Evaluation dashboard now provides:
- ✅ Client-ready status indicator
- ✅ Three highest-priority fixes
- ✅ Expandable score guidance
- ✅ Timeline health diagnostics
- ✅ KPI health diagnostics
- ✅ Evidence/assumptions/resources trace

#### Strategy Transparency View
- **Prompt Tab:** Shows exact prompt sent to LLM
- **Routing Caption:** "Persona X + objective Y → template Z"
- **Knowledge Tree Visibility:** Full audit trail of decision logic

### Multi-Model Generation & Evaluation

When NVIDIA NIM configured:
- **Separate selectors** for strategy-generation model and evaluation model
- **Model options:** Llama 3.1 8B, Nemotron Mini 4B (others removed due to timeouts)
- **Token budgets:** Fast draft (lower) vs Full quality (higher)
- **Configurable timeout** for NVIDIA requests
- **Fallback mechanism:** Timeouts trigger controlled fallback to Llama 3.1 8B with warning
- **Response normalization:** Missing/non-string `message.content` handled safely

---

## LLM Configuration & Research

### Fast Free-Model Pool (September 2026)

- Added `LLM_PROVIDER=free` to expose all configured free/free-tier services in one sidebar.
- Added native OpenAI-compatible clients for Groq and OpenRouter alongside Gemini and NVIDIA NIM.
- Strategy generation and independent evaluation can use different providers/models.
- Each distinct free service receives one bounded attempt (`FREE_MODEL_TIMEOUT=12` by default), followed by automatic cross-provider failover. NVIDIA uses one configured fallback rather than walking its full model catalogue.
- Credentials remain local in `.env`; only blank configuration examples are tracked by Git.
- Quick mode now performs one 700-token generation call and runs evaluation locally, removing the second sequential LLM request. Detailed mode retains the full independent LLM judge for research-quality comparisons.
- If every shared free endpoint is rate-limited, unauthorized, or timed out, Quick mode now returns the structured offline strategy instead of terminating the workflow. The UI clearly labels this fallback.
- The model selector shows every NVIDIA model with a configured model-specific credential (six in the current local setup). Non-default models receive a four-second availability window before falling back to verified Nemotron, and unrelated API keys are no longer retried against the wrong endpoint.

### Recommended Production Multi-Model Panel

| Role | Recommended Model | Why |
|---|---|---|
| **Primary / Quality Benchmark** | Claude Sonnet 4.6 | Tops writing-quality leaderboards; best tone control; strong instruction-following |
| **Cost-Efficient Comparator** | Google Gemini 3.5 Flash | Highest creative-writing Elo per pound; **most generous permanent free API tier** |
| **Structured/Analytical** | OpenAI GPT-5.5 | Strongest at structured output; familiar ChatGPT lineage |
| **Open-Weight / Privacy** | Mistral Large 3 or Llama 4 Maverick | Open licence = transparency & reproducibility for academic study |

### Frontier Models Available (June 2026)

#### Anthropic Claude
- **Opus 4.8** — Deepest reasoning (May 2026, $5/$25 per 1M)
- **Sonnet 4.6** — Best quality/cost balance (Feb 2026, $3/$15 per 1M) ⭐
- **Haiku 4.5** — Cheap & fast (Oct 2025, $1/$5 per 1M)
- **Fable 5** — Most capable; 1M context (⚠️ Access suspended June 12 2026)

#### OpenAI GPT
- **GPT-5.5** — Flagship reasoning (Apr 2026)
- **GPT-5.4 mini/nano** — Cost/latency options (Mar 2026)
- **GPT-5.3-Codex** — Coding-focused

#### Google Gemini
- **Gemini 3.1 Pro** — Top reasoning; 2M context
- **Gemini 3.5 Flash** — Near-Pro quality at Flash price ⭐
- **Gemini 3.1 Flash-Lite** — Cheapest, high-volume

#### Open Weights
- **Llama 4 Maverick** — 400B MoE, 1M context, free/self-host
- **Mistral Large 3** — 675B MoE, Apache 2.0, EU-based
- **DeepSeek V4** — 30× cheaper, MIT licence, 1M context

### Free/Low-Cost Access Strategy

| Provider | Free Option | Practical Limit | Card Needed |
|---|---|---|---|
| **Google Gemini** ⭐ | AI Studio free tier (permanent) | ~1,500 req/day Flash, ~50/day Pro | No |
| **Mistral** | Experiment tier | ~1B tokens/month (opt-in data) | No |
| **OpenAI** | GitHub Models / $5 trial | Strict rate limits | Sometimes |
| **Anthropic** | Limited trial credits (Mar 2026) | Small one-off | Yes |
| **OpenRouter** | 20+ free models, one key | 50–1,000 req/day (tiered) | No |

**Budget Stack:** Combine Gemini + OpenRouter + Groq = ~16,900 free requests/day.

---

## Deployment & Secrets Management

### Streamlit Community Cloud Deployment

**Repository:** Public GitHub repo required  
**Entry Point:** `app.py`  
**Assets:** `config/`, `prompts/`, `docs/`, `data/`, `src/` must remain

#### Pre-Deployment Checklist

1. Create **public** GitHub repository (e.g. `strategic-comms-assistant`)
2. Push code with Git:
   ```powershell
   git init
   git add .
   git commit -m "Prepare Streamlit deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/strategic-comms-assistant.git
   git push -u origin main
   ```
   ⚠️ **Do NOT** commit `.env` or `.streamlit/secrets.toml`

#### Deploy Steps

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Select **Create app** → Choose repo & `main` branch
4. Set **Main file path** to `app.py`
5. Open **Advanced settings** → Paste secrets
6. Select **Deploy**

#### Secrets Configuration

Streamlit secrets are exposed as environment variables (no code changes needed).

**Gemini (Recommended)**
```toml
LLM_PROVIDER = "gemini"
GOOGLE_API_KEY = "your-real-key"
GOOGLE_MODEL = "gemini-3.5-flash-lite"
```

**Anthropic**
```toml
LLM_PROVIDER = "anthropic"
ANTHROPIC_API_KEY = "your-real-key"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
```

**OpenAI**
```toml
LLM_PROVIDER = "openai"
OPENAI_API_KEY = "your-real-key"
OPENAI_MODEL = "gpt-4o-mini"
```

**NVIDIA NIM**
```toml
LLM_PROVIDER = "openai"
OPENAI_BASE_URL = "https://integrate.api.nvidia.com/v1"
OPENAI_API_KEY = "your-real-key"
```

#### Deployment Notes

- ✅ No database or filesystem write required
- ✅ Briefs processed in-memory for active session only
- ⚠️ Public visitors incur API charges against project owner's account
- ⚠️ Streamlit Cloud hosted in US; consider data-handling obligations

---

## Automated Testing & Quality Assurance

### Test Coverage

`tests/test_evaluator.py` verifies:

✅ Complete, meaningful 36-month timeline qualifies for full coverage  
✅ Timeline missing Year 3 is reduced  
✅ Bare "36 months" claim fails deterministic check  
✅ Large timeline gaps fail  
✅ Complete timeline + measurable KPIs passes  
✅ Optimistic LLM response (all-5s) cannot override missing Year 3  

### Running Tests

```powershell
# Run unit tests
python -m unittest discover -s tests -v

# Compile-check critical modules
python -m py_compile app.py src\evaluator.py src\llm_client.py
```

---

## Remaining Work & Priorities

### High Priority — Experiment Phase

1. **Run controlled multi-model experiment**
   - Compare: Generic prompt vs AISCE v4 prompt
   - Personas: Research, Spin-out, SME (on same synthetic briefs)
   - Models: Gemini 3.5 Flash, Claude Sonnet 4.6, GPT-5.5
   - Populate evidence table with results

2. **Obtain human feedback**
   - HelioSera Round 2 strategies (existing)
   - People's Panel review (Edwin's batch)
   - Apply two-layer evaluation form consistently

3. **Comparative cost analysis**
   - Compile tokens, pricing, cost per strategy by model/prompt
   - Include prompt engineering iteration costs

4. **Failure documentation**
   - Record failures caught by deterministic validation
   - Use as reliability evidence in dissertation

### Medium Priority — Refinement

5. Document prompt iteration history: what failed, what was changed
6. Ensure reviewers restart app after code changes (`Ctrl+C` → rerun)
7. Implement optional agentic interview extension (future-proof architecture)

### Dissertation Submission

8. Add Results, Limitations, and Ethical Considerations sections
9. Report human ratings **separately** from LLM-as-judge ratings
10. Include cost-efficiency and token comparisons
11. Present controlled experiment design and findings
12. Discuss reliability evidence (failures caught by validation)

---

## Project Structure Reference

```
strategic-comms-assistant/
├── app.py                          # Streamlit UI & pipeline orchestration
├── config/
│   └── personas.json               # 3 personas + 31-question questionnaires
├── prompts/
│   ├── full_strategy.txt           # AISCE v4 template (main)
│   ├── messaging_framework.txt
│   ├── stakeholder_analysis.txt
│   ├── channel_plan.txt
│   └── evaluation.txt              # LLM-as-judge rubric
├── data/
│   └── sample_uploads/             # Synthetic demo briefs per persona
├── ground_truth/                   # Task 4: Worked input→output examples
│   ├── 01_research_tidalcarbon/
│   ├── 02_spinout_neurosight/
│   └── 03_sme_greencrate/
├── docs/
│   ├── AISCE_prompt_template.md
│   ├── cost_model.md
│   ├── evaluation_rubric.md
│   ├── human_evaluation_method.md
│   ├── likert_scale.md
│   ├── project_strategy_and_change_log.md
│   └── specialist_llms.md
├── src/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── cost.py
│   ├── document_extractor.py
│   ├── evaluator.py
│   ├── knowledge_tree.py
│   ├── likert_scale.py
│   ├── llm_client.py
│   ├── output_formatter.py
│   ├── persona_classifier.py
│   ├── prompt_builder.py
│   ├── questionnaire_parser.py
│   └── report_exporter.py
├── tests/
│   ├── test_evaluator.py
│   └── test_llm_response_handling.py
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── LLM_RESEARCH.md
└── render.yaml                     # Render.com deployment config
```

---

## Key Metrics & Evaluation Dimensions

### Quality Dimensions (LLM-as-Judge + Human Review)

- **Clarity:** Writing quality, structure, readability
- **Relevance:** Tailoring to organization & context
- **Actionability:** Concreteness, implementability
- **Resource Appropriateness:** Feasibility within constraints
- **Strategic Value:** Competitive advantage, mission value
- **Data Integrity:** Evidence-based claims, assumption labelling
- **Timeline Quality:** Month 1-36 completeness & detail
- **KPI Quality:** Measurability & realism

### Comparative Dimensions

| Dimension | Comparison |
|---|---|
| **Prompt** | Generic baseline vs AISCE structured |
| **Persona** | Research, Spin-out, SME |
| **Model** | Gemini 3.5 Flash, Claude Sonnet 4.6, GPT-5.5 |
| **Review** | LLM-as-judge + Deterministic checks + Human |
| **Cost** | Tokens, pricing, cost per strategy |

---

## Research Evidence & Reliability

### How Reliability Is Assured

1. **Deterministic Validation (v2.1)**
   - Catches incomplete timelines, invalid KPIs, malformed output
   - Prevents false "Useful" verdicts

2. **LLM-as-Judge + Human Review**
   - Independent human ratings on two layers (output + process)
   - Never treat LLM score as ground truth

3. **Systematic Failure Tracking**
   - Record and analyze strategies that fail deterministic checks
   - Use as evidence of reliability mechanism

4. **Multi-Model Comparison**
   - Compare results across Gemini, Claude, OpenAI, open-weight
   - Identify model-specific failure modes

---

## Quick Start Guide

```bash
# 1. Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure (optional)
copy .env.example .env        # Windows
# Edit .env with your LLM provider & key

# 4. Run
streamlit run app.py
```

**App opens at:** http://localhost:8501

### Demo Script (≈2 minutes)

1. Select **SME Innovator** persona
2. Upload `data/sample_uploads/sme_brief.txt` (GreenCrate)
3. Fill questionnaire (or leave partial — upload provides context)
4. Click **Generate strategy**
5. Show tabs: **Strategy Report**, **Evaluation Dashboard**, **Prompt** (transparency)
6. Point out routing caption to show knowledge tree in action

---

## Contact & Documentation

- **Client:** Scientia Scripta
- **Academic Supervisor:** [Your Institution]
- **Project Code:** 6G7V0007
- **Repository:** https://github.com/JanhviTambavekar/strategic-comms-assistant
- **Live App:** https://strategic-comms-assistant.onrender.com

**For questions on:**
- **LLM Selection:** See `LLM_RESEARCH.md`
- **Evaluation Rubric:** See `docs/evaluation_rubric.md`
- **Deployment:** See `DEPLOYMENT.md`
- **Project Strategy:** See `docs/project_strategy_and_change_log.md`

---

*End of Project Updates — Generated 2026-08-31*


