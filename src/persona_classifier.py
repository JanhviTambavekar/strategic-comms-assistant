"""Rule-based persona classifier.

Mirrors the 'Persona Classifier' box in the architecture diagram. The user can
pick a persona explicitly; this module can also *suggest* one from free text
(e.g. an uploaded document) using simple keyword scoring.
"""
from .config_loader import load_personas


def suggest_persona(text: str) -> str:
    """Suggest a persona key from free text via keyword frequency scoring."""
    personas = load_personas()
    text_l = (text or "").lower()
    best_key, best_score = None, -1
    for key, p in personas.items():
        score = sum(text_l.count(kw) for kw in p.get("keywords", []))
        if score > best_score:
            best_key, best_score = key, score
    # fall back to the first persona if nothing matched
    return best_key or next(iter(personas))
