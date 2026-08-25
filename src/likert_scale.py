"""Load and manage the Likert scale configuration for human evaluation.

Reads the scale options from docs/likert_scale.md and provides them
to the application for display in the evaluation interface.
"""
import re
from pathlib import Path

# Default Likert scale options (used if config file is missing)
DEFAULT_LIKERT_SCALE = [
    "Strongly Disagree",
    "Disagree",
    "Neither Agree nor Disagree",
    "Agree",
    "Strongly Agree",
]


def load_likert_scale() -> list[str]:
    """Load the Likert scale options from docs/likert_scale.md.

    Parses the markdown file to extract the scale options in order.
    Falls back to DEFAULT_LIKERT_SCALE if the file is missing or malformed.

    Returns:
        List of scale option strings, e.g. ["Strongly Disagree", "Disagree", ...]
    """
    config_path = Path(__file__).parent.parent / "docs" / "likert_scale.md"

    if not config_path.exists():
        return DEFAULT_LIKERT_SCALE.copy()

    try:
        content = config_path.read_text(encoding="utf-8")

        # Extract numbered list items (e.g., "1. **Strongly Disagree**")
        pattern = r"^\d+\.\s+\*\*(.+?)\*\*"
        matches = re.findall(pattern, content, re.MULTILINE)

        if matches:
            return matches

        # Fallback: look for lines with bold text after a number
        pattern2 = r"^\d+\.\s+(.+)$"
        matches2 = re.findall(pattern2, content, re.MULTILINE)
        if matches2:
            return [m.strip() for m in matches2]

        return DEFAULT_LIKERT_SCALE.copy()

    except Exception:
        return DEFAULT_LIKERT_SCALE.copy()


# Load the scale once at module import
LIKERT_SCALE = load_likert_scale()


def get_likert_scale() -> list[str]:
    """Return the current Likert scale options."""
    return LIKERT_SCALE.copy()


def get_likert_value(label: str) -> int:
    """Convert a Likert scale label to its numeric value (1-5).

    Args:
        label: The scale label, e.g. "Agree"

    Returns:
        Integer value (1-5), or 0 if not found
    """
    try:
        return LIKERT_SCALE.index(label) + 1
    except ValueError:
        return 0


def get_likert_label(value: int) -> str:
    """Convert a numeric value (1-5) to its Likert scale label.

    Args:
        value: Integer value (1-5)

    Returns:
        Scale label string, or empty string if invalid
    """
    if 1 <= value <= len(LIKERT_SCALE):
        return LIKERT_SCALE[value - 1]
    return ""