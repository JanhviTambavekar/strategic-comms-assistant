# Specialist LLMs — Feasibility Note & Shortlist (Task 8)

**Question (from the proposal):** *Are there LLMs trained specifically on science,
research, or innovation ecosystems that the AISCE assistant should use — and which
are the "best LLMs in the science world", including on cost and trust?*

**Short answer:** Yes, a number of domain-specialised LLMs exist, but almost all
are tuned for **scientific content reasoning** (chemistry, biomedicine, equations,
patents) — *not* for **strategic communications writing**, which is AISCE's actual
task. For generating comms strategies, a **general frontier model** (Claude / GPT
class) remains the best engine. Specialist models and RAG research tools are
relevant mainly for **grounding** a client's technical material and for
**trust/citations**. Details and shortlist below.

---

## 1. Why this matters for AISCE

AISCE's job is to turn a client's inputs into a *communications & engagement
strategy* — stakeholder maps, messages, channels, timelines. That is a
**general reasoning + writing** task, not a science-knowledge task. So the
relevant question is not "which model knows the most chemistry" but:

1. Could a **science-tuned model** write better strategies for science clients? *(Mostly no — they're tuned for technical QA, not strategy.)*
2. Could specialist tools **ground** AISCE in the client's real research so outputs are more accurate and trustworthy? *(Yes — via RAG research tools.)*
3. What gives the best **cost / trust / quality** trade-off for the prototype? *(A frontier general model, optionally + RAG grounding.)*

## 2. Shortlist by category

### A. Scientific-text foundation models (general science)
| Model | Scale / base | Open? | Notes for AISCE |
|---|---|---|---|
| **Galactica** (Meta) | 125M–120B, 48M papers | Open weights (withdrawn demo) | Landmark science LLM; tuned to *store/reason over* scientific knowledge, not write comms plans. Reputational caveats at launch. |
| **SciGLM** (SciInstruct, NeurIPS'24) | 6B, ChatGLM base | Open | College-level scientific *reasoning*; not a comms tool. |
| **SciDFM / INDUS / DARWIN / FORGE** | various (MoE & domain) | Open (research) | Science-application models; same mismatch — content, not strategy. |

### B. Biomedical / clinical models (if a client is health-led, e.g. NeuroSight)
| Model | Scale / base | Open? | Notes |
|---|---|---|---|
| **Meditron** (EPFL) | 7B / 70B, Llama-2 (+ Qwen2.5/Llama-3.1 variants) | Open | Strong medical reasoning; **not safety-aligned for actionable advice** — use only for grounding, never client-facing claims. |
| **OpenBioLLM-70B** | 70B | Open | Reports beating GPT-4/Med-PaLM on biomedical benchmarks. |
| **BioMistral / PMC-LLaMA / BioMedLM / BioGPT** | 2.7B–7B | Open | Lightweight biomedical models; useful to summarise a client's clinical evidence. |
| **Med-PaLM / Med-PaLM 2** (Google) | PaLM-based | **Closed** | Benchmark-leading but proprietary; not viable for an open-source prototype. |

### C. Innovation / IP / patent models (relevant to spin-outs & SMEs)
| Model | Focus | Open? | Notes |
|---|---|---|---|
| **PatentGPT (IP)** — Bai et al. 2024 | IP knowledge, drafting | Open base + SMoE | Beat GPT-4 on the MOZIP IP benchmark and a patent-agent exam; relevant if clients need IP/patent narrative help. |
| **PatentGPT (concept gen)** — Ren/Ma/Luo 2025 | Invention & concept generation | Research | Generates novel technical concepts; tangential to comms but interesting for spin-out positioning. |

### D. RAG-based scholarly research tools (grounding & trust) — **most relevant**
These are not base LLMs but **retrieval-augmented assistants over scholarly
corpora** — the right tool for *grounding* AISCE in a client's actual research and
producing **cited, trustworthy** evidence.
| Tool | Corpus | Why it matters for AISCE |
|---|---|---|
| **Elicit** | 138M+ papers | Structured evidence extraction; good for systematic grounding. |
| **Consensus** | Semantic Scholar (200M+) | Evidence-weighted yes/no questions ("does X help Y?"); trust signal. |
| **SciSpace** | 280M+ (multi-DB) | Discovery-to-drafting; parses dense papers into plain language. |
| (also Semantic Scholar, Scite, ResearchRabbit, Perplexity) | — | Discovery / citation verification. |

> **Trust note (proposal RQ on trust):** these tools raise trust by **grounding
> claims in retrievable citations** (RAG). A frontier LLM alone can sound fluent
> but unverified — so the trust lever for AISCE is *retrieval + citation*, not a
> bigger science model.

## 3. Feasibility verdict

1. **Don't swap the strategy engine for a science-tuned model.** The specialist
   science/biomedical models are optimised for technical QA and reasoning, not for
   writing resource-appropriate communications strategies. On AISCE's actual task,
   a **general frontier model** (e.g. Claude `claude-sonnet-4-6`, GPT-4-class) is
   expected to outperform them — and is what the prototype already uses.
2. **Use specialist models only for *grounding*, opportunistically.** If a client
   uploads dense clinical/technical material (e.g. NeuroSight), a biomedical model
   or a RAG tool could pre-summarise it into clean `{document_context}` before the
   AISCE template runs. This is an *optional pre-processing* step, not a
   replacement.
3. **RAG research tools are the highest-value addition for trust.** Wiring
   Elicit/Consensus/SciSpace-style retrieval (or an open Semantic Scholar / OpenAlex
   API) into the document-ingestion stage would let AISCE cite real evidence —
   directly addressing the proposal's **trust** research question.
4. **Cost.** Open models (Meditron, BioMistral, SciGLM, PatentGPT bases) are free
   to self-host but need GPU infrastructure; frontier APIs cost per-token but need
   no infra. For an MVP/dissertation, **frontier API + optional RAG** is the
   cheapest path to quality and trust.

## 4. Recommendation for the project

| Layer | Recommendation |
|---|---|
| **Strategy generation** | Keep a **general frontier model** (Claude / GPT). Run the proposal's multi-LLM comparison *between frontier models* on the AISCE rubric, not between narrow science models. |
| **Grounding (optional)** | Add a RAG step over an open scholarly API (Semantic Scholar / OpenAlex) to cite evidence and raise trust. |
| **Domain pre-processing (optional, client-dependent)** | Use a biomedical/IP open model only when a client's uploaded material is highly technical. |
| **Out of scope for MVP** | Self-hosting/fine-tuning a science LLM — high cost, wrong task fit. Revisit only if grounding proves insufficient. |

> **Bottom line:** specialist science LLMs exist and are impressive on technical
> benchmarks, but they solve a different problem than AISCE. The feasible,
> trust-improving, low-cost path is **frontier model for strategy + RAG over
> scholarly sources for grounding**, with domain models reserved for optional
> technical pre-processing.

## 5. Sources

- [A Survey of Scientific Large Language Models (2025)](https://www.aimodels.fyi/papers/arxiv/survey-scientific-large-language-models-data-foundations) · [Awesome-Scientific-Language-Models (EMNLP'24)](https://github.com/yuzhimanhua/Awesome-Scientific-Language-Models)
- [Galactica: A Large Language Model for Science](https://arxiv.org/abs/2211.09085)
- [SciInstruct / SciGLM](https://arxiv.org/pdf/2401.07950) · [SciDFM (MoE for science)](https://arxiv.org/pdf/2409.18412)
- [Meditron (open medical LLMs)](https://github.com/epfllm/meditron) · [BioMedLM 2.7B](https://arxiv.org/pdf/2403.18421) · [BioMistral](https://arxiv.org/html/2402.10373v1) · [OpenBioLLM](https://huggingface.co/blog/aaditya/openbiollm)
- [PatentGPT: A Large Language Model for Intellectual Property](https://arxiv.org/abs/2404.18255) · [Large Language Model for Patent Concept Generation](https://arxiv.org/abs/2409.00092)
- [SciSpace vs Elicit vs Consensus benchmark](https://scispace.com/resources/scispace-vs-elicit-vs-consensus-an-ai-literature-search-benchmark-across-200-queries/) · [Trust in AI: Scite, Elicit, Consensus, Scopus AI (HKUST Library)](https://library.hkust.edu.hk/sc/trust-ai-lit-rev/)
