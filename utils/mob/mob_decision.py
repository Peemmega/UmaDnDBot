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

FUTURE_LOOKAHEAD_TURNS = 4
MIN_FUTURE_GAIN_TO_HOLD = 40
BIG_FUTURE_GAIN_TO_HOLD = 80

def has_position(position_groups, *targets):
    return any(t in position_groups for t in targets)

# =========================================================
# FUTURE DICE EVALUATION
# =========================================================

def estimate_rule_value(rule: dict) -> float:
    dice = rule.get("d", 1)
    kh = rule.get("kh", 0)

    # dice หลายลูก scale แรงกว่าตรง ๆ
    value = (dice ** 2) * 20
    if kh > 0:
        value = (kh ** 2) * 20

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
        "dice": rule.get("d", 1),
        "kh": rule.get("kh", 0),
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

        for color in ("White", "Gold"):
            future_rule = get_dice_rule(
                player.get("style", "Pace"),
                color,
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
        "best_future_dice": best_future_rule.get("d", 1),
        "best_future_kh": best_future_rule.get("kh", 0),
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
# EFFECT ANALYSIS
# =========================================================

ROLL_SCALING_EFFECTS = {
    "modify_roll_cap",
    "modify_roll_floor",
    "modify_selected_die",
    "add_d",
    "add_kh",
    "add_dkh",
}

SPEED_EFFECTS = {
    "modify_velocity",
    "modify_current_speed",
}

RECOVERY_EFFECTS = {
    "recover_stamina",
    "self_heal_stamina",
}

DEBUFF_EFFECTS = {
    "reduce_stamina",
    "modify_enemy_gold_range",
    "apply_debuff_next_turn",
    "modify_enemy_velocity",
    "slow_enemy",
}

def get_effect_value(effect: dict) -> float:
    value = effect.get("value", 0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def analyze_skill_effects(skill: dict) -> dict:
    result = {
        "roll_scaling": 0,
        "speed": 0,
        "current_speed": 0,
        "recovery": 0,
        "debuff": 0,

        "cap": 0,
        "floor": 0,
        "add_d": 0,
        "add_kh": 0,
        "add_dkh": 0,
        "selected_die": 0,
    }

    for effect in skill.get("effects", []):
        effect_type = effect.get("type")
        value = get_effect_value(effect)

        # --------------------------------
        # roll scaling
        # --------------------------------
        if effect_type == "modify_roll_cap":
            result["cap"] += value
            result["roll_scaling"] += value * 1.2

        elif effect_type == "modify_roll_floor":
            result["floor"] += value
            result["roll_scaling"] += value * 1.0

        elif effect_type == "modify_selected_die":
            result["selected_die"] += value
            result["roll_scaling"] += value * 1.5

        elif effect_type == "add_d":
            result["add_d"] += value
            result["roll_scaling"] += value * 22

        elif effect_type == "add_kh":
            result["add_kh"] += value
            result["roll_scaling"] += value * 28

        elif effect_type == "add_dkh":
            result["add_dkh"] += value
            result["roll_scaling"] += value * 42

        # --------------------------------
        # speed
        # --------------------------------
        elif effect_type == "modify_velocity":
            result["speed"] += value

        elif effect_type == "modify_current_speed":
            result["current_speed"] += value

        # --------------------------------
        # recovery
        # --------------------------------
        elif effect_type in RECOVERY_EFFECTS:
            result["recovery"] += value

        # --------------------------------
        # debuff
        # --------------------------------
        elif effect_type in DEBUFF_EFFECTS:
            result["debuff"] += abs(value)

    return result


# =========================================================
# SKILL SCORE
# =========================================================

def evaluate_skill_score(game, user_id, skill):
    player = game["players"][user_id]

    score = 10
    future = get_future_dice_context(game, user_id)

    current_turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)

    phase = get_phase_from_turn(current_turn, max_turn)

    stamina_left = player.get("stamina_left", 0)

    position_group = get_position_groups(game, user_id)
    distance_to_front = get_distance_to_front(game, user_id)
    nearby_count = get_nearby_count(game, user_id)
    path_type = get_current_path_type(game)

    effect_info = analyze_skill_effects(skill)

    has_roll_scaling = effect_info["roll_scaling"] > 0
    has_speed = (
        effect_info["speed"] > 0
        or effect_info["current_speed"] > 0
    )
    has_recovery = effect_info["recovery"] > 0
    has_debuff = effect_info["debuff"] > 0

    # =====================================================
    # dice power
    # =====================================================

    dice_power = (
        future["current_dice"]
        + future["current_kh"] * 0.6
    )

    future_dice_power = (
        future["best_future_dice"]
        + future["best_future_kh"] * 0.6
    )

    future_gain = future["future_gain"]

    # =====================================================
    # roll scaling
    # =====================================================

    if has_roll_scaling:
        score += effect_info["roll_scaling"]

        if dice_power <= 1.5:
            score -= 120

        elif dice_power <= 2.5:
            score -= 60

        elif dice_power >= 5:
            score += 60

        # future better dice
        if phase < 4:
            if future_dice_power >= dice_power + 3:
                score -= 130

            elif future_dice_power >= dice_power + 2:
                score -= 85

            elif future_dice_power >= dice_power + 1:
                score -= 35

    # =====================================================
    # speed
    # =====================================================

    if effect_info["speed"] > 0:
        score += effect_info["speed"] / 4

        if phase >= 3:
            score += effect_info["speed"] * 0.25

        if future_gain >= BIG_FUTURE_GAIN_TO_HOLD and phase < 4:
            score -= effect_info["speed"] * 0.45

    if effect_info["current_speed"] > 0:
        score += effect_info["current_speed"] * 18

        if phase <= 2:
            score += effect_info["current_speed"] * 8

        elif phase >= 4:
            score += effect_info["current_speed"] * 12

    # =====================================================
    # recovery
    # =====================================================

    if has_recovery:
        if stamina_left <= 2:
            score += effect_info["recovery"] * 38

        elif stamina_left <= 4:
            score += effect_info["recovery"] * 22

        else:
            score += effect_info["recovery"] * 6

    # =====================================================
    # debuff / red skill
    # =====================================================

    if has_debuff:
        score += effect_info["debuff"] * 22

        if nearby_count >= 1:
            score += 35

        if nearby_count >= 2:
            score += 25

        if phase >= 3:
            score += 30

        if "front" in position_group:
            if nearby_count >= 1:
                score += 25
            else:
                score -= 10

        elif (
            "middle" in position_group
            or "back" in position_group
        ):
            if distance_to_front <= 120:
                score += 25

        if nearby_count == 0 and distance_to_front > 160:
            score -= 30

    # =====================================================
    # board state
    # =====================================================

    if "back" in position_group:
        if has_speed:
            score += 20

    elif "front" in position_group:
        if has_speed:
            score += 10

        if has_recovery:
            score += 10

    # =====================================================
    # path logic
    # =====================================================

    tags = set(skill.get("tags", []))

    if path_type == 2 and "corner" in tags:
        score += 12

    elif path_type == 1 and "straight" in tags:
        score += 10

    elif path_type == 3 and "uphill" in tags:
        score += 14

    elif path_type == 4 and "downhill" in tags:
        score += 12

    # =====================================================
    # unique
    # =====================================================

    if "unique" in tags:
        if phase >= 3:
            score += 20
        else:
            score -= 10

    # =====================================================
    # cooldown
    # =====================================================

    cooldown = skill.get("cooldown", 0)

    if cooldown >= 10 and phase <= 2:
        score -= 20

    # =====================================================
    # random
    # =====================================================

    score += random.randint(-4, 4)

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

    position_group = get_position_groups(game, user_id)
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

    if "back" in position_group:
        if total_accel > 0:
            score += 25
        if total_velocity > 0:
            score += 15

    if stamina_left <= 2 and total_recovery > 0:
        score += 35

    if "front" in position_group and total_debuff > 0:
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


def get_position_groups(game, user_id):
    if game is None:
        return {"middle"}

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"]
        for uid, p in game["players"].items()
    }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    total = len(ranked)

    if total <= 1:
        return {"front"}

    for index, (uid, _) in enumerate(ranked):
        if uid != user_id:
            continue

        # rank เริ่มที่ 1
        rank = index + 1

        groups = set()

        ratio = rank / total

        # =====================
        # FRONT
        # top ~55%
        # =====================
        if ratio <= 0.55:
            groups.add("front")

        # =====================
        # MIDDLE
        # overlap หนัก
        # =====================
        if 0.25 <= ratio <= 0.80:
            groups.add("middle")

        # =====================
        # BACK
        # bottom ~55%
        # =====================
        if ratio >= 0.45:
            groups.add("back")

        return groups

    return {"middle"}


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