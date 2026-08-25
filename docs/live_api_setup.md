# Live API Setup — Google Gemini (Primary Provider)

This note records how to run the app against a **real LLM**. The primary provider
is now **Google Gemini**; Anthropic and OpenAI remain supported as alternatives.

## TL;DR

| Want to… | Do this |
|---|---|
| Demo offline, no key | Leave `.env` as `LLM_PROVIDER=mock` (default). Always works. |
| Run live with Google Gemini | `LLM_PROVIDER=gemini` + a Google API key in `.env` |
| Run live with Anthropic | `LLM_PROVIDER=anthropic` + a genuine `sk-ant-...` key in `.env` |
| Run live with OpenAI | `LLM_PROVIDER=openai` + an `sk-...` key in `.env` |

## Getting a Google Gemini API key

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account.
3. Click **Create API key** and select a Google Cloud project (or create one).
4. Copy the key (starts with `AIza...`).

## Configuring `.env`

```bash
# in strategic-comms-assistant/.env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIza...                # from https://aistudio.google.com/apikey
GOOGLE_MODEL=gemini-2.0-flash
```

Then run:

```bash
streamlit run app.py
```

The sidebar badge will read **🟢 Google Gemini** instead of **🟡 Mock**.

## Provider precedence

- An **explicit** `LLM_PROVIDER` (gemini/anthropic/openai/mock) is always respected.
- `LLM_PROVIDER=mock` genuinely forces mock even when API keys are present.
- Auto-detection only happens when `LLM_PROVIDER` is unset: it checks for
  `GOOGLE_API_KEY` first, then `ANTHROPIC_API_KEY`, then `OPENAI_API_KEY`.
- `load_dotenv(override=True)` in `app.py` ensures the project `.env` is
  authoritative over globally-set environment variables.

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `Gemini rejected the API key (401)` | Invalid or missing `GOOGLE_API_KEY` | Check the key in `.env` |
| `Gemini returned 404` | Invalid model name | Check `GOOGLE_MODEL` against https://ai.google.dev/gemini-api/docs/models |
| `Gemini rate limit hit (429)` | Too many requests | Wait and retry, or upgrade to a paid tier |
# NVIDIA NIM keys by model

For NVIDIA NIM, keep secrets in the local `.env` file rather than Python source
files. You may either use one shared key:

```text
OPENAI_API_KEY=your_nvidia_key
```

or keep separate keys that are automatically selected by the chosen model:

```text
NVIDIA_DIFFUSIONGEMMA_API_KEY=your_diffusiongemma_key
NVIDIA_NEMOTRON_API_KEY=your_nemotron_key
```

The model-specific key takes priority over `OPENAI_API_KEY`. Do not commit `.env`
or paste API keys into `app.py`, prompts, notebooks or documentation.
