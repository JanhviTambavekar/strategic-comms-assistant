# Free-Model Comparison Protocol

## Purpose

This protocol supports a reproducible comparison of the models available in the Strategic Communications Assistant. It separates measured results from provider claims and prevents offline fallback output from being treated as a model response.

## Comparison set

| ID | Provider | Model | Project role |
|---|---|---|---|
| G1 | Groq | `qwen/qwen3.8-27b` | Default strategy generation |
| G2 | Groq | `qwen/qwen3.6-27b` | Long-form drafting comparison |
| G3 | Groq | `openai/gpt-oss-20b` | Fast structured-output comparison |
| G4 | Groq | `openai/gpt-oss-120b` | Higher-capacity reasoning comparison |
| X1 | Google | `gemini-3.5-flash-lite` | Cross-provider comparison and failover |

The four Groq models offer model-level diversity but share one provider. Gemini supplies a separate infrastructure path.

## Controlled procedure

1. Define a fixed test case for each project persona.
2. Preserve identical inputs and the generated prompt for every model.
3. Run each model at least three times with the same mode and token budget.
4. Use one fixed judge, or only the deterministic local evaluator, throughout.
5. Save the raw output and metadata immediately after every run.
6. Mark failover explicitly and exclude mock outputs from quality averages.
7. Report medians and ranges because shared-service latency varies.

## Measurements

| Measure | Interpretation |
|---|---|
| Live completion rate | Requests returning a usable selected-model response |
| End-to-end latency | Time from submission to completed strategy |
| Input/output tokens | Prompt size and response verbosity |
| Rubric score | Quality indicator under a fixed evaluator |
| Mandatory gates passed | Essential factual and structural compliance |
| Human usefulness | Clarity, relevance, actionability, and resource fit |
| Fallback rate | Runs produced by a model other than the selected one |

## Results template

| Model | Runs | Live success | Median latency | Median rubric | Gate pass rate | Human rating | Fallbacks |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen 3.8 27B | | | | | | | |
| Qwen 3.6 27B | | | | | | | |
| GPT-OSS 20B | | | | | | | |
| GPT-OSS 120B | | | | | | | |
| Gemini 3.5 Flash Lite | | | | | | | |

## Validity considerations

- Provider load and free quotas affect availability and latency independently of model quality.
- Model output is stochastic, so one run is insufficient.
- LLM judging can introduce model-family or stylistic bias.
- Deterministic evaluation is repeatable but cannot fully measure strategic usefulness.
- Human evaluators should be blinded to model identity where practical.
- Record experiment dates and exact model identifiers because catalogues change.
