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

    return {
        "name": zone.get("name", "Default Zone"),
        "image_url": zone.get("image_url") or DEFAULT_ZONE_IMAGE,
        "points": zone.get("points", 5),
        "build": zone.get("build", {}),
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


def get_zone_effect_preview(zone: dict) -> dict:
    build = zone.get("build", {})

    return {
        "flat": int(build.get("flat", 0)) * ZONE_VALUE["flat"],
        "add_d": int(build.get("add_d", 0)) * ZONE_VALUE["add_d"],
        "add_kh": int(build.get("add_kh", 0)) * ZONE_VALUE["add_kh"],
        "floor": int(build.get("floor", 0)) * ZONE_VALUE["floor"],
        "selected_die": int(build.get("selected_die", 0)) * ZONE_VALUE["selected_die"],
        "cap": int(build.get("cap", 0)) * ZONE_VALUE["cap"],
    }