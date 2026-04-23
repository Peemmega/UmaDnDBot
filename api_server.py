import os
import sqlite3

from fastapi import FastAPI, HTTPException
from utils.database import get_player
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
def api_get_player(user_id: int):
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

DB_PATH = "/app/data/player.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

class UpdateStatsPayload(BaseModel):
    user_id: int
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

    try:
        cur.execute("""
            SELECT speed, stamina, power, gut, wit, stats_point
            FROM players
            WHERE user_id = ?
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
            WHERE user_id = ?
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