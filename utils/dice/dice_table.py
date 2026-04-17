from utils.dice.dice_presets import DICE_PRESET, MAX_DICE_VALUE

STYLES = ["Front", "Pace", "Late", "End"]
PHASES = [1, 2, 3, 4]


def format_rule(rule: dict) -> str:
    d = rule["d"]
    kh = rule.get("kh")

    text = f"d{MAX_DICE_VALUE}" if d == 1 else f"{d}d{MAX_DICE_VALUE}"
    if kh is not None:
        text += f"kh{kh}"
    return text


def build_style_table(color_type: str) -> str:
    lines = []
    for style in STYLES:
        row = [style]
        for phase in PHASES:
            row.append(format_rule(DICE_PRESET[style][color_type][phase]))
        lines.append(
            f"**{row[0]}** | {row[1]} | {row[2]} | {row[3]} | {row[4]}"
        )
    return "\n".join(lines)

