# AISCE Token Cost Model (TOKEN COST ANALYSIS)

**Status:** Implemented. Every run of the app now reports, for each generated
strategy: **which model was used, how many input/output tokens it consumed, and
how much it cost.** This document is the cost-model deliverable: the formula, the
assumptions, where the numbers come from, and representative per-strategy
estimates across models.

- **Pricing table:** `src/cost.py` → `PRICING` (USD per 1M tokens). Last updated **2026-06-04**.
- **Token capture:** `src/llm_client.py` → returns a `cost.Usage` (provider, model, input/output tokens) from every call.
- **Aggregation:** `src/cost.py` → `summarize()` (generation + evaluation = per strategy).
- **Display:** `app.py` → compact caption + the **💰 Token & Cost** tab.

---

## 1. What counts as the cost of one strategy

Each strategy triggers **two LLM calls**:

| Call | Where | Purpose | Typical size |
|---|---|---|---|
| **Generation** | `llm_client.generate_with_usage()` via `full_strategy.txt` | Produce the 10-section v4 plan | larger output |
| **Evaluation** | `evaluator.evaluate()` via `evaluation.txt` (LLM-as-judge) | Score against the rubric v2.0 | small output (JSON) |

> **Cost per strategy = generation cost + evaluation cost.** Both are tracked and
> summed; the app shows the breakdown and the total.

## 2. The formula

For each call, with prices in USD per 1,000,000 tokens:

```
call_cost   = input_tokens/1e6 * input_rate(model)
            + output_tokens/1e6 * output_rate(model)

strategy_cost = generation_call_cost + evaluation_call_cost
```

Token counts come straight from the provider's API response
(`usage_metadata.prompt_token_count` / `candidates_token_count` for Gemini;
`usage.input_tokens` / `output_tokens` for Anthropic;
`usage.prompt_tokens` / `completion_tokens` for OpenAI). In **mock mode** there is
no API call, so tokens are estimated at ~4 characters/token and priced *as if*
run on the reference model (`claude-sonnet-4-6`) — clearly flagged as an
estimate, with **$0 actually charged**.

## 3. Pricing table (USD per 1M tokens)

| Model | Input | Output | Source |
|---|---|---|---|
| **Gemini 2.5 Pro (`gemini-2.5-pro`)** | $1.25 | $10.00 | Google |
| **Gemini 2.5 Flash (`gemini-2.5-flash`)** | $0.30 | $2.50 | Google |
| **Gemini 2.0 Flash (`gemini-2.0-flash`) — app default** | **$0.10** | **$0.40** | Google |
| Gemini 2.0 Flash-Lite (`gemini-2.0-flash-lite`) | $0.075 | $0.30 | Google |
| Gemini 1.5 Pro (`gemini-1.5-pro`) | $1.25 | $5.00 | Google |
| Gemini 1.5 Flash (`gemini-1.5-flash`) | $0.075 | $0.30 | Google |
| Claude Sonnet 4.6 (`claude-sonnet-4-6`) | $3.00 | $15.00 | Anthropic |
| OpenAI `gpt-4o-mini` | $0.15 | $0.60 | OpenAI *(verify)* |

> Prices change. Update `src/cost.py` → `PRICING` and bump `PRICING_LAST_UPDATED`.
> Gemini figures verified 2026-06-04 at ai.google.dev/gemini-api/docs/pricing.

## 4. Representative per-strategy estimate

Assumptions for a typical AISCE run (the three ground-truth cases land near these):

| Call | Input tokens | Output tokens |
|---|---|---|
| Generation | ~1,200 | ~2,500 |
| Evaluation | ~1,800 | ~200 |
| **Per strategy** | **~3,000** | **~2,700** |

Applying the formula gives the estimated **cost per strategy** by model:

| Model | Input cost | Output cost | **Total / strategy** | Strategies per $1 |
|---|---|---|---|---|
| Gemini 2.0 Flash (default) | $0.0003 | $0.0011 | **≈ $0.0014** | ~700 |
| Gemini 2.0 Flash-Lite | $0.0002 | $0.0008 | **≈ $0.0010** | ~1,000 |
| Gemini 2.5 Flash | $0.0009 | $0.0068 | **≈ $0.0077** | ~130 |
| Gemini 1.5 Flash | $0.0002 | $0.0008 | **≈ $0.0010** | ~1,000 |
| Gemini 2.5 Pro | $0.0038 | $0.0270 | **≈ $0.0308** | ~32 |
| Claude Sonnet 4.6 | $0.0090 | $0.0405 | **≈ $0.0495** | ~20 |
| OpenAI gpt-4o-mini | $0.0005 | $0.0016 | **≈ $0.0021** | ~470 |

> These are **estimates for planning**. The app reports the **actual** figure per
> run from real token counts — output length varies with persona and detail, and
> output tokens dominate cost (rates are higher for output), so a longer plan
> costs more.

### Reading the table

- The default **Gemini 2.0 Flash** costs roughly **0.14 cents per strategy** —
  extremely cheap for a prototype and for user-testing dozens of strategies.
- **Flash-Lite / 1.5 Flash** are even cheaper if cost matters more than depth;
  **2.5 Pro** costs more but suits the hardest cases.
- A full evaluation pass over, say, 50 strategies × 3 models stays well under
  a few dollars at Flash tiers.

## 5. How to extend

- **New model** → add a `model_id: (input_rate, output_rate)` row to `PRICING`.
- **Prompt caching** (future) → not modelled yet because the app sends fresh
  prompts each run.
- **Batch API** (future) → could be a per-call multiplier.