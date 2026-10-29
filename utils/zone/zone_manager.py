from typing import Optional

from utils.zone.zone_preset import (
    DEFAULT_ZONE_IMAGE, 
    ZONE_POINT_COST, 
    ZONE_FIELDS,
    ZONE_VALUE,
    normalize_zone_build,
)
from utils.database import get_player, set_player_zone_build
from utils.race.race_history import record_race_action
from utils.in_game_manager import incrase_speed_by_acceleration
from utils.race.stamina_rules import calculate_percent_stamina_amount
from utils.race.runtime_stamina import (
    set_runtime_stamina,
    sync_runtime_stamina,
)


def get_player_zone(user_id: int) -> Optional[dict]:
    player = get_player(user_id)
    if player is None:
        return None

    zone = player.get("zone") or {}
    build = zone.get("build", {})
    normalized_build = normalize_zone_build(build)

    if build != normalized_build:
        set_player_zone_build(user_id, normalized_build)

    return {
        "name": zone.get("name", "Default Zone"),
        "image_url": zone.get("image_url") or DEFAULT_ZONE_IMAGE,
        "points": zone.get("points", 5),
        "build": normalized_build,
    }


def get_zone_points_used(zone: dict) -> int:
    build = normalize_zone_build(zone.get("build", {}))
    total = 0

    for field, cost in ZONE_POINT_COST.items():
        total += int(build.get(field, 0)) * cost

    return total


def get_zone_points_left(zone: dict) -> int:
    total_points = int(zone.get("points", 0))
    used = get_zone_points_used(zone)
    return total_points - used


def upgrade_zone_stat(user_id: int, field: str, amount: int = 1) -> tuple[bool, str]:
    if field not in ZONE_FIELDS:
        return False, "ไม่พบค่านี้ใน Zone"

    zone = get_player_zone(user_id)
    if zone is None:
        return False, "ไม่พบข้อมูลผู้เล่น"

    build = zone["build"]
    cost = ZONE_POINT_COST[field] * amount
    left = get_zone_points_left(zone)

    if left < cost:
        return False, f"Zone point ไม่พอ (ต้องใช้ {cost})"

    build[field] = int(build.get(field, 0)) + amount
    set_player_zone_build(user_id, build)
    return True, f"อัป {field} +{amount} สำเร็จ"


def downgrade_zone_stat(user_id: int, field: str, amount: int = 1) -> tuple[bool, str]:
    if field not in ZONE_FIELDS:
        return False, "ไม่พบค่านี้ใน Zone"

    zone = get_player_zone(user_id)
    if zone is None:
        return False, "ไม่พบข้อมูลผู้เล่น"

    build = zone["build"]
    current = int(build.get(field, 0))

    if current - amount < 0:
        return False, "ค่านี้ต่ำกว่า 0 ไม่ได้"

    build[field] = current - amount
    set_player_zone_build(user_id, build)
    return True, f"ลด {field} -{amount} สำเร็จ"

def get_zone_effects_from_build(zone_build: dict) -> dict:
    normalized_build = normalize_zone_build(zone_build)
    cap_floor_value = int(normalized_build.get("cap_floor", 0)) * ZONE_VALUE["cap_floor"]

    return {
        "flat": int(normalized_build.get("flat", 0)) * ZONE_VALUE["flat"],
        "add_dkh": int(normalized_build.get("add_dkh", 0)) * ZONE_VALUE["add_dkh"],
        "floor": cap_floor_value,
        "cap": cap_floor_value,
        "cap_floor": cap_floor_value,
        "self_heal_stamina": int(normalized_build.get("self_heal_stamina", 0)) * ZONE_VALUE["self_heal_stamina"],
        "modify_current_speed": int(normalized_build.get("modify_current_speed", 0)) * ZONE_VALUE["modify_current_speed"],
        "race_speed": int(normalized_build.get("race_speed", 0)) * ZONE_VALUE["race_speed"],
        "reduce_block_penalty": int(normalized_build.get("reduce_block_penalty", 0)) * ZONE_VALUE["reduce_block_penalty"],
    }

def get_zone_effect(zone: dict) -> tuple[bool, str]:
    if not zone:
        return False, "ไม่พบข้อมูล Zone"

    zone_build = zone.get("build", {})
    if not zone_build:
        return "ไม่พบข้อมูล zone_build"

    effects = get_zone_effects_from_build(zone_build)
    heal_value = effects.get("self_heal_stamina", 0)
    modify_current_speed = effects.get("modify_current_speed", 0)
    race_speed = effects.get("race_speed", 0)

    lines = []
    if effects["flat"]:
        lines.append(f"✨ เพิ่มผลรวม +{effects['flat']}")
    if effects["add_dkh"]:
        lines.append(f"🎲 เพิ่มลูกเต๋า d/kh +{effects['add_dkh']}")
    if effects["cap_floor"]:
        lines.append(f"🧱📈 เพิ่มแต้มขั้นต่ำและสูงสุด +{effects['cap_floor']}")
    if heal_value:
        lines.append(f"❤️ ฟื้นฟู STA ตัวเอง +{heal_value}%")
    if modify_current_speed:
        lines.append(f"👟 เพิ่มความเร่ง {modify_current_speed} ระดับ")
    if race_speed:
        lines.append(f"🏇 เพิ่มเพดานความเร็วสูงสุด +{race_speed}")
    if effects["reduce_block_penalty"]:
        lines.append(f"🛡️ ลดโทษ Blocked {effects['reduce_block_penalty']}% สำหรับ Run ถัดไป")
    if not lines:
        lines.append("Zone ทำงาน แต่ยังไม่มีค่าที่อัปไว้")   

    return "\n".join(lines)

def apply_zone_in_game(game, player: dict) -> tuple[bool, str]:
    if not (game.get("game_rules") or {}).get("AllowSkill", True):
        return False, "ห้องนี้ปิดการใช้ Skill และ Zone"

    zone = player.get("zone")
    if not zone:
        return False, "ไม่พบข้อมูล Zone"
    
    zone_left = player.get("zone_left", 0)
    if zone_left <= 0:
        return False, "Zone ถูกใช้ไปแล้ว"

    zone_build = zone.get("build", {})
    effects = get_zone_effects_from_build(zone_build)
    zone_race_stat_changes = []

    player["next_roll_flat_bonus"] = player.get("next_roll_flat_bonus", 0) + effects["flat"]
    player["next_roll_add_d"] = player.get("next_roll_add_d", 0) + effects["add_dkh"]
    player["next_roll_add_kh"] = player.get("next_roll_add_kh", 0) + effects["add_dkh"]
    player["next_roll_floor_bonus"] = player.get("next_roll_floor_bonus", 0) + effects["floor"]
    player["next_roll_cap_bonus"] = player.get("next_roll_cap_bonus", 0) + effects["cap"]
    player["next_roll_block_reduction"] = player.get("next_roll_block_reduction", 0) + effects["reduce_block_penalty"] // 10

    heal_value = effects.get("self_heal_stamina", 0)
    gain = 0
    if heal_value > 0:
        snapshot = sync_runtime_stamina(player)
        gain = calculate_percent_stamina_amount(
            snapshot["max_stamina"], heal_value / 10
        )
        set_runtime_stamina(
            player,
            player.get("stamina_stat", 0),
            player.get("stamina_left", 0) + gain,
        )
        
    # Apply the cap before acceleration so both Zone effects work together.
    race_speed = effects.get("race_speed", 0)
    if race_speed > 0:
        player["zone_speed_cap_bonus"] = player.get("zone_speed_cap_bonus", 0) + race_speed

    modify_current_speed = effects.get("modify_current_speed", 0)
    if modify_current_speed > 0:
        incrase_speed_by_acceleration(game, player, modify_current_speed)

    player["zone_left"] = zone_left - 1
    player["_last_zone_race_stat_changes"] = zone_race_stat_changes

    zone_effect = get_zone_effect(zone)

    actor_id = next(
        (
            player_id
            for player_id, candidate in (game.get("players") or {}).items()
            if candidate is player
        ),
        None,
    )
    if actor_id is not None:
        record_race_action(
            game,
            actor_id,
            "Zone",
            {
                "zone_name": zone.get("name") or zone.get("zone_name"),
                "effects": effects,
                "stamina_heal": gain,
                "speed_increase": modify_current_speed,
                "speed_cap_increase": race_speed,
                "summary": zone_effect,
            },
        )

    return True, zone_effect
    
def get_zone_effect_preview(zone: dict) -> dict:
    return get_zone_effects_from_build(zone.get("build", {}))
