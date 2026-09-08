# AI-Driven Strategic Communications Assistant

An MSc software project that generates tailored communication and engagement strategies for researchers, start-ups, and science-led organisations.

[![Live application](https://img.shields.io/badge/Live_application-Render-46E3B7?style=for-the-badge)](https://strategic-comms-assistant.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-ff4b4b)](https://streamlit.io/)

## Overview

The application collects a client persona, questionnaire responses, and an optional brief. It routes this evidence through a knowledge tree, constructs a standardised prompt, generates a ten-section strategy, and evaluates the result against the project rubric.

The deployed comparison panel uses four verified Groq free-tier models and one Gemini free-tier model. NVIDIA trial endpoints were removed from the active pool after repeated hosted-service timeouts.

## Current model panel

| Provider | Model | Intended comparison role |
|---|---|---|
| Groq | Qwen 3.8 27B | Default writer and instruction following |
| Groq | Qwen 3.6 27B | Long-form drafting comparator |
| Groq | GPT-OSS 20B | Fast structured-output comparator |
| Groq | GPT-OSS 120B | Higher-capacity reasoning comparator |
| Google | Gemini 3.5 Flash Lite | Cross-provider fallback/comparator |

Model availability and free-tier limits are controlled by providers and may change. No API keys are stored in this repository.

## Features

- Three client personas: researcher, university spin-out, and innovative SME
- Persona-specific questionnaires and optional document upload
- Knowledge-tree routing and transparent prompt construction
- Ten-section strategic communications report
- Quick mode with one model request and deterministic local evaluation
- Detailed mode with an independently selectable LLM judge
- Bounded cross-provider failover and labelled offline demonstration fallback
- Token, model, latency, and estimated-cost recording
- Evaluation rubric with ten criteria and mandatory quality gates

## Architecture

```text
Streamlit UI -> input and document extraction -> persona classification
             -> knowledge-tree routing -> prompt construction
             -> free-model pool -> strategy formatting and evaluation
```

## Local setup

Python 3.11 or later is recommended.

```powershell
git clone https://github.com/JanhviTambavekar/strategic-comms-assistant.git
cd strategic-comms-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

For live generation, edit `.env`:

```dotenv
LLM_PROVIDER=free
GROQ_API_KEY=your_key_here
GROQ_MODEL=qwen/qwen3.8-27b
GROQ_REQUEST_TIMEOUT=30
```

Run the application:

```powershell
streamlit run app.py
```

Open http://localhost:8501. With no API key, use `LLM_PROVIDER=mock` for the offline workflow.

## Model comparison workflow

For a fair report comparison:

1. Keep the persona, questionnaire responses, evidence, prompt, mode, and token budget fixed.
2. Select a different strategy model for each run.
3. Keep the judge and evaluation settings constant.
4. Record output, score, latency, tokens, fallback status, and provider errors.
5. Repeat each condition because free endpoints vary in load and output.

See [`docs/model_comparison.md`](docs/model_comparison.md) for the protocol, measurements, limitations, and results template.

## Testing

```powershell
python -m unittest discover -s tests -q
```

## Project structure

```text
strategic-comms-assistant/
|-- app.py                    Streamlit UI and pipeline orchestration
|-- config/                   Persona and questionnaire configuration
|-- data/sample_uploads/      Synthetic demonstration briefs
|-- docs/                     Design, evaluation, and research documentation
|-- ground_truth/             Worked examples and reference outputs
|-- prompts/                  Standardised prompt templates
|-- src/                      Routing, LLM, extraction, formatting, evaluation
|-- tests/                    Automated unit tests
|-- render.yaml               Render deployment blueprint
`-- PROJECT_UPDATES.md        Chronological implementation record
```

## Reproducibility and security

- Local secrets belong in `.env`, which is ignored by Git.
- Render secrets are environment variables marked `sync: false` in the blueprint.
- Quick mode uses local evaluation to reduce latency and avoid a second request.
- Offline fallback results are labelled and must not be counted as live-model results.
- `main` deploys automatically to Render; free instances may cold-start after inactivity.

Live application: https://strategic-comms-assistant.onrender.com

## Academic artefacts

| Artefact | Location |
|---|---|
| AISCE prompt template | `prompts/full_strategy.txt`, `docs/AISCE_prompt_template.md` |
| Evaluation rubric | `docs/evaluation_rubric.md`, `src/evaluator.py` |
| Model-comparison protocol | `docs/model_comparison.md` |
| Human evaluation method | `docs/human_evaluation_method.md` |
| Ground-truth examples | `ground_truth/` |
| Cost and token model | `docs/cost_model.md`, `src/cost.py` |
| Development history | `PROJECT_UPDATES.md` |

## Limitations

- Free-tier quotas, model identifiers, and availability may change.
- Outputs require human review before operational use.
- Automated scores are comparative indicators, not proof of effectiveness.
- Offline fallback output is for demonstrations, not model benchmarking.
