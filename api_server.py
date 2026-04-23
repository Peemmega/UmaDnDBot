from fastapi import FastAPI, HTTPException
from utils.database import get_player
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://umabotapp-production-c99a.up.railway.app",
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