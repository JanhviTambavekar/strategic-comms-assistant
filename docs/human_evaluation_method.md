# Human Evaluation Method for Strategies — Draft Criteria Framework (Task 6)

**Owners:** Edwin + Eva
**Status:** Draft, *pre-rubric*. This document defines **how a human decides
whether a generated strategy is good**. It is intentionally informal — it
captures human judgement in plain language so that Task 7 can turn it into a
formal, numeric rubric. It must not jump ahead to fixed scores or thresholds;
that is Task 7's job.

**Grounded in:** the three Task 4 ground-truth strategies and the contrast `mock`
baseline (see `ground_truth/usefulness_evaluation.md`).

---

## 1. Purpose and scope

When a strategy comes out of the AISCE workflow, a human reviewer needs a
consistent, repeatable way to answer one question:

> *"Could Scientia Scripta hand this to the client as useful, or not?"*

The study records two related but distinct layers of evidence:

1. **Strategy output quality** — whether the generated plan is useful for the
   client; this is the purpose of the four criteria below and the formal rubric.
2. **Service and process experience** — whether supplying information, uploading
   a brief and understanding the input-to-output flow was usable for the
   participant. These are evaluated with separate Likert statements in the app;
   they are not qualities that can be inferred from strategy text alone.

Do not combine the two layers into a single average. A participant can have a
positive experience of the service and still receive a weak strategy, or the
reverse.

This framework breaks that judgement into the **four core human criteria** named
in the project plan — **Clear, Relevant, Actionable, Resource-appropriate** — and
gives each a definition, the questions a reviewer asks, and concrete "looks good /
looks weak" indicators taken from real output.

> These four are the *human-facing* criteria. The system's automated judge also
> tracks **coherence** and **strategic value** (`src/evaluator.py`); the
> relationship is mapped in §7 so the human method and the machine rubric stay
> aligned.

## 2. Who evaluates, and with what

- **Primary reviewers:** Edwin + Eva (project team), acting as a proxy for the
  Scientia Scripta consultant.
- **Secondary (later stages):** the client persona representatives during user
  testing (proposal §6).
- **What they read:** the generated 10-section v4 strategy (see
  `docs/AISCE_prompt_template.md` §3) **plus** the client's
  input script (so "relevant" and "resource-appropriate" can actually be checked
  against what the client said).
- **How long:** a single careful read (~5–10 minutes) per strategy. The method is
  designed to be usable at that pace.

## 3. The judgement scale (informal, pre-rubric)

For each criterion the reviewer gives one of three verdicts and a one-line reason:

| Verdict | Meaning |
|---|---|
| **Strong** | Clearly meets the criterion; no reservations |
| **OK** | Acceptable but with a noted weakness |
| **Weak** | Fails the criterion; would not pass to a client as-is |

A short free-text reason is **required** for every "OK" and "Weak" — these reasons
are the raw material Task 7 converts into scoring anchors.

### 3.1 Supplementary participant form

Alongside the reviewer judgement, participants complete the in-app 5-point
agreement form (1 = Strongly Disagree; 5 = Strongly Agree). Its **Strategy
output** statements cover clarity, tailoring, actionability, resource realism,
messages/channels, timeline/KPIs and overall usefulness. Its **Service and
process experience** statements cover questionnaire clarity, effort, upload or
entry, transparency and confidence to reuse. See
`docs/prompt_evaluation_alignment.md` for the traceability review.

---

## 4. The four criteria

### 4.1 Clear
> *Definition:* a non-expert client can read the strategy once and understand
> what it says and what it recommends.

**Reviewer asks:**
- Is it written in plain language, not jargon or AI-padding?
- Is the structure easy to follow (the 10 v4 sections, sensible tables)?
- Are the recommendations stated plainly, not buried in hedging?

**Looks Strong:** "depth with ~20–30 decision-makers over broad public reach" —
a single, plainly-stated strategic idea you grasp immediately (TidalCarbon §1).
**Looks Weak:** vague, generic prose; long sentences that restate the question;
recommendations you have to hunt for.

> *Note:* Clarity is **necessary but not sufficient**. The `mock` baseline was
> perfectly clear yet still not useful — so "Clear = Strong" can never on its own
> mean "good strategy."

### 4.2 Relevant
> *Definition:* the strategy is visibly **about this client** — it could not be
> sent to a different organisation unchanged.

**Reviewer asks:**
- Does it name the client's actual audiences, assets, numbers and context?
- Does it engage with *their* situation, or could you find-and-replace the name
  and send it to anyone?
- Does it use the uploaded brief / questionnaire answers, not just the persona?

**Looks Strong:** names EPSRC/NERC, Defra, the £5k budget and the month-30 policy
workshop (TidalCarbon); spots that GreenCrate's Instagram reaches the wrong buyers
and reallocates effort.
**Looks Weak:** the `mock` baseline — a stakeholder table and channel list that
fit "almost any organisation," with no client name, figures or specifics.

> *Relevance is the single strongest signal of usefulness* (Task 4 finding). A
> "Weak" here should weigh heavily against the strategy overall.

### 4.3 Actionable
> *Definition:* the client could **do something concrete on Monday morning** from
> the plan.

**Reviewer asks:**
- Are the Next Steps specific and ownable, or vague aspirations?
- Could a named person start each one this week without further briefing?
- Are timelines and success indicators concrete enough to act on and check?

**Looks Strong:** "Interview the three pilot customers and turn each into a
one-page, numbers-led case study within two weeks" (GreenCrate); "Draft and
request the NHS letter of intent" (NeuroSight).
**Looks Weak:** "raise awareness", "engage stakeholders", "leverage social media"
with no who/what/when.

> *Caution (Task 4 finding):* actionability is **not** "a longer task list." 3–5
> concrete, ownable steps beat fifteen vague ones.

### 4.4 Resource-appropriate
> *Definition:* every recommendation fits the client's **stated budget, team and
> time**.

**Reviewer asks:**
- Could this client actually afford and staff this plan?
- Does it respect the explicit limits (e.g. £5k total, £2k/month, one part-time
  marketer, 4 months' runway)?
- Does it spend the budget *deliberately* (says where the money/effort goes), and
  acknowledge the team's capacity?

**Looks Strong:** allocates ~£1k of TidalCarbon's £5k to a designed policy brief;
names GreenCrate's part-time marketer as the bottleneck and says what to stop
doing; sequences NeuroSight's raise around 4 months of runway.
**Looks Weak:** recommends paid ad campaigns, agencies or conference circuits with
no regard for a tiny budget — the default failure mode of generic LLM output.

> *Task 4 finding:* this deserves to be its **own** criterion. Folded into
> "actionable," resource realism gets lost — yet it is one of the clearest
> dividers between a useful plan and a generic one.

---

## 5. Overall usefulness judgement

After the four criteria, the reviewer gives a single overall verdict:

> **Useful** / **Useful with edits** / **Not useful**

Draft decision guidance (to be formalised in Task 7):
- **Relevant = Weak** or **Resource-appropriate = Weak** → cannot be better than
  *Not useful* / *Useful with edits*, even if clear and actionable. (These two
  criteria are the "must-pass" gates.)
- **All four Strong** → *Useful*.
- **Clear only** is never enough on its own.

## 6. Worked application (calibration set)

Applying this method to the Task 4 outputs (full detail in
`ground_truth/usefulness_evaluation.md`):

| Strategy | Clear | Relevant | Actionable | Resource-appropriate | Overall |
|---|---|---|---|---|---|
| TidalCarbon | Strong | Strong | Strong | Strong | Useful |
| NeuroSight | Strong | Strong | Strong | Strong | Useful |
| GreenCrate | Strong | Strong | Strong | Strong | Useful |
| `mock` baseline | Strong | Weak | OK | Weak | Not useful |

These four cases are the **calibration set**: any rubric from Task 7 must
reproduce these human verdicts to be considered aligned.

## 7. Hand-off to the rubric (Task 7)

This framework gives Task 7 everything it needs:

1. **Criteria to score** — Clear, Relevant, Actionable, Resource-appropriate
   (plus Coherence and Strategic value from the existing judge, for completeness).
2. **Anchor descriptions** — the Strong / OK / Weak indicators above become the
   wording for numeric score anchors (e.g. 5 / 3 / 1).
3. **Gating constraints** — Relevant and Resource-appropriate as "must-pass"
   criteria become the rubric's quality thresholds/constraints.
4. **A calibration set** — the four cases in §6 to validate that the rubric's
   numeric scores agree with human judgement.

| Human criterion (Task 6) | Machine criterion (`src/evaluator.py`) |
|---|---|
| Clear | `clarity` |
| Relevant | `relevance` |
| Actionable | `actionability` |
| Resource-appropriate | `resource_appropriateness` |
| — | `coherence` |
| — | `strategic_value` |
| — | `data_integrity` (v4 prompt: Absolute Figures) |
| — | `persona_quality` (v4 prompt: Personas) |
| — | `timeline_quality` (v4 prompt: Engagement Timeline) |
| — | `kpi_quality` (v4 prompt: KPI Framework) |
