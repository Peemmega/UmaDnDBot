from utils.database import get_player_skill_in_slot, ensure_player
from utils.skill.skill_presets import SKILLS, ICON
from utils.game_manager import (
    get_game,
    get_player_in_game,
    update_player_score,
)

def is_lastspurt(turn: int, max_turn: int) -> bool:
    return turn >= max_turn - 2


def get_position_group(channel_id: int, user_id: int) -> str:
    game = get_game(channel_id)
    if game is None:
        return "mid"

    ranked = sorted(
        game["players"].items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )

    total = len(ranked)
    if total <= 1:
        return "front"

    for index, (uid, _) in enumerate(ranked):
        if uid == user_id:
            if index == 0:
                return "front"
            elif index >= total - max(1, total // 3):
                return "back"
            return "mid"

    return "mid"


def get_nearest_front_gap(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return None

    my_score = game["players"][user_id]["score"]
    gaps = []

    for uid, info in game["players"].items():
        if uid == user_id:
            continue
        gap = info["score"] - my_score
        if gap > 0:
            gaps.append(gap)

    return min(gaps) if gaps else None


def get_nearest_back_gap(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return None

    my_score = game["players"][user_id]["score"]
    gaps = []

    for uid, info in game["players"].items():
        if uid == user_id:
            continue
        gap = my_score - info["score"]
        if gap > 0:
            gaps.append(gap)

    return min(gaps) if gaps else None


def check_skill_trigger(channel_id: int, user_id: int, skill: dict, *, path_type: int, phase: int) -> tuple[bool, str | None]:
    game = get_game(channel_id)
    player = get_player_in_game(channel_id, user_id)

    if game is None or player is None:
        return False, "ไม่พบข้อมูลเกมหรือผู้เล่น"

    trigger = skill.get("trigger", {})

    if "style" in trigger and trigger["style"] != player["style"]:
        return False, f"ใช้ได้เฉพาะสาย {trigger['style']}"

    if "path_type" in trigger and trigger["path_type"] != path_type:
        return False, "เงื่อนไขสนามไม่ตรง"

    if "turn_min" in trigger and game["turn"] < trigger["turn_min"]:
        return False, f"ใช้ได้ตั้งแต่เทิร์น {trigger['turn_min']}"

    if "turn_max" in trigger and game["turn"] > trigger["turn_max"]:
        return False, f"ใช้ได้ถึงเทิร์น {trigger['turn_max']}"

    if "phase_min" in trigger and phase < trigger["phase_min"]:
        return False, f"ใช้ได้ตั้งแต่ Phase {trigger['phase_min']}"

    if "phase_max" in trigger and phase > trigger["phase_max"]:
        return False, f"ใช้ได้ถึง Phase {trigger['phase_max']}"

    if trigger.get("lastspurt") is True and not is_lastspurt(game["turn"], game["max_turn"]):
        return False, "ยังไม่เข้าสู่ Last Spurt"

    if "position_group" in trigger:
        position_group = get_position_group(channel_id, user_id)
        if position_group != trigger["position_group"]:
            return False, f"ต้องอยู่ตำแหน่งกลุ่ม {trigger['position_group']}"

    if "target_distance_min" in trigger or "target_distance_max" in trigger:
        min_d = trigger.get("target_distance_min")
        max_d = trigger.get("target_distance_max")

        gap = None
        if max_d is not None and max_d >= 0:
            gap = get_nearest_front_gap(channel_id, user_id)
        elif min_d is not None and min_d < 0:
            gap = get_nearest_back_gap(channel_id, user_id)

        if gap is None:
            return False, "ไม่มีเป้าหมายในระยะ"

        if min_d is not None:
            if min_d >= 0 and gap < min_d:
                return False, "ระยะเป้าหมายไม่ถึงขั้นต่ำ"
            if min_d < 0 and gap < abs(min_d):
                return False, "ระยะเป้าหมายด้านหลังไม่ถึงขั้นต่ำ"

        if max_d is not None:
            if max_d >= 0 and gap > max_d:
                return False, "เป้าหมายไกลเกินไป"
            if max_d < 0 and gap > abs(max_d):
                return False, "เป้าหมายด้านหลังไกลเกินไป"

    return True, None

def get_skill_emoji(skill_id: str) -> str:
    skill = SKILLS.get(skill_id)
    if not skill:
        return "❓"
    return ICON.get(skill.get("icon"), "❓")


def get_equipped_skill(user_id: int, slot: int):
    skill_id = get_player_skill_in_slot(user_id, slot)
    if not skill_id:
        return None, None

    skill = SKILLS.get(skill_id)
    if not skill:
        return skill_id, None

    return skill_id, skill


def apply_non_active_skill(channel_id: int, user_id: int, skill_id: str, skill: dict):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = get_player_in_game(channel_id, user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    applied_texts = []

    for effect in skill.get("effects", []):
        effect_type = effect.get("type")
        value = effect.get("value", 0)

        if effect_type == "recover_stamina":
            player["stamina_left"] += value
            applied_texts.append(f"ฟื้นฟู STA +{value}")

        elif effect_type == "flat_score_change":
            success, _ = update_player_score(channel_id, user_id, value)
            if success:
                sign = "+" if value >= 0 else ""
                applied_texts.append(f"ปรับคะแนนทันที {sign}{value}")

        elif effect_type == "reduce_stamina":
            # เริ่มแบบง่าย: ลดเป้าหมายด้านหน้าที่ใกล้ที่สุด
            my_score = player["score"]
            candidates = []

            for target_id, target_info in game["players"].items():
                if target_id == user_id:
                    continue
                gap = target_info["score"] - my_score
                if gap > 0:
                    candidates.append((gap, target_id, target_info))

            if candidates:
                candidates.sort(key=lambda x: x[0])
                _, target_id, target_info = candidates[0]
                target_info["stamina_left"] = max(0, target_info["stamina_left"] - value)
                applied_texts.append(f"ลด STA ของ <@{target_id}> -{value}")

        elif effect_type == "apply_debuff_next_turn":
            # เริ่มแบบง่าย: ใส่ debuff ให้คนหน้าใกล้สุด
            my_score = player["score"]
            candidates = []

            for target_id, target_info in game["players"].items():
                if target_id == user_id:
                    continue
                gap = target_info["score"] - my_score
                if gap > 0:
                    candidates.append((gap, target_id, target_info))

            if candidates:
                candidates.sort(key=lambda x: x[0])
                _, target_id, target_info = candidates[0]
                target_info.setdefault("next_roll_flat_bonus", 0)
                target_info["next_roll_flat_bonus"] += effect.get("value", 0)
                applied_texts.append(
                    f"ใส่ดีบัฟให้ <@{target_id}> เทิร์นหน้า {effect.get('value', 0)}"
                )

        elif effect_type == "modify_gold_range":
            player.setdefault("gold_range_bonus_this_turn", 0)
            player["gold_range_bonus_this_turn"] += value
            applied_texts.append(f"เพิ่มระยะตรวจ Gold +{value}")

        elif effect_type == "modify_enemy_gold_range":
            # เริ่มแบบง่าย: ใส่ให้คู่แข่งทุกคน
            for target_id, target_info in game["players"].items():
                if target_id == user_id:
                    continue
                target_info.setdefault("enemy_gold_range_penalty_next_turn", 0)
                target_info["enemy_gold_range_penalty_next_turn"] += value
            applied_texts.append(f"ลดระยะตรวจ Gold ของคู่แข่ง {value}")

    if not applied_texts:
        return False, "สกิลนี้ยังไม่มีผลที่รองรับในระบบตอนนี้"

    return True, "\n".join(applied_texts)