import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional
from utils.zone.zone_preset import ZONE_FIELDS, DEFAULT_ZONE_IMAGE, ZONE_POINT_COST, normalize_zone_build
import json
from utils.profile_images import resolve_public_url
from utils.icon_presets import USING_MAIN_EMOJIS

DB_PATH = os.getenv("PLAYER_DB_PATH", "/app/data/player.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)  # ⬅️ เพิ่ม timeout
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")  # ⬅️ แก้ lock ได้ดีที่สุด
    conn.execute("PRAGMA synchronous=NORMAL;")

    return conn


@contextmanager
def database_connection() -> Iterator[sqlite3.Connection]:
    """Provide a connection that always commits successful writes and closes."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,

        speed INTEGER NOT NULL DEFAULT 1,
        stamina INTEGER NOT NULL DEFAULT 1,
        power INTEGER NOT NULL DEFAULT 1,
        gut INTEGER NOT NULL DEFAULT 1,
        wit INTEGER NOT NULL DEFAULT 1,

        turf INTEGER NOT NULL DEFAULT 1,
        dirt INTEGER NOT NULL DEFAULT 1,

        sprint INTEGER NOT NULL DEFAULT 1,
        mile INTEGER NOT NULL DEFAULT 1,
        medium INTEGER NOT NULL DEFAULT 1,
        long INTEGER NOT NULL DEFAULT 1,

        front INTEGER NOT NULL DEFAULT 1,
        pace INTEGER NOT NULL DEFAULT 1,
        late INTEGER NOT NULL DEFAULT 1,
        end_style INTEGER NOT NULL DEFAULT 1,

        stats_point INTEGER NOT NULL DEFAULT 5,
        fans INTEGER NOT NULL DEFAULT 1,
        skill_point INTEGER NOT NULL DEFAULT 12,

        skill_slot_1 TEXT,
        skill_slot_2 TEXT,
        skill_slot_3 TEXT,
        skill_slot_4 TEXT,

        profile_image_url TEXT,
        profile_image_updated_at INTEGER,

        zone_name TEXT DEFAULT 'Default Zone',
        zone_image_url TEXT DEFAULT '{DEFAULT_ZONE_IMAGE}',
        zone_points INTEGER NOT NULL DEFAULT 5,
        zone_build TEXT DEFAULT ('{{}}')
    )
    """)
    
    zone_columns = [
        ("zone_name", "TEXT DEFAULT 'Default Zone'"),
        ("zone_image_url", f"TEXT DEFAULT '{DEFAULT_ZONE_IMAGE}'"),
        ("zone_points", "INTEGER NOT NULL DEFAULT 5"),
        ("zone_build", "TEXT DEFAULT ('{}')")
    ]

    for col, col_type in zone_columns:
        try:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # migration กันกรณี table เก่ามีอยู่แล้ว
    for col in ["skill_slot_1", "skill_slot_2", "skill_slot_3", "skill_slot_4"]:
        try:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} TEXT")
        except Exception:
            pass

    for col, col_type in [
        ("profile_image_url", "TEXT"),
        ("profile_image_updated_at", "INTEGER"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # Uma Coin was replaced by Fans. Keep the legacy column untouched for
    # SQLite compatibility, but expose and maintain only the new column.
    player_columns = {row["name"] for row in cursor.execute("PRAGMA table_info(players)").fetchall()}
    if "fans" not in player_columns:
        cursor.execute("ALTER TABLE players ADD COLUMN fans INTEGER NOT NULL DEFAULT 1")
        if "uma_coin" in player_columns:
            cursor.execute(
                """
                UPDATE players
                SET fans = CASE
                    WHEN COALESCE(uma_coin, 0) > 0 THEN uma_coin
                    ELSE 1
                END
                """
            )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mailbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        reward_type TEXT,
        reward_amount INTEGER DEFAULT 0,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trainer_teams (
        trainer_user_id TEXT NOT NULL,
        trainee_user_id TEXT NOT NULL UNIQUE,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (trainer_user_id, trainee_user_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile_presets (
        user_id TEXT NOT NULL,
        profile_type TEXT NOT NULL,
        name TEXT NOT NULL,
        image_url TEXT NOT NULL DEFAULT '',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, profile_type)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS team_invitations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_user_id TEXT NOT NULL,
        trainee_user_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        responded_at TEXT
    )
    """)

    mailbox_columns = {row["name"] for row in cursor.execute("PRAGMA table_info(mailbox)").fetchall()}
    if "profile_type" not in mailbox_columns:
        cursor.execute("ALTER TABLE mailbox ADD COLUMN profile_type TEXT NOT NULL DEFAULT 'trainee'")
    if "invitation_id" not in mailbox_columns:
        cursor.execute("ALTER TABLE mailbox ADD COLUMN invitation_id INTEGER")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS race_rankings (
        stage_key TEXT NOT NULL,
        user_id TEXT NOT NULL,
        best_score INTEGER NOT NULL,
        style TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (stage_key, user_id)
    )
    """)

    conn.commit()
    conn.close()


def upsert_race_ranking(stage_key: str, user_id, score: int, style: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT best_score
    FROM race_rankings
    WHERE stage_key = ? AND user_id = ?
    """, (stage_key, str(user_id)))
    row = cursor.fetchone()

    if row is not None and int(row["best_score"]) >= int(score):
        conn.close()
        return False

    cursor.execute("""
    INSERT INTO race_rankings (stage_key, user_id, best_score, style, updated_at)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(stage_key, user_id) DO UPDATE SET
        best_score = excluded.best_score,
        style = excluded.style,
        updated_at = CURRENT_TIMESTAMP
    """, (stage_key, str(user_id), int(score), str(style)))

    conn.commit()
    conn.close()
    return True


def record_race_rankings(stage_key: str, ranked_players) -> int:
    updated_count = 0

    for user_id, info in ranked_players:
        if str(user_id).startswith("mob_") or info.get("is_mob"):
            continue

        updated = upsert_race_ranking(
            stage_key=stage_key,
            user_id=user_id,
            score=info.get("score", 0),
            style=info.get("style", "-"),
        )
        if updated:
            updated_count += 1

    return updated_count


def clear_race_rankings(stage_key: str | None = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    if stage_key:
        cursor.execute("DELETE FROM race_rankings WHERE stage_key = ?", (stage_key,))
    else:
        cursor.execute("DELETE FROM race_rankings")

    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def reset_all_data() -> dict[str, int]:
    """Remove every persisted player and gameplay record without dropping the schema."""
    tables = (
        "mailbox",
        "trainer_teams",
        "profile_presets",
        "team_invitations",
        "race_rankings",
        "players",
    )
    deleted_counts: dict[str, int] = {}

    with database_connection() as conn:
        cursor = conn.cursor()
        for table_name in tables:
            cursor.execute(f"DELETE FROM {table_name}")
            deleted_counts[table_name] = cursor.rowcount

    return deleted_counts


def get_race_rankings(stage_key: str, limit: int = 10) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        r.stage_key,
        r.user_id,
        COALESCE(p.username, r.user_id) AS username,
        r.best_score,
        r.style,
        r.updated_at
    FROM race_rankings r
    LEFT JOIN players p
        ON CAST(p.user_id AS TEXT) = r.user_id
    WHERE r.stage_key = ?
    ORDER BY r.best_score DESC, r.updated_at ASC
    LIMIT ?
    """, (stage_key, limit))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "stage_key": row["stage_key"],
            "user_id": row["user_id"],
            "username": row["username"],
            "best_score": row["best_score"],
            "style": row["style"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]

def add_mail(conn, user_id, title, message, reward_type, reward_amount):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mailbox (user_id, title, message, reward_type, reward_amount)
        VALUES (?, ?, ?, ?, ?)
    """, (str(user_id), title, message, reward_type, reward_amount))


def get_available_trainees(trainer_user_id: str) -> list[dict]:
    conn = get_connection()
    same_account_filter = "AND CAST(p.user_id AS TEXT) <> ?" if USING_MAIN_EMOJIS else ""
    params = (str(trainer_user_id),) if USING_MAIN_EMOJIS else ()
    rows = conn.execute(f"""
        SELECT CAST(p.user_id AS TEXT) AS user_id, p.username, p.profile_image_url, p.fans
        FROM players p
        LEFT JOIN trainer_teams t ON t.trainee_user_id = CAST(p.user_id AS TEXT)
        WHERE p.profile_image_url IS NOT NULL AND TRIM(p.profile_image_url) <> ''
          AND t.trainee_user_id IS NULL
          {same_account_filter}
        ORDER BY p.username COLLATE NOCASE
    """, params).fetchall()
    conn.close()
    return [{"user_id": row["user_id"], "username": row["username"], "image_url": resolve_public_url(row["profile_image_url"]), "fans": row["fans"]} for row in rows]


def get_trainer_team(trainer_user_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT CAST(p.user_id AS TEXT) AS user_id, p.username, p.profile_image_url, p.fans
        FROM trainer_teams t JOIN players p ON CAST(p.user_id AS TEXT) = t.trainee_user_id
        WHERE t.trainer_user_id = ? ORDER BY t.joined_at ASC
    """, (str(trainer_user_id),)).fetchall()
    conn.close()
    return [{"user_id": row["user_id"], "username": row["username"], "image_url": resolve_public_url(row["profile_image_url"]), "fans": row["fans"]} for row in rows]


def get_trainee_trainer(trainee_user_id: str) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("""
        SELECT t.trainer_user_id AS user_id, preset.name, preset.image_url
        FROM trainer_teams t
        JOIN profile_presets preset
          ON preset.user_id = t.trainer_user_id AND preset.profile_type = 'trainer'
        WHERE t.trainee_user_id = ?
    """, (str(trainee_user_id),)).fetchone()
    conn.close()
    if not row:
        return None
    return {"user_id": row["user_id"], "username": row["name"], "image_url": row["image_url"]}


def save_profile_preset(user_id: str, profile_type: str, name: str, image_url: str) -> None:
    if profile_type not in {"trainer", "npc"}:
        raise ValueError("Only trainer and npc presets are supported")
    with database_connection() as conn:
        conn.execute("""
            INSERT INTO profile_presets (user_id, profile_type, name, image_url, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, profile_type) DO UPDATE SET
              name = excluded.name, image_url = excluded.image_url, updated_at = CURRENT_TIMESTAMP
        """, (str(user_id), profile_type, name.strip() or profile_type.title(), image_url or ""))


def list_uploaded_profile_summaries() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT user_id, profile_type, name, image_url FROM profile_presets
        WHERE TRIM(image_url) <> '' ORDER BY name COLLATE NOCASE
    """).fetchall()
    conn.close()
    return [{"id": f"{row['user_id']}:{row['profile_type']}", "name": row["name"], "image_url": row["image_url"], "type": row["profile_type"].title()} for row in rows]


def create_team_invitation(trainer_user_id: str, trainee_user_id: str) -> int:
    with database_connection() as conn:
        trainee = conn.execute("SELECT username FROM players WHERE CAST(user_id AS TEXT) = ?", (str(trainee_user_id),)).fetchone()
        trainer = conn.execute("""
            SELECT COALESCE(NULLIF(preset.name, ''), player.username) AS username
            FROM players player
            LEFT JOIN profile_presets preset
              ON preset.user_id = CAST(player.user_id AS TEXT) AND preset.profile_type = 'trainer'
            WHERE CAST(player.user_id AS TEXT) = ?
        """, (str(trainer_user_id),)).fetchone()
        if not trainee or not trainer:
            raise ValueError("Profile not found")
        if conn.execute("SELECT 1 FROM trainer_teams WHERE trainee_user_id = ?", (str(trainee_user_id),)).fetchone():
            raise ValueError("Trainee already has a trainer")
        existing = conn.execute("SELECT id FROM team_invitations WHERE trainer_user_id = ? AND trainee_user_id = ? AND status = 'pending'", (str(trainer_user_id), str(trainee_user_id))).fetchone()
        if existing:
            raise ValueError("Invitation is already pending")
        cur = conn.execute("INSERT INTO team_invitations (trainer_user_id, trainee_user_id) VALUES (?, ?)", (str(trainer_user_id), str(trainee_user_id)))
        invitation_id = cur.lastrowid
        conn.execute("INSERT INTO mailbox (user_id, profile_type, invitation_id, title, message) VALUES (?, 'trainee', ?, ?, ?)", (str(trainee_user_id), invitation_id, "Team invitation", f"{trainer['username']} invited you to join their team."))
        return invitation_id


def respond_to_team_invitation(invitation_id: int, trainee_user_id: str, accepted: bool) -> None:
    with database_connection() as conn:
        invite = conn.execute("SELECT trainer_user_id, trainee_user_id, status FROM team_invitations WHERE id = ?", (invitation_id,)).fetchone()
        if not invite or invite["trainee_user_id"] != str(trainee_user_id) or invite["status"] != "pending":
            raise ValueError("Invitation is no longer available")
        status = "accepted" if accepted else "declined"
        conn.execute("UPDATE team_invitations SET status = ?, responded_at = CURRENT_TIMESTAMP WHERE id = ?", (status, invitation_id))
        if accepted:
            conn.execute("INSERT INTO trainer_teams (trainer_user_id, trainee_user_id) VALUES (?, ?)", (invite["trainer_user_id"], str(trainee_user_id)))
        trainee_name = conn.execute("SELECT username FROM players WHERE CAST(user_id AS TEXT) = ?", (str(trainee_user_id),)).fetchone()["username"]
        conn.execute("INSERT INTO mailbox (user_id, profile_type, title, message) VALUES (?, 'trainer', ?, ?)", (invite["trainer_user_id"], "Team invitation response", f"{trainee_name} {'joined your team' if accepted else 'declined your invitation'}."))

def reset_all_zone_data():
    conn = get_connection()
    cursor = conn.cursor()

    default_build = {
        "flat": 0,
        "add_dkh": 0,
        "cap_floor": 0,
        "self_heal_stamina": 0,
        "modify_current_speed": 0,
    }

    cursor.execute("""
    UPDATE players
    SET zone_build = ?,
        zone_points = 5
    """, (json.dumps(default_build),))

    conn.commit()
    conn.close()

def add_player_aptitude(user_id, aptitude_field, amount):
    valid_fields = {
        "turf", "dirt",
        "sprint", "mile", "medium", "long",
        "front", "pace", "late", "end_style",
    }

    if aptitude_field not in valid_fields:
        return False, "ไม่พบ aptitude นี้"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
    UPDATE players
    SET {aptitude_field} = COALESCE({aptitude_field}, 0) + ?
    WHERE user_id = ?
    """, (amount, user_id))

    add_mail(
        conn,
        user_id,
        "เลื่อนความถนัด",
        f"คุณได้รับการเลื่อนระดับ {aptitude_field}",
        "aptitude",
        1
    )

    conn.commit()
    conn.close()
    return True, f"เพิ่ม {aptitude_field} +{amount} สำเร็จ"

def add_player_stats_point(user_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET stats_point = COALESCE(stats_point, 0) + ?
    WHERE user_id = ?
    """, (amount, user_id))

    if (amount > 0):
        add_mail(
            conn,
            user_id,
            "ได้รับ Stats Point",
            "คุณได้รับ stat points",
            "stats_point",
            amount
        )
    else:
        add_mail(
            conn,
            user_id,
            "ได้รับ Stats Point",
            "คุณถูดลด stat points",
            "stats_point",
            amount
        )

    conn.commit()
    conn.close()
    return True, f"เพิ่ม stats_point +{amount} สำเร็จ"

def add_player_skill_point(user_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET skill_point = COALESCE(skill_point, 0) + ?
    WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()
    return True, f"เพิ่ม skill_point +{amount} สำเร็จ"

def set_player_zone_build(user_id: int, build: dict) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    safe_build = normalize_zone_build(build)

    cursor.execute("""
    UPDATE players
    SET zone_build = ?
    WHERE user_id = ?
    """, (json.dumps(safe_build), user_id))

    conn.commit()
    conn.close()

def set_player_zone_name(user_id: int, zone_name: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET zone_name = ?
    WHERE user_id = ?
    """, (zone_name, user_id))

    conn.commit()
    conn.close()

def set_player_zone_image_url(user_id: int, image_url: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET zone_image_url = ?
    WHERE user_id = ?
    """, (image_url, user_id))

    conn.commit()
    conn.close()


def set_player_profile_image(user_id: int | str, profile_image_url: str, updated_at: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET profile_image_url = ?,
        profile_image_updated_at = ?
    WHERE CAST(user_id AS TEXT) = ?
    """, (profile_image_url, updated_at, str(user_id)))

    conn.commit()
    conn.close()

def set_player_skill_slot(user_id: int, slot: int, skill_id: str):
    if slot not in (1, 2, 3, 4):
        return False, "slot ต้องเป็น 1-4"

    conn = get_connection()
    cursor = conn.cursor()

    column = f"skill_slot_{slot}"
    cursor.execute(
        f"UPDATE players SET {column} = ? WHERE user_id = ?",
        (skill_id, user_id)
    )

    conn.commit()
    conn.close()
    return True, f"ติดตั้งสกิล {skill_id} ลงช่อง {slot} เรียบร้อย"

def clear_player_skill_slot(user_id: int, slot: int):
    if slot not in (1, 2, 3, 4):
        return False, "slot ต้องเป็น 1-4"

    conn = get_connection()
    cursor = conn.cursor()

    column = f"skill_slot_{slot}"
    cursor.execute(
        f"UPDATE players SET {column} = NULL WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()
    return True, f"ลบสกิลในช่อง {slot} เรียบร้อย"

def get_player_skill_slots(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT skill_slot_1, skill_slot_2, skill_slot_3, skill_slot_4
    FROM players
    WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "slot_1": row[0],
        "slot_2": row[1],
        "slot_3": row[2],
        "slot_4": row[3],
    }

def create_player(user_id: int, username: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO players (
        user_id, username,
        speed, stamina, power, gut, wit,
        turf, dirt,
        sprint, mile, medium, long,
        front, pace, late, end_style,
        stats_point, fans, skill_point
    )
    VALUES (
        ?, ?,
        1, 1, 1, 1, 1,
        1, 1,
        1, 1, 1, 1,
        1, 1, 1, 1,
        12, 1, 0
    )
    """, (user_id, username))

    conn.commit()
    conn.close()

def remove_player_stat(user_id: int, stat_name: str, amount: int = 1) -> dict:
    valid_stats = {"speed", "stamina", "power", "gut", "wit"}

    if stat_name not in valid_stats:
        raise ValueError("Invalid stat name")

    player = get_player(user_id)
    if player is None:
        raise ValueError("Player not found")

    if player[stat_name] - amount < 1:
        raise ValueError("Stat cannot go below 1")

    conn = get_connection()
    cursor = conn.cursor()

    new_stat_value = player[stat_name] - amount
    new_stats_point = player["stats_point"] + amount

    cursor.execute(
        f"""
        UPDATE players
        SET {stat_name} = ?, stats_point = ?
        WHERE user_id = ?
        """,
        (new_stat_value, new_stats_point, user_id)
    )

    conn.commit()
    conn.close()

    return get_player(user_id)

def add_player_stat(user_id: int, stat_name: str, amount: int = 1) -> dict:
    valid_stats = {"speed", "stamina", "power", "gut", "wit"}

    if stat_name not in valid_stats:
        raise ValueError("Invalid stat name")

    player = get_player(user_id)
    if player is None:
        raise ValueError("Player not found")

    if player["stats_point"] < amount:
        raise ValueError("Not enough stats points")

    if player[stat_name] + amount > MAX_CORE_STAT:
        raise ValueError(f"{stat_name} cannot exceed {MAX_CORE_STAT}")

    conn = get_connection()
    cursor = conn.cursor()

    new_stat_value = player[stat_name] + amount
    new_stats_point = player["stats_point"] - amount

    cursor.execute(
        f"""
        UPDATE players
        SET {stat_name} = ?, stats_point = ?
        WHERE user_id = ?
        """,
        (new_stat_value, new_stats_point, user_id)
    )

    conn.commit()
    conn.close()

    return get_player(user_id)

def get_player_skill_in_slot(user_id: int, slot: int):
    if slot not in (1, 2, 3, 4):
        return None

    conn = get_connection()
    cursor = conn.cursor()

    column = f"skill_slot_{slot}"
    cursor.execute(
        f"SELECT {column} FROM players WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return row[0]

def get_player(user_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        user_id, username,
        speed, stamina, power, gut, wit,
        turf, dirt,
        sprint, mile, medium, long,
        front, pace, late, end_style,
        stats_point, fans, skill_point,
        profile_image_url, profile_image_updated_at,
        zone_name, zone_image_url, zone_points, zone_build
    FROM players
    WHERE CAST(user_id AS TEXT) = ?
    """, (str(user_id),))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    raw_zone_build = json.loads(row[25] or "{}")
    zone_build = normalize_zone_build(raw_zone_build)

    if raw_zone_build != zone_build:
        cursor.execute(
            """
            UPDATE players
            SET zone_build = ?
            WHERE CAST(user_id AS TEXT) = ?
            """,
            (json.dumps(zone_build), str(user_id)),
        )
        conn.commit()

    conn.close()

    return {
        "user_id": row[0],
        "username": row[1],

        "speed": row[2],
        "stamina": row[3],
        "power": row[4],
        "gut": row[5],
        "wit": row[6],

        "turf": row[7],
        "dirt": row[8],

        "sprint": row[9],
        "mile": row[10],
        "medium": row[11],
        "long": row[12],

        "front": row[13],
        "pace": row[14],
        "late": row[15],
        "end_style": row[16],

        "stats_point": row[17],
        "fans": row[18],
        "skill_point": row[19],
        "profile_image_url": resolve_public_url(row[20]),
        "profile_image_updated_at": row[21],

        "zone": {
            "name": row[22],
            "image_url": row[23],
            "points": row[24],
            "build": zone_build,
        }
    }


def get_player_summary(user_id: int | str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    columns = {row["name"] for row in cursor.execute("PRAGMA table_info(players)").fetchall()}
    has_profile_image = "profile_image_url" in columns

    if has_profile_image:
        cursor.execute(
            """
            SELECT user_id, username, profile_image_url
            FROM players
            WHERE CAST(user_id AS TEXT) = ?
            """,
            (str(user_id),),
        )
    else:
        cursor.execute(
            """
            SELECT user_id, username
            FROM players
            WHERE CAST(user_id AS TEXT) = ?
            """,
            (str(user_id),),
        )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": str(row["user_id"]),
        "name": row["username"],
        "image_url": resolve_public_url(row["profile_image_url"]) if has_profile_image else "",
        "type": "Player",
    }


def list_player_summaries() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    columns = {row["name"] for row in cursor.execute("PRAGMA table_info(players)").fetchall()}
    has_profile_image = "profile_image_url" in columns

    if has_profile_image:
        cursor.execute(
            """
            SELECT user_id, username, profile_image_url
            FROM players
            WHERE username IS NOT NULL AND TRIM(username) <> ''
            ORDER BY username COLLATE NOCASE ASC, user_id ASC
            """
        )
    else:
        cursor.execute(
            """
            SELECT user_id, username
            FROM players
            WHERE username IS NOT NULL AND TRIM(username) <> ''
            ORDER BY username COLLATE NOCASE ASC, user_id ASC
            """
        )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": str(row["user_id"]),
            "name": row["username"],
            "image_url": resolve_public_url(row["profile_image_url"]) if has_profile_image else "",
            "type": "Player",
        }
        for row in rows
    ]

def set_all_aptitude(user_id: int, value: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET
        turf = ?,
        dirt = ?,
        sprint = ?,
        mile = ?,
        medium = ?,
        long = ?,
        front = ?,
        pace = ?,
        late = ?,
        end_style = ?
    WHERE user_id = ?
    """, (
        value, value,
        value, value, value, value,
        value, value, value, value,
        user_id
    ))

    conn.commit()
    conn.close()

def reset_zone_build(zone: dict) -> None:
    if "build" not in zone or not isinstance(zone["build"], dict):
        zone["build"] = {}

    for key in ZONE_POINT_COST.keys():
        zone["build"][key] = 0

    for legacy_key in ("floor", "cap"):
        zone["build"].pop(legacy_key, None)

def ensure_player(user_id: int, username: str) -> dict:
    player = get_player(user_id)
    if player is None:
        create_player(user_id, username)
        player = get_player(user_id)

    return player

def update_player_username(user_id: str, username: str):
    player = get_player(user_id)
    if player is None:
        raise ValueError("Player not found")
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET username = ?
    WHERE CAST(user_id AS TEXT) = ?
    """, (username, str(user_id)))

    if cursor.rowcount == 0:
        conn.close()
        raise ValueError("Player not found")

    conn.commit()
    conn.close()


CORE_STAT_FIELDS = ("speed", "stamina", "power", "gut", "wit")
MAX_CORE_STAT = 8


def update_player_stat_pool(user_id: int | str, *, stats: dict[str, int], stats_point: int) -> dict:
    """Replace core stats while preserving the player's total stat-point pool.

    Keeping this rule next to the persistence code ensures every future caller
    gets the same validation and avoids partially-updated player records.
    """
    if set(stats) != set(CORE_STAT_FIELDS):
        raise ValueError("Stats must contain speed, stamina, power, gut, and wit")
    if any(not isinstance(value, int) or not 1 <= value <= MAX_CORE_STAT for value in stats.values()):
        raise ValueError(f"Each stat must be an integer from 1 to {MAX_CORE_STAT}")
    if not isinstance(stats_point, int) or stats_point < 0:
        raise ValueError("Stats point must be a non-negative integer")

    with database_connection() as conn:
        row = conn.execute(
            """
            SELECT speed, stamina, power, gut, wit, stats_point
            FROM players
            WHERE CAST(user_id AS TEXT) = ?
            """,
            (str(user_id),),
        ).fetchone()
        if row is None:
            raise LookupError("Player not found")

        old_total = sum(row[field] for field in (*CORE_STAT_FIELDS, "stats_point"))
        new_total = sum(stats.values()) + stats_point
        if old_total != new_total:
            raise ValueError("Invalid total stat pool")

        conn.execute(
            """
            UPDATE players
            SET speed = ?, stamina = ?, power = ?, gut = ?, wit = ?, stats_point = ?
            WHERE CAST(user_id AS TEXT) = ?
            """,
            (*[stats[field] for field in CORE_STAT_FIELDS], stats_point, str(user_id)),
        )

    return {**stats, "stats_point": stats_point}

def update_player_stats(
    user_id: int,
    *,
    speed: Optional[int] = None,
    stamina: Optional[int] = None,
    power: Optional[int] = None,
    gut: Optional[int] = None,
    wit: Optional[int] = None,

    turf: Optional[int] = None,
    dirt: Optional[int] = None,

    sprint: Optional[int] = None,
    mile: Optional[int] = None,
    medium: Optional[int] = None,
    long: Optional[int] = None,

    front: Optional[int] = None,
    pace: Optional[int] = None,
    late: Optional[int] = None,
    end_style: Optional[int] = None,

    stats_point: Optional[int] = None,
    fans: Optional[int] = None,
    skill_point: Optional[int] = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    current = get_player(user_id)
    if current is None:
        conn.close()
        raise ValueError("Player not found")

    new_speed = current["speed"] if speed is None else speed
    new_stamina = current["stamina"] if stamina is None else stamina
    new_power = current["power"] if power is None else power
    new_gut = current["gut"] if gut is None else gut
    new_wit = current["wit"] if wit is None else wit

    if any(not isinstance(value, int) or not 1 <= value <= MAX_CORE_STAT for value in (new_speed, new_stamina, new_power, new_gut, new_wit)):
        conn.close()
        raise ValueError(f"Core stats must be integers from 1 to {MAX_CORE_STAT}")

    new_turf = current["turf"] if turf is None else turf
    new_dirt = current["dirt"] if dirt is None else dirt

    new_sprint = current["sprint"] if sprint is None else sprint
    new_mile = current["mile"] if mile is None else mile
    new_medium = current["medium"] if medium is None else medium
    new_long = current["long"] if long is None else long

    new_front = current["front"] if front is None else front
    new_pace = current["pace"] if pace is None else pace
    new_late = current["late"] if late is None else late
    new_end_style = current["end_style"] if end_style is None else end_style

    new_stats_point = current["stats_point"] if stats_point is None else stats_point
    new_fans = current["fans"] if fans is None else fans
    new_skill_point = current["skill_point"] if skill_point is None else skill_point

    cursor.execute("""
    UPDATE players
    SET
        speed = ?,
        stamina = ?,
        power = ?,
        gut = ?,
        wit = ?,
        turf = ?,
        dirt = ?,
        sprint = ?,
        mile = ?,
        medium = ?,
        long = ?,
        front = ?,
        pace = ?,
        late = ?,
        end_style = ?,
        stats_point = ?,
        fans = ?,
        skill_point = ?
    WHERE user_id = ?
    """, (
        new_speed,
        new_stamina,
        new_power,
        new_gut,
        new_wit,
        new_turf,
        new_dirt,
        new_sprint,
        new_mile,
        new_medium,
        new_long,
        new_front,
        new_pace,
        new_late,
        new_end_style,
        new_stats_point,
        new_fans,
        new_skill_point,
        user_id
    ))

    conn.commit()
    conn.close()
