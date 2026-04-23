import os
from fastapi import FastAPI, HTTPException, Header
from utils.database import get_player

app = FastAPI()
API_KEY = os.getenv("API_KEY")


def verify_api_key(x_api_key: str | None):
    if not API_KEY:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/player/{user_id}")
def api_get_player(user_id: int, x_api_key: str | None = Header(default=None)):
    verify_api_key(x_api_key)

    player = get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player