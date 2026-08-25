# LLM Research & Recommendations

**For:** MSc Project 06 — AI-Driven Strategic Communications Assistant
**Compiled:** June 2026
**Purpose:** Identify which Large Language Models are best suited to generating
strategic communication & engagement plans, with versions, links, descriptions,
pricing, free-tier access, and a recommended evaluation setup that matches the
project's objectives (compare multiple LLMs on clarity, relevance, coherence,
accuracy, strategic value, actionability and trust).

> ⚠️ **Verify before citing.** Model versions and pricing change almost weekly.
> Always confirm the exact model ID and price on the provider's official docs
> (linked below) before you put a number in your dissertation.

---

## 1. TL;DR — Recommendation for THIS project

Your proposal explicitly mentions testing **free LLMs (Claude / Copilot / OpenAI
API)** and emphasises **trust, quality and cost**. Strategic-communications output
is fundamentally a **high-quality writing + reasoning** task, not a coding task.
Based on the research, the best fit is a **small multi-model panel**:

| Role in your study | Recommended model | Why |
|---|---|---|
| **Primary / quality benchmark** | **Claude Sonnet 4.6** (or Opus 4.8 for the hardest cases) | Tops writing-quality & instruction-following leaderboards; best tone control for brand voice; what your MVP already uses |
| **Cost-efficient comparator** | **Google Gemini 3.5 Flash** (or 3.1 Pro) | Highest creative-writing Elo per pound; **most generous permanent free API tier** — ideal for a student budget |
| **Structured/analytical comparator** | **OpenAI GPT-5.5** (or GPT-5.4 mini) | Strongest at structured output and analytical deliverables; familiar ChatGPT/Copilot lineage |
| **Open-weight / privacy comparator (optional)** | **Mistral Large 3** or **Llama 4 Maverick** | Open licence = transparency & reproducibility, which strengthens an academic study; free/self-hostable |

**Practical default for the dissertation experiment:** compare **Claude Sonnet 4.6
vs Gemini 3.5 Flash vs GPT-5.5** as the three "production-realistic, accessible"
contenders, and add **one open-weight model (Mistral Large 3)** to discuss the
open-source angle your proposal cares about. This gives you a clean 3–4 model
experimental matrix that is cheap, defensible, and directly answers your RQ
("which are the best LLMs… on trust and cost?").

---

## 2. Quick comparison table (frontier models, June 2026)

| Model | Provider | Version / ID | Released | Context | Price (in/out per 1M) | Open weights? | Best for |
|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 | Anthropic | `claude-opus-4-8` | May 2026 | 200K | $5 / $25 | No | Deepest reasoning, hardest strategy docs |
| Claude Sonnet 4.6 | Anthropic | `claude-sonnet-4-6` | Feb 2026 | 200K | $3 / $15 | No | **Best balance for writing quality** |
| Claude Haiku 4.5 | Anthropic | `claude-haiku-4-5-20251001` | Oct 2025 | 200K | $1 / $5 | No | Cheap, fast, high-volume |
| Claude Fable 5 | Anthropic | (Mythos-class) | Jun 2026 | 1M | $10 / $50 | No | Top creative-writing Elo *(see availability note)* |
| GPT-5.5 | OpenAI | `gpt-5.5-2026-04-23` | Apr 2026 | large | (see docs) | No | Flagship reasoning + structured output |
| GPT-5.4 mini / nano | OpenAI | `gpt-5.4-mini` / `-nano` | Mar 2026 | large | low | No | Cost/latency-sensitive tasks |
| GPT-5.3-Codex | OpenAI | `gpt-5.3-codex` | Feb 2026 | large | (see docs) | No | Code generation (not your use case) |
| Gemini 3.1 Pro | Google | `gemini-3.1-pro` | 2026 | 2M | (see docs) | No | Top reasoning, huge context |
| Gemini 3.5 Flash | Google | `gemini-3.5-flash` | May 2026 | 1M | $1.50 / $9 | No | **Best value writing; near-Pro quality** |
| Gemini 3.1 Flash-Lite | Google | `gemini-3.1-flash-lite` | 2026 | 1M | very low | No | Cheapest, high-volume |
| Llama 4 Maverick | Meta | `llama-4-maverick` | Apr 2025 | 1M | free / self-host | **Yes** (Llama licence) | Open generalist, 400B MoE |
| Llama 4 Scout | Meta | `llama-4-scout` | Apr 2025 | 10M | free / self-host | **Yes** | Ultra-long-context docs |
| Mistral Large 3 | Mistral | `mistral-large-3` | Dec 2025 | large | free / self-host | **Yes** (Apache 2.0) | Open MoE, concise tone |
| Mistral Small 4 | Mistral | `mistral-small-4` | Mar 2026 | large | free / self-host | **Yes** (Apache 2.0) | Unified small reasoning+vision |
| DeepSeek V4 (Pro/Flash) | DeepSeek | `deepseek-v4` | Apr 2026 | 1M | ~30× cheaper than frontier | **Yes** (MIT) | Cheapest capable, 1M context |
| Grok 4.3 | xAI | `grok-4.3` | Apr 2026 | 1M | (see docs) | No | Always-on reasoning, video input |
| Qwen 3.7 Max | Alibaba | `qwen3.7-max` | May 2026 | 1M | $2.50 / $7.50 | No (Max) | Agent workflows |
| Qwen 3.6 (27B/35B) | Alibaba | `qwen3.6-*` | Apr 2026 | long | free / self-host | **Yes** (Apache 2.0) | Open agent models |
| Command A+ | Cohere | `command-a-plus-05-2026` | May 2026 | long | free / self-host | **Yes** (Apache 2.0) | Enterprise RAG, multilingual |
| Nova Premier | Amazon | `nova-premier` | Early 2026 | large | (Bedrock) | No | AWS-native multimodal |

---

## 3. Detailed listings by provider

### 🟣 Anthropic — Claude
- **Website / docs:** https://platform.claude.com/docs/ · https://www.anthropic.com
- **Why it matters for you:** Consistently **#1 for writing quality, instruction
  following and tone control** — exactly the criteria in your evaluation rubric
  (clarity, tone accuracy, strategic value). This is what your MVP runs on.

| Model | ID | Released | Notes |
|---|---|---|---|
| Opus 4.8 | `claude-opus-4-8` | May 28 2026 | Flagship; deepest reasoning for complex strategy |
| Sonnet 4.6 | `claude-sonnet-4-6` | Feb 17 2026 | **Recommended default** — best quality/cost balance |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Oct 15 2025 | Cheap & fast for high-volume prompt testing |
| Fable 5 | Mythos-class | Jun 9 2026 | Most capable; 1M context. ⚠️ **Access suspended 12 Jun 2026** under a US export-control directive — do not rely on it for the project |

- **Free access:** No traditional free API tier historically; **limited free trial
  credits for new API accounts since March 2026**. Free *chat* (claude.ai) gives
  Sonnet-quality with a ~30–40 message / 5-hour cap.
- **Pricing:** Opus $5/$25, Sonnet $3/$15, Haiku $1/$5 (per 1M in/out).

### 🟢 OpenAI — GPT
- **Website / docs:** https://developers.openai.com/api/docs/models · https://openai.com
- **Why it matters for you:** Best for **structured, analytical deliverables** and
  the lineage behind **Microsoft Copilot** (named in your proposal). Strong
  instruction-following (IFEval 96).

| Model | ID | Released | Notes |
|---|---|---|---|
| GPT-5.5 / 5.5 Pro | `gpt-5.5-2026-04-23` | Apr 24 2026 | Flagship; reasoning effort none→xhigh |
| GPT-5.5 Instant | `chat-latest` | May 5 2026 | ChatGPT default; lower hallucination in law/medicine/finance |
| GPT-5.4 mini / nano | `gpt-5.4-mini` / `-nano` | Mar 17 2026 | Cost/latency options; nano is API-only |
| GPT-5.3-Codex | `gpt-5.3-codex` | Feb 5 2026 | Coding-focused (not your use case) |

- **Free access:** One-time ~$5 credit (now inconsistent, expires in 3 months).
  **GitHub Models** gives free access to GPT models with stricter rate limits —
  good for a student prototype.
- **Pricing:** See docs; >272K-token prompts billed at 2× input / 1.5× output.

### 🔵 Google — Gemini
- **Website / docs:** https://ai.google.dev/gemini-api/docs · https://deepmind.google/models/gemini/
- **Why it matters for you:** **Highest creative-writing Elo per pound** and the
  **most generous permanent free API tier** — the single best option for a
  budget-constrained student doing lots of prompt-testing iterations.

| Model | ID | Released | Notes |
|---|---|---|---|
| Gemini 3.1 Pro | `gemini-3.1-pro` | 2026 | Top reasoning (77.1% ARC-AGI-2), 2M context |
| Gemini 3.5 Flash | `gemini-3.5-flash` | May 19 2026 | **Near-Pro quality at Flash cost** — great default |
| Gemini 3.1 Flash-Lite | `gemini-3.1-flash-lite` | 2026 | Cheapest, high-volume |
| Gemini 3 Deep Think | — | 2026 | Extended reasoning variant |

- **Free access:** **Best in class.** Google AI Studio free tier persists
  indefinitely — e.g. Flash ~1,500 requests/day, Pro ~50/day, **no credit card**.
  (Quotas were cut in late 2025 — verify current numbers.)
- **Note:** Gemini 2.0 retired June 1 2026; 2.5 line now largely legacy.

### 🟠 Meta — Llama (open weights)
- **Website / docs:** https://ai.meta.com/blog/llama-4-multimodal-intelligence/ · https://huggingface.co/blog/llama4-release
- **Why it matters for you:** **Open weights** = transparency & reproducibility for
  an academic study, and free to self-host. Supports your proposal's open-source goal.

| Model | Params | Context | Notes |
|---|---|---|---|
| Llama 4 Maverick | 400B total / 17B active (MoE) | 1M | Generalist; runs at ~17B cost |
| Llama 4 Scout | 109B total / 17B active | **10M** | Long-context specialist |
| Llama 4 Behemoth | ~2T total / 288B active | — | "Teacher" model; **unreleased / shelved** |
| Meta Muse Spark | — | — | Apr 8 2026; Meta's first **closed-weight** frontier model |

- **Licence caveat:** Llama licence allows most commercial use; **EU licensees
  cannot use the multimodal/vision paths** (text-only is fine). >700M MAU needs a
  special licence.

### 🔴 Mistral AI (open weights, EU-based)
- **Website / docs:** https://mistral.ai/news/mistral-3/
- **Why it matters for you:** **Apache 2.0** licence (fully open), **EU-hosted /
  GDPR-friendly**, concise tone, and a very generous free tier (~1B tokens/month
  on the Experiment tier if you opt into data sharing). Strong open-weight comparator.

| Model | Params | Released | Notes |
|---|---|---|---|
| Mistral Large 3 | 675B total / 41B active (MoE) | Dec 2 2025 | Flagship; largest open MoE from a major lab |
| Mistral Small 4 | small dense | Mar 16 2026 | Merges reasoning + vision + coding |
| Ministral 3 (14B/8B/3B) | dense | 2026 | 14B reasoning variant scores 85% AIME 2025 |

- **Limitation:** Non-reasoning Large 3 trails frontier models on the hardest
  reasoning benchmarks — fine for comms writing, weaker for deep analysis.

### ⚫ DeepSeek (open weights, MIT)
- **Website / docs:** https://deepseek.ai · Hugging Face
- **Why it matters for you:** **~30× cheaper** than frontier models at comparable
  quality, MIT-licensed, 1M context. Excellent "cost" data point for your RQ.

| Model | Notes |
|---|---|
| DeepSeek V4 (Pro / Flash) | Apr 24 2026; 1.6T MoE, 1M context, new Compressed Sparse Attention |
| DeepSeek R1 | Reasoning/chain-of-thought model |
| DeepSeek V3.1 / V3.2 | Hybrid reasoning models (R2 not yet released) |

### ⚪ Other notable players
- **xAI Grok 4.3** (`grok-4.3`, Apr 30 2026) — 1M context, always-on reasoning,
  native video. Docs: https://docs.x.ai/developers/models
- **Alibaba Qwen 3.7 Max** (May 2026) — agent-focused, 1M context, $2.50/$7.50;
  open-weight Qwen 3.6 (Apache 2.0) for self-hosting. https://github.com/QwenLM
- **Cohere Command A+** (`command-a-plus-05-2026`, May 2026) — Apache 2.0,
  enterprise RAG + multilingual (23+ languages). https://cohere.com/command
- **Amazon Nova Premier** (early 2026) — AWS Bedrock only, multimodal.

---

## 4. Free / low-cost access (important for a student project)

| Provider | Free option | Practical limit | Card needed? |
|---|---|---|---|
| **Google Gemini** ⭐ | AI Studio free tier (permanent) | ~1,500 req/day Flash, ~50/day Pro | No |
| **Mistral** | "Experiment" tier | ~1B tokens/month (must opt into data training) | No |
| **OpenAI** | GitHub Models / $5 trial credit | Strict rate limits / expires 3 mo | Sometimes |
| **Anthropic** | Limited trial credits (since Mar 2026) | Small one-off | Yes |
| **Groq** | Free API (fast inference of open models) | ~14,400 req/day | No |
| **Cerebras** | Free API | ~1M tokens/day | No |
| **OpenRouter** | 20+ free models, one key | 50–1,000 req/day (tiered) | No |

**Stacking strategy for a budget prototype:** route across **Gemini + Groq +
OpenRouter (+ Cerebras)** — independent rate limits combine to ~16,900 free
requests/day, easily enough for all your prompt-evaluation experiments. Use
**OpenRouter** or **LiteLLM** as the router so you can swap models with one key.

> For your experiment, OpenRouter is especially useful: it gives you Claude, GPT,
> Gemini, Llama, Mistral and DeepSeek through a **single OpenAI-compatible API**,
> which means you can run your whole multi-LLM comparison with one integration.

---

## 5. Recommended evaluation setup (maps to your objectives)

Your proposal's objective: *"create and test a suite of standardised prompts
across multiple LLMs, comparing output quality using predefined criteria."* Here's
a defensible, low-cost experimental design:

1. **Models under test (4):**
   - Claude Sonnet 4.6 (proprietary, quality benchmark)
   - Gemini 3.5 Flash (proprietary, value/free-tier)
   - GPT-5.5 (proprietary, structured/analytical, Copilot lineage)
   - Mistral Large 3 (open-weight, transparency/cost)
2. **Held constant:** same standardised prompts (your `prompts/` library), same
   3 personas, same synthetic client inputs.
3. **Scoring criteria (your rubric):** clarity, relevance, coherence, accuracy,
   strategic value, actionability, tone accuracy, **trust**. Score 1–5.
4. **Method:** combine (a) **LLM-as-judge** automated scoring (already implemented
   in `src/evaluator.py`) for scale + (b) **human/client ratings** from Scientia
   Scripta for validity. Report inter-rater agreement.
5. **Also record:** cost per 1M tokens and latency per model → directly answers the
   "best LLM on **trust and cost**" research question.
6. **Output:** a comparison matrix (model × criterion) with descriptive statistics,
   exactly as your methodology section describes.

> Your `src/llm_client.py` already abstracts the provider — add Gemini/Mistral
> branches (or point it at OpenRouter) and you can run this whole matrix from the
> existing codebase.

---

## 6. Sources

**Anthropic / Claude**
- https://platform.claude.com/docs/en/about-claude/model-deprecations
- https://tygartmedia.com/current-claude-model-version/
- https://en.wikipedia.org/wiki/Claude_(language_model)

**OpenAI / GPT**
- https://developers.openai.com/api/docs/models
- https://openai.com/index/introducing-gpt-5-5/
- https://help.openai.com/en/articles/9624314-model-release-notes

**Google / Gemini**
- https://ai.google.dev/gemini-api/docs/changelog
- https://deepmind.google/models/gemini/
- https://en.wikipedia.org/wiki/Gemini_(language_model)

**Meta / Llama**
- https://ai.meta.com/blog/llama-4-multimodal-intelligence/
- https://huggingface.co/blog/llama4-release

**Mistral**
- https://mistral.ai/news/mistral-3/
- https://llm-stats.com/llm-updates

**DeepSeek**
- https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond
- https://en.wikipedia.org/wiki/DeepSeek_(chatbot)

**xAI / Grok**
- https://docs.x.ai/developers/models
- https://x.ai/news/grok-4

**Alibaba / Qwen**
- https://github.com/QwenLM
- https://en.wikipedia.org/wiki/Qwen

**Cohere / Amazon**
- https://cohere.com/command
- https://cohere.com/blog/command-a-plus

**Best-LLM-for-writing & free-tier comparisons**
- https://intellectualead.com/best-llm-writing/
- https://pricepertoken.com/leaderboards/writing
- https://teamai.com/blog/generative-ai-and-business/top-7-large-language-models-llms-for-businesses-ranked/
- https://openrouter.ai/blog/tutorials/free-llm-apis-compared/
- https://wetheflywheel.com/en/ai-model-access/free-llm-api-tiers-2026/

---

*Compiled via web research, June 2026. Treat all benchmark/pricing figures as
indicative and verify against official provider docs before citing in your
dissertation.*
