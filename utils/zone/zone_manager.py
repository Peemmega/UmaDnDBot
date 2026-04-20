from typing import Optional

from utils.zone.zone_preset import (
    DEFAULT_ZONE_IMAGE, 
    ZONE_POINT_COST, 
    ZONE_FIELDS,
    ZONE_VALUE
)
from utils.database import set_player_zone_build, get_player


def get_player_zone(user_id: int) -> Optional[dict]:
    player = get_player(user_id)
    if player is None:
        return None

    zone = player.get("zone") or {}
    build = zone.get("build", {})

    normalized_build = {
        "flat": int(build.get("flat", 0)),
        "add_d": int(build.get("add_d", 0)),
        "add_kh": int(build.get("add_kh", 0)),
        "floor": int(build.get("floor", 0)),
        "selected_die": int(build.get("selected_die", 0)),
        "cap": int(build.get("cap", 0)),
        "self_heal_stamina": int(build.get("self_heal_stamina", 0)), 
    }

    if build != normalized_build:
        set_player_zone_build(user_id, normalized_build)

    return {
        "name": zone.get("name", "Default Zone"),
        "image_url": zone.get("image_url") or DEFAULT_ZONE_IMAGE,
        "points": zone.get("points", 5),
        "build": normalized_build,
    }


def get_zone_points_used(zone: dict) -> int:
    build = zone.get("build", {})
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
    return {
        "flat": int(zone_build.get("flat", 0)) * 18,
        "add_d": int(zone_build.get("add_d", 0)) * 2,
        "add_kh": int(zone_build.get("add_kh", 0)) * 3,
        "floor": int(zone_build.get("floor", 0)) * 5,
        "selected_die": int(zone_build.get("selected_die", 0)) * 3,
        "cap": int(zone_build.get("cap", 0)) * 7,
        "self_heal_stamina": int(zone_build.get("self_heal_stamina", 0)) * 2,
    }

def get_zone_effect(zone: dict) -> tuple[bool, str]:
    zone_build = zone.get("build", {})
    if not zone_build:
        return "ไม่พบข้อมูล zone_build"

    effects = get_zone_effects_from_build(zone_build)
    heal_value = effects.get("self_heal_stamina", 0)

    lines = []
    if effects["flat"]:
        lines.append(f"✨ เพิ่มผลรวม +{effects['flat']}")
    if effects["add_d"]:
        lines.append(f"🎲 เพิ่มลูกเต๋า +{effects['add_d']}")
    if effects["add_kh"]:
        lines.append(f"🖐️ เพิ่มจำนวนลูกที่เลือก +{effects['add_kh']}")
    if effects["floor"]:
        lines.append(f"🧱 เพิ่มแต้มขั้นต่ำ +{effects['floor']}")
    if effects["selected_die"]:
        lines.append(f"🎯 เพิ่มแต้มลูกที่เลือก +{effects['selected_die']}")
    if effects["cap"]:
        lines.append(f"📈 เพิ่มแต้มสูงสุด +{effects['cap']}")
    if heal_value:
        lines.append(f"❤️ ฟื้นฟู STA ตัวเอง +{heal_value}")

    if not lines:
        lines.append("Zone ทำงาน แต่ยังไม่มีค่าที่อัปไว้")   

    return "\n".join(lines)

def apply_zone_in_game(player: dict) -> tuple[bool, str]:
    zone = player.get("zone")
    zone_left = player.get("zone_left")
    if not zone:
        return False, "ไม่พบข้อมูล Zone"

    if zone_left:
        if zone_left <= 0:
            return False, "Zone ถูกใช้ไปแล้ว"
        else:
            player["zone_left"] -= 1

    zone_build = zone.get("build", {})
    effects = get_zone_effects_from_build(zone_build)

    # Apply Effect to player
    player["next_roll_flat_bonus"] = player.get("next_roll_flat_bonus", 0) + effects["flat"]
    player["next_roll_add_d"] = player.get("next_roll_add_d", 0) + effects["add_d"]
    player["next_roll_add_kh"] = player.get("next_roll_add_kh", 0) + effects["add_kh"]
    player["next_roll_floor_bonus"] = player.get("next_roll_floor_bonus", 0) + effects["floor"]
    player["next_roll_selected_die_bonus"] = player.get("next_roll_selected_die_bonus", 0) + effects["selected_die"]
    player["next_roll_cap_bonus"] = player.get("next_roll_cap_bonus", 0) + effects["cap"]

    heal_value = effects.get("self_heal_stamina", 0)
    if heal_value > 0:
        player["stamina_left"] = player.get("stamina_left", 0) + heal_value


    zone_detail = get_zone_effect(zone)

    return True, zone_detail

    
def get_zone_effect_preview(zone: dict) -> dict:
    build = zone.get("build", {})

    return {
        "flat": int(build.get("flat", 0)) * ZONE_VALUE["flat"],
        "add_d": int(build.get("add_d", 0)) * ZONE_VALUE["add_d"],
        "add_kh": int(build.get("add_kh", 0)) * ZONE_VALUE["add_kh"],
        "floor": int(build.get("floor", 0)) * ZONE_VALUE["floor"],
        "selected_die": int(build.get("selected_die", 0)) * ZONE_VALUE["selected_die"],
        "cap": int(build.get("cap", 0)) * ZONE_VALUE["cap"],
        "self_heal_stamina": int(build.get("self_heal_stamina", 0)) * ZONE_VALUE["self_heal_stamina"],
    }