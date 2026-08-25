"""Loads persona definitions and prompt templates from disk."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
PROMPTS_DIR = ROOT / "prompts"


def load_personas() -> dict:
    with open(CONFIG_DIR / "personas.json", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(name: str) -> str:
    """Load a prompt template by filename stem, e.g. 'full_strategy'."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")
