"""Knowledge-tree / rule engine.

Maps (persona, objective) -> the prompt template that should be used to
generate the strategy. This is the routing backbone described in the project
document. For the MVP every route resolves to the full_strategy template, but
the structure makes it trivial to branch to specialised prompts per objective.
"""

# (persona_key, objective) -> prompt template stem.
# "*" acts as a wildcard fallback for any objective under that persona.
ROUTES = {
    ("research_project", "*"): "full_strategy",
    ("university_spinout", "*"): "full_strategy",
    ("sme_innovator", "*"): "full_strategy",
}

DEFAULT_PROMPT = "full_strategy"


def route(persona_key: str, objective: str) -> str:
    """Return the prompt template stem for a persona + objective."""
    if (persona_key, objective) in ROUTES:
        return ROUTES[(persona_key, objective)]
    if (persona_key, "*") in ROUTES:
        return ROUTES[(persona_key, "*")]
    return DEFAULT_PROMPT


def explain_route(persona_key: str, objective: str) -> str:
    """Human-readable trace of the routing decision, for the demo UI."""
    template = route(persona_key, objective)
    return (
        f"Persona `{persona_key}` + objective `{objective}` "
        f"-> prompt template `{template}.txt`"
    )
