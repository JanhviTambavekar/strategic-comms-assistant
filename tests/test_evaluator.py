import unittest
from unittest.mock import patch

from src.evaluator import (
    VERDICT_EDITS,
    audit_completion,
    evaluate,
    validate_kpis,
    validate_timeline,
)


def strategy_with_timeline(timeline: str, kpis: str = "") -> str:
    return f"""## 1. Executive Summary
Plan.
## Objectives and Outcome Measures
Objective.
## 2. Assumptions for Review
Assumption.
## 3. Stakeholder Analysis
Analysis.
## 4. Audience Journey Map
Journey.
## 5. Key Messages
Messages.
## 6. Communication Channels
Channels.
## 7. Engagement Timeline
| Period | Investors |
|---|---|
{timeline}
## 8. KPI and Success Measures
{kpis}
## 9. Risk Assessment
Risk.
## 10. Next Steps
Owner completes first action.
"""


class TimelineValidationTests(unittest.TestCase):
    def test_complete_36_months_allows_full_score(self):
        timeline = "\n".join([
            "| Months 1-3 | Task: Publish briefing; AIDA: Attention; Channel: LinkedIn |",
            "| Months 4-6 | Task: Run webinars; AIDA: Interest; Channel: webinar |",
            "| Months 7-9 | Task: Share pilot evidence; AIDA: Desire; Channel: case study |",
            "| Months 10-12 | Task: Hold funding meetings; AIDA: Action; Channel: event |",
            "| Months 13-18 | Task: Convert partners; AIDA: Interest; Channel: email |",
            "| Months 19-24 | Task: Refresh evidence; AIDA: Desire; Channel: report |",
            "| Months 25-30 | Task: Expand outreach; AIDA: Attention; Channel: LinkedIn |",
            "| Months 31-36 | Task: Review results; AIDA: Action; Channel: webinar |",
        ])
        result = validate_timeline(strategy_with_timeline(timeline))
        self.assertTrue(result["timeline_valid"])
        self.assertEqual(result["timeline_coverage"], 100.0)
        self.assertEqual(result["timeline_score"], 5)

    def test_missing_year_three_is_reduced(self):
        timeline = "\n".join([
            "| Months 1-6 | Publish investor briefing |",
            "| Months 7-12 | Run partner webinars |",
            "| Months 13-18 | Share pilot evidence |",
            "| Months 19-24 | Hold funding meetings |",
        ])
        result = validate_timeline(strategy_with_timeline(timeline))
        self.assertFalse(result["timeline_valid"])
        self.assertEqual(result["timeline_coverage"], 66.7)
        self.assertLess(result["timeline_score"], 5)

    def test_fake_36_month_claim_is_not_timeline(self):
        result = validate_timeline(strategy_with_timeline(
            "The organisation will implement the strategy over 36 months."
        ))
        self.assertFalse(result["timeline_valid"])
        self.assertEqual(result["timeline_coverage"], 0.0)

    def test_large_gaps_are_invalid(self):
        timeline = "\n".join([
            "| Months 1-6 | Publish investor briefing |",
            "| Months 13-18 | Run partner webinars |",
            "| Months 25-30 | Share pilot evidence |",
        ])
        result = validate_timeline(strategy_with_timeline(timeline))
        self.assertFalse(result["timeline_valid"])
        self.assertEqual(result["timeline_coverage"], 50.0)

    def test_complete_timeline_and_measurable_kpis_pass(self):
        timeline = "\n".join([
            "| Year 1 | Task: Publish briefing; AIDA: Attention; Channel: LinkedIn |",
            "| Year 2 | Task: Convert partners; AIDA: Desire; Channel: webinar |",
            "| Year 3 | Task: Scale evidence; AIDA: Action; Channel: report |",
        ])
        kpis = "\n".join([
            "| 12 qualified enquiries | Partners | by Month 12 |",
            "| 6 investor meetings | Investors | by Month 18 |",
            "| 3 regulator briefings | Regulators | by Month 24 |",
        ])
        strategy = strategy_with_timeline(timeline, kpis)
        self.assertTrue(validate_timeline(strategy)["timeline_valid"])
        self.assertTrue(validate_kpis(strategy)["kpi_valid"])
        issues, caps = audit_completion(strategy)
        self.assertFalse(issues)
        self.assertNotIn("timeline_quality", caps)

    def test_llm_cannot_override_missing_year_three(self):
        timeline = "\n".join([
            "| Months 1-6 | Publish investor briefing |",
            "| Months 7-12 | Run partner webinars |",
            "| Months 13-18 | Share pilot evidence |",
            "| Months 19-24 | Hold funding meetings |",
        ])
        kpis = "\n".join([
            "| 12 qualified enquiries | Partners | by Month 12 |",
            "| 6 investor meetings | Investors | by Month 18 |",
        ])
        llm_scores = (
            '{"clarity": 5, "relevance": 5, "actionability": 5, '
            '"resource_appropriateness": 5, "coherence": 5, "strategic_value": 5, '
            '"data_integrity": 5, "persona_quality": 5, "timeline_quality": 5, '
            '"kpi_quality": 5, "comment": "Incorrectly optimistic judge."}'
        )
        with patch("src.evaluator.llm_client.generate_with_usage", return_value=(llm_scores, None)):
            scores, _ = evaluate(strategy_with_timeline(timeline, kpis), "Client context")
        self.assertEqual(scores["timeline_quality"], 2)
        self.assertEqual(scores["kpi_quality"], 3)
        self.assertEqual(scores["verdict"], VERDICT_EDITS)


if __name__ == "__main__":
    unittest.main()
