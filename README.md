# AI-Driven Strategic Communications Assistant (MVP)

MSc Project 06 — *Design and Development of an AI-Driven Strategic Communications
Assistant for Researchers, Start-Ups and Science-led Innovators* (client: Scientia Scripta).

This is a minimal, demoable prototype of the system described in the project
proposal. A client selects a **persona**, answers a **questionnaire**,
optionally **uploads a brief**, and the system routes their inputs through a
**knowledge tree** to build a **prompt**, calls an **LLM**, and returns a
**tailored communication & engagement strategy** plus an **evaluation score**.

## What it demonstrates (maps to the proposal)

| Proposal concept | Where it lives |
|---|---|
| 3 client personas (research / spin-out / SME) | `config/personas.json` |
| Structured questionnaire + document upload | `app.py`, `src/document_extractor.py` |
| Persona classifier | `src/persona_classifier.py` |
| Knowledge-tree routing mechanism | `src/knowledge_tree.py` |
| Standardised prompt library | `prompts/` |
| Google Gemini support (primary) + multi-LLM (Claude / OpenAI) | `src/llm_client.py` |
| Strategy report (10-section v4 structure) | `prompts/full_strategy.txt` |
| Evaluation rubric v2.0 (10 criteria + MUST-PASS gates + verdict) | `src/evaluator.py`, `docs/evaluation_rubric.md` |
| Worked ground-truth examples (3 personas) | `ground_truth/` |
| Standardised AISCE prompt template (v4) | `prompts/full_strategy.txt`, `docs/AISCE_prompt_template.md` |
| Human evaluation method (pre-rubric) | `docs/human_evaluation_method.md` |
| Specialist-LLM feasibility note | `docs/specialist_llms.md` |
| Token & cost analysis (model, tokens, cost per strategy) | `src/cost.py`, `docs/cost_model.md`, 💰 tab in `app.py` |

### Architecture (from `diagram.png`)
```
UI → Input Collector → [Persona Classifier + Document Extractor]
   → Knowledge Tree → Prompt Builder → LLM → Output Formatter
   → [Strategy Report + Evaluation Dashboard]
```

## Quick start

```bash
# 1. (optional but recommended) create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. configure (optional — runs in MOCK mode without this)
copy .env.example .env        # Windows  (cp on macOS/Linux)
#  then edit .env and set LLM_PROVIDER + your API key

# 4. run
streamlit run app.py
```

The app opens in your browser at http://localhost:8501.

## Mock mode (no API key needed)

If you don't set an API key, the app runs in **mock mode** and returns a
realistic canned strategy + scores. This means **the demo always works** — useful
for showing the flow to your professor offline. To produce genuinely tailored,
client-specific strategies, add an API key to `.env`:

- **Google Gemini:** set `LLM_PROVIDER=gemini` and `GOOGLE_API_KEY=...` (from https://aistudio.google.com/apikey)
- **Anthropic:** set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=...`
- **OpenAI:** set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...`

## Demo script (≈2 minutes)

1. Pick the **SME Innovator** persona.
2. Upload `data/sample_uploads/sme_brief.txt` (GreenCrate).
3. Fill a couple of questionnaire fields (or leave them — the upload provides context).
4. Click **Generate strategy**.
5. Show the three tabs: **Strategy Report**, **Evaluation Dashboard**, and the
   **Prompt** tab (transparency — shows exactly what the knowledge tree built).
6. Point out the **routing caption** ("Persona X + objective Y → template Z") to
   show the knowledge tree in action.

## Project layout

```
strategic-comms-assistant/
├── app.py                  # Streamlit UI + pipeline wiring
├── config/personas.json    # 3 personas + 31-question questionnaires (the persona system)
├── prompts/                # standardised prompt library (full_strategy.txt = AISCE v4)
├── data/sample_uploads/    # synthetic demo briefs (one per persona)
├── ground_truth/           # Task 4: worked input→prompt→output examples + usefulness eval
├── docs/                   # Tasks 5-8: template spec, human eval method, rubric, specialist-LLM note, live-API setup
└── src/                    # pipeline modules (one per architecture box)
```

## Project artefacts (Tasks 4–8)

| Task | Deliverable | Location |
|---|---|---|
| 4 · Test full prompt→output workflow | 3 ground-truth strategies + pre-rubric usefulness eval | `ground_truth/` |
| 5 · Standardised template prompt | AISCE v4 template + spec | `prompts/full_strategy.txt`, `docs/AISCE_prompt_template.md` |
| 6 · Human evaluation method | Draft criteria framework (Clear/Relevant/Actionable/Resource-appropriate) | `docs/human_evaluation_method.md` |
| 7 · Evaluation rubric | Formal rubric v2.0 (10 criteria, gates, verdict) wired into the judge | `docs/evaluation_rubric.md`, `src/evaluator.py` |
| 8 · Specialist LLMs | Feasibility note + shortlist | `docs/specialist_llms.md` |
| — · Live API | Google Gemini setup | `docs/live_api_setup.md`, `.env` |

## Stretch goal (not in MVP)

The second diagram (`diagram (1).png`) shows an **agentic interview loop**
(gap-analysis → "enough information?" → interview agent). This MVP implements the
linear path; the interview loop is the natural next iteration.