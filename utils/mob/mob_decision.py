import random
from itertools import combinations

from utils.race.race_dice import get_phase_from_turn

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

def evaluate_skill_score(game, user_id, skill):
    player = game["players"][user_id]
    race = game.get("race", {})

    score = 10

    # =====================================================
    # BASIC INFO
    # =====================================================

    current_turn = game.get("turn", 1)
    max_turn = race.get("max_turn", 20)
    phase = get_phase_from_turn(current_turn, max_turn)

    stamina_left = player.get("stamina_left", 0)

    style = player.get("style", "Pace")

    position_group = get_position_group(game, user_id)

    current_speed = player.get("current_speed", 0)

    distance_to_front = get_distance_to_front(game, user_id)

    nearby_count = get_nearby_count(game, user_id)

    path_type = get_current_path_type(game)

    is_last_spurt = phase >= 4

    tags = set(skill.get("tags", []))

    effects = skill.get("effects", [])

    # =====================================================
    # SAVE IMPORTANT SKILLS
    # =====================================================

    if phase <= 2:
        if "burst" in tags:
            score -= 40

        if "late_race" in tags:
            score -= 25

    # =====================================================
    # POSITION LOGIC
    # =====================================================

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

    # =====================================================
    # PHASE LOGIC
    # =====================================================

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

    # =====================================================
    # PATH LOGIC
    # =====================================================

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

    # =====================================================
    # STAMINA LOGIC
    # =====================================================

    if stamina_left <= 2:

        if "recovery" in tags:
            score += 60

        if "stamina" in tags:
            score += 30

    elif stamina_left <= 4:

        if "recovery" in tags:
            score += 25

    # =====================================================
    # PACK RACING
    # =====================================================

    if nearby_count >= 2:

        if "positioning" in tags:
            score += 20

        if "velocity" in tags:
            score += 10

    # =====================================================
    # LAST SPURT CHASE
    # =====================================================

    if is_last_spurt:

        if distance_to_front <= 50:

            if "acceleration" in tags:
                score += 35

            if "burst" in tags:
                score += 35

        elif distance_to_front >= 120:

            if "velocity" in tags:
                score += 20

    # =====================================================
    # STYLE LOGIC
    # =====================================================

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

    # =====================================================
    # EFFECT ANALYSIS
    # =====================================================

    for effect in effects:

        effect_type = effect.get("type")

        value = effect.get("value", 0)

        # ---------------------------
        # Velocity
        # ---------------------------

        if effect_type == "modify_velocity":
            score += value / 5

        # ---------------------------
        # Acceleration
        # ---------------------------

        elif effect_type == "modify_current_speed":
            score += value * 18

        # ---------------------------
        # Roll cap
        # ---------------------------

        elif effect_type == "modify_roll_cap":
            score += value * 1.5

        # ---------------------------
        # Roll floor
        # ---------------------------

        elif effect_type == "modify_roll_floor":
            score += value

        # ---------------------------
        # dkh
        # ---------------------------

        elif effect_type == "add_dkh":
            score += value * 16

        # ---------------------------
        # Recovery
        # ---------------------------

        elif effect_type == "recover_stamina":

            if stamina_left <= 4:
                score += value * 25
            else:
                score += value * 8

        # ---------------------------
        # Debuff
        # ---------------------------

        elif effect_type == "reduce_stamina":
            score += value * 20

        elif effect_type == "modify_enemy_gold_range":
            score += 15

    # =====================================================
    # UNIQUE SKILLS
    # =====================================================

    if "unique" in tags:

        if phase >= 3:
            score += 25
        else:
            score -= 15

    # =====================================================
    # COOLDOWN MANAGEMENT
    # =====================================================

    cooldown = skill.get("cooldown", 0)

    if cooldown >= 10 and phase <= 2:
        score -= 20

    # =====================================================
    # RANDOMNESS
    # =====================================================

    score += random.randint(-5, 5)

    return max(0, int(score))

def evaluate_skill_combo_score(game, user_id, combo):
    player = game["players"][user_id]
    race = game.get("race", {})
    current_turn = game.get("turn", 1)
    max_turn = race.get("max_turn", 20)
    phase = get_phase_from_turn(current_turn, max_turn)

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