import random
from itertools import combinations

from utils.race.race_dice import (
    get_phase_from_turn,
    get_distance_color,
    get_dice_rule,
)

# =========================================================
# MOB AI SKILL DECISION SYSTEM
# =========================================================

def estimate_rule_value(rule: dict) -> float:
    dice = rule.get("dice", 1)
    kh = rule.get("kh", 0)

    value = dice * 15
    if (kh != 0):
        value = dice * 15

    return value


def get_future_dice_context(game, user_id, lookahead_turns=2):
    cache_key = f"dice_future:{game.get('turn', 1)}:{user_id}:{lookahead_turns}"
    cache = game.setdefault("_mob_ai_future_cache", {})

    if cache_key in cache:
        return cache[cache_key]

    player = game["players"][user_id]

    current_turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)

    score_map = {
        pid: p.get("score", 0)
        for pid, p in game["players"].items()
    }

    skill_effects = player.get("active_effects", [])

    distance_color, nearby_count = get_distance_color(
        user_id,
        score_map,
        skill_effects or []
    )

    current_phase = get_phase_from_turn(current_turn, max_turn)

    current_rule = get_dice_rule(
        player.get("style", "Pace"),
        distance_color,
        current_phase,
    )

    current_value = estimate_rule_value(current_rule)

    best_future_value = current_value
    best_future_turn = current_turn
    best_future_phase = current_phase
    best_future_rule = current_rule

    for offset in range(1, lookahead_turns + 1):
        future_turn = min(max_turn, current_turn + offset)
        future_phase = get_phase_from_turn(future_turn, max_turn)

        future_rule = get_dice_rule(
            player.get("style", "Pace"),
            distance_color,
            future_phase,
        )

        future_value = estimate_rule_value(future_rule)

        if future_value > best_future_value:
            best_future_value = future_value
            best_future_turn = future_turn
            best_future_phase = future_phase
            best_future_rule = future_rule

    context = {
        "distance_color": distance_color,
        "nearby_count": nearby_count,
        "current_turn": current_turn,
        "current_phase": current_phase,
        "current_rule": current_rule,
        "current_value": current_value,
        "best_future_turn": best_future_turn,
        "best_future_phase": best_future_phase,
        "best_future_rule": best_future_rule,
        "best_future_value": best_future_value,
        "future_gain": best_future_value - current_value,
        "has_better_future_dice": best_future_value > current_value + 15,
    }

    cache[cache_key] = context
    return context


def estimate_roll_value(game, user_id):
    player = game["players"][user_id]

    turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)
    phase = get_phase_from_turn(turn, max_turn)

    score_map = {
        pid: p.get("score", 0)
        for pid, p in game["players"].items()
    }

    skill_effects = player.get("active_effects", [])

    distance_color, _nearby_count = get_distance_color(
        user_id,
        score_map,
        skill_effects or []
    )

    rule = get_dice_rule(
        player.get("style", "Pace"),
        distance_color,
        phase,
    )

    base_dice = rule.get("dice", 1)
    base_kh = rule.get("kh", 0)

    dice_count = base_dice + player.get("next_roll_add_d", 0)
    kh = base_kh + player.get("next_roll_add_kh", 0)

    dkh = player.get("next_roll_add_dkh", 0)

    selected_bonus = player.get("next_roll_selected_die_bonus", 0)
    floor_bonus = player.get("next_roll_floor_bonus", 0)
    cap_bonus = player.get("next_roll_cap_bonus", 0)

    value = dice_count * 18
    value += kh * 20
    value += dkh * 35
    value += floor_bonus * 1.2
    value += cap_bonus * 0.9
    value += selected_bonus * 2

    return value


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


def evaluate_skill_score(game, user_id, skill):
    player = game["players"][user_id]
    score = 10
    roll_value = estimate_roll_value(game, user_id)

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

    if phase <= 2:
        if "burst" in tags:
            score -= 40

        if "late_race" in tags:
            score -= 25

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

    if phase == 1:
        if "start" in tags:
            score += 30
        if "acceleration" in tags:
            score += 15

    elif phase == 2:
        if "mid_race" in tags:
            score += 25

    elif phase == 3:
        if "burst" in tags:
            score += 20
        if "acceleration" in tags:
            score += 15

    elif phase >= 4:
        if "last_spurt" in tags:
            score += 50
        if "burst" in tags:
            score += 40
        if "velocity" in tags:
            score += 20
        if "acceleration" in tags:
            score += 35

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

    if stamina_left <= 2:
        if "recovery" in tags:
            score += 60
        if "stamina" in tags:
            score += 30

    elif stamina_left <= 4:
        if "recovery" in tags:
            score += 25

    if nearby_count >= 2:
        if "positioning" in tags:
            score += 20
        if "velocity" in tags:
            score += 10

    if is_last_spurt:
        if distance_to_front <= 50:
            if "acceleration" in tags:
                score += 35
            if "burst" in tags:
                score += 35

        elif distance_to_front >= 120:
            if "velocity" in tags:
                score += 20

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

    for effect in effects:
        effect_type = effect.get("type")
        value = effect.get("value", 0)

        if effect_type == "modify_velocity":
            score += value / 5

            if roll_value <= 25:
                score += value * 0.2

        elif effect_type == "modify_current_speed":
            score += value * 18

        elif effect_type == "modify_roll_cap":
            score += value * 1.5

            if roll_value <= 25:
                score -= value * 1.4
            elif roll_value <= 45:
                score -= value * 0.6
            elif roll_value >= 80:
                score += value * 0.8

        elif effect_type == "modify_roll_floor":
            score += value

            if roll_value <= 30:
                score -= value * 0.7
            elif roll_value >= 70:
                score += value * 0.5

        elif effect_type == "add_dkh":
            score += value * 16

        elif effect_type == "recover_stamina":
            if stamina_left <= 4:
                score += value * 25
            else:
                score += value * 8

        elif effect_type == "reduce_stamina":
            score += value * 20

        elif effect_type == "modify_enemy_gold_range":
            score += 15

    if "unique" in tags:
        if phase >= 3:
            score += 25
        else:
            score -= 15

    cooldown = skill.get("cooldown", 0)

    if cooldown >= 10 and phase <= 2:
        score -= 20

    score += random.randint(-5, 5)

    return max(0, int(score))


def evaluate_skill_combo_score(game, user_id, combo):
    player = game["players"][user_id]

    current_turn = game.get("turn", 1)
    max_turn = game.get("max_turn", 20)
    phase = get_phase_from_turn(current_turn, max_turn)

    position_group = get_position_group(game, user_id)
    stamina_left = player.get("stamina_left", 0)
    roll_value = estimate_roll_value(game, user_id)

    score = sum(item["score"] for item in combo)

    total_cost = 0
    total_velocity = 0
    total_cap = 0
    total_floor = 0
    total_dkh = 0
    total_accel = 0
    total_recovery = 0
    total_debuff = 0

    for item in combo:
        skill = item["skill"]
        total_cost += item["cost"]

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

    if total_cap > 0 and total_velocity > 0:
        score += 25

    if total_floor > 0 and total_cap > 0:
        score += 18

    if total_accel > 0 and total_dkh > 0:
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
            score -= 35

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

    future_value = estimate_future_value(game, user_id, combo)

    if future_value > 0:
        score -= future_value
    elif future_value < 0:
        score += abs(future_value)

    return int(max(0, score))


def estimate_future_value(game, user_id, combo):
    future = get_future_dice_context(game, user_id, lookahead_turns=2)

    total_cap = 0
    total_floor = 0
    total_velocity = 0
    total_dkh = 0
    cooldown_sum = 0

    for item in combo:
        skill = item["skill"]
        cooldown_sum += skill.get("cooldown", 0)

        for effect in skill.get("effects", []):
            effect_type = effect.get("type")
            value = effect.get("value", 0)

            if effect_type == "modify_roll_cap":
                total_cap += value
            elif effect_type == "modify_roll_floor":
                total_floor += value
            elif effect_type == "modify_velocity":
                total_velocity += value
            elif effect_type == "add_dkh":
                total_dkh += value

    penalty = 0

    if future["has_better_future_dice"]:
        if total_cap > 0 or total_floor > 0:
            penalty += 35

        if total_dkh > 0:
            penalty += 25

        if total_velocity > 0:
            penalty += 10

        if cooldown_sum >= 16:
            penalty += 20

    else:
        penalty -= 15

    return penalty


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