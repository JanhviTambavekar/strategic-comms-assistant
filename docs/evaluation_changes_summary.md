# Evaluation Changes Summary

**Status:** Implemented

This document is the single record of the evaluation changes requested after
reviewing the improved strategy outputs and considering the suitability of the
evaluation form for the Strategic Communications Assistant.

## 1. Why the evaluation form changed

The original form treated all questions as ratings of the generated strategy.
This mixed two different things:

1. **Strategy output quality** — whether the generated plan is useful,
   tailored, feasible and actionable for the organisation.
2. **Service and process experience** — whether completing the questionnaire,
   adding supporting information and understanding the input-to-output flow was
   straightforward for the participant.

These layers are now assessed separately. They must not be combined into one
overall score: a participant may find the service easy to use but receive a weak
strategy, or receive a strong strategy after a difficult process.

## 2. Rating scale

The evaluation uses a five-point Likert agreement scale:

| Score | Response |
|---:|---|
| 1 | Strongly Disagree |
| 2 | Disagree |
| 3 | Neither Agree nor Disagree |
| 4 | Agree |
| 5 | Strongly Agree |

A five-point scale was retained instead of a seven-point scale because it is
easy for a small formative study to understand and interpret, while still
providing a neutral option and a clear direction of agreement.

## 3. Revised human evaluation form

### Layer A — Strategy output quality

Participants rate their agreement with these statements:

1. The strategy is clearly written and easy to follow.
2. The strategy is specific to this organisation's context, audiences and objectives.
3. The recommendations are concrete enough to act on immediately.
4. The recommendations are realistic for the stated budget, team and timeframe.
5. The messages and channels are tailored to the priority audiences.
6. The timeline and KPIs provide a credible way to deliver and measure the strategy.
7. Overall, this is a useful strategic communications plan for this organisation.

### Layer B — Service and process experience

Participants separately rate their agreement with these statements:

1. The questionnaire made it clear what information was needed.
2. The time and effort required to provide the information felt appropriate.
3. Uploading or entering supporting information was straightforward.
4. The process made it clear how my inputs informed the generated strategy.
5. I would feel confident using this service again or recommending it to a colleague.

Every rating starts as **Select a rating** (unanswered), rather than defaulting
to Strongly Disagree. The application displays a separate average for each layer
only after all statements have been intentionally rated, and retains the response
distribution as supporting context. A **Clear human evaluation ratings** control
allows a reviewer to start again.

## 4. Prompt and evaluation alignment

The output-quality questions are aligned with the strategy-generation prompt
and the formal LLM-as-judge rubric:

| Output evaluation question | Prompt / rubric evidence |
|---|---|
| Clear and easy to follow | Fixed 10-section Markdown output contract; Clarity criterion |
| Specific to the organisation | Client inputs and supporting-document grounding; anti-generic requirement; Relevance criterion |
| Concrete recommendations | Next Steps, AIDA journey and timeline requirements; Actionability criterion |
| Realistic for resources | Budget, team and business-stage requirement; Resource-appropriateness criterion |
| Audience-tailored messages and channels | Persona, Message Architecture and Channel Strategy requirements |
| Credible timeline and KPIs | Mandatory 36-month table, absolute figures and KPI derivation rules; Timeline and KPI criteria |
| Overall usefulness | Formal verdict, including relevance and resource-appropriateness must-pass gates |

The process-experience questions are intentionally **not** assessed by the
LLM-as-judge. They concern the participant's interaction with the system and
require direct user feedback.

The LLM-as-judge is also presented as an automated assessment, not proof that a
strategy is 100% correct. It should be checked against the client inputs and
supplemented by the human review form and reviewer comments.

## 5. Use with strategy-review batches

For each reviewed strategy, retain the completed form with the strategy version,
persona, model/provider, date and reviewer. Keep reviewer annotations as
qualitative evidence alongside the numerical ratings.

- The HelioSeras Round 2 strategies can be recorded as an additional review set.
- Edwin's forthcoming People's Panel review can use the same form without any
  change to the instrument.
- Compare strategy-output scores across batches.
- Report service/process scores separately; do not fold them into strategy quality.

## 6. Implementation locations

| Item | Location |
|---|---|
| Revised two-layer form and separate averages | `app.py` — Evaluation Dashboard |
| Five-point scale configuration | `docs/likert_scale.md`, `src/likert_scale.py` |
| Formal output-quality rubric | `docs/evaluation_rubric.md`, `prompts/evaluation.txt`, `src/evaluator.py` |
| Strategy-generation requirements | `prompts/full_strategy.txt` |
| Detailed human evaluation method | `docs/human_evaluation_method.md` |

## 7. Strategy-completeness improvements

The strategy generator now has a 5,000-token output budget. This replaces the
previous 2,000-token limit, which could cut a response off before Months 13-36,
KPIs, Risk Assessment and Next Steps. The generation prompt also requires a
completion check, explicit priority/de-priority choices, owners and resource
trade-offs, and clear labelling of unsupported facts as assumptions.

The LLM-as-judge now applies deterministic completion checks in addition to its
rubric assessment. A missing KPI section, Risk Assessment, Next Steps section,
or incomplete 36-month timeline produces a visible warning and caps the relevant
criterion, so an incomplete plan cannot receive a misleading **Useful** verdict.

For smaller instruction models, generation uses a low temperature (0.2) to
reduce unstable, repetitive or unrelated text in long structured outputs. The
completion audit also flags malformed Markdown headings and unusually long,
unstructured text blocks as invalid output that should be regenerated.

The strategy prompt includes a decision-readiness clarity standard. It requires
plain language, evidence-led claims, no duplicated content, and a clear owner,
timing, trade-off and success measure for recommendations. This improves quality
rather than manipulating the LLM-as-judge score; each judge criterion remains an
integer from 1 to 5.
