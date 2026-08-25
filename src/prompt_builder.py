"""Assembles the final LLM prompt from a template + client inputs."""
from .config_loader import load_prompt


def format_client_inputs(answers: dict, questionnaire: list) -> str:
    """Turn questionnaire answers into a readable labelled block."""
    label_by_id = {q["id"]: q["label"] for q in questionnaire}
    lines = []
    for qid, value in answers.items():
        if value:
            label = label_by_id.get(qid, qid)
            lines.append(f"- {label}: {value}")
    return "\n".join(lines) if lines else "(no answers provided)"


def build_prompt(template_name: str, persona: dict, objective: str,
                 client_inputs: str, document_context: str) -> str:
    """Fill a prompt template with the client's context."""
    template = load_prompt(template_name)
    return template.format(
        persona_label=persona.get("label", ""),
        persona_description=persona.get("description", ""),
        objective=objective,
        client_inputs=client_inputs,
        document_context=document_context.strip() or "(none uploaded)",
    )
