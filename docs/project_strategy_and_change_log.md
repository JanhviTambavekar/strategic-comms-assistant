# AI-Driven Strategic Communications Assistant — Project Strategy and Change Log

**Project:** 6G7V0007 MSc Project 06  
**Client:** Scientia Scripta  
**Status:** Living implementation and evaluation record

This is the single consolidated document for the project strategy, research
approach, implemented changes and remaining work.

## 1. Project aim

Design, develop and evaluate an AI-enabled online system that produces tailored
strategic communication and engagement plans for research organisations,
university spin-outs and SME innovators.

The project is evaluated as a structured human-AI workflow, not merely as a
text-generation application.

## 2. Core research question

> Can a structured, persona-driven LLM workflow produce strategic communication
> plans that are more relevant, actionable and resource-appropriate than a
> generic prompt for small research and innovation-led organisations?

Supporting questions:

1. How does structured prompt design affect strategy quality compared with a
   generic prompt?
2. How do selected LLMs differ in quality, reliability, cost and consistency?
3. Does the workflow produce useful, credible and usable outputs for the three
   client personas?
4. Can deterministic validation plus human review catch important LLM failures?

## 3. Recommended evaluation design

Use the same synthetic client briefs across all experimental conditions.

| Dimension | Recommended comparison |
|---|---|
| Prompt | Generic baseline prompt vs structured AISCE prompt |
| Persona | Research project, University spin-out, SME innovator |
| Model | At least two, ideally three, available LLMs |
| Review | Automated rubric, deterministic checks and human review |
| Cost | Input/output tokens and estimated cost per strategy |

For every generated strategy, retain:

- Client brief and persona
- Model, model version and provider
- Prompt version
- Generated strategy
- LLM-as-judge scores and comment
- Deterministic validation results
- Human reviewer ratings and qualitative comments
- Token use and cost
- Noted failure modes and corrective prompt iteration

## 4. Current workflow

```text
Client questionnaire + uploaded brief
        ↓
Persona selection and knowledge-tree routing
        ↓
Standardised AISCE prompt construction
        ↓
LLM strategy generation
        ↓
Deterministic timeline/KPI/completion validation
        ↓
LLM-as-judge rubric assessment
        ↓
Human output review + process-experience review
        ↓
Prompt and workflow refinement
```

## 5. Implemented artefact features

- Three client personas: Research Project Team, University Spin-out and SME
  Innovator.
- Structured questionnaire and brief upload/extraction.
- Persona-aware knowledge-tree routing and prompt assembly.
- Standardised ten-section AISCE strategy prompt.
- Multi-provider LLM client, mock mode, cost and token reporting.
- LLM-as-judge rubric with ten criteria and verdict gates.
- Strategy download and prompt transparency view.
- Two-layer human evaluation form: strategy-output quality and service/process
  experience.

## 6. Implemented strategy-output improvements

### 6.1 Clarity and decision-readiness

The strategy prompt now requires:

- Plain language for a non-specialist founder/client.
- No duplicated headings, tables or repeated material.
- Evidence-led claims; unsupported marketing terms are prohibited.
- Every recommendation to identify what to do, audience, owner, timing,
  cost/trade-off and success measure.
- Unknown facts or figures to be marked as assumptions and validated in Months
  1-3.

### 6.2 Source integrity

The prompt prohibits treating unconfirmed organisations, partnerships, pilots,
regulatory dialogue, conferences or performance claims as facts. Such items must
be grounded in client information or labelled as assumptions/illustrative
examples.

### 6.3 Complete 36-month timeline

The strategy generator uses a 5,000-token output allowance. The prompt requires
a single Month 1-36 table and requires every audience cell to include:

```text
Task: ...
AIDA: Attention / Interest / Desire / Action
Channel/message: ...
```

### 6.4 KPI quality

The prompt requires audience-tagged, measurable KPI targets. It prohibits
invented baselines, markets, reach or conversion rates. Unknown measures must be
recorded as a Month 1-3 baseline-setting task. Reach × conversion arithmetic
must reconcile with the stated absolute target.

## 7. Evaluation framework

### 7.1 Automated rubric

The LLM-as-judge scores these criteria from 1 to 5:

1. Clarity
2. Relevance — must-pass
3. Actionability
4. Resource appropriateness — must-pass
5. Coherence
6. Strategic value
7. Data integrity
8. Persona quality
9. Timeline quality
10. KPI quality

The LLM judge is evidence, not proof of correctness. Its results must be
reviewed alongside deterministic checks and human feedback.

### 7.2 Deterministic validation

The evaluator is versioned as `2.1` and adds strategy hash metadata. It checks:

- Mandatory output sections and headings
- Meaningful Month 1-36 coverage, rather than a bare statement of “36 months”
- Gaps in timeline coverage
- Presence of AIDA and channel/message detail in timeline periods
- KPI measurability, timeframe and audience link
- KPI reach/conversion arithmetic where supplied
- Large unstructured or malformed text blocks

An LLM cannot override these checks. Incomplete timelines or invalid KPIs cap
the relevant scores before the final verdict is calculated.

### 7.3 Human evaluation

The application uses a five-point agreement scale:

1. Strongly Disagree
2. Disagree
3. Neither Agree nor Disagree
4. Agree
5. Strongly Agree

Human ratings are intentionally split into two layers:

| Layer | What it measures |
|---|---|
| Strategy output | Clarity, tailoring, actionability, feasibility, messages/channels, timeline/KPIs and overall usefulness |
| Service/process | Questionnaire clarity, effort, document handling, transparency and confidence to reuse |

The two averages must be reported separately.

## 8. Automated test coverage

`tests/test_evaluator.py` verifies:

1. A complete, meaningful 36-month timeline qualifies for full coverage.
2. A timeline missing Year 3 is reduced.
3. A bare “36 months” claim fails.
4. Large timeline gaps fail.
5. A complete timeline plus measurable KPIs passes.
6. An optimistic all-5 LLM response cannot override a missing Year 3.

Run tests with:

```powershell
python -m unittest discover -s tests -v
python -m py_compile app.py src\evaluator.py src\llm_client.py
```

## 9. Recommended experimental output table

| Run ID | Persona | Prompt | Model | Cost | LLM score | Timeline coverage | KPI valid | Human output rating | Process rating | Notes |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Example | Spin-out | AISCE v4 | Model name | $0.00 | 0.0 | 100% | Yes/No | 0.0 | 0.0 | Failure/correction notes |

## 10. Priorities for a strong final submission

1. Complete controlled prompt/model/persona comparisons.
2. Obtain and document Scientia Scripta feedback on selected strategy outputs.
3. Report human ratings separately from LLM-as-judge ratings.
4. Include failures caught by validation as reliability evidence.
5. Present cost and token comparisons.
6. Document Agile prompt iterations, what failed and what was changed.
7. Keep agentic interview functionality as an optional future extension; a
   reliable, well-evaluated linear workflow is more important.

## 11. Remaining work

- Run the controlled multi-model experiment and populate the evidence table.
- Obtain human feedback for HelioSera and People’s Panel outputs.
- Compare generic and AISCE prompts on the same briefs.
- Add results, limitations and ethical considerations to the dissertation.
- Ensure reviewers restart the application after code changes:

```powershell
Ctrl+C
python -m streamlit run app.py
```

## 12. Dashboard and experiment enhancements implemented

- **Persona-mismatch warning:** the app suggests a persona from the explicit
  respondent type (or questionnaire/document keywords) and warns when it does
  not match the selected persona.
- **Confirmed facts and assumptions:** the intake form now captures these in
  separate fields and passes them to the strategy prompt with distinct labels.
- **Strategy readiness panel:** the Evaluation Dashboard now displays client
  readiness, timeline coverage/detail, KPI validation and specific corrective
  actions before the LLM-as-judge metrics.
- **Resource and KPI tables:** the strategy prompt requires a resource-allocation
  table and an operational KPI table with owner, baseline/source, measurement
  tool and review cadence.
- **Experiment and export dashboard:** each generated strategy is recorded for
  the browser session with model, prompt, persona, score, validation, token and
  cost data. Runs can be downloaded as CSV or JSON for multi-model analysis.
- **Decision-support dashboard:** the evaluation view now gives a client-ready
  status, the three highest-priority fixes, expandable score guidance, timeline
  and KPI-health diagnostics, and an evidence/assumptions/resources trace.

## 13. Client evidence and assumptions guidance

The intake form now includes two optional fields to improve traceability and
reduce unsupported LLM claims.

| Field | What the user provides | How the strategy uses it |
|---|---|---|
| **Confirmed facts to use as evidence** | Reliable, approved information from the questionnaire, uploaded documents, internal records, CRM, funding documents, pilot records or approved public material | May be stated as evidence in the strategy |
| **Assumptions / facts to validate** | Unknown, future, planned or uncertain information | Must be labelled as an assumption and converted into a validation task, normally in Months 1-3 |

Examples of confirmed facts include a named pilot deployment, a completed funding
round, approved budget, verified technical-performance figure, location, or an
existing relationship. Examples of assumptions include an unknown CRM baseline,
unconfirmed public use of a partner name, future regulatory approval, a proposed
budget allocation, or an unverified market/conversion estimate.

The distinction is deliberately simple:

```text
Confirmed facts = safe to state as true.
Assumptions to validate = do not state as true until checked.
```

For the HelioSera synthetic case, the confirmed-evidence field can contain
Imperial College collaboration, BASF pilot deployment, Port of Rotterdam
initiative, early UK Environment Agency engagement, Series A funding,
parts-per-billion-range sensitivity, £40k annual communications budget and the
listed London/Germany/Netherlands/Kenya activity. Assumptions include baseline
enquiry volumes, number of current pilots, public permission to name BASF,
communications owners, detailed budget allocation, addressable-market figures,
future regulatory milestones and future commercial-readiness claims.

## 14. Independent model generation and judging

When NVIDIA NIM is configured, the sidebar provides separate selectors for the
strategy-generation model and the independent evaluation model. Current choices
are Meta Llama 3.1 8B Instruct, DiffusionGemma 26B A4B IT, and NVIDIA
Nemotron Mini 4B Instruct. Llama 3.2 1B was removed after repeated hosted
timeouts. Gemma 4 31B, GLM-5.2,
and the retired Qwen3-Next model were removed from the selector. The app
defaults to Llama 3.1 8B for responsive testing, offers Fast draft and Full
quality token budgets, and applies a configurable NVIDIA request timeout.
Nemotron Mini requests are capped at its 1,024-token output limit, use its
recommended `top_p=0.7`, and omit Gemma-only thinking parameters.
Intermittent NVIDIA trial-endpoint timeouts now trigger a controlled fallback
to Llama 3.1 8B. The dashboard warns when fallback occurs and records the model
actually used so exported experiment data remains traceable.
NVIDIA responses with missing or non-string `message.content` are now
normalised safely. If a selected model returns no usable strategy text, the
client retries with the configured fallback instead of passing `None` to the
report formatter.

The selected strategy model generates the plan. The selected judge model scores
that completed plan against the same rubric. The app warns if both selectors use
the same model, because using a different evaluator reduces single-model bias.
Both model names are recorded in the in-session experiment log and CSV/JSON
exports for controlled comparison.

API keys remain in `.env` only and must never be pasted into code, prompts,
exports or documentation. If an API key is accidentally exposed, revoke and
replace it through the provider console.
