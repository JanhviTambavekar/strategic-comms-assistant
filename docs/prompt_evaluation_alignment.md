# Prompt and Evaluation Alignment Review

**Status:** v1.0 — review framework for the revised human evaluation form.

The evaluation distinguishes two layers. This avoids treating a good interface
as evidence of a good strategy, or judging the interface from the strategy text
alone.

| Evaluation layer | What is assessed | Evidence source | Covered by the generation prompt? |
|---|---|---|---|
| Strategy output | Clarity, tailoring, actionability, feasibility, messages/channels, timeline/KPIs, overall usefulness | Generated strategy plus the client inputs | Yes — directly assessed by the formal rubric and instructed in `full_strategy.txt` |
| Service and process experience | Questionnaire clarity, effort, document handling, input-to-output transparency, confidence to reuse | The participant's experience of completing the workflow | No — these are interface and workflow measures, so they must not be scored by the LLM-as-judge |

## Output-question traceability

| Human form question | Prompt / rubric evidence |
|---|---|
| Clear and easy to follow | Exact 10-section Markdown output contract; C1 Clarity |
| Specific to the organisation | Client inputs and supporting documents; anti-generic requirement; C2 Relevance |
| Concrete enough to act on | Next Steps, AIDA journey and timeline requirements; C3 Actionability |
| Realistic for resources | Budget/team/business-stage requirement; C4 Resource-appropriateness |
| Messages and channels tailored to audiences | Personas, Message Architecture and Channel Strategy requirements |
| Credible timeline and KPIs | Mandatory 36-month table, absolute figures and KPI derivation rules; C9/C10 |
| Overall useful plan | Formal verdict, with relevance and resource-appropriateness as must-pass gates |

## Use with HelioSeras and People's Panel reviews

For each reviewed strategy, retain the completed form with the strategy version,
persona, model/provider, date and reviewer. Record reviewer annotations as
qualitative evidence alongside the ratings. Compare strategy-output scores across
batches; report process scores separately and do not combine them into one overall
mean. The HelioSeras Round 2 strategies can therefore serve as an additional
review set, while Edwin's forthcoming People's Panel review can be added without
changing the instrument.

## Scale

All statements use the same 5-point scale: **1 Strongly Disagree, 2 Disagree,
3 Neither Agree nor Disagree, 4 Agree, 5 Strongly Agree**. This is easier to
interpret and sufficient for a small formative evaluation; it also matches the
existing automated-rubric range, though the two measures must remain separate.
