from __future__ import annotations


def _normalize_spaces(text: str) -> str:
    return " ".join(str(text or "").split())


def format_bonus_display(bonus_display: str, *, block_label: str = "BLOCK") -> str:
    text = _normalize_spaces(bonus_display)
    if not text or text == "-":
        return "-"

    tokens = [token for token in text.split(" ") if token != "DRAFT"]
    formatted = " ".join(tokens)
    if not formatted:
        return "-"
    return formatted.replace("BLOCK", block_label)


def format_stamina_line(stamina_note: str, *, drafting_active: bool = False, draft_label: str = "DRAFT") -> str:
    text = str(stamina_note or "").strip()
    if drafting_active:
        return f"{text} {draft_label}".strip()
    return text
