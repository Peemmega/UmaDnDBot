import random
import math
from utils.dice.dice_presets import DICE_PRESET
from utils.icon_presets import STAT_EMOJIS, Status_Icon_Type
from utils.skill.skill_presets import ICON
from utils.dice.dice_table import format_rule

def get_stat_emoji(value: int) -> str:
    value = max(1, min(value, 8))
    return STAT_EMOJIS[value]

def get_stat_icon(value: str) -> str:
    return Status_Icon_Type[value]

def count_nearby_players(player_id: int, score_map: dict[int, int], radius: int = 20) -> int:
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

def get_distance_color(
    player_id: int,
    score_map: dict[int, int],
    skill_effects: list | None = None,
) -> str:
    """
    score_map = {user_id: score}

    ถ้าระยะห่างจากม้าที่ใกล้ที่สุด <= 10 + bonus => Gold
    ถ้ามากกว่า => White
    """

    if player_id not in score_map:
        return "Gold",0

    player_score = score_map[player_id]

    other_scores = [
        score for uid, score in score_map.items()
        if uid != player_id
    ]

    if not other_scores:
        return "Gold",0

    nearest_gap = min(abs(player_score - score) for score in other_scores)

    skill_effects = skill_effects or []

    bonus = 0
    penalty = 0

    for eff in skill_effects:
        if eff.get("type") == "modify_gold_range":
            bonus += eff.get("value", 0)
        elif eff.get("type") == "modify_enemy_gold_range":
            penalty += eff.get("value", 0)

    max_range = 20 + bonus - penalty
    gold_range = max(1, max_range)
    umaInRange = count_nearby_players(player_id, score_map, radius=max_range)

    if nearest_gap <= gold_range:
        return "Gold", umaInRange
    return "White", umaInRange


def get_dice_rule(style: str, distance_color: str, phase: int) -> dict:
    return DICE_PRESET[style][distance_color][phase]

def roll_by_rule(rule: dict, player_stats: dict, game_player: dict, context: dict) -> dict:
    d = rule["d"]
    kh = rule.get("kh")

    skill_effects = context.get("skill_effects", [])

    extra_d = 0
    extra_kh = 0
    extra_floor = 0
    flat_velocity_bonus = 0
    selected_die_bonus = 0
    roll_cap_increase = 0

    for effect in skill_effects:
        effect_type = effect.get("type")
        value = effect.get("value", 0)
        if effect_type == "add_d":
            extra_d += value
        elif effect_type == "add_kh":
            extra_kh += value
        elif effect_type == "modify_roll_floor":
            extra_floor += value
        elif effect_type == "modify_velocity":
            flat_velocity_bonus += value
        elif effect_type == "modify_selected_die":
            selected_die_bonus += value
        elif effect_type == "modify_roll_cap":
            roll_cap_increase += value
            

    d += extra_d

    path_effect = context.get("path_effect", {})

   
    # Roll Dice --------------------------------------
    current_max_speed = math.floor(game_player.get("current_max_speed", 0))
    print(current_max_speed)

    max_dice_value = (
        current_max_speed
        + roll_cap_increase
        + path_effect.get("extra_max_from_wit", 0)
        - path_effect.get("reduce_dice_value", 0)
    )
    
    max_dice_value
    roll_min = math.floor(max_dice_value * 0.25) + extra_floor
    max_dice_value = max(max_dice_value, roll_min)

    rolls = [random.randint(roll_min, max_dice_value) for _ in range(d)]
    original_rolls = rolls.copy()

    if kh is not None:
        kh = min(d, kh + extra_kh)
        selected = sorted(rolls, reverse=True)[:kh]
    else:
        selected = rolls.copy()
    # Roll Dice --------------------------------------

    modified_selected = []

    spd_multiplier = path_effect.get("spd_multiplier", 1.0)
    power_total_multiplier = path_effect.get("power_total_multiplier", 1.0)

    spd_bonus_raw = player_stats.get("speed", 1)
    spd_bonus = int(spd_bonus_raw * spd_multiplier)

    power_bonus = player_stats.get("power", 1) * 3
    nearby_count = min(context.get("nearby_count", 0), 2)
    gut_scale = player_stats.get("gut", 1) * 5
    gut_bonus = (gut_scale * nearby_count ) if context.get("distance_color") == "Gold" else 0

    total_selected_die_bonus = 0
    speedBonus = spd_bonus * 3

    for r in selected:
        value = r

        if selected_die_bonus > 0:
            value += selected_die_bonus
            total_selected_die_bonus += selected_die_bonus

        modified_selected.append(value)

    base_total = sum(selected)

    final_power_bonus = int(power_bonus * power_total_multiplier)
    total = sum(modified_selected) + final_power_bonus + gut_bonus + flat_velocity_bonus + speedBonus

    bonus_parts = []
    if speedBonus > 0:
        bonus_parts.append(f"+{speedBonus}{get_stat_icon('SPD')}")
    if gut_bonus > 0:
        bonus_parts.append(f"+{gut_bonus}{get_stat_icon('GUT')}")
    if final_power_bonus > 0:
        bonus_parts.append(f"+{final_power_bonus}{get_stat_icon('POW')}")
    if flat_velocity_bonus > 0:
        bonus_parts.append(f"+{flat_velocity_bonus}{ICON['Velocity']}")
    if total_selected_die_bonus > 0:
        bonus_parts.append(f"+{total_selected_die_bonus}{ICON['Velocity']}")


    bonus_display = " ".join(bonus_parts) if bonus_parts else "-"
    total_display = str(total)

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
        "display": " , ".join(display_parts),
        "base_total": base_total,
        "total": total,
        "total_display": total_display,
        "bonus_display": bonus_display,
    }

def roll_race_dice(
    game_player: dict,
    player_stats: dict,
    player_id: int,
    score_map: dict[int, int],
    turn: int,
    max_turn: int,
    path_effect: dict | None = None,
    skill_effects: list | None = None,
) -> dict:
    phase = get_phase_from_turn(turn, max_turn)
    distance_color,nearby_count = get_distance_color(player_id, score_map, skill_effects or [])
    rule = get_dice_rule(game_player["style"], distance_color, phase)

    dice_result = roll_by_rule(rule, player_stats, game_player, {
        "distance_color": distance_color,
        "nearby_count": nearby_count,
        "path_effect": path_effect or {},
        "skill_effects": skill_effects or [],
    })

    return {
        "phase": phase,
        "turn": turn,
        "distance_color": distance_color,
        "rule": rule,
        "rolls": dice_result["rolls"],
        "selected": dice_result["selected"],
        "modified_selected": dice_result["modified_selected"],
        "display": dice_result["display"],
        "base_total": dice_result["base_total"],
        "total": dice_result["total"],
        "total_display": dice_result["total_display"],
        "bonus_display": dice_result["bonus_display"],
    }

def build_dice_table_grid(dice_preset: dict, color: str) -> str:
    styles = ["Front", "Pace", "Late", "End"]
    phases = [1, 2, 3, 4]

    # header
    lines = []
    header = f"{'Style':<7} {'P1':<6} {'P2':<6} {'P3':<6} {'P4':<6}"
    lines.append(header)
    lines.append("-" * len(header))

    for style in styles:
        row = [f"{style:<7}"]

        for phase in phases:
            rule = format_rule(dice_preset[style][color][phase])
            row.append(f"{rule:<6}")

        lines.append(" ".join(row))

    return "\n".join(lines)

def build_dice_table_text(dice_preset: dict) -> tuple[str, str]:
    styles = ["Front", "Pace", "Late", "End"]
    phases = [1, 2, 3, 4]

    def build_section(color: str) -> str:
        lines = []

        for style in styles:
            parts = [f"**{style}**"]
            for phase in phases:
                rule = format_rule(dice_preset[style][color][phase])
                parts.append(f"P{phase} `{rule}`")
            lines.append(" • ".join(parts))

        return "\n".join(lines)

    white_text = build_section("White")
    gold_text = build_section("Gold")
    return white_text, gold_text