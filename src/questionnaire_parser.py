"""Parse questionnaire answers from an uploaded file.

Supports three formats:
  1. AISCE format: "Q1. Label ... **Answer** value" (as in the provided prompt)
  2. Numbered format: "1. Question title\nAnswer text..." with ___ separators
  3. Simple: "Label: value" lines

Returns a dict of {question_id: answer_value} keyed by the questionnaire's
question ids (e.g. "org_name", "mission_vision_goals").
"""
import re


def parse_questionnaire_file(text: str, questionnaire: list) -> dict:
    """Parse uploaded file text into {question_id: answer} for the given questionnaire.

    `questionnaire` is the list of question dicts from config/personas.json.
    """
    answers = {}
    if not text:
        return answers

    # Build a map from question number (1..31) -> question id.
    num_to_id = {}
    for q in questionnaire:
        label = q.get("label", "")
        # Extract the Q-number from the label (e.g. "Q1. Consent and ...")
        m = re.match(r"Q?(\d+)\.", label)
        if m:
            num_to_id[int(m.group(1))] = q["id"]

    # --- Format 1: "Q1. / 1. Question header ... Answer value" blocks ---
    # Split on lines that look like a question header (Q1. or 1. at line start).
    # Also handle the numbered format where answers are separated by ___ lines.
    blocks = re.split(r"(?m)^\s*(?:Q?\d+\.\s*.+?)(?=\n\s*(?:Q?\d+\.|_)|\Z)", text)
    if len(blocks) <= 1:
        # The regex above may not split properly; try an alternative approach.
        blocks = _split_numbered_blocks(text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        m = re.match(r"^Q?(\d+)\.\s*(.*)$", block, re.DOTALL)
        if not m:
            continue
        qnum = int(m.group(1))
        body = m.group(2)

        # Extract the answer:
        # 1. After **Answer** marker
        ans_match = re.search(r"\*\*Answer\*\*\s*(.*)", body, re.DOTALL)
        if ans_match:
            value = ans_match.group(1).strip()
        else:
            # 2. After "Answer -" / "Answer:" marker
            ans_match = re.search(r"(?i)Answer\s*[-:]\s*(.*)", body, re.DOTALL)
            if ans_match:
                value = ans_match.group(1).strip()
            else:
                # 3. Numbered format: the question heading is the first line,
                #    everything after is the answer (strip separators).
                lines = block.splitlines()
                if len(lines) > 1:
                    value = "\n".join(lines[1:]).strip()
                else:
                    value = ""

        # Strip separator artifacts and trailing markers.
        value = re.sub(r"^[\s_\-*]+", "", value).strip()
        value = re.sub(r"[\s_\-*]+$", "", value).strip()
        value = value.replace("________________________________________", "").strip()

        if qnum in num_to_id and value:
            answers[num_to_id[qnum]] = value

    # --- Format 3: "Label: value" lines (fallback if nothing was parsed) ---
    if not answers:
        label_to_id = {}
        for q in questionnaire:
            label = re.sub(r"^Q\d+\.\s*", "", q.get("label", "")).strip().lower()
            label_to_id[label] = q["id"]

        for line in text.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            label_part, _, value = line.partition(":")
            label_part = re.sub(r"^Q?\d+\.\s*", "", label_part).strip().lower()
            value = value.strip()
            if value and label_part in label_to_id:
                answers[label_to_id[label_part]] = value

    return answers


def _split_numbered_blocks(text: str) -> list:
    """Split text into blocks starting with 'N.' or 'QN.' headings.

    Handles the format where answers are separated by lines of underscores:
        1. Question title
        Answer text
        ____________________
        2. Next question
        Answer text
    """
    lines = text.splitlines()
    blocks = []
    current = []
    for line in lines:
        stripped = line.strip()
        # A new question starts with "N." or "QN." at the beginning of a line.
        if re.match(r"^Q?\d+\.\s*\S", stripped):
            if current:
                blocks.append("\n".join(current))
                current = []
            current.append(stripped)
        elif stripped.startswith("___") or stripped.startswith("---") or stripped.startswith("==="):
            # Separator line: end current block if it has content.
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks