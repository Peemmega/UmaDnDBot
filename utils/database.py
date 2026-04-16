import os
import sqlite3
from typing import Optional

DB_PATH = "data/player.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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

        stats_point INTEGER NOT NULL DEFAULT 12,
        uma_coin INTEGER NOT NULL DEFAULT 0,
        skill_point INTEGER NOT NULL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


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
        stats_point, uma_coin, skill_point
    )
    VALUES (
        ?, ?,
        1, 1, 1, 1, 1,
        1, 1,
        1, 1, 1, 1,
        1, 1, 1, 1,
        12, 0, 0
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
        stats_point, uma_coin, skill_point
    FROM players
    WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

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
        "uma_coin": row[18],
        "skill_point": row[19],
    }


def ensure_player(user_id: int, username: str) -> dict:
    player = get_player(user_id)
    if player is None:
        create_player(user_id, username)
        player = get_player(user_id)

    return player

def update_player_username(user_id: int, username: str):
    player = get_player(user_id)
    if player is None:
        raise ValueError("Player not found")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE players
    SET username = ?
    WHERE user_id = ?
    """, (username, user_id))

    conn.commit()
    conn.close()

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
    uma_coin: Optional[int] = None,
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
    new_uma_coin = current["uma_coin"] if uma_coin is None else uma_coin
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
        uma_coin = ?,
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
        new_uma_coin,
        new_skill_point,
        user_id
    ))

    conn.commit()
    conn.close()