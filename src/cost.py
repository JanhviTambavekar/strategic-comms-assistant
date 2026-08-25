"""Token-usage costing for the AISCE pipeline (TOKEN COST ANALYSIS).

Tracks tokens for each LLM call (prompt + output) and converts them to a USD
cost using the pricing table below, so every generated strategy can report:
  - which model was used
  - how many input / output tokens it consumed
  - how much it cost (generation + evaluation = cost per strategy)

PRICES CHANGE. Update PRICING and bump PRICING_LAST_UPDATED when they do.
"""
from dataclasses import dataclass

# When the PRICING table below was last verified.
PRICING_LAST_UPDATED = "2026-06-04"

# USD per 1,000,000 tokens, as (input_per_mtok, output_per_mtok).
# Google Gemini: ai.google.dev/gemini-api/docs/pricing (2026-06-04).
# Anthropic:     platform.claude.com/docs (Claude API reference, 2026-06-04).
# OpenAI:        openai.com/api/pricing — APPROXIMATE, verify before relying on it.
PRICING = {
    # --- Google Gemini ---
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-2.0-flash-lite": (0.075, 0.30),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    # --- Anthropic (Claude) ---
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-4-7": (5.00, 25.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-fable-5": (10.00, 50.00),
    # --- OpenAI (approximate — verify) ---
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    # --- NVIDIA NIM (Google Gemma / Meta Llama via NVIDIA API) ---
    "google/gemma-4-31b-it": (0.20, 0.20),
    "meta/llama-3.1-8b-instruct": (0.10, 0.10),
}

# In mock mode no real model runs, so cost is $0 — but we still want a meaningful
# estimate. Mock usage is priced *as if* it had run on this reference model.
MOCK_REFERENCE_MODEL = "claude-sonnet-4-6"


@dataclass
class Usage:
    """Token usage for a single LLM call."""
    provider: str          # "gemini" | "anthropic" | "openai" | "mock"
    model: str             # model id, or "mock"
    input_tokens: int
    output_tokens: int
    estimated: bool = False  # True when counts are estimated (mock mode)


def price_for(model: str):
    """Return (input_per_mtok, output_per_mtok) for a model, or None if unknown."""
    return PRICING.get(model)


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) for mock mode, where no API
    usage is returned."""
    return max(1, len(text or "") // 4)


def cost_of(usage: Usage) -> dict:
    """Cost of one Usage record.

    Mock usage is priced against MOCK_REFERENCE_MODEL so the figure is meaningful
    offline. Returns input/output/total cost, the model the price came from, and
    whether that model was in the pricing table.
    """
    priced_model = MOCK_REFERENCE_MODEL if usage.provider == "mock" else usage.model
    price = price_for(priced_model)
    if price is None:
        return {
            "input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0,
            "priced_model": priced_model, "known": False,
        }
    in_rate, out_rate = price
    input_cost = usage.input_tokens / 1_000_000 * in_rate
    output_cost = usage.output_tokens / 1_000_000 * out_rate
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "priced_model": priced_model,
        "known": True,
    }


def summarize(usages, labels=None) -> dict:
    """Aggregate several Usage records (e.g. generation + evaluation) into a
    per-strategy cost report.

    `labels` is an optional list of human names aligned with `usages`.
    """
    labels = labels or [f"call {i + 1}" for i in range(len(usages))]
    calls = []
    total_in = total_out = 0
    total_cost = 0.0
    any_estimated = False
    any_unknown = False
    for label, u in zip(labels, usages):
        if u is None:
            continue
        c = cost_of(u)
        calls.append({"label": label, "usage": u, "cost": c})
        total_in += u.input_tokens
        total_out += u.output_tokens
        total_cost += c["total_cost"]
        any_estimated = any_estimated or u.estimated
        any_unknown = any_unknown or not c["known"]
    return {
        "calls": calls,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_tokens": total_in + total_out,
        "total_cost": total_cost,
        "estimated": any_estimated,   # mock — counts/cost are estimates
        "has_unknown_price": any_unknown,
        "pricing_last_updated": PRICING_LAST_UPDATED,
    }
