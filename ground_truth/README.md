# Ground-Truth Workflow Examples (Task 4)

> **Purpose:** A worked, end-to-end record of the *full input → AISCE prompt →
> output strategy* workflow for **all three personas**. These are the
> **ground-truth examples** the project uses to (a) sanity-check that the
> pipeline produces useful strategies and (b) anchor later refinement of the
> prompt template (Task 5) and the evaluation rubric (Tasks 6–7).

## What "running the workflow" means here

This reproduces, by hand, exactly what `app.py` does at runtime:

```
Input script (filled questionnaire + uploaded brief)
   → Persona + objective
   → Knowledge tree  (knowledge_tree.route → "full_strategy")
   → Prompt builder  (prompts/full_strategy.txt filled with the inputs)
   → LLM             (Claude — claude-sonnet-4-6, the system's default model)
   → Output strategy (7-section Markdown plan)
```

Each persona folder contains three files that mirror the three stages:

| File | Pipeline stage it captures |
|---|---|
| `input_script.md` | The complete client input (questionnaire answers + uploaded brief) |
| `assembled_prompt.txt` | The exact prompt the knowledge tree + prompt builder produced |
| `output_strategy.md` | The generated Strategic Communication & Engagement Plan |

## The three ground-truth cases

| # | Persona | Case | Primary objective |
|---|---|---|---|
| 01 | Research Project Team | **TidalCarbon** — blue-carbon restoration research | Secure follow-on funding |
| 02 | University Spin-out | **NeuroSight** — AI diabetic-retinopathy detection | Secure seed funding |
| 03 | SME Innovator | **GreenCrate** — reusable packaging crates | Acquire customers |

> The case briefs are the synthetic samples in `data/sample_uploads/`.

## How these outputs were generated

The system's default LLM is **Claude (`claude-sonnet-4-6`)** — see
`src/llm_client.py`. The outputs in this folder were generated with that same
model family, so they are representative of live system output (not the offline
`mock` placeholder in `llm_client._MOCK_STRATEGY`). To reproduce them live once
an API key is configured:

```bash
streamlit run app.py
# pick the persona → paste the input_script answers → upload the matching brief
# from data/sample_uploads/ → Generate strategy
```

## Informal usefulness evaluation (pre-rubric)

`usefulness_evaluation.md` records a **light-touch, pre-rubric** judgement of how
useful each strategy is. This is deliberately *before* the formal rubric
(Tasks 6–7) — its job is to surface what "good" looks like in practice so the
rubric can be grounded in real examples rather than defined in the abstract.
