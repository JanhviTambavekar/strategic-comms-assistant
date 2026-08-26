"""LLM provider abstraction.

Supports Google Gemini, Anthropic and OpenAI, plus a 'mock' provider that returns
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
    "Meta Llama 3.1 8B Instruct": "meta/llama-3.1-8b-instruct",
    "Google DiffusionGemma 26B A4B IT": "google/diffusiongemma-26b-a4b-it",
    "NVIDIA Nemotron Mini 4B Instruct": "nvidia/nemotron-mini-4b-instruct",
}


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
    if explicit in {"gemini", "anthropic", "openai", "mock"}:
        return explicit
    # No explicit provider -> auto-detect from available keys, else mock.
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
    if provider == "gemini":
        return _with_retries(_gemini, prompt, max_tokens, provider="Gemini", model=model)
    if provider == "anthropic":
        return _with_retries(_anthropic, prompt, max_tokens, provider="Anthropic", model=model)
    if provider == "openai":
        return _with_retries(_openai, prompt, max_tokens, provider="OpenAI", model=model)
    return _mock(prompt)


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
            "Try the Fast draft mode or select the smaller Llama model."
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


def _nvidia(prompt: str, max_tokens: int, base_url: str, model: str):
    """Call NVIDIA NIM API directly using requests (per NVIDIA's docs)."""
    import requests

    # Keep provider credentials outside source control. Separate optional keys
    # make it easy to rotate or change credentials by model in .env.
    key_by_model_prefix = {
        "google/diffusiongemma": "NVIDIA_DIFFUSIONGEMMA_API_KEY",
        "nvidia/nemotron-mini": "NVIDIA_NEMOTRON_API_KEY",
        "qwen/": "NVIDIA_QWEN_API_KEY",
    }
    api_key = next(
        (
            os.getenv(env_name)
            for prefix, env_name in key_by_model_prefix.items()
            if model.startswith(prefix) and os.getenv(env_name)
        ),
        None,
    ) or os.getenv("OPENAI_API_KEY")
    # Users may paste an entire Authorization value from provider examples.
    # Store either form in .env; normalise it before constructing the header.
    api_key = (api_key or "").strip()
    if api_key.lower().startswith("bearer "):
        api_key = api_key[7:].strip()

    invoke_url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
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
    timeout_seconds = int(os.getenv("NVIDIA_REQUEST_TIMEOUT", "120"))
    # Fail over sooner for NVIDIA trial models that regularly sit in a shared
    # queue. Llama retains the full configured timeout because it is the
    # reliable fallback target.
    if model == "nvidia/nemotron-mini-4b-instruct":
        timeout_seconds = min(timeout_seconds, 50)
    elif model == "google/diffusiongemma-26b-a4b-it":
        timeout_seconds = min(timeout_seconds, 70)
    try:
        response = requests.post(
            invoke_url,
            headers=headers,
            json=payload,
            timeout=(10, timeout_seconds),
        )
    except requests.Timeout:
        fallback_model = os.getenv(
            "NVIDIA_FALLBACK_MODEL", "meta/llama-3.1-8b-instruct"
        ).strip()
        if model != fallback_model:
            return _nvidia(prompt, max_tokens, base_url, fallback_model)
        raise
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
            "NVIDIA_FALLBACK_MODEL", "meta/llama-3.1-8b-instruct"
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
