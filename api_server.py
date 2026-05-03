from fastapi import FastAPI, HTTPException
import json

from utils.database import (
    get_player, 
    get_connection, 
    ensure_player, 
    update_player_username,
    set_player_skill_slot,
    get_player_skill_slots,
)
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from utils.zone.zone_preset import ZONE_POINT_COST
from utils.race.race_presets import RACE_SCHEDULE, RACE_PRESET
from utils.skill.skill_presets import SKILLS, SKILL_TAG_OPTIONS
from utils.skill.skill_manager import describe_trigger, describe_target, describe_effect, get_skill_display
from utils.game_manager import get_game, create_game
from views.create_game_view import LobbyView, build_lobby_embed
from bot_instance import bot

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://umabotapp-production-c99a.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/player/{user_id}")
def api_get_player(user_id: str, username: str = "Unknown"):
    player = get_player(user_id)

    if not player:
        ensure_player(user_id, username)
        player = get_player(user_id)

    return player

class UpdateStatsPayload(BaseModel):
    user_id: str
    speed: int
    stamina: int
    power: int
    gut: int
    wit: int
    stats_point: int

@app.post("/player/stats/update")
def update_player_stats(payload: UpdateStatsPayload):
    conn = get_connection()
    cur = conn.cursor()
    print(payload)

    try:
        cur.execute("""
            SELECT speed, stamina, power, gut, wit, stats_point
            FROM players
            WHERE CAST(user_id AS TEXT) = ?
        """, (payload.user_id,))
        row = cur.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Player not found")

        old_speed, old_stamina, old_power, old_gut, old_wit, old_stats_point = row

        stat_values = [
            payload.speed,
            payload.stamina,
            payload.power,
            payload.gut,
            payload.wit,
        ]

        if any(v < 1 for v in stat_values):
            raise HTTPException(status_code=400, detail="Each stat must be at least 1")

        total_before = (
            old_speed +
            old_stamina +
            old_power +
            old_gut +
            old_wit +
            old_stats_point
        )

        total_after = (
            payload.speed +
            payload.stamina +
            payload.power +
            payload.gut +
            payload.wit +
            payload.stats_point
        )

        if total_before != total_after:
            raise HTTPException(status_code=400, detail="Invalid total stat pool")

        cur.execute("""
            UPDATE players
            SET speed = ?,
                stamina = ?,
                power = ?,
                gut = ?,
                wit = ?,
                stats_point = ?
            WHERE CAST(user_id AS TEXT) = ?
        """, (
            payload.speed,
            payload.stamina,
            payload.power,
            payload.gut,
            payload.wit,
            payload.stats_point,
            payload.user_id,
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Stats updated successfully",
            "player": {
                "speed": payload.speed,
                "stamina": payload.stamina,
                "power": payload.power,
                "gut": payload.gut,
                "wit": payload.wit,
                "stats_point": payload.stats_point,
            }
        }
    finally:
        conn.close()

@app.get("/mailbox/{user_id}")
def get_mailbox(user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM mailbox
        WHERE is_read = 1
          AND created_at <= datetime('now', '-7 days')
    """)

    cur.execute("""
        SELECT id, title, message, reward_type, reward_amount, is_read, created_at
        FROM mailbox
        WHERE CAST(user_id AS TEXT) = ?
        ORDER BY id DESC
    """, (str(user_id),))

    rows = cur.fetchall()
    conn.commit()
    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "message": row[2],
            "reward_type": row[3],
            "reward_amount": row[4],
            "is_read": bool(row[5]),
            "created_at": row[6],
        }
        for row in rows
    ]


@app.post("/mailbox/{mail_id}/read")
def mark_mail_read(mail_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE mailbox
        SET is_read = 1
        WHERE id = ?
    """, (mail_id,))

    conn.commit()
    conn.close()

    return {"success": True}

class UpdateUsernamePayload(BaseModel):
    user_id: str
    username: str

@app.post("/player/username/update")
def api_update_username(payload: UpdateUsernamePayload):
    username = payload.username.strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    if len(username) > 24:
        raise HTTPException(status_code=400, detail="Username too long")

    try:
        update_player_username(payload.user_id, username)
    except ValueError:
        raise HTTPException(status_code=404, detail="Player not found")

    return {
        "success": True,
        "username": username
    }



class ZoneUpdatePayload(BaseModel):
    user_id: str
    name: str
    image_url: str = ""
    build: dict


def calc_zone_used(build: dict) -> int:
    return sum(
        int(build.get(key, 0)) * cost
        for key, cost in ZONE_POINT_COST.items()
    )


@app.post("/player/zone/update")
def api_update_player_zone(payload: ZoneUpdatePayload):
    safe_build = {
        key: max(0, int(payload.build.get(key, 0)))
        for key in ZONE_POINT_COST.keys()
    }

    used_points = calc_zone_used(safe_build)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT zone_points
            FROM players
            WHERE CAST(user_id AS TEXT) = ?
        """, (str(payload.user_id),))

        row = cur.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Player not found")

        max_points = int(row["zone_points"] or 0)

        if used_points > max_points:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough zone points: used={used_points}, max={max_points}"
            )

        zone_name = payload.name.strip() or "Default Zone"

        cur.execute("""
            UPDATE players
            SET zone_name = ?,
                zone_image_url = ?,
                zone_build = ?
            WHERE CAST(user_id AS TEXT) = ?
        """, (
            zone_name,
            payload.image_url,
            json.dumps(safe_build),
            str(payload.user_id),
        ))

        conn.commit()

        return {
            "success": True,
            "zone": {
                "name": zone_name,
                "image_url": payload.image_url,
                "points": max_points,
                "build": safe_build,
            }
        }

    finally:
        conn.close()

@app.get("/races")
def api_get_all_races(distance: str = "all"):
    result = []

    for race_id, race in RACE_PRESET.items():
        race_distance = race.get("distance", "unknown")

        if distance != "all" and race_distance.lower() != distance.lower():
            continue

        result.append({
            "id": race_id,
            "name": race.get("name"),
            "image": race.get("image"),
            "thumbnail": race.get("thumnail"),
            "track": race.get("track"),
            "distance": race_distance,
            "turn": race.get("turn"),
            "path": race.get("path", []),
        })

    return result


RACE_ROOM_CHANNEL_IDS = [
    1496059539085201529,
    1496124234240622673,
    1496124268352639007,
]

class CreateRaceRoomPayload(BaseModel):
    user_id: str
    race_id: str

@app.post("/race/room/create")
async def api_create_race_room(payload: CreateRaceRoomPayload):
    for channel_id in RACE_ROOM_CHANNEL_IDS:
        if get_game(channel_id) is None:
            success = create_game(
                channel_id=channel_id,
                stage_key=payload.race_id,
                owner_id=int(payload.user_id),
            )

            if not success:
                return {"success": False, "message": "สร้างห้องไม่สำเร็จ"}

            channel = bot.get_channel(channel_id)
            if channel is None:
                channel = await bot.fetch_channel(channel_id)
                
            embed = build_lobby_embed(channel_id)

            await channel.send(
                embed=embed,
                view=LobbyView(channel_id)
            )

            return {
                "success": True,
                "message": "สร้างห้องสำเร็จ",
                "channel_id": str(channel_id),
            }

    return {"success": False, "message": "ไม่มีห้องว่าง"}

@app.get("/race/calendar")
def get_race_calendar():
    events = []

    for item in RACE_SCHEDULE:
        race = RACE_PRESET.get(item["race_id"])
        if not race:
            continue

        events.append({
            "id": item["race_id"],
            "date": item["date"],
            "time": item["time"],
            "name": race['name'],
            "image": race.get("image"),
            "thumbnail": race.get("thumnail"),
            "track": race.get("track"),
            "distance": race.get("distance"),
        })

    return events

@app.get("/skills")
def api_get_skills(tag: str = "all"):
    result = []

    for skill_id, skill in SKILLS.items():
        tags = skill.get("tags", [])

        if tag != "all" and tag not in tags:
            continue

        result.append({
            "id": skill_id,
            "name": skill['name'],
            "icon": skill.get("icon"),
            "cooldown": skill.get("cooldown", 0),
            "cost": skill.get("cost", 0),
            "tags": tags,
            "target": describe_target(skill.get("target", {})),
            "trigger": describe_trigger(skill.get("trigger", {})),
            "effects": [
                describe_effect(effect)
                for effect in skill.get("effects", [])
            ],
        })

    return result


@app.get("/skills/tags")
def api_get_skill_tags():
    return [
        {"value": value, "label": label}
        for value, label in SKILL_TAG_OPTIONS
    ]

class EquipSkillPayload(BaseModel):
    user_id: str
    username: str = "Unknown"
    slot: int
    skill_id: str


@app.post("/player/skill/equip")
def api_equip_skill(payload: EquipSkillPayload):
    user_id = int(payload.user_id)
    skill_id = payload.skill_id.strip().lower()

    ensure_player(user_id, payload.username)

    if payload.slot not in (1, 2, 3, 4):
        raise HTTPException(status_code=400, detail="slot ต้องเป็น 1-4")

    if skill_id not in SKILLS:
        raise HTTPException(status_code=404, detail=f"ไม่พบสกิล `{skill_id}`")

    slots = get_player_skill_slots(user_id)
    if slots and skill_id in slots.values():
        raise HTTPException(status_code=400, detail="คุณติดตั้งสกิลนี้ไว้แล้ว")

    success, message = set_player_skill_slot(
        user_id=user_id,
        slot=payload.slot,
        skill_id=skill_id
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "slot": payload.slot,
        "skill_id": skill_id,
        "skill_text": get_skill_display(skill_id),
    }

@app.get("/player/{user_id}/skills")
def api_get_player_skills(user_id: str):
    slots = get_player_skill_slots(int(user_id))

    if slots is None:
        raise HTTPException(status_code=404, detail="Player not found")

    result = {}

    for slot_key, skill_id in slots.items():
        if not skill_id:
            result[slot_key] = None
            continue

        skill = SKILLS.get(skill_id)
        if not skill:
            result[slot_key] = {
                "id": skill_id,
                "missing": True,
            }
            continue

        result[slot_key] = {
            "id": skill_id,
            "name": skill['name'],
            "icon": skill.get("icon"),
            "cooldown": skill.get("cooldown", 0),
            "cost": skill.get("cost", 0),
            "tags": skill.get("tags", []),
            "target": describe_target(skill.get("target", {})),
            "trigger": describe_trigger(skill.get("trigger", {})),
            "effects": [
                describe_effect(effect)
                for effect in skill.get("effects", [])
            ],
        }

    return result