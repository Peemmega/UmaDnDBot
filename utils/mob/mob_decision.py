import random
from itertools import combinations

# =========================================================
# MOB AI SKILL DECISION SYSTEM
# =========================================================

def decide_mob_skill_combo(
    game,
    user_id,
    usable_skills,
    *,
    max_skill_per_turn=3,
    min_combo_score=45,
):
    """
    เลือกหลายสกิลพร้อมกันสำหรับ mob

    usable_skills: list[(skill_id, skill_data)]
    return: list[str]
    """

    if not usable_skills:
        return []

    player = game["players"][user_id]
    skill_point = player.get("skill_point", player.get("wit_mana", 0))

    scored = []

    for skill_id, skill in usable_skills:
        score = evaluate_skill_score(game, user_id, skill)

        if score <= 0:
            continue

        cost = skill.get("cost", 0)

        if cost > skill_point:
            continue

        scored.append({
            "skill_id": skill_id,
            "skill": skill,
            "score": score,
            "cost": cost,
        })

    if not scored:
        return []

    best_combo = []
    best_combo_score = 0

    max_size = min(max_skill_per_turn, len(scored))

    for size in range(1, max_size + 1):
        for combo in combinations(scored, size):
            total_cost = sum(item["cost"] for item in combo)

            if total_cost > skill_point:
                continue

            combo_score = evaluate_skill_combo_score(
                game,
                user_id,
                combo,
            )

            if combo_score > best_combo_score:
                best_combo_score = combo_score
                best_combo = combo

    if best_combo_score < min_combo_score:
        return []

    # ทำให้บอทไม่ perfect 100%
    if random.random() < 0.12:
        return []

    return [item["skill_id"] for item in best_combo]

# =========================================================
# MAIN EVALUATION
# =========================================================

def evaluate_skill_combo_score(game, user_id, combo):
    player = game["players"][user_id]
    phase = game.get("phase", 1)
    position_group = get_position_group(game, user_id)
    stamina_left = player.get("stamina_left", 0)

    score = sum(item["score"] for item in combo)

    effects = []
    tags = set()

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
        tags.update(skill.get("tags", []))

        for effect in skill.get("effects", []):
            effects.append(effect)

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

    # -----------------------------
    # Synergy Bonus
    # -----------------------------

    # cap + velocity = ดีมาก เพราะเพดานสูงขึ้นแล้วมีแต้มเติม
    if total_cap > 0 and total_velocity > 0:
        score += 25

    # floor + cap = ทำให้ roll เสถียร
    if total_floor > 0 and total_cap > 0:
        score += 18

    # acceleration + dkh = เร่งแล้วได้ลูกเพิ่ม
    if total_accel > 0 and total_dkh > 0:
        score += 25

    # last spurt combo
    if phase >= 4:
        if total_accel > 0:
            score += 25
        if total_velocity > 0:
            score += 15
        if total_cap > 0:
            score += 15

    # ตามหลังแล้ว burst combo จะมีค่ามาก
    if position_group == "back":
        if total_accel > 0:
            score += 25
        if total_velocity > 0:
            score += 15

    # stamina ต่ำแล้ว recovery มีค่า
    if stamina_left <= 2 and total_recovery > 0:
        score += 35

    # debuff + ตัวเองอยู่หน้า = ไม่ค่อยคุ้ม
    if position_group == "front" and total_debuff > 0:
        score -= 20

    # -----------------------------
    # Anti-overstack / diminishing
    # -----------------------------

    if total_cap > 35:
        score -= (total_cap - 35) * 1.5

    if total_velocity > 120:
        score -= (total_velocity - 120) * 0.6

    if total_accel > 3:
        score -= (total_accel - 3) * 18

    # ใช้หลายสกิลเกินไปโดยไม่ใช่จังหวะท้ายเกม
    if len(combo) >= 3 and phase < 4:
        score -= 25

    # ใช้ SP เยอะเกินไปช่วงต้น
    if phase <= 2 and total_cost >= 160:
        score -= 35

    # จังหวะท้ายเกมใช้ SP เยอะได้
    if phase >= 4 and total_cost >= 160:
        score += 20

    return int(max(0, score))

# =========================================================
# HELPERS
# =========================================================

def get_position_group(game, user_id):
    players = list(game["players"].items())

    players.sort(key=lambda x: x[1]["score"], reverse=True)

    index = next(
        (i for i, (pid, _) in enumerate(players) if pid == user_id),
        0
    )

    total = len(players)

    if index <= total * 0.3:
        return "front"

    elif index <= total * 0.7:
        return "middle"

    return "back"


def get_distance_to_front(game, user_id):
    player_score = game["players"][user_id]["score"]

    front_score = max(
        p["score"]
        for pid, p in game["players"].items()
        if pid != user_id
    )

    return front_score - player_score


def get_nearby_count(game, user_id):
    player_score = game["players"][user_id]["score"]

    count = 0

    for pid, other in game["players"].items():

        if pid == user_id:
            continue

        if abs(other["score"] - player_score) <= 20:
            count += 1

    return count


def get_current_path_type(game):
    """
    1 = straight
    2 = corner
    3 = uphill
    4 = downhill
    """

    return game.get("current_path_type", 1)