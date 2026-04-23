from fastapi import FastAPI, HTTPException
from utils.database import get_player
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
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

def get_connection():
    return sqlite3.connect("uma_database.db")

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

    cur.execute("""
        SELECT speed, stamina, power, gut, wit, stats_point
        FROM players
        WHERE user_id = ?
    """, (payload.user_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")

    old_speed, old_stamina, old_power, old_gut, old_wit, old_stats_point = row

    spent = (
        (payload.speed - old_speed)
        + (payload.stamina - old_stamina)
        + (payload.power - old_power)
        + (payload.gut - old_gut)
        + (payload.wit - old_wit)
    )

    if spent < 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot decrease below saved stats")

    if spent > old_stats_point:
        conn.close()
        raise HTTPException(status_code=400, detail="Not enough stats points")

    new_stats_point = old_stats_point - spent

    if payload.stats_point != new_stats_point:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid stats_point value")

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
        new_stats_point,
        payload.user_id,
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Stats updated successfully",
        "player": {
            "speed": payload.speed,
            "stamina": payload.stamina,
            "power": payload.power,
            "gut": payload.gut,
            "wit": payload.wit,
            "stats_point": new_stats_point,
        }
    }