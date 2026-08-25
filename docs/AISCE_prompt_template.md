# AISCE Standardised Prompt Template (Task 5)

**AISCE** = *AI-driven Strategic Communications & Engagement* assistant.

This document defines the **standardised, reusable, persona-modular prompt
template** that the system uses to generate strategies. It is the formal output
of Task 5 ("Standardise prompt for reuse; ensure modularity across personas").

- **Canonical template file:** [`prompts/full_strategy.txt`](../prompts/full_strategy.txt)
- **Current version:** `v4`
- **Assembled by:** [`src/prompt_builder.py`](../src/prompt_builder.py) → `build_prompt()`
- **Selected by:** [`src/knowledge_tree.py`](../src/knowledge_tree.py) → `route()`

---

## 1. Why standardise?

Before standardisation, a useful strategy depended on how each prompt happened to
be written. A single canonical template means:

- **Reuse** — one tested template serves every client, every run.
- **Comparability** — because the prompt is fixed, differences in output can be
  attributed to the *client inputs* or the *LLM*, which is exactly what the
  project's multi-LLM evaluation (proposal §4) needs.
- **Modularity** — the same template adapts to any persona by filling slots,
  with no template rewrite.

## 2. The slot contract (the modular interface)

The template is a plain-text file with exactly **five named slots**, filled via
Python `str.format()` in `prompt_builder.build_prompt()`. These five slots are
the *entire* interface between the persona system and the prompt:

| Slot | Source | What makes it persona-specific |
|---|---|---|
| `{persona_label}` | `config/personas.json` → `label` | Names the client type (Research Project Team / University Spin-out / SME Innovator) |
| `{persona_description}` | `config/personas.json` → `description` | Frames the persona's situation and goals |
| `{objective}` | questionnaire answer `objective` (or persona `default_objective`) | The primary communication goal driving the plan |
| `{client_inputs}` | questionnaire answers, formatted by `format_client_inputs()` | All the client's specific answers (name, audience, budget, timeline, key message…) |
| `{document_context}` | uploaded brief, via `document_extractor.extract_text()` | Free-text evidence from an uploaded file |

> **Contract rule:** the template may contain **only** these five
> `{...}` tokens and no other literal braces, or `str.format()` will raise
> `KeyError`. Any new variable must be added to `build_prompt()` at the same time.

### How modularity actually works

The template body is **persona-neutral**: it never hard-codes "research" or "SME".
All persona variation enters through the five slots above, which are sourced from
`config/personas.json`. To support a new persona you add a block to
`personas.json` — **the template does not change at all**. That is the modularity
guarantee: *one template, N personas.*

```
config/personas.json  ──(label, description, questionnaire)──┐
questionnaire answers ──(objective, client_inputs)───────────┤
uploaded brief        ──(document_context)───────────────────┤
                                                              ▼
                         prompts/full_strategy.txt  →  build_prompt()  →  LLM
```

## 3. The output contract (10-section v4 structure)

Every strategy must come back in the same ten Markdown sections (with exact
headings as specified in the v4 prompt):

1. Executive Summary
2. Assumptions for Review
3. Stakeholder Analysis
4. Audience Journey Map
5. Key Messages
6. Communication Channels
7. Engagement Timeline
8. KPI and Success Measures
9. Risk Assessment
10. Next Steps

Plus the **Objectives and Outcome Measures**, **Stakeholder Personas**,
**Priority Audience Segments**, **AIDA Stage Mapping**, **Message Architecture
by Audience**, **Calls to Action**, **Channel Strategy**, and **High-level
Communications Timeline and Cadence** sub-headings within the main sections.

This fixed shape is what makes outputs **scoreable** (Tasks 6–7) and
**comparable** across LLMs.

## 4. Key v4 requirements built into the template

The v4 prompt adds several mandated requirements, designed so the model *cannot
skip* them:

| Requirement (in template) | Why it matters |
|---|---|
| AIDA framework required | Gives the strategy a coherent narrative arc |
| Mandatory persona disclaimer sentence | Makes the "early-stage sketch" status impossible to skip |
| Mandatory engagement timeline table (36 months, 3 audience columns) | Previous prose timelines were not specific enough |
| Addressable-market arithmetic for headline targets | Prevents unjustified round numbers |
| Source citations / assumption flags | Keeps numbers verifiable and honest |
| Named-entity grounding rule | Only confirmed relationships used as facts |
| Explicit channel tactics per audience | Prevents lower-priority audiences disappearing |
| KPI audience tagging + absolute figures | Every KPI traceable to an audience and a derivation |

## 5. Version history

| Version | Change | Rationale |
|---|---|---|
| `v1.0` | Original template: role + persona/objective/inputs/docs slots + 7-section output contract | Initial working template; produced the ground-truth examples |
| `v1.1` | Added Guiding Principles block; required explicit de-prioritisation in §4 | Fold in Task 4 learnings so usefulness is *instructed*, not left to chance |
| `v4` | Full rewrite: 10-section structure, AIDA framework, persona sketch disclaimer, 36-month timeline table, addressable-market arithmetic, data-integrity and source-citation rules, channel tactics per audience, KPI audience-tagging requirements | Align the system with the latest client questionnaire (31 questions) and the latest strategy-generation prompt |

## 6. The component-prompt library (modular extension point)

`prompts/` also holds focused, single-section templates —
`stakeholder_analysis.txt`, `messaging_framework.txt`, `channel_plan.txt` — plus
the judge template `evaluation.txt`. These are the **modular building blocks** for
the next iteration: the knowledge tree can branch a given *(persona, objective)*
to a specialised composition instead of always resolving to `full_strategy`.
Today every route resolves to `full_strategy` (see `knowledge_tree.ROUTES`); the
slot contract above is what makes swapping in component prompts safe.

## 7. How to extend safely

- **New persona** → add to `config/personas.json` only. Template untouched.
- **New objective-specific template** → add a `prompts/<name>.txt` using the
  same five slots, then add a `(persona, objective) → <name>` route to
  `knowledge_tree.ROUTES`.
- **New slot** → add the `{slot}` to the template **and** pass it from
  `build_prompt()` in the same change, or `str.format()` will fail.