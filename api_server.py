from fastapi import FastAPI, HTTPException
from utils.database import get_player, get_connection, ensure_player
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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