import random
from itertools import combinations

from utils.race.race_dice import (
    get_phase_from_turn,
    get_distance_color,
    get_dice_rule,
)

# =========================================================
# CONFIG
# =========================================================

FUTURE_LOOKAHEAD_TURNS = 2
MIN_FUTURE_GAIN_TO_HOLD = 40
BIG_FUTURE_GAIN_TO_HOLD = 80


# =========================================================
# FUTURE DICE EVALUATION
# =========================================================
def get_rule_dice(rule: dict) -> int:
    if not isinstance(rule, dict):
        return 1

    value = rule.get("d")
    if value is None:
        value = rule.get("dice", 1)

    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def get_rule_kh(rule: dict) -> int | None:
    if not isinstance(rule, dict):
        return None

    value = rule.get("kh")
    if value is None:
        return None

    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return None


def estimate_rule_value(rule: dict) -> float:
    d = get_rule_dice(rule)
    kh = get_rule_kh(rule)

    # selected = d if kh is None else min(d, kh)

    # d เยอะ + kh เยอะ = สกิล roll scaling คุ้มขึ้นมาก
    value = 0
    # value += selected * 28

    if kh is not None:
        value = (kh ** 2) * 16
        value += (d) * 16
    else:
        value = (d ** 2) * 16

    return value

def get_current_dice_context(game, user_id):
    player = game["players"][user_id]

    turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)
    phase = get_phase_from_turn(turn, max_turn)

    score_map = {
        pid: p.get("score", 0)
        for pid, p in game["players"].items()
    }

    skill_effects = player.get("active_effects", [])

    distance_color, nearby_count = get_distance_color(
        user_id,
        score_map,
        skill_effects or [],
    )

    rule = get_dice_rule(
        player.get("style", "Pace"),
        distance_color,
        phase,
    )

    return {
        "turn": turn,
        "phase": phase,
        "distance_color": distance_color,
        "nearby_count": nearby_count,
        "rule": rule,
        "dice": get_rule_dice(rule),
        "kh": get_rule_kh(rule) or 0,
        "rule_value": estimate_rule_value(rule),
    }


def get_future_dice_context(game, user_id, lookahead_turns=FUTURE_LOOKAHEAD_TURNS):
    cache_key = f"dice_future:{game.get('turn', 1)}:{user_id}:{lookahead_turns}"
    cache = game.setdefault("_mob_ai_future_cache", {})

    if cache_key in cache:
        return cache[cache_key]

    player = game["players"][user_id]

    current = get_current_dice_context(game, user_id)

    current_turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)

    best_future_value = current["rule_value"]
    best_future_turn = current_turn
    best_future_phase = current["phase"]
    best_future_rule = current["rule"]

    for offset in range(1, lookahead_turns + 1):
        future_turn = min(max_turn, current_turn + offset)
        future_phase = get_phase_from_turn(future_turn, max_turn)

        future_rule = get_dice_rule(
            player.get("style", "Pace"),
            current["distance_color"],
            future_phase,
        )

        future_value = estimate_rule_value(future_rule)

        if future_value > best_future_value:
            best_future_value = future_value
            best_future_turn = future_turn
            best_future_phase = future_phase
            best_future_rule = future_rule

    context = {
        "current_turn": current_turn,
        "current_phase": current["phase"],
        "current_rule": current["rule"],
        "current_dice": current["dice"],
        "current_kh": current["kh"],
        "current_value": current["rule_value"],

        "best_future_turn": best_future_turn,
        "best_future_phase": best_future_phase,
        "best_future_rule": best_future_rule,
        "best_future_dice": get_rule_dice(best_future_rule),
        "best_future_kh": get_rule_kh(best_future_rule) or 0,
        "best_future_value": best_future_value,

        "future_gain": best_future_value - current["rule_value"],
        "has_better_future_dice": (
            best_future_value - current["rule_value"]
            >= MIN_FUTURE_GAIN_TO_HOLD
        ),
        "has_much_better_future_dice": (
            best_future_value - current["rule_value"]
            >= BIG_FUTURE_GAIN_TO_HOLD
        ),

        "distance_color": current["distance_color"],
        "nearby_count": current["nearby_count"],
    }

    cache[cache_key] = context
    return context


def estimate_roll_value(game, user_id):
    player = game["players"][user_id]
    current = get_current_dice_context(game, user_id)

    dice_count = current["dice"] + player.get("next_roll_add_d", 0)
    kh = current["kh"] + player.get("next_roll_add_kh", 0)

    dkh = player.get("next_roll_add_dkh", 0)
    selected_bonus = player.get("next_roll_selected_die_bonus", 0)
    floor_bonus = player.get("next_roll_floor_bonus", 0)
    cap_bonus = player.get("next_roll_cap_bonus", 0)

    value = (dice_count ** 2) * 18
    value += kh * 30
    value += dkh * 45
    value += floor_bonus * 1.4
    value += cap_bonus * 1.0
    value += selected_bonus * 2

    return value


# =========================================================
# MAIN DECISION
# =========================================================

def decide_mob_skill_combo(
    game,
    user_id,
    usable_skills,
    *,
    max_skill_per_turn=3,
    min_combo_score=45,
    debug=False,
):
    if debug:
        print(f"[MOB AI] {user_id} usable_skills = {[sid for sid, _ in usable_skills]}")

        future = get_future_dice_context(game, user_id)
        print(
            "[MOB AI] dice_future "
            f"now={future['current_value']} "
            f"future={future['best_future_value']} "
            f"gain={future['future_gain']} "
            f"dice={future['current_dice']}->{future['best_future_dice']} "
            f"kh={future['current_kh']}->{future['best_future_kh']} "
            f"phase={future['current_phase']}->{future['best_future_phase']}"
        )

    if not usable_skills:
        if debug:
            print("[MOB AI] no usable skills")
        return []

    player = game["players"][user_id]
    skill_point = player.get("skill_point", player.get("wit_mana", 0))

    scored = []

    for skill_id, skill in usable_skills:
        score = evaluate_skill_score(game, user_id, skill)
        cost = skill.get("cost", 0)

        if debug:
            print(
                f"[MOB AI] skill={skill_id} name={skill.get('name')} "
                f"score={score} cost={cost} wit={skill_point}"
            )

        if score <= 0:
            continue

        if cost > skill_point:
            if debug:
                print(f"[MOB AI] skip {skill_id}: cost too high")
            continue

        scored.append({
            "skill_id": skill_id,
            "skill": skill,
            "score": score,
            "cost": cost,
        })

    if not scored:
        if debug:
            print("[MOB AI] no scored skills")
        return []

    best_combo = []
    best_combo_score = 0

    max_size = min(max_skill_per_turn, len(scored))

    for size in range(1, max_size + 1):
        for combo in combinations(scored, size):
            total_cost = sum(item["cost"] for item in combo)

            if total_cost > skill_point:
                if debug:
                    ids = [item["skill_id"] for item in combo]
                    print(
                        f"[MOB AI] skip combo={ids}: "
                        f"total_cost={total_cost} > wit={skill_point}"
                    )
                continue

            combo_score = evaluate_skill_combo_score(game, user_id, combo)
            ids = [item["skill_id"] for item in combo]

            if debug:
                print(
                    f"[MOB AI] combo={ids} "
                    f"combo_score={combo_score} "
                    f"total_cost={total_cost}"
                )

            if combo_score > best_combo_score:
                best_combo_score = combo_score
                best_combo = combo

    if debug:
        print(
            f"[MOB AI] best_combo={[item['skill_id'] for item in best_combo]} "
            f"best_score={best_combo_score} min={min_combo_score}"
        )

    if best_combo_score < min_combo_score:
        if debug:
            print("[MOB AI] best combo score too low")
        return []

    return [item["skill_id"] for item in best_combo]


# =========================================================
# SKILL SCORE
# =========================================================

def evaluate_skill_score(game, user_id, skill):
    player = game["players"][user_id]

    score = 10
    roll_value = estimate_roll_value(game, user_id)
    future = get_future_dice_context(game, user_id)
    current_dice = future["current_dice"]

    current_turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)
    phase = get_phase_from_turn(current_turn, max_turn)

    stamina_left = player.get("stamina_left", 0)
    style = player.get("style", "Pace")

    position_group = get_position_group(game, user_id)
    distance_to_front = get_distance_to_front(game, user_id)
    nearby_count = get_nearby_count(game, user_id)
    path_type = get_current_path_type(game)

    is_last_spurt = phase >= 4

    tags = set(skill.get("tags", []))
    effects = skill.get("effects", [])

    is_burst_skill = (
        "burst" in tags
        or "last_spurt" in tags
        or "late_race" in tags
    )

    has_big_roll_scaling = any(
        effect.get("type") in [
            "modify_roll_cap",
            "modify_roll_floor",
            "add_dkh",
            "add_d",
            "add_kh",
        ]
        for effect in effects
    )

    # -----------------------------
    # save important skill
    # -----------------------------
    if phase <= 2:
        if "burst" in tags:
            score -= 50

        if "late_race" in tags:
            score -= 40

        if style in ["Late", "End"] and is_burst_skill:
            score -= 50

    # -----------------------------
    # future dice hold
    # -----------------------------
    future_gain = future["future_gain"]

    if phase < 4:
        if future["has_much_better_future_dice"]:
            if is_burst_skill:
                score -= 140
            if has_big_roll_scaling:
                score -= 120

        elif future["has_better_future_dice"]:
            if is_burst_skill:
                score -= 75
            if has_big_roll_scaling:
                score -= 60

    # ถ้าสกิลเป็นพวกเพิ่มเต๋า/cap/floor ให้ผูกกับจำนวนเต๋าปัจจุบัน
    dice_power = future["current_dice"] + (future["current_kh"] * 0.6)
    future_dice_power = future["best_future_dice"] + (future["best_future_kh"] * 0.6)

    if has_big_roll_scaling:
        if dice_power <= 1.5:
            score -= 120
        elif dice_power <= 2.5:
            score -= 60
        elif dice_power >= 5:
            score += 55

        # ถ้าอีกไม่กี่เทิร์นมีเต๋าดีกว่าเยอะ ให้เก็บไว้
        if phase < 4 and future_dice_power >= dice_power + 2:
            score -= 90

    # current dice too weak
    if phase < 4:
        if current_dice <= 1 and has_big_roll_scaling:
            score -= 90
        elif current_dice == 2 and has_big_roll_scaling:
            score -= 35

    # -----------------------------
    # position logic
    # -----------------------------
    if position_group == "back":
        if "acceleration" in tags:
            score += 25
        if "velocity" in tags:
            score += 10
        if "debuff" in tags:
            score += 15

    elif position_group == "front":
        if "lead" in tags:
            score += 20
        if "recovery" in tags:
            score += 10
        if "debuff" in tags:
            score -= 10

    elif position_group == "middle":
        if "positioning" in tags:
            score += 20

    # -----------------------------
    # phase logic
    # -----------------------------
    if phase == 1:
        if "start" in tags:
            score += 30
        if "acceleration" in tags:
            score += 15

    elif phase == 2:
        if "mid_race" in tags:
            score += 20

    elif phase == 3:
        if "burst" in tags:
            score += 35
        if "acceleration" in tags:
            score += 20

    elif phase >= 4:
        if "last_spurt" in tags:
            score += 60
        if "burst" in tags:
            score += 50
        if "velocity" in tags:
            score += 25
        if "acceleration" in tags:
            score += 40

    # -----------------------------
    # path logic
    # -----------------------------
    if path_type == 2:
        if "corner" in tags:
            score += 35

    elif path_type == 1:
        if "straight" in tags:
            score += 30

    elif path_type == 3:
        if "uphill" in tags:
            score += 35
        if "acceleration" in tags:
            score += 10

    elif path_type == 4:
        if "downhill" in tags:
            score += 30
        if "velocity" in tags:
            score += 15

    # -----------------------------
    # stamina logic
    # -----------------------------
    if stamina_left <= 2:
        if "recovery" in tags:
            score += 60
        if "stamina" in tags:
            score += 30

    elif stamina_left <= 4:
        if "recovery" in tags:
            score += 25

    # -----------------------------
    # pack racing
    # -----------------------------
    if nearby_count >= 2:
        if "positioning" in tags:
            score += 20
        if "velocity" in tags:
            score += 10

    # -----------------------------
    # last spurt chase
    # -----------------------------
    if is_last_spurt:
        if distance_to_front <= 50:
            if "acceleration" in tags:
                score += 35
            if "burst" in tags:
                score += 35
        elif distance_to_front >= 120:
            if "velocity" in tags:
                score += 20

    # -----------------------------
    # style logic
    # -----------------------------
    if style == "Front":
        if "lead" in tags:
            score += 30
        if "front" in tags:
            score += 25

    elif style == "Pace":
        if "pace" in tags:
            score += 25
        if "positioning" in tags:
            score += 15

    elif style == "Late":
        if "late" in tags:
            score += 30
        if "acceleration" in tags:
            score += 15

    elif style == "End":
        if "end" in tags:
            score += 35
        if "last_spurt" in tags:
            score += 25

    # -----------------------------
    # effect value
    # -----------------------------
    for effect in effects:
        effect_type = effect.get("type")
        value = effect.get("value", 0)

        if effect_type == "modify_velocity":
            score += value / 5

            if roll_value <= 25:
                score += value * 0.2

            if future_gain >= BIG_FUTURE_GAIN_TO_HOLD and phase < 4:
                score -= value * 0.6
            elif future_gain >= MIN_FUTURE_GAIN_TO_HOLD and phase < 4:
                score -= value * 0.3

        elif effect_type == "modify_current_speed":
            score += value * 18

        elif effect_type == "modify_roll_cap":
            score += value * 1.5

            if roll_value <= 25:
                score -= value * 1.8
            elif roll_value <= 45:
                score -= value * 0.9
            elif roll_value >= 80:
                score += value * 0.8

        elif effect_type == "modify_roll_floor":
            score += value

            if roll_value <= 30:
                score -= value * 0.9
            elif roll_value >= 70:
                score += value * 0.5

        elif effect_type == "add_dkh":
            score += value * 18

        elif effect_type == "recover_stamina":
            if stamina_left <= 4:
                score += value * 25
            else:
                score += value * 8

        elif effect_type == "reduce_stamina":
            score += value * 20

        elif effect_type == "modify_enemy_gold_range":
            score += 15

        elif effect_type == "add_d":
            score += value * (18 + current_dice * 8)

        elif effect_type == "add_kh":
            score += value * 32

        elif effect_type == "add_dkh":
            score += value * (38 + current_dice * 8)

        elif effect_type == "modify_selected_die":
            score += value * max(1, current_dice)


    if "unique" in tags:
        if phase >= 3:
            score += 25
        else:
            score -= 15

    cooldown = skill.get("cooldown", 0)

    if cooldown >= 10 and phase <= 2:
        score -= 25

    score += random.randint(-5, 5)

    return max(0, int(score))


# =========================================================
# COMBO SCORE
# =========================================================

def evaluate_skill_combo_score(game, user_id, combo):
    player = game["players"][user_id]

    current_turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)
    phase = get_phase_from_turn(current_turn, max_turn)

    future = get_future_dice_context(game, user_id)

    position_group = get_position_group(game, user_id)
    stamina_left = player.get("stamina_left", 0)
    roll_value = estimate_roll_value(game, user_id)

    score = sum(item["score"] for item in combo)

    total_cost = 0
    total_velocity = 0
    total_cap = 0
    total_floor = 0
    total_dkh = 0
    total_add_d = 0
    total_add_kh = 0
    total_accel = 0
    total_recovery = 0
    total_debuff = 0
    has_burst_tag = False
    has_late_tag = False

    for item in combo:
        skill = item["skill"]
        total_cost += item["cost"]

        tags = set(skill.get("tags", []))
        if "burst" in tags:
            has_burst_tag = True
        if "late_race" in tags or "last_spurt" in tags:
            has_late_tag = True

        for effect in skill.get("effects", []):
            effect_type = effect.get("type")
            value = effect.get("value", 0)

            if effect_type == "modify_velocity":
                total_velocity += value
            elif effect_type == "modify_roll_cap":
                total_cap += value
            elif effect_type == "modify_roll_floor":
                total_floor += value
            elif effect_type == "add_dkh":
                total_dkh += value
            elif effect_type == "add_d":
                total_add_d += value
            elif effect_type == "add_kh":
                total_add_kh += value
            elif effect_type == "modify_current_speed":
                total_accel += value
            elif effect_type in ("recover_stamina", "self_heal_stamina"):
                total_recovery += value
            elif effect_type in (
                "reduce_stamina",
                "modify_enemy_gold_range",
                "apply_debuff_next_turn",
            ):
                total_debuff += abs(value)

    has_big_roll_scaling = (
        total_cap > 0
        or total_floor > 0
        or total_dkh > 0
        or total_add_d > 0
        or total_add_kh > 0
    )

    if total_cap > 0 and total_velocity > 0:
        score += 25

    if total_floor > 0 and total_cap > 0:
        score += 18

    if total_accel > 0 and (total_dkh > 0 or total_add_d > 0 or total_add_kh > 0):
        score += 25

    if phase >= 4:
        if total_accel > 0:
            score += 25
        if total_velocity > 0:
            score += 15
        if total_cap > 0:
            score += 15

    if total_cap > 0:
        if total_dkh > 0:
            score += 35
        if total_floor > 0:
            score += 20
        if roll_value >= 70:
            score += 25
        elif roll_value <= 25:
            score -= 45

    if position_group == "back":
        if total_accel > 0:
            score += 25
        if total_velocity > 0:
            score += 15

    if stamina_left <= 2 and total_recovery > 0:
        score += 35

    if position_group == "front" and total_debuff > 0:
        score -= 20

    if total_cap > 35:
        score -= (total_cap - 35) * 1.5

    if total_velocity > 120:
        score -= (total_velocity - 120) * 0.6

    if total_accel > 3:
        score -= (total_accel - 3) * 18

    if len(combo) >= 3 and phase < 4:
        score -= 25

    if phase <= 2 and total_cost >= 160:
        score -= 35

    if phase >= 4 and total_cost >= 160:
        score += 20

    future_gain = future["future_gain"]

    if phase < 4:
        if future["has_much_better_future_dice"]:
            if has_big_roll_scaling:
                score -= 120
            if has_burst_tag or has_late_tag:
                score -= 120

        elif future["has_better_future_dice"]:
            if has_big_roll_scaling:
                score -= 65
            if has_burst_tag or has_late_tag:
                score -= 75

        if future["current_dice"] <= 1 and has_big_roll_scaling:
            score -= 90
        elif future["current_dice"] == 2 and has_big_roll_scaling:
            score -= 35

        if total_velocity > 0 and future_gain >= BIG_FUTURE_GAIN_TO_HOLD:
            score -= total_velocity * 0.6
        elif total_velocity > 0 and future_gain >= MIN_FUTURE_GAIN_TO_HOLD:
            score -= total_velocity * 0.3

    return int(max(0, score))


# =========================================================
# HELPERS
# =========================================================

def get_position_group(game, user_id):
    players = list(game["players"].items())

    players.sort(key=lambda x: x[1].get("score", 0), reverse=True)

    index = next(
        (i for i, (pid, _) in enumerate(players) if pid == user_id),
        0
    )

    total = len(players)

    if total <= 1:
        return "front"

    if index <= total * 0.3:
        return "front"

    if index <= total * 0.7:
        return "middle"

    return "back"


def get_distance_to_front(game, user_id):
    player_score = game["players"][user_id].get("score", 0)

    front_scores = [
        p.get("score", 0)
        for pid, p in game["players"].items()
        if pid != user_id
    ]

    if not front_scores:
        return 0

    front_score = max(front_scores)

    return front_score - player_score


def get_nearby_count(game, user_id):
    player_score = game["players"][user_id].get("score", 0)

    count = 0

    for pid, other in game["players"].items():
        if pid == user_id:
            continue

        if abs(other.get("score", 0) - player_score) <= 20:
            count += 1

    return count


def get_current_path_type(game):
    return game.get("current_path_type", 1)