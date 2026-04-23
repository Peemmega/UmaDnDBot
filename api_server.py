from fastapi import FastAPI, HTTPException
from utils.database import get_player

app = FastAPI()

@app.get("/player/{user_id}")
def api_get_player(user_id: int):
    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player