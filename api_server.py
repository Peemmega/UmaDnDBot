from fastapi import FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import io
import time
from pathlib import Path
import os

from utils.database import (
    get_player, 
    get_player_summary,
    list_player_summaries,
    get_connection, 
    ensure_player, 
    update_player_username,
    set_player_skill_slot,
    get_player_skill_slots,
    init_db,
    set_player_profile_image,
    update_player_stat_pool,
)
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, UnidentifiedImageError
from utils.zone.zone_preset import ZONE_POINT_COST, normalize_zone_build
from utils.race.race_presets import RACE_SCHEDULE, RACE_PRESET, get_web_race_finish_distance
from utils.skill.skill_presets import SKILLS, SKILL_TAG_OPTIONS
from utils.skill.skill_manager import describe_trigger, describe_target, describe_effect, get_skill_display
from utils.game_manager import get_game, create_game, delete_game, run_bot_race_test
from utils.race.race_log_embed import build_race_log_embed, build_race_log_file
from utils.race.race_web import race_web_manager
from utils.profile_images import (
    ALLOWED_IMAGE_CONTENT_TYPES,
    MAX_PROFILE_IMAGE_BYTES,
    PROFILE_IMAGE_SIZE,
    build_profile_image_relative_url,
    ensure_upload_dirs,
    get_profile_uploads_dir,
    get_upload_root_dir,
    resolve_public_url,
    sanitize_numeric_user_id,
)
from views.create_game_view import LobbyView, build_lobby_message_payload
import bot_instance

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

app = FastAPI()


def _cors_origins() -> list[str]:
    """Allow production, local development, and the Railway web URL for this environment."""
    origins = {
        "https://umaroleplaycommunity.up.railway.app",
        "https://umaroleplaytest.up.railway.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }
    configured_origins = os.getenv("CORS_ORIGINS") or os.getenv("FRONTEND_URL") or ""
    origins.update(origin.strip().rstrip("/") for origin in configured_origins.split(",") if origin.strip())
    return sorted(origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ensure_upload_dirs()
app.mount("/uploads", StaticFiles(directory=str(get_upload_root_dir())), name="uploads")
app.mount("/app/assets", StaticFiles(directory=str(ASSETS_DIR)), name="app-assets")


@app.exception_handler(RequestValidationError)
async def log_timing_validation_error(request: Request, exc: RequestValidationError):
    if request.url.path.endswith("/timing"):
        body = (await request.body()).decode("utf-8", errors="replace")
        print(f"[race-web] timing validation failed path={request.url.path} errors={exc.errors()} body={body}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.on_event("startup")
def api_startup():
    init_db()
    ensure_upload_dirs()

@app.get("/player/{user_id}")
def api_get_player(user_id: str, username: str = "Unknown"):
    player = get_player(user_id)

    if not player:
        ensure_player(user_id, username)
        player = get_player(user_id)

    return player


@app.get("/api/players/summary")
def api_get_players_summary():
    return {"players": list_player_summaries()}


@app.get("/api/players/{user_id}/summary")
def api_get_player_summary(user_id: str):
    player = get_player_summary(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.post("/player/{user_id}/profile-image")
async def api_upload_profile_image(user_id: str, file: UploadFile = File(...)):
    try:
        safe_user_id = sanitize_numeric_user_id(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    player = get_player(safe_user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    content_type = (file.content_type or "").lower().strip()
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    raw_bytes = await file.read(MAX_PROFILE_IMAGE_BYTES + 1)
    await file.close()

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty upload")
    if len(raw_bytes) > MAX_PROFILE_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="File too large")

    try:
        source_image = Image.open(io.BytesIO(raw_bytes))
        source_image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="Invalid image file") from exc

    fitted_image = ImageOps.fit(
        source_image.convert("RGBA"),
        PROFILE_IMAGE_SIZE,
        method=Image.Resampling.LANCZOS,
    )

    output_path = get_profile_uploads_dir() / f"{safe_user_id}.webp"
    fitted_image.save(output_path, format="WEBP", quality=90, method=6)

    updated_at = int(time.time())
    relative_url = build_profile_image_relative_url(safe_user_id, updated_at)
    set_player_profile_image(safe_user_id, relative_url, updated_at)

    return {
        "ok": True,
        "user_id": safe_user_id,
        "profile_image_url": resolve_public_url(relative_url),
        "profile_image_updated_at": updated_at,
    }

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
    try:
        player = update_player_stat_pool(
            payload.user_id,
            stats={
                "speed": payload.speed,
                "stamina": payload.stamina,
                "power": payload.power,
                "gut": payload.gut,
                "wit": payload.wit,
            },
            stats_point=payload.stats_point,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"success": True, "message": "Stats updated successfully", "player": player}

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
        key: max(0, int(value))
        for key, value in normalize_zone_build(payload.build).items()
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
            "finish_distance": get_web_race_finish_distance(race),
        })

    return result


RACE_ROOM_CHANNEL_IDS = [
    1496059539085201529,
    1496124234240622673,
    1496124268352639007,
    1502236301074763787,
    1502236315544977539,
    1502236327918174381,
]

class CreateRaceRoomPayload(BaseModel):
    user_id: str
    race_id: str


class WebRacePlayerPayload(BaseModel):
    user_id: str
    username: str = "Unknown"
    avatar_url: str = ""
    style: str = "Pace"
    stage_key: str = "Debut"
    mob_preset: str | None = None
    level: int = 1
    gameplay_mode: str = "timing"


class WebRaceSkillPayload(BaseModel):
    user_id: str
    skill_id: str | None = None
    slot: int | None = None


class WebRaceTimingPayload(BaseModel):
    user_id: str
    cycle_id: int
    timing_score: float
    timing_offset: float = 0.0
    phase: str | None = None
    running_style: str | None = None


class WebRaceLanePayload(BaseModel):
    user_id: str
    target_lane: int

async def send_lobby_message(channel_id: int):
    bot = bot_instance.bot

    if bot is None or not bot.is_ready():
        return False, "Bot ยังไม่พร้อม"

    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    embed, file = build_lobby_message_payload(channel_id)

    if file:
        await channel.send(
            file=file,
            view=LobbyView(channel_id)
        )
    else:
        await channel.send(
            embed=embed,
            view=LobbyView(channel_id)
        )

    return True, "ส่ง lobby embed แล้ว"

async def send_test_log_to_discord(bot, log_channel_id, log_embed, log_file):
    log_channel = bot.get_channel(log_channel_id)

    if log_channel is None:
        return False, "ไม่พบห้อง log ที่กำหนด"

    await log_channel.send(embed=log_embed, file=log_file)
    return True, "ส่ง log สำเร็จ"

async def run_api_test_bot_race(bot, channel_id: int):
    game = get_game(channel_id)

    if game is None:
        return {"success": False, "message": "ยังไม่มีเกมในห้องนี้"}

    success, payload = run_bot_race_test(channel_id)

    if not success:
        delete_game(channel_id)
        return {
            "success": False,
            "message": payload.get("message", "ทดสอบบอทไม่สำเร็จ"),
        }

    game = payload["game"]
    ranked_players = payload["ranked_players"]

    log_embed = build_race_log_embed(game, ranked_players)
    log_file = build_race_log_file(game, ranked_players)

    log_channel_id = 1502217575717798050

    future = asyncio.run_coroutine_threadsafe(
        send_test_log_to_discord(bot, log_channel_id, log_embed, log_file),
        bot.loop
    )

    ok, msg = future.result(timeout=10)

    if not ok:
        delete_game(channel_id)
        return {
            "success": False,
            "message": msg,
        }

    delete_game(channel_id)

    return {
        "success": True,
        "message": "✅ Test Bot Race จบแล้ว ส่ง log และปิดห้องแข่งเรียบร้อย",
        "channel_id": str(channel_id),
    }

@app.post("/race/room/create")
async def api_create_race_room(payload: CreateRaceRoomPayload):
    bot = bot_instance.bot

    if bot is None or not bot.is_ready():
        return {"success": False, "message": "Bot ยังไม่พร้อม"}

    for channel_id in RACE_ROOM_CHANNEL_IDS:
        if get_game(channel_id) is None:
            success = create_game(
                channel_id=channel_id,
                stage_key=payload.race_id,
                owner_id=int(payload.user_id),
            )

            if not success:
                return {"success": False, "message": "สร้างห้องไม่สำเร็จ"}

            race_name = str(payload.race_id).lower()

            if race_name.startswith("test"):
                result = await run_api_test_bot_race(
                    bot=bot,
                    channel_id=channel_id,
                )

                return result

            future = asyncio.run_coroutine_threadsafe(
                send_lobby_message(channel_id),
                bot.loop
            )

            ok, msg = future.result(timeout=10)

            if not ok:
                return {"success": False, "message": msg}

            return {
                "success": True,
                "message": "สร้างห้องสำเร็จ",
                "channel_id": str(channel_id),
            }

    return {"success": False, "message": "ไม่มีห้องว่าง"}

@app.get("/race/rooms")
def api_web_race_rooms():
    return {"rooms": race_web_manager.list_rooms()}


@app.post("/race/rooms/create")
async def api_web_race_create_room(payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.create_room(
            owner_id=payload.user_id,
            username=payload.username,
            avatar_url=payload.avatar_url,
            stage_key=payload.stage_key,
            style=payload.style,
            gameplay_mode=payload.gameplay_mode,
        )
        await race_web_manager.broadcast(room["room_id"])
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/race/rooms/{room_id}")
def api_web_race_room(room_id: str, user_id: str = ""):
    try:
        return race_web_manager.get_room(room_id, user_id or None)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/race/rooms/{room_id}/players/{user_id}/preview.png")
async def api_web_race_player_preview(room_id: str, user_id: str, v: str = ""):
    try:
        _ = v
        image_bytes = await race_web_manager.build_player_preview_png(room_id, user_id)
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/race/rooms/{room_id}/players/{user_id}/preview.webp")
async def api_web_race_player_preview_webp(room_id: str, user_id: str, v: str = ""):
    try:
        _ = v
        image_bytes = await race_web_manager.build_player_preview_webp(room_id, user_id)
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type="image/webp",
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/race/rooms/{room_id}/join")
async def api_web_race_join_room(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.join_room(
            room_id=room_id,
            user_id=payload.user_id,
            username=payload.username,
            avatar_url=payload.avatar_url,
            style=payload.style,
            mob_preset=payload.mob_preset,
        )
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/leave")
async def api_web_race_leave_room(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.leave_room(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/bot")
async def api_web_race_add_bot(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.add_bot(
            room_id=room_id,
            user_id=payload.user_id,
            preset_key=payload.mob_preset or "rookie_pace",
            level=payload.level,
        )
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/start")
async def api_web_race_start_room(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.start_room(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/run")
async def api_web_race_run(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.run(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/timing")
async def api_web_race_timing(room_id: str, payload: WebRaceTimingPayload):
    try:
        room = race_web_manager.timing(
            room_id=room_id,
            user_id=payload.user_id,
            cycle_id=payload.cycle_id,
            timing_score=payload.timing_score,
            timing_offset=payload.timing_offset,
            phase=payload.phase,
        )
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/confirm")
async def api_web_race_confirm(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.confirm(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/reroll")
async def api_web_race_reroll(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.reroll(room_id, payload.user_id, use_wit=False)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/wit-reroll")
async def api_web_race_wit_reroll(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.reroll(room_id, payload.user_id, use_wit=True)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/skill")
async def api_web_race_skill(room_id: str, payload: WebRaceSkillPayload):
    try:
        room = race_web_manager.skill(
            room_id=room_id,
            user_id=payload.user_id,
            skill_id=payload.skill_id,
            slot=payload.slot,
        )
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/zone")
async def api_web_race_zone(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.zone(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/block")
async def api_web_race_block(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.block(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/rush")
async def api_web_race_rush(room_id: str, payload: WebRacePlayerPayload):
    try:
        room = race_web_manager.rush(room_id, payload.user_id)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/race/rooms/{room_id}/change-lane")
async def api_web_race_change_lane(room_id: str, payload: WebRaceLanePayload):
    try:
        room = race_web_manager.change_lane(room_id, payload.user_id, payload.target_lane)
        await race_web_manager.broadcast(room_id)
        return room
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.websocket("/ws/race/{room_id}")
async def websocket_race_room(websocket: WebSocket, room_id: str, user_id: str = ""):
    try:
        await race_web_manager.connect(room_id, websocket)
        await race_web_manager.broadcast(room_id)
    except ValueError:
        await websocket.close(code=1008)
        return

    try:
        while True:
            message = await websocket.receive_json()
            try:
                message_type = message.get("type")
                action_user_id = user_id or message.get("user_id")
                if message_type == "RUN":
                    race_web_manager.run(room_id, action_user_id)
                elif message_type == "TIMING":
                    race_web_manager.timing(
                        room_id,
                        action_user_id,
                        cycle_id=message.get("cycle_id"),
                        timing_score=message.get("timing_score"),
                        timing_offset=message.get("timing_offset", 0.0),
                        phase=message.get("phase"),
                    )
                elif message_type == "CONFIRM":
                    race_web_manager.confirm(room_id, action_user_id)
                elif message_type == "REROLL":
                    race_web_manager.reroll(room_id, action_user_id, use_wit=False)
                elif message_type == "WIT_REROLL":
                    race_web_manager.reroll(room_id, action_user_id, use_wit=True)
                elif message_type == "SKILL":
                    race_web_manager.skill(
                        room_id,
                        action_user_id,
                        skill_id=message.get("skill_id"),
                        slot=message.get("slot"),
                    )
                elif message_type == "ZONE":
                    race_web_manager.zone(room_id, action_user_id)
                elif message_type == "BLOCK":
                    race_web_manager.block(room_id, action_user_id)
                elif message_type == "RUSH":
                    race_web_manager.rush(room_id, action_user_id)
                elif message_type == "CHANGE_LANE":
                    race_web_manager.change_lane(room_id, action_user_id, message.get("target_lane"))
                elif message_type == "LEAVE_ROOM":
                    race_web_manager.leave_room(room_id, action_user_id)
                await race_web_manager.broadcast(room_id)
            except ValueError as exc:
                await websocket.send_json({"type": "ERROR", "message": str(exc)})
    except WebSocketDisconnect:
        race_web_manager.disconnect(room_id, websocket)


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
