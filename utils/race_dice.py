import random
import math
from utils.dice_presets import DICE_PRESET, MAX_DICE_VALUE
from utils.icon_presets import STAT_EMOJIS, Status_Icon_Type

def get_stat_emoji(value: int) -> str:
    value = max(1, min(value, 8))
    return STAT_EMOJIS[value]

def get_stat_icon(value: str) -> str:
    return Status_Icon_Type[value]

def count_nearby_players(player_id: int, score_map: dict[int, int], radius: int = 10) -> int:
    if player_id not in score_map:
        return 0

    player_score = score_map[player_id]

    count = 0
    for uid, score in score_map.items():
        if uid == player_id:
            continue

        if abs(player_score - score) <= radius:
            count += 1

    return count

def get_phase_from_turn(turn: int, max_turn: int) -> int:
    """
    แบ่งสนามเป็น 4 phase ตามจำนวน turn ของสนาม
    เช่น
    max_turn = 8  -> phase ละ 2 turn
    max_turn = 12 -> phase ละ 3 turn
    max_turn = 16 -> phase ละ 4 turn
    """
    if max_turn <= 0:
        return 1

    phase_size = max_turn / 4
    phase = math.ceil(turn / phase_size)
    return min(max(phase, 1), 4)

def get_distance_color(player_id: int, score_map: dict[int, int]) -> str:
    """
    score_map = {user_id: score}

    ถ้าระยะห่างจากม้าที่ใกล้ที่สุด <= 10 => Gold
    ถ้ามากกว่า 10 => White
    ถ้าอยู่คนเดียวในเกม => Gold
    """

    if player_id not in score_map:
        return "Gold"

    player_score = score_map[player_id]

    other_scores = [
        score for uid, score in score_map.items()
        if uid != player_id
    ]

    if not other_scores:
        return "Gold"

    nearest_gap = min(abs(player_score - score) for score in other_scores)

    if nearest_gap <= 10:
        return "Gold"
    return "White"


def get_dice_rule(style: str, distance_color: str, phase: int) -> dict:
    return DICE_PRESET[style][distance_color][phase]

def roll_by_rule(rule: dict, player: dict, context: dict) -> dict:
    d = rule["d"]
    kh = rule.get("kh")

    rolls = [random.randint(player.get("power", 1), MAX_DICE_VALUE) for _ in range(d)]
    original_rolls = rolls.copy()

    if kh is not None:
        selected = sorted(rolls, reverse=True)[:kh]
    else:
        selected = rolls.copy()

    modified_selected = []
    bonus_log = []

    total_spd_bonus = 0

    spd_bonus = player.get("speed", 0)
    power_bonus = player.get("power", 1)

    nearby_count = min(context.get("nearby_count", 0), 2)
    gut_bonus = (player.get("gut", 1) * nearby_count * 2) if context.get("distance_color") == "Gold" else 0

    for r in selected:
        value = r
        bonuses = []

        if spd_bonus > 0:
            value += spd_bonus
            total_spd_bonus += spd_bonus
            bonuses.append(f"SPD+{spd_bonus}")

        modified_selected.append(value)
        bonus_log.append(bonuses)

    base_total = sum(selected)

    # SPD ยังนับจากลูกเต๋า
    # POW / GUT บวกทีเดียวตอนรวม
    total = sum(modified_selected) + power_bonus + gut_bonus

    bonus_parts = []
    if total_spd_bonus > 0:
        bonus_parts.append(f"{get_stat_icon('SPD')}+{total_spd_bonus}")

    if gut_bonus > 0:
        bonus_parts.append(f"{get_stat_icon('GUT')}+{gut_bonus}")

    if power_bonus > 0:
        bonus_parts.append(f"{get_stat_icon('POW')}+{power_bonus}")

    if bonus_parts:
        total_display = f"{base_total} " + " ".join(bonus_parts)
    else:
        total_display = str(base_total)

    display_parts = []
    temp_selected = selected.copy()

    for r in original_rolls:
        if r in temp_selected:
            display_parts.append(f"__{r}__")
            temp_selected.remove(r)
        else:
            display_parts.append(str(r))

    return {
        "rolls": original_rolls,
        "selected": selected,
        "modified_selected": modified_selected,
        "bonus_log": bonus_log,
        "display": " , ".join(display_parts),
        "base_total": base_total,
        "total": total,
        "total_display": total_display,
    }

def roll_race_dice(
    style: str,
    player: dict,
    player_id: int,
    score_map: dict[int, int],
    turn: int,
    max_turn: int
) -> dict:
    phase = get_phase_from_turn(turn, max_turn)
    distance_color = get_distance_color(player_id, score_map)
    nearby_count = count_nearby_players(player_id, score_map, radius=10)
    rule = get_dice_rule(style, distance_color, phase)

    dice_result = roll_by_rule(rule, player, {
        "distance_color": distance_color,
        "nearby_count": nearby_count
    })

    return {
        "phase": phase,
        "distance_color": distance_color,
        "nearby_count": nearby_count,
        "rule": rule,
        "rolls": dice_result["rolls"],
        "selected": dice_result["selected"],
        "modified_selected": dice_result["modified_selected"],
        "bonus_log": dice_result["bonus_log"],
        "display": dice_result["display"],
        "base_total": dice_result["base_total"],
        "total": dice_result["total"],
        "total_display": dice_result["total_display"],
    }

def format_rule(rule: dict) -> str:
        d = rule["d"]
        kh = rule.get("kh")

        if d == 1:
            base = f"d{MAX_DICE_VALUE}"
        else:
            base = f"{d}d{MAX_DICE_VALUE}"

        if kh is not None:
            base += f"kh{kh}"

        return base

def build_dice_table_text(dice_preset: dict) -> str:
        styles = ["Front", "Pace", "Late", "End"]
        phases = [1, 2, 3, 4]

        lines = []

        lines.append("WHITE")
        lines.append("| Style | Phase1 | Phase2 | Phase3 | Phase4 |")
        lines.append("|---|---|---|---|---|")

        for style in styles:
            row = [style]
            for phase in phases:
                row.append(format_rule(dice_preset[style]["White"][phase]))
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")
        lines.append("GOLD")
        lines.append("| Style | Phase1 | Phase2 | Phase3 | Phase4 |")
        lines.append("|---|---|---|---|---|")

        for style in styles:
            row = [style]
            for phase in phases:
                row.append(format_rule(dice_preset[style]["Gold"][phase]))
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)
