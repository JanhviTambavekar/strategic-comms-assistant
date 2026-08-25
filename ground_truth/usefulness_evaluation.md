# Informal Usefulness Evaluation (Pre-Rubric) — Task 4

> **Status:** deliberately *informal*. This is the judgement we make **before**
> the formal human-evaluation method (Task 6) and rubric (Tasks 6–7) exist. Its
> job is to (a) confirm the workflow produces genuinely useful strategies and
> (b) surface *what makes an AISCE strategy useful or not*, so the rubric is
> grounded in real output rather than defined in the abstract.
>
> **What was evaluated:** the three generated strategies in this folder
> (TidalCarbon, NeuroSight, GreenCrate), plus the offline `mock` strategy in
> `src/llm_client.py` as a deliberate "generic" contrast case.

## Method (light-touch)

For each strategy a single reviewer (acting as the Scientia Scripta consultant)
asked five plain questions and gave a quick Strong / OK / Weak verdict:

1. **Clear** — Could a non-expert client read it once and understand it?
2. **Relevant** — Is it visibly *about this client*, or could it be sent to anyone?
3. **Actionable** — Could the client do something on Monday morning from it?
4. **Resource-appropriate** — Does it respect the stated budget / team / time?
5. **Strategically valuable** — Does it make a real *choice* (what to prioritise,
   what to drop), not just list everything?

These five questions are the raw material that Task 6 will formalise.

## Scores at a glance (informal 3-point scale)

| Strategy | Clear | Relevant | Actionable | Resource-appropriate | Strategic value | Overall |
|---|---|---|---|---|---|---|
| 01 · TidalCarbon (research) | Strong | Strong | Strong | Strong | Strong | **Useful** |
| 02 · NeuroSight (spin-out) | Strong | Strong | Strong | Strong | Strong | **Useful** |
| 03 · GreenCrate (SME) | Strong | Strong | Strong | Strong | Strong | **Useful** |
| `mock` baseline (no LLM) | Strong | **Weak** | OK | **Weak** | **Weak** | **Not useful for a real client** |

## Per-strategy notes

### 01 · TidalCarbon — *Useful*
- **What worked:** Names real funders/policy bodies (EPSRC/NERC, Defra, EA);
  anchors the whole plan to the month-30 policy workshop the client actually has;
  spends the £5k explicitly (~£1k on a designed policy brief); makes a clear
  *choice* — "depth with ~20–30 decision-makers over broad public reach."
- **Strategic value signal:** the explicit de-prioritisation list ("paid ads,
  broad social, multiple conferences") is what separates a strategy from a
  checklist.
- **Watch-out it correctly flagged:** over-claiming the "40%" before peer review —
  a domain-appropriate risk, not a generic one.

### 02 · NeuroSight — *Useful*
- **What worked:** Respects the hard 4-month runway constraint by sequencing the
  raise from day 1 and recommending a "first close"; turns NHS interest into a
  *letter of intent* used as investor proof; addresses the real soft spot (founders
  inexperienced at pitching) with concrete coaching steps.
- **Strategic value signal:** reframes the pitch from "our algorithm" to "NHS
  demand + cost case" — a genuine strategic correction, not a restatement.
- **Domain care:** keeps medical-AI claims evidence-bounded — important and
  client-specific.

### 03 · GreenCrate — *Useful*
- **What worked:** Identifies that the active Instagram account reaches the wrong
  buyers and reallocates effort to direct B2B outreach + LinkedIn; converts the
  three pilots into case studies + an ROI one-pager; gives concrete numeric
  targets per phase (3 → 30).
- **Strategic value signal:** picks a single repeatable loop ("case study →
  targeted outreach → trade-show conversion") instead of doing a bit of everything.
- **Resource realism:** explicitly names the part-time marketer as the bottleneck
  and tells the client what to *stop* doing.

### `mock` baseline — *Not useful for a real client (by design)*
- Structurally complete and clear, but **generic**: the stakeholder table and
  channels would suit almost any organisation. No client name, no budget figures,
  no real trade-offs. It is fine as an offline demo placeholder but would fail a
  client review.
- **Why it matters:** it is the perfect *negative* example. The gap between it and
  the three real strategies is exactly what the rubric must be able to detect —
  especially on **Relevance** and **Strategic value**.

## What this tells us for the rubric (feeds Tasks 6 & 7)

1. **Specificity is the strongest discriminator.** "Useful" strategies name the
   client's people, money and dates; the weak one doesn't. The rubric's
   *Relevance* criterion should explicitly reward named, client-specific detail
   and penalise interchangeable content.
2. **Useful strategies make trade-offs.** All three real strategies say what to
   *de-prioritise*. The rubric should reward explicit prioritisation, not just
   coverage — this is the *Strategic value* criterion.
3. **Resource-appropriateness needs to be its own criterion.** Generic LLM output
   tends to ignore budget/team limits; respecting them (£5k, 4-month runway,
   part-time marketer) is a defining feature of a *useful* plan and is easy to
   miss if folded into "actionability."
4. **Actionability ≠ a long task list.** The useful strategies give 3–5 concrete
   next steps a named owner can start immediately; length is not the signal.
5. **Clarity is necessary but not sufficient.** The mock scored well on clarity
   yet was not useful — so clarity alone must never be enough to "pass."

> **Conclusion:** The full prompt → output workflow produces client-useful
> strategies across all three personas, and the contrast with the generic `mock`
> output gives us a clear sense of the "floor." This is the ground truth Task 5
> (template) and Tasks 6–7 (human method + rubric) build on.
