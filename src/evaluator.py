"""LLM-as-judge evaluation of generated strategies against the project rubric.

Implements the formal rubric in docs/evaluation_rubric.md (v2.0):
10 criteria scored 1-5, an average, MUST-PASS gates, and a three-tier verdict.
"""
import json
import re
from hashlib import sha256

from .config_loader import load_prompt
from . import llm_client

# The 10 rubric criteria. The first four map 1:1 to the human criteria in
# docs/human_evaluation_method.md; the rest are structural/quality criteria.
CRITERIA = [
    "clarity",
    "relevance",
    "actionability",
    "resource_appropriateness",
    "coherence",
    "strategic_value",
    "data_integrity",
    "persona_quality",
    "timeline_quality",
    "kpi_quality",
]

# Criteria that act as hard gates: if either is below MUST_PASS_MIN the strategy
# is capped at "Not useful", regardless of the other scores.
MUST_PASS = ["relevance", "resource_appropriateness"]
MUST_PASS_MIN = 3

VERDICT_USEFUL = "Useful"
VERDICT_EDITS = "Useful with edits"
VERDICT_NOT_USEFUL = "Not useful"
EVALUATOR_VERSION = "2.1"


def evaluate(
    strategy: str,
    client_inputs: str,
    judge_model: str | None = None,
    max_tokens: int = 800,
):
    """Score a strategy on the rubric.

    Returns a tuple (scores, usage):
      - scores: dict of {criterion -> 1-5} plus 'average', 'verdict', 'comment'
      - usage:  cost.Usage for the judge call (for token/cost accounting)
    """
    prompt = load_prompt("evaluation").format(
        client_inputs=client_inputs, strategy=strategy
    )
    raw, usage = llm_client.generate_with_usage(
        prompt, max_tokens=max_tokens, model=judge_model
    )
    scores = _parse_json(raw)

    clean = {}
    for c in CRITERIA:
        try:
            value = int(round(float(scores.get(c, 0))))
            clean[c] = value if 1 <= value <= 5 else 0
        except (TypeError, ValueError):
            clean[c] = 0
    clean["comment"] = str(scores.get("comment", "")).strip()

    validation = validate_strategy_structure(strategy)
    validation_issues, score_caps = audit_completion(strategy, validation)
    for criterion, cap in score_caps.items():
        if clean[criterion]:
            clean[criterion] = min(clean[criterion], cap)
    clean["validation_issues"] = validation_issues
    clean["timeline_validation"] = validation["timeline"]
    clean["kpi_validation"] = validation["kpi"]
    clean["evaluator_version"] = EVALUATOR_VERSION
    clean["judge_model"] = getattr(usage, "model", judge_model or "")
    clean["strategy_hash"] = sha256(strategy.encode("utf-8")).hexdigest()[:12]

    valid = [clean[c] for c in CRITERIA if clean[c] > 0]
    clean["average"] = round(sum(valid) / len(valid), 2) if valid else 0
    clean["verdict"] = verdict(clean)
    return clean, usage


def validate_strategy_structure(strategy: str) -> dict:
    """Return deterministic timeline and KPI validation for a strategy."""
    timeline = validate_timeline(strategy)
    kpi = validate_kpis(strategy)
    return {"timeline": timeline, "kpi": kpi}


def _section_text(strategy: str, start_pattern: str, end_pattern: str | None = None) -> str:
    """Extract a Markdown section while tolerating numbered subheadings."""
    start = re.search(start_pattern, strategy, re.IGNORECASE | re.MULTILINE)
    if not start:
        return ""
    remainder = strategy[start.end():]
    if not end_pattern:
        return remainder
    end = re.search(end_pattern, remainder, re.IGNORECASE | re.MULTILINE)
    return remainder[:end.start()] if end else remainder


def _is_meaningful_period(line: str, match: re.Match) -> bool:
    """Reject a bare date/range but accept a row that includes an activity."""
    remainder = (line[:match.start()] + " " + line[match.end():]).strip()
    words = re.findall(r"[A-Za-z]{3,}", remainder.lower())
    ignored = {
        "month", "months", "year", "years", "period", "time", "timeline",
        "investors", "partners", "regulators", "aida", "stage", "channel",
    }
    return len([word for word in words if word not in ignored]) >= 2


def validate_timeline(strategy: str) -> dict:
    """Parse meaningful implementation coverage across Months 1-36.

    A mention of "36 months" is deliberately not evidence of a timeline. Each
    recognised month range or Year 1/2/3 marker must share a line with an actual
    activity, milestone or other substantive content.
    """
    timeline_text = _section_text(
        strategy,
        r"^(?:#{1,6}\s*)?(?:\d+\.\s*)?engagement timeline\b",
        r"^(?:#{1,6}\s*)?(?:8\.\s*)?(?:kpi|risk assessment|next steps)\b",
    )
    covered: set[int] = set()
    labels: list[str] = []
    period_lines: list[str] = []
    has_month_column = bool(re.search(r"\bmonths?\b", timeline_text, re.IGNORECASE))
    for line in timeline_text.splitlines():
        month_matches = list(re.finditer(
            r"\bmonths?\s*(\d{1,2})\s*(?:-|–|—|to)\s*(\d{1,2})\b",
            line,
            re.IGNORECASE,
        ))
        for match in month_matches:
            start, end = int(match.group(1)), int(match.group(2))
            if 1 <= start <= end <= 36 and _is_meaningful_period(line, match):
                covered.update(range(start, end + 1))
                labels.append(f"Months {start}-{end}")
                period_lines.append(line)

        # Tables commonly put "Month" in the header, then use compact 1-3,
        # 4-6 rows. Treat that as a timeline range only inside this context.
        if has_month_column and not month_matches:
            for match in re.finditer(r"(?<!\d)(\d{1,2})\s*(?:-|–|—|to)\s*(\d{1,2})(?!\d)", line):
                start, end = int(match.group(1)), int(match.group(2))
                if 1 <= start <= end <= 36 and _is_meaningful_period(line, match):
                    covered.update(range(start, end + 1))
                    labels.append(f"Months {start}-{end}")
                    period_lines.append(line)

        year_matches = list(re.finditer(r"\byear\s*([123])\b", line, re.IGNORECASE))
        for match in year_matches:
            if _is_meaningful_period(line, match):
                year = int(match.group(1))
                start, end = (year - 1) * 12 + 1, year * 12
                covered.update(range(start, end + 1))
                labels.append(f"Year {year}")
                period_lines.append(line)

    missing = [month for month in range(1, 37) if month not in covered]
    coverage = round(len(covered) / 36 * 100, 1)
    aida_terms = r"\b(?:aida|attention|interest|desire|action)\b"
    channel_terms = r"\b(?:channel|message|linkedin|webinar|email|event|conference|report|case study)\b"
    has_required_cell_detail = bool(period_lines) and all(
        re.search(aida_terms, line, re.IGNORECASE) and re.search(channel_terms, line, re.IGNORECASE)
        for line in period_lines
    )
    if coverage == 100 and has_required_cell_detail:
        score, valid, reason = 5, True, "Meaningful activities cover every month from 1 to 36 with AIDA and channel/message detail."
    elif coverage == 100:
        score, valid, reason = 3, False, "Months 1-36 are covered, but timeline cells lack required AIDA and channel/message detail."
    elif coverage >= 75:
        score, valid, reason = 3, False, "The timeline covers most of the period but has material gaps."
    elif coverage > 0:
        score, valid, reason = 2, False, "The timeline covers only part of the 36-month implementation period."
    else:
        score, valid, reason = 1, False, "No meaningful Month 1-36 implementation timeline was found."

    return {
        "timeline_valid": valid,
        "timeline_coverage": coverage,
        "covered_periods": labels,
        "missing_periods": missing,
        "timeline_score": score,
        "timeline_detail_valid": has_required_cell_detail,
        "timeline_validation_reason": reason,
    }


def validate_kpis(strategy: str) -> dict:
    """Check that KPI content contains measurable, timed and audience-linked targets."""
    kpi_text = _section_text(
        strategy,
        r"^(?:#{1,6}\s*)?(?:8\.\s*)?(?:kpi and success measures|kpi)\b",
        r"^(?:#{1,6}\s*)?(?:9\.\s*)?(?:risk assessment|next steps)\b",
    )
    valid_rows = 0
    for line in kpi_text.splitlines():
        has_target = bool(re.search(
            r"\b\d+(?:\.\d+)?(?:\s*%|(?:\s+[A-Za-z-]+){0,2}\s+"
            r"(?:enquiries|leads|meetings|contracts|pilots|investors|partners|organisations))\b",
            line,
            re.IGNORECASE,
        ))
        has_timeframe = bool(re.search(r"\b(?:month|months|quarter|quarters|year|years)\s*\d+\b|\b(?:by|within|over)\s+\d+\s+(?:month|months|year|years)\b", line, re.IGNORECASE))
        has_audience = bool(re.search(r"\b(?:investors?|partners?|regulators?)\b", line, re.IGNORECASE))
        if has_target and has_timeframe and has_audience:
            valid_rows += 1
    # Validate the detailed KPI blocks used by the strategy prompt. This also
    # catches unsupported arithmetic such as 200 reached x 10% = 2 enquiries.
    arithmetic_blocks = 0
    arithmetic_valid = 0
    audience_blocks = re.split(r"(?im)^\s*(?:#+\s*)?(investors?|partners?|regulators?)\s*$", kpi_text)
    for index in range(2, len(audience_blocks), 2):
        block = audience_blocks[index]
        market = re.search(r"addressable market:\s*([\d,.]+)", block, re.IGNORECASE)
        reach = re.search(r"reach:\s*(\d+(?:\.\d+)?)%[^\n]*?\([^\d]*([\d,.]+)", block, re.IGNORECASE)
        conversion = re.search(r"conversion rate:\s*(\d+(?:\.\d+)?)%[^\n]*?\([^\d]*([\d,.]+)", block, re.IGNORECASE)
        if not (market and reach and conversion):
            continue
        arithmetic_blocks += 1
        market_value = float(market.group(1).replace(",", ""))
        reach_percent, reach_value = float(reach.group(1)), float(reach.group(2).replace(",", ""))
        conversion_percent, conversion_value = float(conversion.group(1)), float(conversion.group(2).replace(",", ""))
        expected_reach = market_value * reach_percent / 100
        expected_conversion = reach_value * conversion_percent / 100
        if abs(expected_reach - reach_value) <= 1 and abs(expected_conversion - conversion_value) <= 1:
            arithmetic_valid += 1

    valid = valid_rows >= 2 or (arithmetic_blocks >= 2 and arithmetic_valid >= 2)
    return {
        "kpi_valid": valid,
        "validated_kpi_rows": valid_rows,
        "kpi_arithmetic_blocks": arithmetic_blocks,
        "kpi_arithmetic_valid_blocks": arithmetic_valid,
        "kpi_validation_reason": (
            "At least two measurable, timed and audience-linked KPI rows were found."
            if valid else
            "KPIs need measurable targets with a timeframe and named audience; any reach/conversion arithmetic must reconcile."
        ),
    }


def audit_completion(strategy: str, validation: dict | None = None) -> tuple[list[str], dict[str, int]]:
    """Check mandatory v4 sections before a plan can receive a high verdict."""
    text = strategy.lower()
    issues: list[str] = []
    caps: dict[str, int] = {}

    required_sections = {
        "## 8. kpi and success measures": ("KPI and Success Measures section is missing", "kpi_quality"),
        "## 9. risk assessment": ("Risk Assessment section is missing", "coherence"),
        "## 10. next steps": ("Next Steps section is missing", "actionability"),
    }
    for heading, (message, criterion) in required_sections.items():
        if heading not in text:
            issues.append(message)
            caps[criterion] = 1

    required_headings = (
        "## 1. executive summary",
        "## objectives and outcome measures",
        "## 2. assumptions for review",
        "## 3. stakeholder analysis",
        "## 4. audience journey map",
        "## 5. key messages",
        "## 6. communication channels",
        "## 7. engagement timeline",
    )
    if any(heading not in text for heading in required_headings):
        issues.append("Required Markdown output headings are missing or malformed")
        caps["clarity"] = 1
        caps["coherence"] = 1

    validation = validation or validate_strategy_structure(strategy)
    timeline = validation["timeline"]
    kpi = validation["kpi"]
    if not timeline["timeline_valid"]:
        issues.append(
            f"36-month Engagement Timeline is incomplete: {timeline['timeline_coverage']}% coverage. "
            f"{timeline['timeline_validation_reason']}"
        )
        caps["timeline_quality"] = timeline["timeline_score"]
        # A KPI framework cannot earn the maximum score when the delivery plan
        # it is meant to measure has material gaps.
        caps["kpi_quality"] = min(caps.get("kpi_quality", 5), 3)
    if "## 7. engagement timeline" in text and "|" not in strategy:
        issues.append("Engagement Timeline is not presented as a table")
        caps["timeline_quality"] = 1

    if not kpi["kpi_valid"]:
        issues.append(kpi["kpi_validation_reason"])
        caps["kpi_quality"] = min(caps.get("kpi_quality", 5), 2)

    if any(len(line) > 1_200 for line in strategy.splitlines()):
        issues.append("Output contains an unstructured text block and should be regenerated")
        caps["clarity"] = 1
        caps["coherence"] = 1
        caps["timeline_quality"] = 1

    return issues, caps


def verdict(scores: dict) -> str:
    """Apply the rubric thresholds + MUST-PASS gates to produce a verdict.

    See docs/evaluation_rubric.md §3-4.
    """
    average = scores.get("average", 0)
    must_pass_vals = [scores.get(c, 0) for c in MUST_PASS]

    # Gate: any must-pass criterion below the floor caps the verdict.
    if any(v < MUST_PASS_MIN for v in must_pass_vals):
        return VERDICT_NOT_USEFUL

    all_scores = [scores.get(c, 0) for c in CRITERIA]
    if average >= 4.0 and all(v >= 4 for v in must_pass_vals) and all(
        v >= 3 for v in all_scores
    ) and scores.get("timeline_quality", 0) >= 4 and scores.get("kpi_quality", 0) >= 3:
        return VERDICT_USEFUL
    if average >= 3.0:
        return VERDICT_EDITS
    return VERDICT_NOT_USEFUL


def _parse_json(raw: str) -> dict:
    """Best-effort extraction of a JSON object from an LLM response."""
    if not raw:
        return {}
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
