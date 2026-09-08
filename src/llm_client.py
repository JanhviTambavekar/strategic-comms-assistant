"""LLM provider abstraction.

Supports Google Gemini, Anthropic, OpenAI and free OpenAI-compatible services,
plus a 'mock' provider that returns
a realistic canned strategy so the project can be demoed with NO API key. The
provider is chosen via the LLM_PROVIDER env var (see .env.example).
"""
import os
import time

from . import cost


class LLMError(Exception):
    """Raised when the LLM provider call fails (auth, rate limit, network, etc.).

    Carries a human-readable message suitable for showing in the UI.
    """


# Statuses worth retrying: 429 (rate limit), 529 (overloaded), 5xx (server).
_RETRYABLE_STATUS = {429, 500, 502, 503, 504, 529}
_MAX_RETRIES = 3

NVIDIA_MODELS = {
    "NVIDIA Nemotron 3.5 Lightning 30B": "nvidia/nemotron-3.5-lightning-30b-a3b",
    "Kimi K3": "moonshotai/kimi-k3",
    "DeepSeek V4 Pro": "deepseek-ai/deepseek-v4-pro-0813",
    "DeepSeek V4 Flash": "deepseek-ai/deepseek-v4-flash-0731",
    "Google DiffusionGemma": "google/diffusiongemma-26b-a4b-it",
    "Google Gemma 4 31B": "google/gemma-4-31b-it",
}

NVIDIA_MODEL_KEY = {
    "nvidia/nemotron-3.5-lightning-30b-a3b": "NVIDIA_NEMOTRON_API_KEY",
    "moonshotai/kimi-k3": "NVIDIA_KIMI_API_KEY",
    "deepseek-ai/deepseek-v4-pro-0813": "NVIDIA_DEEPSEEK_PRO_API_KEY",
    "deepseek-ai/deepseek-v4-flash-0731": "NVIDIA_DEEPSEEK_FLASH_API_KEY",
    "google/diffusiongemma-26b-a4b-it": "NVIDIA_DIFFUSIONGEMMA_API_KEY",
    "google/gemma-4-31b-it": "NVIDIA_GEMMA_API_KEY",
}


def available_free_models() -> dict[str, str]:
    """Return configured no-cost/free-tier targets for the model selectors."""
    models = {}
    if os.getenv("GROQ_API_KEY"):
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        models[f"Groq · {model}"] = f"groq::{model}"
    if os.getenv("OPENROUTER_API_KEY"):
        model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        models[f"OpenRouter · {model}"] = f"openrouter::{model}"
    if os.getenv("GOOGLE_API_KEY"):
        model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash-lite")
        models[f"Gemini · {model}"] = f"gemini::{model}"
    if os.getenv("OPENAI_API_KEY") and "nvidia" in (os.getenv("OPENAI_BASE_URL") or "").lower():
        fallback = os.getenv("NVIDIA_FALLBACK_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
        ordered = [fallback, *NVIDIA_MODELS.values()]
        labels_by_model = {model: label for label, model in NVIDIA_MODELS.items()}
        for model in dict.fromkeys(ordered):
            key_name = NVIDIA_MODEL_KEY.get(model)
            if model == fallback or (key_name and os.getenv(key_name)):
                label = labels_by_model.get(model, model)
                models[f"NVIDIA · {label}"] = f"openai::{model}"
    return models


def nvidia_api_keys(model: str | None = None) -> list[str]:
    """Return configured NVIDIA keys in order, without duplicates."""
    model = model or ""
    model_key_names = []
    if model.startswith("google/diffusiongemma"):
        model_key_names = ["NVIDIA_DIFFUSIONGEMMA_API_KEY", "NVIDIA_GEMMA_API_KEY"]
    elif model == "google/gemma-4-31b-it":
        model_key_names = ["NVIDIA_GEMMA_API_KEY"]
    elif model == "moonshotai/kimi-k3":
        model_key_names = ["NVIDIA_KIMI_API_KEY"]
    elif model == "deepseek-ai/deepseek-v4-pro-0813":
        model_key_names = ["NVIDIA_DEEPSEEK_PRO_API_KEY"]
    elif model == "deepseek-ai/deepseek-v4-flash-0731":
        model_key_names = ["NVIDIA_DEEPSEEK_FLASH_API_KEY"]
    elif model.startswith("nvidia/nemotron-mini"):
        model_key_names = ["NVIDIA_NEMOTRON_API_KEY"]
    elif model.startswith("qwen/"):
        model_key_names = ["NVIDIA_QWEN_API_KEY"]

    names = [
        "NVIDIA_API_KEY_1",
        "NVIDIA_API_KEY_2",
        "NVIDIA_API_KEY_3",
        *model_key_names,
        "OPENAI_API_KEY",
    ]
    keys = []
    for name in names:
        value = (os.getenv(name) or "").strip()
        if value.lower().startswith("bearer "):
            value = value[7:].strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def _message_content_text(message: dict) -> str:
    """Normalise OpenAI-compatible text content without returning None."""
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts).strip()
    return ""


def get_provider() -> str:
    """Resolve the active provider.

    An *explicit* LLM_PROVIDER (gemini/anthropic/openai/mock) is always respected —
    so `LLM_PROVIDER=mock` genuinely forces mock even when an API key happens to be
    present in the environment. Only when LLM_PROVIDER is unset/blank do we
    auto-detect from whichever key is available.
    """
    explicit = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    if explicit in {"free", "groq", "openrouter", "gemini", "anthropic", "openai", "mock"}:
        return explicit
    # No explicit provider -> auto-detect from available keys, else mock.
    if os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY"):
        return "free"
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "mock"


def generate_with_usage(prompt: str, max_tokens: int = 2000, model: str | None = None):
    """Send a prompt to the configured LLM; return (text, cost.Usage).

    The Usage records provider, model and input/output token counts so the
    caller can compute cost (see src/cost.py). Retries transient errors a few
    times, then raises LLMError with a friendly message.
    """
    provider = get_provider()
    target_provider = None
    if model and "::" in model:
        target_provider, model = model.split("::", 1)
    if provider == "free" or target_provider:
        return _free_generate(prompt, max_tokens, preferred_provider=target_provider, model=model)
    if provider == "groq":
        return _with_retries(_groq, prompt, max_tokens, provider="Groq", model=model)
    if provider == "openrouter":
        return _with_retries(_openrouter, prompt, max_tokens, provider="OpenRouter", model=model)
    if provider == "gemini":
        return _with_retries(_gemini, prompt, max_tokens, provider="Gemini", model=model)
    if provider == "anthropic":
        return _with_retries(_anthropic, prompt, max_tokens, provider="Anthropic", model=model)
    if provider == "openai":
        return _with_retries(_openai, prompt, max_tokens, provider="OpenAI", model=model)
    return _mock(prompt)


def _free_generate(prompt: str, max_tokens: int, preferred_provider: str | None, model: str | None):
    """Try configured free services once each, failing over quickly."""
    candidates = []
    if preferred_provider:
        candidates.append((preferred_provider, model))
    seen_providers = {preferred_provider} if preferred_provider else set()
    for target in available_free_models().values():
        provider, candidate_model = target.split("::", 1)
        # Fail over across services, not across a long catalogue on the same
        # hosted service. NVIDIA performs its own single model fallback.
        if provider not in seen_providers:
            candidates.append((provider, candidate_model))
            seen_providers.add(provider)

    errors = []
    handlers = {"groq": _groq, "openrouter": _openrouter, "gemini": _gemini, "openai": _openai}
    for provider, candidate_model in candidates:
        handler = handlers.get(provider)
        if not handler:
            continue
        try:
            return handler(prompt, max_tokens, candidate_model)
        except Exception as exc:  # one attempt per free endpoint keeps latency bounded
            errors.append(f"{provider}: {_status_code(exc) or type(exc).__name__}")
    if not candidates:
        raise LLMError("No free-model API key is configured. Add GROQ_API_KEY, OPENROUTER_API_KEY, GOOGLE_API_KEY, or an NVIDIA key.")
    raise LLMError("All configured free models were unavailable (" + ", ".join(errors) + ").")


def generate(prompt: str, max_tokens: int = 2000, model: str | None = None) -> str:
    """Backward-compatible helper: return only the text response."""
    text, _usage = generate_with_usage(prompt, max_tokens, model=model)
    return text


def _with_retries(fn, prompt: str, max_tokens: int, provider: str, model: str | None = None) -> str:
    last_exc = None
    for attempt in range(_MAX_RETRIES):
        try:
            return fn(prompt, max_tokens, model)
        except Exception as exc:  # noqa: BLE001 - normalised into LLMError below
            last_exc = exc
            status = _status_code(exc)
            if status in _RETRYABLE_STATUS and attempt < _MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # 1s, 2s backoff
                continue
            raise LLMError(_friendly_message(provider, exc, status)) from exc
    # Should be unreachable, but keep the type checker / safety net happy.
    raise LLMError(_friendly_message(provider, last_exc, _status_code(last_exc)))


def _status_code(exc: Exception):
    """Best-effort extraction of an HTTP status code from a provider exception."""
    return getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )


def _friendly_message(provider: str, exc: Exception, status) -> str:
    if "timeout" in type(exc).__name__.lower():
        return (
            f"{provider} did not respond before the configured timeout. "
            "Try Fast draft mode; the app will also retry with Nemotron 3.5 Lightning."
        )
    if status == 401:
        return (f"{provider} rejected the API key (401 Unauthorized). "
                "Check GOOGLE_API_KEY / ANTHROPIC_API_KEY / OPENAI_API_KEY in your "
                "environment or .env, or set LLM_PROVIDER=mock to run without a key.")
    if status == 404:
        return (f"{provider} returned 404 — the model name is likely invalid. "
                "Check GOOGLE_MODEL / ANTHROPIC_MODEL / OPENAI_MODEL.")
    if status == 410:
        return (f"{provider} reports that this model has been retired (410 Gone). "
                "Select a currently available model in the sidebar.")
    if status == 429:
        return f"{provider} rate limit hit (429). Please wait a moment and try again."
    if status in {529, 500, 502, 503, 504}:
        return (f"{provider} is temporarily unavailable ({status}) after several retries. "
                "Please try again shortly.")
    return f"{provider} request failed: {exc}"


def _gemini(prompt: str, max_tokens: int, selected_model: str | None = None):
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = selected_model or os.getenv("GOOGLE_MODEL", "gemini-3.5-flash-lite")
    model_obj = genai.GenerativeModel(model)
    resp = model_obj.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
        ),
        request_options={"timeout": 180},
    )
    text = resp.text

    # Extract token usage from the response if available.
    input_tokens = 0
    output_tokens = 0
    if hasattr(resp, "usage_metadata") and resp.usage_metadata:
        um = resp.usage_metadata
        input_tokens = getattr(um, "prompt_token_count", 0) or 0
        output_tokens = getattr(um, "candidates_token_count", 0) or 0

    usage = cost.Usage(
        provider="gemini", model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    return text, usage


def _anthropic(prompt: str, max_tokens: int, selected_model: str | None = None):
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model = selected_model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in msg.content if hasattr(block, "text"))
    usage = cost.Usage(
        provider="anthropic", model=model,
        input_tokens=getattr(msg.usage, "input_tokens", 0),
        output_tokens=getattr(msg.usage, "output_tokens", 0),
    )
    return text, usage


def _openai(prompt: str, max_tokens: int, selected_model: str | None = None):
    base_url = os.getenv("OPENAI_BASE_URL") or ""
    model = selected_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # NVIDIA NIM API — use requests directly (matches NVIDIA's documented API).
    if "nvidia" in base_url.lower():
        return _nvidia(prompt, max_tokens, base_url, model)

    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=base_url or None)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.choices[0].message.content
    u = getattr(resp, "usage", None)
    usage = cost.Usage(
        provider="openai", model=model,
        input_tokens=getattr(u, "prompt_tokens", 0) if u else 0,
        output_tokens=getattr(u, "completion_tokens", 0) if u else 0,
    )
    return text, usage


def _openai_compatible(prompt: str, max_tokens: int, *, api_key: str, base_url: str,
                       model: str, provider: str):
    """Call a small OpenAI-compatible endpoint with a bounded timeout."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=float(os.getenv("FREE_MODEL_TIMEOUT", "12")), max_retries=0)
    resp = client.chat.completions.create(
        model=model, max_tokens=max_tokens, temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    text = (resp.choices[0].message.content or "").strip()
    if not text:
        raise ValueError(f"{provider} returned no usable text.")
    u = getattr(resp, "usage", None)
    return text, cost.Usage(
        provider=provider, model=model,
        input_tokens=getattr(u, "prompt_tokens", 0) if u else 0,
        output_tokens=getattr(u, "completion_tokens", 0) if u else 0,
    )


def _groq(prompt: str, max_tokens: int, selected_model: str | None = None):
    return _openai_compatible(
        prompt, max_tokens, api_key=os.getenv("GROQ_API_KEY", ""),
        base_url="https://api.groq.com/openai/v1",
        model=selected_model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"), provider="groq",
    )


def _openrouter(prompt: str, max_tokens: int, selected_model: str | None = None):
    return _openai_compatible(
        prompt, max_tokens, api_key=os.getenv("OPENROUTER_API_KEY", ""),
        base_url="https://openrouter.ai/api/v1",
        model=selected_model or os.getenv("OPENROUTER_MODEL", "openrouter/free"), provider="openrouter",
    )


def _nvidia(prompt: str, max_tokens: int, base_url: str, model: str):
    """Call NVIDIA NIM API directly using requests (per NVIDIA's docs)."""
    import requests

    api_keys = nvidia_api_keys(model)
    api_key = api_keys[0] if api_keys else ""

    invoke_url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Accept": "application/json"}
    request_prompt = prompt
    if model == "nvidia/nemotron-mini-4b-instruct" and len(prompt) > 9000:
        # Nemotron Mini has a much smaller practical context budget than the
        # other selectable models. Preserve prompt instructions at the start
        # and the client evidence at the end instead of letting NVIDIA reject
        # the complete request with HTTP 400.
        request_prompt = (
            prompt[:5200]
            + "\n\n[Middle reference material omitted to fit Nemotron Mini's context window.]\n\n"
            + prompt[-3600:]
        )

    payload = {
        "messages": [{"role": "user", "content": request_prompt}],
        "model": model,
        "max_tokens": max_tokens,
        "stream": False,
        # Low temperature keeps long, structured strategies stable on smaller
        # instruction models and reduces unrelated continuation text.
        "temperature": 0.2,
        "top_p": 0.95,
    }
    # Thinking controls are supported by the Gemma endpoint but are not a
    # portable OpenAI-compatible parameter across all NVIDIA-hosted models.
    if model.startswith("google/"):
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    if model == "nvidia/nemotron-mini-4b-instruct":
        payload["max_tokens"] = min(max_tokens, 1024)
        payload["top_p"] = 0.7
    # Do not leave the Streamlit UI waiting indefinitely. The value can be
    # increased in .env for unusually long, full-quality generations.
    timeout_seconds = int(os.getenv("NVIDIA_REQUEST_TIMEOUT", "15"))
    fallback_model = os.getenv(
        "NVIDIA_FALLBACK_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
    ).strip()
    if model != fallback_model:
        timeout_seconds = min(timeout_seconds, int(os.getenv("NVIDIA_EXPERIMENTAL_TIMEOUT", "4")))
    # Fail over sooner for NVIDIA trial models that regularly sit in a shared
    # queue. Llama retains the full configured timeout because it is the
    # reliable fallback target.
    if model == "nvidia/nemotron-mini-4b-instruct":
        timeout_seconds = min(timeout_seconds, 50)
    elif model == "google/diffusiongemma-26b-a4b-it":
        timeout_seconds = min(timeout_seconds, 70)
    response = None
    last_timeout = None
    for candidate_key in api_keys or [""]:
        headers["Authorization"] = f"Bearer {candidate_key}"
        try:
            response = requests.post(
                invoke_url,
                headers=headers,
                json=payload,
                timeout=(10, timeout_seconds),
            )
        except requests.Timeout as exc:
            last_timeout = exc
            # A timeout is a model/endpoint availability problem, not a bad
            # credential. Trying every key repeats the same wait needlessly.
            break
        if response.status_code not in {401, 403, 429}:
            break

    if response is None:
        fallback_model = os.getenv(
            "NVIDIA_FALLBACK_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
        ).strip()
        if model != fallback_model:
            return _nvidia(prompt, max_tokens, base_url, fallback_model)
        if last_timeout is not None:
            raise last_timeout
    # Some Nemotron deployments enforce a smaller combined context limit than
    # their catalogue metadata suggests. Retry once with a stricter budget.
    if response.status_code == 400 and model == "nvidia/nemotron-mini-4b-instruct":
        payload["messages"][0]["content"] = request_prompt[:4000] + "\n\n" + request_prompt[-2500:]
        payload["max_tokens"] = min(payload["max_tokens"], 768)
        response = requests.post(
            invoke_url,
            headers=headers,
            json=payload,
            timeout=(10, timeout_seconds),
        )
    # A previously saved sidebar choice may point at an NVIDIA endpoint that
    # has since been retired. Continue with the current default once instead
    # of failing an otherwise valid strategy request.
    if response.status_code in {401, 403, 404, 410, 429}:
        fallback_model = os.getenv(
            "NVIDIA_FALLBACK_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
        ).strip()
        if model != fallback_model:
            return _nvidia(prompt, max_tokens, base_url, fallback_model)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        # Preserve NVIDIA's useful validation detail without leaking headers or
        # credentials into the Streamlit error message.
        try:
            detail = response.json().get("detail", "")
        except (ValueError, AttributeError):
            detail = ""
        if detail:
            raise requests.HTTPError(
                f"{response.status_code} from NVIDIA: {detail}",
                response=response,
            ) from exc
        raise
    data = response.json()

    choices = data.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    text = _message_content_text(message)
    if not text:
        fallback_model = os.getenv(
            "NVIDIA_FALLBACK_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b"
        ).strip()
        if model != fallback_model:
            return _nvidia(prompt, max_tokens, base_url, fallback_model)
        raise ValueError(
            f"NVIDIA returned no usable text for model '{model}'."
        )
    u = data.get("usage", {})
    usage = cost.Usage(
        provider="openai", model=model,
        input_tokens=u.get("prompt_tokens", 0) or 0,
        output_tokens=u.get("completion_tokens", 0) or 0,
    )
    return text, usage


def _mock(prompt: str):
    """Return (canned response, estimated Usage). Detects eval vs strategy prompts."""
    if "Return ONLY a valid JSON object" in prompt:
        text = ('{"clarity": 4, "relevance": 4, "actionability": 4, '
                '"resource_appropriateness": 4, "coherence": 4, "strategic_value": 3, '
                '"data_integrity": 4, "persona_quality": 4, "timeline_quality": 4, '
                '"kpi_quality": 3, '
                '"comment": "Clear and actionable; could add more sector-specific depth (mock score)."}')
    else:
        text = _MOCK_STRATEGY
    usage = cost.Usage(
        provider="mock", model="mock",
        input_tokens=cost.estimate_tokens(prompt),
        output_tokens=cost.estimate_tokens(text),
        estimated=True,
    )
    return text, usage


_MOCK_STRATEGY = """## 1. Executive Summary
This is a **mock strategy** generated without an LLM API key so the prototype can be demonstrated offline. It illustrates the exact structure the system produces. To generate real, client-specific strategies, set an API key in `.env` (see README).

## 2. Stakeholder Analysis
| Stakeholder | Interest | Influence | Engagement Approach |
|---|---|---|---|
| Funders / Investors | Return on investment, impact | High | Targeted briefings, impact reports |
| End users / Customers | Practical value | High | Demos, case studies, pilots |
| Partners | Strategic alignment | Medium | Joint workshops, co-marketing |
| Media | Newsworthy stories | Medium | Press releases, expert commentary |
| Internal team | Clarity of direction | Low | Regular updates |

## 3. Key Messages
**We solve a real, costly problem.** Our approach delivers measurable benefits for our audience.
**We are credible and evidence-led.** Our results are backed by data and expertise.
**Now is the time to engage.** Early collaborators gain the most value.

## 4. Communication Channels
- **LinkedIn** — low cost, reaches professional/investor audiences.
- **Targeted email** — direct line to key stakeholders.
- **Sector events / trade shows** — high-trust face-to-face engagement.
- **Website case studies** — builds credibility for inbound interest.

## 5. Engagement Timeline
| Phase | Timeframe | Key Activities | Success Indicator |
|---|---|---|---|
| Foundation | Month 1 | Finalise messaging, refresh website | Assets ready |
| Outreach | Months 2-3 | Email + LinkedIn campaign | 20+ qualified conversations |
| Conversion | Months 4-6 | Meetings, demos, follow-ups | Target commitments secured |

## 6. Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Limited time/resources | High | Medium | Focus on 2 highest-value channels |
| Message not landing | Medium | High | Test messaging with a friendly audience first |
| Low response rates | Medium | Medium | Personalise outreach, use warm intros |

## 7. Next Steps
1. Confirm the single most important audience to reach first.
2. Finalise the three key messages above for your context.
3. Refresh your website/LinkedIn with the core value proposition.
4. Launch a small, targeted outreach pilot and measure response.
5. Review results in 4 weeks and iterate.

*(Mock output — connect an LLM in `.env` for tailored, persona-specific strategies.)*
"""
