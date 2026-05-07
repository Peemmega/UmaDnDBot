import random
import discord
from utils.database import get_player_skill_in_slot, ensure_player
from utils.skill.skill_presets import SKILLS, ICON
from utils.game_manager import (
    get_game,
    get_player_in_game,
    update_player_score,
    use_rush,
    can_force_rush_targets,
    is_lastspurt,
    is_last_corner,
    build_pending_effects_from_player,
    apply_next_roll_effects_to_player,
    set_player_skill_cd,
    is_skill_on_cooldown,
    get_current_path_type,
)
from utils.in_game_manager import incrase_speed_by_acceleration
from utils.race.race_dice import get_distance_color, get_phase_from_turn
from utils.icon_presets import Status_Icon_Type



def get_position_group(channel_id: int, user_id: int) -> str:
    game = get_game(channel_id)
    if game is None:
        return "middle"

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"] for uid, p in game["players"].items()
    }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    total = len(ranked)
    if total <= 1:
        return "front"

    base = total // 3
    remainder = total % 3

    front_size = base + (1 if remainder > 0 else 0)
    mid_size = base + (1 if remainder > 1 else 0)

    for index, (uid, _) in enumerate(ranked):
        if uid == user_id:
            if index < front_size:
                return "front"
            elif index < front_size + mid_size:
                return "middle"
            else:
                return "back"

    return "middle"


def get_nearest_front_gap(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return None

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"] for uid, p in game["players"].items()
    }

    my_score = scores[user_id]

    gaps = [
        score - my_score
        for uid, score in scores.items()
        if uid != user_id and score > my_score
    ]

    return min(gaps) if gaps else None

def get_nearest_back_gap(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return None

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"] for uid, p in game["players"].items()
    }

    my_score = scores[user_id]

    gaps = [
        my_score - score
        for uid, score in scores.items()
        if uid != user_id and score < my_score
    ]

    return min(gaps) if gaps else None

def resolve_skill_targets(channel_id: int, user_id: int, skill: dict) -> list[tuple[int, dict]]:
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return []

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"] for uid, p in game["players"].items()
    }

    player = game["players"][user_id]
    my_score = scores[user_id]

    target_cfg = skill.get("target", {})
    scope = target_cfg.get("scope", "self")
    limit = target_cfg.get("limit", 1)

    if scope == "self":
        return [(user_id, player)]

    front = []
    back = []

    for target_id, info in game["players"].items():
        if target_id == user_id:
            continue

        target_score = scores[target_id]

        gap_front = target_score - my_score
        gap_back = my_score - target_score

        if gap_front > 0:
            front.append((gap_front, target_id, info))
        elif gap_back > 0:
            back.append((gap_back, target_id, info))

    front.sort(key=lambda x: x[0])
    back.sort(key=lambda x: x[0])

    if scope == "nearest_front":
        return [(tid, info) for _, tid, info in front[:1]]

    if scope == "nearest_back":
        return [(tid, info) for _, tid, info in back[:1]]

    if scope == "all_front":
        return [(tid, info) for _, tid, info in front[:limit]]

    if scope == "all_back":
        return [(tid, info) for _, tid, info in back[:limit]]

    if scope == "random_enemy":
        enemies = [(tid, info) for _, tid, info in front + back]
        random.shuffle(enemies)
        return enemies[:limit]

    return []

def build_next_roll_buff_text(player: dict) -> str:
    lines = []

    flat = player.get("next_roll_flat_bonus", 0)
    if flat:
        lines.append(f"เพิ่มผลรวม +{flat}")

    add_d = player.get("next_roll_add_d", 0)
    if add_d:
        lines.append(f"เพิ่มลูกเต๋า +{add_d}")

    add_kh = player.get("next_roll_add_kh", 0)
    if add_kh:
        lines.append(f"เพิ่มจำนวนลูกที่เลือก +{add_kh}")

    floor = player.get("next_roll_floor_bonus", 0)
    if floor:
        lines.append(f"เพิ่มแต้มขั้นต่ำ +{floor}")

    gold_range = player.get("gold_range_bonus_this_turn", 0)
    if gold_range:
        lines.append(f"เพิ่มระยะในการนับโรล Gold +{gold_range}")

    selected = player.get("next_roll_selected_die_bonus", 0)
    if selected:
        lines.append(f"เพิ่มแต้มลูกที่เลือก +{selected}")

    cap = player.get("next_roll_cap_bonus", 0)
    if cap:
        sign = "+" if cap > 0 else ""
        lines.append(f"ปรับแต้มสูงสุดลูกเต๋า {sign}{cap}")

    return "\n".join(lines) if lines else "ไม่มีบัฟค้าง"

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

    if "front_blocked" in trigger:
        blocked = has_front_blocked(channel_id, user_id, 20)

        if trigger["front_blocked"] is True and not blocked:
            return False, "ต้องมีคนอยู่ด้านหน้าในระยะ 20 ช่อง"

        if trigger["front_blocked"] is False and blocked:
            return False, "ใช้ไม่ได้เมื่อมีคนขวางด้านหน้าในระยะ 20 ช่อง"

    if trigger.get("nearby_uma_count") is not None:
        score_map = game["turn_snapshot_scores"]
        skill_effects = []
        skill_effects,merged_stats = build_pending_effects_from_player(player)
        distance_color,nearby_count = get_distance_color(player, score_map, skill_effects or [])

        if nearby_count < trigger.get("nearby_uma_count"):
            return False

    if trigger.get("lastspurt") is True and not is_lastspurt(phase, path_type):
        return False, "ยังไม่เข้าสู่ Last Spurt"
    
    if trigger.get("last_corner") is True and not is_last_corner(game):
        return False, "ยังไม่ถึงโค้งสุดท้าย"

    if "position_group" in trigger:
        position_group = get_position_group(channel_id, user_id)
        if position_group != trigger["position_group"]:
            return False, f"ต้องอยู่ตำแหน่งกลุ่ม {trigger['position_group']}"

    if "target_distance_min" in trigger or "target_distance_max" in trigger:
        min_d = trigger.get("target_distance_min", -float('inf')) # Default เป็นน้อยมากๆ
        max_d = trigger.get("target_distance_max", float('inf'))  # Default เป็นมากที่สุด

        candidates = []

        if max_d >= 0:
            f_gap = get_nearest_front_gap(channel_id, user_id)
            if f_gap is not None:
                lower_bound = max(0, min_d)
                if lower_bound <= f_gap <= max_d:
                    candidates.append(f_gap)

        if min_d < 0:
            b_gap = get_nearest_back_gap(channel_id, user_id)
            if b_gap is not None:
                back_limit_min = abs(min_d)
                back_limit_max = abs(max_d) if max_d < 0 else 0 

                if min(back_limit_min, back_limit_max) <= b_gap <= max(back_limit_min, back_limit_max):
                    candidates.append(-b_gap) # เก็บเป็นค่าติดลบเพื่อให้รู้ว่าเป็นด้านหลัง

        if not candidates:
            return False, "ไม่มีเป้าหมายในระยะที่กำหนด"

        gap_val = min(candidates, key=abs)
        gap = abs(gap_val) 
        
        print(f"Selected gap: {gap_val} (distance: {gap})")

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

def has_front_blocked(channel_id: int, user_id: int, max_gap: int = 10) -> bool:
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return False

    my_score = game["players"][user_id]["score"]

    for uid, info in game["players"].items():
        if uid == user_id:
            continue

        gap = info["score"] - my_score
        if 0 < gap <= max_gap:
            return True

    return False

def execute_skill_core(
    channel_id: int,
    user_id,
    skill_id: str,
    *,
    consume_cost: bool = True,
):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ไม่พบเกม"}

    player = game["players"].get(user_id)
    if player is None:
        return False, {"message": "ไม่พบผู้เล่น"}

    skill = SKILLS.get(skill_id)
    if not skill:
        return False, {"message": "ไม่พบข้อมูลสกิล"}

    # =====================================
    # Cooldown
    # =====================================

    on_cd, cd_left = is_skill_on_cooldown(
        channel_id,
        user_id,
        skill_id
    )

    if on_cd:
        return False, {
            "message": f"สกิลติด cooldown {cd_left}"
        }

    # =====================================
    # Trigger
    # =====================================

    path_type = get_current_path_type(game)

    phase = get_phase_from_turn(
        game["turn"],
        game["max_turn"]
    )

    ok, reason = check_skill_trigger(
        channel_id,
        user_id,
        skill,
        path_type=path_type,
        phase=phase
    )

    if not ok:
        return False, {"message": reason}

    # =====================================
    # Cost
    # =====================================

    cost = skill.get("cost", 0)

    if consume_cost:
        if player.get("wit_mana", 0) < cost:
            return False, {
                "message": f"Wit ไม่พอ ({cost})"
            }

    # =====================================
    # Split effects
    # =====================================

    instant_effects = []
    queued_effects = []

    for effect in skill.get("effects", []):

        effect_type = effect.get("type")
        duration = effect.get("duration")

        if (
            effect_type in [
                "modify_velocity",
                "modify_selected_die",
                "modify_roll_floor",
                "modify_roll_cap",
                "add_d",
                "add_kh",
                "add_dkh",
            ]
            or duration == "this_roll"
        ):
            queued_effects.append(effect)

        else:
            instant_effects.append(effect)

    result_texts = []

    # =====================================
    # Instant
    # =====================================

    if instant_effects:

        temp_skill = skill.copy()
        temp_skill["effects"] = instant_effects

        success, result_text = apply_skill(
            channel_id,
            user_id,
            temp_skill
        )

        if not success:
            return False, {"message": result_text}

        result_texts.append(result_text)

    # =====================================
    # Queued
    # =====================================

    if queued_effects:
        apply_next_roll_effects_to_player(
            player,
            queued_effects
        )

        result_texts.append(
            "บัฟถูกสะสมไว้สำหรับการวิ่งครั้งถัดไป"
        )

    if not instant_effects and not queued_effects:
        return False, {
            "message": "ยังไม่มี effect รองรับ"
        }

    # =====================================
    # Consume resource
    # =====================================

    if consume_cost:
        player["wit_mana"] -= cost

    # =====================================
    # Cooldown
    # =====================================

    set_player_skill_cd(
        channel_id,
        user_id,
        skill_id,
        skill.get("cooldown", 0)
    )

    return True, {
        "skill_id": skill_id,
        "skill_name": skill["name"],
        "skill": skill,
        "result_texts": result_texts,
        "cost": cost,
    }

def apply_skill(channel_id: int, user_id: int, skill: dict):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = get_player_in_game(channel_id, user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    targets = resolve_skill_targets(channel_id, user_id, skill)

    for effect in skill.get("effects", []):
        if effect.get("type") == "force_rush":
            ok, reason = can_force_rush_targets(channel_id, targets)
            if not ok:
                return False, reason

    applied_texts = []

    for effect in skill.get("effects", []):
        effect_type = effect.get("type")
        value = effect.get("value", 0)
        print(effect_type)

        if effect_type == "recover_stamina":
            player["stamina_left"] += value
            applied_texts.append(f"ฟื้นฟู STA ตัวเอง +{value}")

        elif effect_type == "modify_current_speed":
            print(effect["value"])

            incrase_speed_by_acceleration(game, player, effect["value"])
            applied_texts.append(f"เร่งความเร็วขึ้น {value} ระดับ")

        elif effect_type == "self_heal_stamina":
            player["stamina_left"] += value
            applied_texts.append(f"ฟื้นฟู STA ตัวเอง +{value}")

        elif effect_type == "flat_total":
            # ถ้า target เป็น self ก็ลงตัวเอง ถ้าไม่ใช่ก็ลง target
            if not targets:
                success, _ = update_player_score(channel_id, user_id, value)
                if success:
                    sign = "+" if value >= 0 else ""
                    applied_texts.append(f"ปรับคะแนนตัวเองทันที {sign}{value}")
            else:
                for target_id, _ in targets:
                    success, _ = update_player_score(channel_id, target_id, value)
                    if success:
                        sign = "+" if value >= 0 else ""
                        if target_id == user_id:
                            applied_texts.append(f"ปรับคะแนนตัวเองทันที {sign}{value}")
                        else:
                            applied_texts.append(f"ปรับคะแนน <@{target_id}> ทันที {sign}{value}")

        elif effect_type == "reduce_stamina":
            if not targets:
                continue

            for target_id, target_info in targets:
                before = target_info.get("stamina_left", 0)
                target_info["stamina_left"] = max(0, before - value)
                applied_texts.append(f"ลด STA ของ <@{target_id}> -{value}")

        elif effect_type == "apply_debuff_next_turn":
            if not targets:
                continue

            stat = effect.get("stat", "flat_total")

            for target_id, target_info in targets:
                value = effect.get("value", 0)

                if stat == "flat_total":
                    target_info.setdefault("next_roll_flat_bonus", 0)
                    target_info["next_roll_flat_bonus"] += value
                    applied_texts.append(
                        f"ใส่ดีบัฟให้ <@{target_id}> เทิร์นหน้า Flat {value}"
                    )

                elif stat == "cap":
                    target_info.setdefault("next_roll_cap_bonus", 0)
                    target_info["next_roll_cap_bonus"] += value
                    applied_texts.append(
                        f"ใส่ดีบัฟให้ <@{target_id}> เทิร์นหน้า Cap {value}"
                    )

        elif effect_type == "force_rush":
            if not targets:
                continue
                
            for effect in skill.get("effects", []):
                if effect.get("type") == "force_rush":
                    ok, reason = can_force_rush_targets(channel_id, targets)
                    if not ok:
                        return False, reason

            for target_id, target_info in targets:
                rush_success, rush_payload = use_rush(channel_id, target_id)

                if rush_success:
                    applied_texts.append(
                        f"บังคับ <@{target_id}> ใช้ Rush สำเร็จ"
                    )
                else:
                    applied_texts.append(
                        f"บังคับ <@{target_id}> ใช้ Rush ไม่สำเร็จ ({rush_payload})"
                    )

        elif effect_type == "modify_gold_range":
            player.setdefault("gold_range_bonus_this_turn", 0)
            player["gold_range_bonus_this_turn"] += value
            applied_texts.append(f"เพิ่มระยะตรวจ Gold +{value}")

        elif effect_type == "modify_enemy_gold_range":
            if not targets:
                continue

            for target_id, target_info in targets:
                target_info.setdefault("enemy_gold_range_penalty_next_turn", 0)
                target_info["enemy_gold_range_penalty_next_turn"] += value
                applied_texts.append(f"ลดระยะตรวจ Gold ของ <@{target_id}> {value}")

    if not applied_texts:
        return False, "สกิลนี้ยังไม่มีผลที่รองรับในระบบตอนนี้"

    return True, "\n".join(applied_texts)