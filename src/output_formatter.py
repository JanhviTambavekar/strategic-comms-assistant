"""Formats and packages the generated strategy for display/download."""
import re


def add_title(strategy_md: str, persona_label: str, org_name: str) -> str:
    """Prepend a title header to the generated markdown strategy."""
    title = (org_name or "").strip() or persona_label
    header = f"# Strategic Communication & Engagement Plan\n### {title} ({persona_label})\n\n"
    return header + (strategy_md or "").strip() + "\n"


def safe_filename(name: str, default: str = "strategy") -> str:
    """Make a filesystem-safe filename stem."""
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", (name or "").strip()).strip("_")
    return (stem or default).lower()
