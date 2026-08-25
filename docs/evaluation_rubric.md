# AISCE Strategy Evaluation Rubric — v2.0

**Status:** Formal rubric. Operationalises the human evaluation method
(`docs/human_evaluation_method.md`) as numeric scoring criteria, quality
thresholds and constraints. Used by both human reviewers and the automated
LLM-as-judge (`src/evaluator.py`, `prompts/evaluation.txt`).

- **Scale:** every criterion is scored **1–5** (integers).
- **Criteria:** 10 — the four human criteria from the evaluation method, the two
  structural criteria, and four new criteria aligned to the v4 prompt structure.
- **Aligned to:** the evaluation calibration set (must reproduce its verdicts — see §5).

---

## 1. Scoring criteria and anchors

Each criterion is scored 1–5. Anchors are given for **5 (excellent)**,
**3 (acceptable)** and **1 (poor)**; 4 and 2 are intermediate.

### C1 · Clarity  *(human: Clear)*
A non-expert can read it once and understand it.
- **5** — Plain, well-structured, recommendations stated plainly; no jargon/padding.
- **3** — Mostly clear; some jargon, hedging, or a section that must be re-read.
- **1** — Confusing, padded, or recommendations buried/absent.

### C2 · Relevance  *(human: Relevant)* — **MUST-PASS**
Visibly about *this* client; could not be sent to another org unchanged.
- **5** — Names the client's actual audiences, assets, figures and context throughout.
- **3** — Some specifics, but noticeably generic in places.
- **1** — Interchangeable; no client-specific detail (the `mock` failure mode).

### C3 · Actionability  *(human: Actionable)*
The client could act on Monday morning.
- **5** — 3–5 concrete, ownable next steps; concrete timelines & success indicators.
- **3** — Some actionable steps mixed with vague aspirations.
- **1** — Vague ("raise awareness") with no who/what/when.

### C4 · Resource-appropriateness  *(human: Resource-appropriate)* — **MUST-PASS**
Every recommendation fits the stated budget, team and time.
- **5** — Deliberately spends the stated budget; respects team capacity; names trade-offs.
- **3** — Broadly affordable but doesn't engage explicitly with the constraints.
- **1** — Recommends tactics the client plainly cannot afford or staff.

### C5 · Coherence  *(structural)*
The plan hangs together logically.
- **5** — Sections reinforce one strategic thread; no contradictions.
- **3** — Generally consistent; minor disconnects between sections.
- **1** — Sections contradict or read as unrelated fragments.

### C6 · Strategic value  *(structural; human: usefulness)*
It makes real choices, not a checklist.
- **5** — A clear strategic bet with explicit prioritisation *and* de-prioritisation.
- **3** — Sensible but safe; lists tactics without strong prioritisation.
- **1** — Generic tactic dump; no discernible strategy.

### C7 · Data integrity  *(v4 prompt: Absolute Figures)*
Every number is cross-checked against the questionnaire and business plan.
- **5** — All figures sourced or explicitly flagged as assumptions; addressable-market arithmetic shown as three explicit numbers for headline targets.
- **3** — Mostly accurate; occasional unlabelled assumption or missing derivation.
- **1** — Figures appear unverified or invented; no sourcing or derivation.

### C8 · Persona quality  *(v4 prompt: Personas)*
Personas follow the v4 persona requirements.
- **5** — Required disclaimer sentence present verbatim; personas grounded in confirmed relationships; tailored to Investors, Partners and Regulators with info sources, touchpoints, influencers, tone, geography and grounding example.
- **3** — Personas present but some requirements missing (e.g. no disclaimer, weak grounding, missing details).
- **1** — No meaningful personas; generic descriptions not tied to the client's audiences.

### C9 · Timeline quality  *(v4 prompt: Engagement Timeline)*
The engagement timeline is a single 36-month table.
- **5** — Single table, rows = time periods (Months 1–36), columns = priority audiences; each cell has task + AIDA stage + channel/message reference; arc-length reasoning before the table; Next Steps consistent with Months 1–3.
- **3** — Table present but structure partially wrong (missing cells, wrong columns, missing arc reasoning).
- **1** — No table or prose-only timeline that fails the v4 mandated format.

### C10 · KPI quality  *(v4 prompt: KPI Framework)*
KPIs follow the absolute-figures and audience-tagging rules.
- **5** — Every KPI tagged to a priority audience; justified against £40k/team/market with defensible arithmetic; absolute numbers with derivation shown.
- **3** — Some KPIs tagged and justified; others untagged or asserted without working.
- **1** — KPIs are round numbers asserted without derivation; no audience tags.

## 2. Aggregate score

```
average = mean(C1..C10)       # rounded to 2 dp, over criteria scored > 0
```

## 3. Quality thresholds (verdict)

The rubric converts scores into one of three verdicts:

| Verdict | Condition (all must hold) |
|---|---|
| **Useful** | `average ≥ 4.0` **AND** every MUST-PASS ≥ 4 **AND** no criterion < 3 |
| **Useful with edits** | `average ≥ 3.0` **AND** every MUST-PASS ≥ 3 |
| **Not useful** | anything else (including any MUST-PASS < 3) |

## 4. Constraints (gates)

These are hard constraints, not averages:

1. **MUST-PASS gate.** **Relevance (C2)** and **Resource-appropriateness (C4)**
   are must-pass. If *either* scores **< 3**, the overall verdict is capped at
   **Not useful**, regardless of the other scores.
2. **Clarity is not sufficient.** A high Clarity score can never on its own lift
   the verdict; it carries no gating power.
3. **Integer scores only**, 1–5. Missing/garbled scores are treated as 0 and
   excluded from the average (and, if a must-pass is 0, the gate fails).

## 5. Calibration against the calibration set

The rubric is valid only if its verdicts match human judgement on the calibration
set. Expected results:

| Strategy | C2 Relevance | C4 Resource-approp. | Gate | Expected verdict |
|---|---|---|---|---|
| TidalCarbon | 5 | 5 | pass | Useful |
| NeuroSight | 5 | 5 | pass | Useful |
| GreenCrate | 5 | 5 | pass | Useful |
| `mock` baseline | 1–2 | 1–2 | **fail** | Not useful |

The MUST-PASS gate is exactly what makes the rubric reject the generic `mock`
output while passing the three tailored strategies.

## 6. Implementation

| Rubric element | Where it lives |
|---|---|
| Criteria list (10) | `src/evaluator.py` → `CRITERIA` |
| Anchored definitions + JSON output shape | `prompts/evaluation.txt` |
| Aggregate + verdict + gate logic | `src/evaluator.py` → `evaluate()`, `verdict()` |
| Display (scores, average, verdict) | `app.py` → Evaluation Dashboard tab |
| Mock scores (offline) | `src/llm_client.py` → `_mock()` |

## 7. Version history

| Version | Change |
|---|---|
| `v1.0` | First formal rubric. 6 criteria; MUST-PASS gate on Relevance + Resource-appropriateness; three-tier verdict aligned to the human method. |
| `v2.0` | Expanded to 10 criteria aligned with the v4 prompt structure: added Data integrity (C7), Persona quality (C8), Timeline quality (C9), KPI quality (C10). Verdict logic unchanged. |