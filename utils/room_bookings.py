"""Persistent scheduling and registration data for Discord race rooms."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import json
import sqlite3
import uuid

from utils.storage.database import DB_PATH, database_connection

THAI_TZ = ZoneInfo("Asia/Bangkok")
ROOM_TYPES = {"practice", "legend", "debut"}
ROOM_STATUSES = {"scheduled", "creating", "restoring", "open", "failed", "completed", "cancelled"}


def init_room_booking_tables() -> None:
    with database_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS room_bookings (
                booking_id TEXT PRIMARY KEY,
                booking_type TEXT NOT NULL CHECK(booking_type IN ('practice','legend','debut')),
                creator_id TEXT NOT NULL,
                creator_name TEXT NOT NULL,
                stage_key TEXT NOT NULL,
                starts_at TEXT NOT NULL,
                visibility TEXT NOT NULL DEFAULT 'public' CHECK(visibility IN ('public','private')),
                settings_json TEXT NOT NULL DEFAULT '{}',
                invited_ids_json TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'scheduled',
                thread_id TEXT,
                parent_channel_id TEXT,
                guild_id TEXT,
                error TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS room_booking_signups (
                booking_id TEXT NOT NULL REFERENCES room_bookings(booking_id) ON DELETE CASCADE,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (booking_id, user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS legend_progress (
                user_id TEXT NOT NULL,
                legend_key TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                won INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, legend_key)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS room_booking_entries (
                booking_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                entered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (booking_id, user_id)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_room_bookings_due ON room_bookings(status, starts_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_room_bookings_creator ON room_bookings(creator_id, starts_at)")
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(room_bookings)").fetchall()}
        if "guild_id" not in columns:
            conn.execute("ALTER TABLE room_bookings ADD COLUMN guild_id TEXT")


def _decode_booking(row: sqlite3.Row, *, include_members: bool = True) -> dict:
    item = dict(row)
    item["settings"] = json.loads(item.pop("settings_json") or "{}")
    item["invited_ids"] = json.loads(item.pop("invited_ids_json") or "[]")
    from utils.race.race_presets import RACE_PRESET
    from utils.mob.mob_presets import MOB_PRESETS

    item["stage_name"] = (RACE_PRESET.get(item["stage_key"]) or {}).get("name", item["stage_key"])
    item["legend_name"] = (MOB_PRESETS.get(item["settings"].get("legend_key")) or {}).get("name")
    if include_members:
        item["members"] = list_booking_members(item["booking_id"])
    return item


def list_booking_members(booking_id: str) -> list[dict]:
    with database_connection() as conn:
        rows = conn.execute(
            "SELECT user_id, username, registered_at FROM room_booking_signups WHERE booking_id=? ORDER BY registered_at",
            (str(booking_id),),
        ).fetchall()
    return [dict(row) for row in rows]


def record_room_booking_signup(booking_id: str, user_id: str, username: str) -> None:
    if not booking_id:
        return
    with database_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO room_booking_signups(booking_id,user_id,username) VALUES(?,?,?)",
            (str(booking_id), str(user_id), str(username or user_id)),
        )


def list_bookings(viewer_id: str | None = None, *, include_past: bool = False) -> list[dict]:
    now_iso = datetime.now(timezone.utc).isoformat()
    clauses = ["status IN ('scheduled','creating','restoring','open','failed')"]
    params: list[object] = []
    if not include_past:
        clauses.append("(starts_at >= ? OR status IN ('scheduled','open','creating','restoring','failed'))")
        params.append(now_iso)
    with database_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM room_bookings WHERE {' AND '.join(clauses)} ORDER BY starts_at",
            params,
        ).fetchall()
    result = []
    for row in rows:
        item = _decode_booking(row)
        if item["visibility"] == "private" and viewer_id not in {item["creator_id"], *item["invited_ids"]}:
            continue
        result.append(item)
    return result


def list_open_bookings() -> list[dict]:
    with database_connection() as conn:
        rows = conn.execute("SELECT * FROM room_bookings WHERE status='open' ORDER BY starts_at").fetchall()
    return [_decode_booking(row) for row in rows]


def get_booking(booking_id: str) -> dict | None:
    with database_connection() as conn:
        row = conn.execute("SELECT * FROM room_bookings WHERE booking_id=?", (str(booking_id),)).fetchone()
    return _decode_booking(row) if row else None


def _parse_start(date_text: str, time_text: str) -> tuple[datetime, datetime]:
    try:
        local_date = date.fromisoformat(date_text)
        normalized_time = "00:00" if time_text == "24:00" else time_text
        local_time = time.fromisoformat(normalized_time)
    except (TypeError, ValueError) as exc:
        raise ValueError("กรุณาระบุวันที่และเวลาให้ถูกต้อง") from exc
    if time_text == "24:00":
        local_date += timedelta(days=1)
        local_time = time(0, 0)
    elif not (time(10, 0) <= local_time <= time(23, 59)):
        raise ValueError("เวลาเริ่มห้องต้องอยู่ระหว่าง 10:00 ถึง 24:00 น.")
    local_start = datetime.combine(local_date, local_time, tzinfo=THAI_TZ)
    now_local = datetime.now(THAI_TZ)
    if local_start <= now_local:
        raise ValueError("เวลาเริ่มห้องต้องเป็นเวลาในอนาคต")
    if local_start.date() > now_local.date() + timedelta(days=7):
        raise ValueError("จองล่วงหน้าได้ไม่เกิน 7 วัน")
    return local_start, local_start.astimezone(timezone.utc)


def create_booking(
    *, booking_type: str, creator_id: str, creator_name: str, stage_key: str,
    local_date: str, local_time: str, visibility: str = "public",
    invited_ids: list[str] | None = None, settings: dict | None = None,
) -> dict:
    booking_type = str(booking_type).strip().lower()
    visibility = str(visibility).strip().lower()
    if booking_type not in ROOM_TYPES:
        raise ValueError("ประเภทห้องไม่ถูกต้อง")
    if visibility not in {"public", "private"}:
        raise ValueError("ประเภทห้องต้องเป็น free-join หรือ private")
    if booking_type != "practice" and visibility != "public":
        raise ValueError("Legend Race และ Debut ต้องเปิดให้ลงทะเบียนแบบสาธารณะ")
    local_start, start_utc = _parse_start(local_date, local_time)
    settings = dict(settings or {})
    invited_ids = list(dict.fromkeys(str(value) for value in (invited_ids or []) if str(value).isdigit()))
    creator_id = str(creator_id)
    if creator_id in invited_ids:
        invited_ids.remove(creator_id)
    if booking_type == "practice":
        mobs = settings.get("mobs") or []
        if len(mobs) > 8:
            raise ValueError("ห้องฝึกซ้อมเพิ่ม Mob ได้ไม่เกิน 8 ตัว")
        if settings.get("weather", "none") not in {"none", "random", "sunny", "rainy"}:
            raise ValueError("สภาพอากาศไม่ถูกต้อง")
    if booking_type == "legend":
        from utils.race.legend_race_presets import LEGEND_RACE_PRESETS
        from utils.race.race_presets import RACE_PRESET
        from utils.mob.mob_presets import MOB_PRESETS

        preset_key = str(settings.get("legend_preset_key") or "")
        preset = LEGEND_RACE_PRESETS.get(preset_key)
        if not preset:
            raise ValueError("กรุณาเลือก Legend preset")
        if preset.get("legend_key") not in MOB_PRESETS:
            raise ValueError("Legend preset อ้างถึงตัวละครที่ไม่มีใน MOB_PRESETS")
        if preset.get("stage_key") not in RACE_PRESET:
            raise ValueError("Legend preset อ้างถึงสนามที่ไม่มีใน RACE_PRESET")
        if not 1 <= int(preset.get("legend_level", 1)) <= 8:
            raise ValueError("ระดับ Legend ใน preset ต้องอยู่ระหว่าง 1 ถึง 8")
        mob_settings = preset.get("mobs") or {}
        mob_level = int(mob_settings.get("level", 2))
        debut_mob_keys = RACE_PRESET.get("Debut", {}).get("auto_mobs", [])
        if len(debut_mob_keys) != 8 or any(mob_key not in MOB_PRESETS for mob_key in debut_mob_keys):
            raise ValueError("Debut preset ต้องมี Mob ที่ถูกต้องครบ 8 ตัว")
        if not 1 <= mob_level <= 8:
            raise ValueError("ระดับ Mob ใน Legend preset ต้องอยู่ระหว่าง 1–8")
        if preset.get("weather", "none") not in {"none", "random", "warm", "sunny", "rainy"}:
            raise ValueError("สภาพอากาศใน Legend preset ไม่ถูกต้อง")
        if preset.get("record_type", "official") not in {"official", "practice"}:
            raise ValueError("record_type ใน Legend preset ต้องเป็น official หรือ practice")
        settings = {
            "legend_preset_key": preset_key,
            "legend_key": str(preset["legend_key"]),
            "legend_level": int(preset.get("legend_level", 1)),
            "mob_level": mob_level,
            "mobs": [
                {"key": mob_key, "level": mob_level, "name": MOB_PRESETS[mob_key].get("name", mob_key)}
                for mob_key in debut_mob_keys
            ],
            "weather": preset.get("weather", "none"),
            "record_type": preset.get("record_type", "official"),
        }
        stage_key = str(preset["stage_key"])
    if booking_type == "debut":
        settings = {"weather": "random", "record_type": "official", "mob_level": 2}

    booking_id = uuid.uuid4().hex[:12]
    with database_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if booking_type == "practice":
            local_day_start = datetime.combine(local_start.date(), time.min, tzinfo=THAI_TZ).astimezone(timezone.utc).isoformat()
            local_day_end = (datetime.combine(local_start.date() + timedelta(days=1), time.min, tzinfo=THAI_TZ)).astimezone(timezone.utc).isoformat()
            count = conn.execute(
                "SELECT COUNT(*) FROM room_bookings WHERE creator_id=? AND booking_type='practice' AND starts_at>=? AND starts_at<? AND status!='cancelled'",
                (creator_id, local_day_start, local_day_end),
            ).fetchone()[0]
            if count >= 2:
                raise ValueError("สร้างห้องฝึกซ้อมได้ไม่เกิน 2 รอบต่อวัน")
        conn.execute(
            """INSERT INTO room_bookings
            (booking_id, booking_type, creator_id, creator_name, stage_key, starts_at, visibility, settings_json, invited_ids_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (booking_id, booking_type, creator_id, creator_name.strip() or "Trainer", stage_key,
             start_utc.isoformat(), visibility, json.dumps(settings, ensure_ascii=False),
             json.dumps(invited_ids)),
        )
        conn.execute(
            "INSERT INTO room_booking_signups (booking_id,user_id,username) VALUES (?,?,?)",
            (booking_id, creator_id, creator_name.strip() or "Trainer"),
        )
        for user_id in invited_ids:
            # Names are refreshed from the server-side player directory by the API before use.
            conn.execute(
                "INSERT OR IGNORE INTO room_booking_signups (booking_id,user_id,username) VALUES (?,?,?)",
                (booking_id, user_id, user_id),
            )
    return get_booking(booking_id)


def register_for_booking(booking_id: str, user_id: str, username: str) -> dict:
    user_id = str(user_id)
    with database_connection() as conn:
        row = conn.execute("SELECT * FROM room_bookings WHERE booking_id=?", (booking_id,)).fetchone()
        if not row:
            raise ValueError("ไม่พบห้องที่เลือก")
        booking = _decode_booking(row, include_members=False)
        if booking["status"] not in {"scheduled", "open"}:
            raise ValueError("ห้องนี้ปิดรับลงทะเบียนแล้ว")
        if booking["visibility"] == "private" and user_id not in {booking["creator_id"], *booking["invited_ids"]}:
            raise ValueError("ห้องนี้เป็น private และคุณไม่ได้รับเชิญ")
        if booking["booking_type"] == "practice" and booking["visibility"] != "public":
            raise ValueError("ห้องฝึกซ้อมนี้ไม่เปิด free-join")
        if booking["booking_type"] == "legend":
            progress = conn.execute("SELECT attempts,won FROM legend_progress WHERE user_id=? AND legend_key=?", (user_id, booking["settings"].get("legend_key", ""))).fetchone()
            if progress and progress["won"]:
                raise ValueError("คุณชนะ Legend นี้แล้ว จึงลงซ้ำไม่ได้")
            if progress and progress["attempts"] >= 2:
                raise ValueError("คุณใช้สิทธิ์ลง Legend นี้ครบ 2 ครั้งแล้ว")
        if booking["booking_type"] == "debut":
            player = conn.execute("SELECT debut_attempted_week,debut_won FROM players WHERE CAST(user_id AS TEXT)=?", (user_id,)).fetchone()
            scheduled_date = datetime.fromisoformat(booking["starts_at"]).astimezone(THAI_TZ).date()
            sunday = (scheduled_date - timedelta(days=(scheduled_date.weekday() + 1) % 7)).isoformat()
            if player and player["debut_won"]:
                raise ValueError("คุณชนะ Debut แล้ว จึงลงแข่งซ้ำไม่ได้")
            if player and player["debut_attempted_week"] == sunday:
                raise ValueError("สัปดาห์นี้คุณลง Debut ไปแล้ว")
        conn.execute(
            "INSERT OR IGNORE INTO room_booking_signups (booking_id,user_id,username) VALUES (?,?,?)",
            (booking_id, user_id, username.strip() or user_id),
        )
    return get_booking(booking_id)


def claim_due_bookings() -> list[dict]:
    now_iso = datetime.now(timezone.utc).isoformat()
    claimed = []
    with database_connection() as conn:
        rows = conn.execute(
            "SELECT booking_id FROM room_bookings WHERE status='scheduled' AND starts_at<=? ORDER BY starts_at LIMIT 12",
            (now_iso,),
        ).fetchall()
        for row in rows:
            cursor = conn.execute(
                "UPDATE room_bookings SET status='creating',updated_at=CURRENT_TIMESTAMP WHERE booking_id=? AND status='scheduled'",
                (row["booking_id"],),
            )
            if cursor.rowcount:
                item = conn.execute("SELECT * FROM room_bookings WHERE booking_id=?", (row["booking_id"],)).fetchone()
                claimed.append(_decode_booking(item))
    return claimed


def mark_booking_open(booking_id: str, thread_id: str, parent_channel_id: str, guild_id: str | None = None) -> None:
    with database_connection() as conn:
        conn.execute(
            "UPDATE room_bookings SET status='open',thread_id=?,parent_channel_id=?,guild_id=?,error=NULL,updated_at=CURRENT_TIMESTAMP WHERE booking_id=?",
            (str(thread_id), str(parent_channel_id), str(guild_id or ""), str(booking_id)),
        )


def save_booking_thread(booking_id: str, thread_id: str, parent_channel_id: str, guild_id: str | None = None) -> None:
    """Persist the Discord thread as soon as it exists so retries reuse it."""
    with database_connection() as conn:
        conn.execute(
            "UPDATE room_bookings SET thread_id=?,parent_channel_id=?,guild_id=? WHERE booking_id=?",
            (str(thread_id), str(parent_channel_id), str(guild_id or ""), str(booking_id)),
        )


def claim_open_booking_for_restore(booking_id: str) -> bool:
    """Ensure only one worker at a time rebuilds the in-memory lobby for a booking."""
    with database_connection() as conn:
        cursor = conn.execute(
            "UPDATE room_bookings SET status='restoring',updated_at=CURRENT_TIMESTAMP WHERE booking_id=? AND status='open'",
            (str(booking_id),),
        )
    return cursor.rowcount == 1


def mark_booking_failed(booking_id: str, error: str) -> None:
    with database_connection() as conn:
        conn.execute(
            "UPDATE room_bookings SET status='failed',error=?,updated_at=CURRENT_TIMESTAMP WHERE booking_id=?",
            (str(error)[:500], str(booking_id)),
        )


def release_booking_claim(booking_id: str) -> None:
    """Put a due booking back in the queue when Discord is temporarily unavailable."""
    with database_connection() as conn:
        conn.execute(
            "UPDATE room_bookings SET status='scheduled',updated_at=CURRENT_TIMESTAMP WHERE booking_id=? AND status='creating'",
            (str(booking_id),),
        )


def retry_failed_bookings() -> int:
    with database_connection() as conn:
        conn.execute(
            "UPDATE room_bookings SET status='open',updated_at=CURRENT_TIMESTAMP WHERE status='restoring' AND updated_at <= datetime('now','-5 minutes')"
        )
        conn.execute(
            "UPDATE room_bookings SET status='scheduled',updated_at=CURRENT_TIMESTAMP WHERE status='creating' AND updated_at <= datetime('now','-5 minutes')"
        )
        cursor = conn.execute(
            "UPDATE room_bookings SET status='scheduled',updated_at=CURRENT_TIMESTAMP WHERE status='failed' AND updated_at <= datetime('now','-1 minute') AND starts_at >= ?",
            ((datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),),
        )
    return cursor.rowcount


def consume_scheduled_entry(user_id: str, game: dict) -> tuple[bool, str]:
    """Atomically validate and record one Legend/Debut attempt on room entry."""
    booking_type = str(game.get("booking_type") or "").lower()
    user_id = str(user_id)
    if booking_type not in {"legend", "debut"}:
        return True, ""
    with database_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        booking_id = str(game.get("booking_id") or "")
        if booking_id:
            already_entered = conn.execute(
                "SELECT 1 FROM room_booking_entries WHERE booking_id=? AND user_id=?",
                (booking_id, user_id),
            ).fetchone()
            if already_entered:
                return True, ""
        if booking_type == "legend":
            legend_key = str(game.get("legend_key") or "")
            row = conn.execute(
                "SELECT attempts,won FROM legend_progress WHERE user_id=? AND legend_key=?",
                (user_id, legend_key),
            ).fetchone()
            if row and row["won"]:
                return False, "คุณชนะ Legend นี้แล้ว จึงลงซ้ำไม่ได้"
            if row and row["attempts"] >= 2:
                return False, "คุณใช้สิทธิ์ลง Legend นี้ครบ 2 ครั้งแล้ว"
            conn.execute(
                """INSERT INTO legend_progress(user_id,legend_key,attempts,won) VALUES(?,?,1,0)
                ON CONFLICT(user_id,legend_key) DO UPDATE SET attempts=attempts+1""",
                (user_id, legend_key),
            )
            if booking_id:
                conn.execute("INSERT OR IGNORE INTO room_booking_entries(booking_id,user_id) VALUES(?,?)", (booking_id, user_id))
            return True, ""

        starts_at = datetime.fromisoformat(str(game.get("booking_starts_at") or datetime.now(timezone.utc).isoformat()))
        local_date = starts_at.astimezone(THAI_TZ).date()
        week_sunday = (local_date - timedelta(days=(local_date.weekday() + 1) % 7)).isoformat()
        row = conn.execute(
            "SELECT debut_attempted_week,debut_won FROM players WHERE CAST(user_id AS TEXT)=?",
            (user_id,),
        ).fetchone()
        if row and row["debut_won"]:
            return False, "คุณชนะ Debut แล้ว จึงลงแข่งซ้ำไม่ได้"
        if row and row["debut_attempted_week"] == week_sunday:
            return False, "สัปดาห์นี้คุณลง Debut ไปแล้ว"
        conn.execute(
            "UPDATE players SET debut_attempted_week=? WHERE CAST(user_id AS TEXT)=?",
            (week_sunday, user_id),
        )
        if booking_id:
            conn.execute("INSERT OR IGNORE INTO room_booking_entries(booking_id,user_id) VALUES(?,?)", (booking_id, user_id))
        return True, ""


def record_scheduled_winner(game: dict) -> None:
    """Persist the permanent win lock for a scheduled Legend or Debut race."""
    booking_type = str(game.get("booking_type") or "").lower()
    winner_id = str(game.get("winner_id") or "")
    winner = next(
        (player for player_id, player in (game.get("players") or {}).items() if str(player_id) == winner_id),
        None,
    )
    if not winner or winner.get("is_mob") or winner.get("using_mob_preset"):
        return
    with database_connection() as conn:
        if booking_type == "debut":
            conn.execute(
                "UPDATE players SET debut_won=1 WHERE CAST(user_id AS TEXT)=?",
                (winner_id,),
            )
        elif booking_type == "legend":
            conn.execute(
                """INSERT INTO legend_progress(user_id,legend_key,attempts,won) VALUES(?,?,0,1)
                ON CONFLICT(user_id,legend_key) DO UPDATE SET won=1""",
                (winner_id, str(game.get("legend_key") or "")),
            )


def mark_bookings_completed_for_thread(thread_id: str) -> None:
    with database_connection() as conn:
        conn.execute(
            "UPDATE room_bookings SET status='completed',updated_at=CURRENT_TIMESTAMP WHERE thread_id=? AND status='open'",
            (str(thread_id),),
        )


def has_completed_race_for_room(thread_id: str) -> bool:
    """Detect a previously finished race before rebuilding an old open booking."""
    try:
        with database_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM race_history WHERE CAST(room_id AS TEXT)=? LIMIT 1",
                (str(thread_id),),
            ).fetchone()
    except sqlite3.OperationalError:
        return False
    return row is not None
