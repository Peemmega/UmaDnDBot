import os

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.tcg.tcg_cards import CARD_DATABASE
from utils.tcg.tcg_decks import PREDEFINED_DECKS
from utils.tcg.tcg_room_manager import tcg_room_manager
from utils.tcg.tcg_visibility import sanitize_room


def _cors_origins() -> list[str]:
    default_origins = [
        "https://umabotapp-production-c99a.up.railway.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    env_origins = os.getenv("CORS_ORIGINS") or os.getenv("FRONTEND_URL") or ""
    configured_origins = [
        origin.strip().rstrip("/")
        for origin in env_origins.split(",")
        if origin.strip()
    ]
    return list(dict.fromkeys(default_origins + configured_origins))


app = FastAPI(title="Uma TCG Online Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TcgPlayerPayload(BaseModel):
    user_id: str
    username: str = "Unknown"
    avatar_url: str = ""


class TcgDeckConfirmPayload(BaseModel):
    user_id: str
    deck_id: str


class TcgLoadoutPayload(BaseModel):
    user_id: str
    deck_id: str


@app.on_event("startup")
def log_routes() -> None:
    print("TCG server started")
    print("Registered FastAPI routes:")
    for route in app.routes:
        methods = ",".join(sorted(getattr(route, "methods", []) or []))
        print(f"{methods:12} {route.path}")


@app.get("/health")
def health():
    return {"ok": True, "service": "tcg-online"}


@app.get("/tcg/cards")
def api_tcg_cards():
    return {"version": "2", "cards": CARD_DATABASE}


@app.get("/tcg/decks")
def api_tcg_decks():
    return {"version": "2", "decks": PREDEFINED_DECKS}


@app.get("/tcg/rooms")
def api_tcg_rooms():
    return {"rooms": tcg_room_manager.list_rooms()}


@app.post("/tcg/rooms/clear")
def api_tcg_clear_rooms():
    return {"success": True, "cleared": tcg_room_manager.clear_rooms()}


@app.get("/tcg/rooms/{room_id}")
def api_tcg_room(room_id: str, user_id: str = ""):
    try:
        return sanitize_room(tcg_room_manager.get_room(room_id), user_id or None)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/tcg/rooms/create")
async def api_tcg_create_room(payload: TcgPlayerPayload):
    room = tcg_room_manager.create_room(
        payload.user_id,
        payload.username,
        payload.avatar_url,
    )
    await tcg_room_manager.broadcast(room["room_id"])
    return sanitize_room(room, payload.user_id)


@app.post("/tcg/rooms/{room_id}/join")
async def api_tcg_join_room(room_id: str, payload: TcgPlayerPayload):
    try:
        room = tcg_room_manager.join_room(
            room_id,
            payload.user_id,
            payload.username,
            payload.avatar_url,
        )
        await tcg_room_manager.broadcast(room_id)
        return sanitize_room(room, payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/tcg/rooms/{room_id}/leave")
async def api_tcg_leave_room(room_id: str, payload: TcgPlayerPayload):
    try:
        room = tcg_room_manager.leave_room(room_id, payload.user_id)
        if room_id in tcg_room_manager.rooms:
            await tcg_room_manager.broadcast(room_id)
        return sanitize_room(room, payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/tcg/rooms/{room_id}/start")
async def api_tcg_start_room(room_id: str, payload: TcgPlayerPayload):
    try:
        room = tcg_room_manager.start_deck_select(room_id, payload.user_id)
        await tcg_room_manager.broadcast(room_id)
        return sanitize_room(room, payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/tcg/rooms/{room_id}/deck/confirm")
async def api_tcg_confirm_deck(room_id: str, payload: TcgDeckConfirmPayload):
    try:
        room = tcg_room_manager.confirm_deck(room_id, payload.user_id, payload.deck_id)
        await tcg_room_manager.broadcast(room_id)
        return sanitize_room(room, payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/tcg/rooms/{room_id}/loadout")
async def api_tcg_loadout(room_id: str, payload: TcgLoadoutPayload):
    try:
        room = tcg_room_manager.confirm_loadout(
            room_id, payload.user_id, payload.deck_id
        )
        await tcg_room_manager.broadcast(room_id)
        return sanitize_room(room, payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.websocket("/ws/tcg/{room_id}")
async def websocket_tcg_room(websocket: WebSocket, room_id: str, user_id: str):
    try:
        await tcg_room_manager.connect(room_id, user_id, websocket)
        await tcg_room_manager.broadcast(room_id)
    except ValueError:
        return
    try:
        while True:
            message = await websocket.receive_json()
            try:
                room = (
                    tcg_room_manager.leave_room(room_id, user_id)
                    if message.get("type") == "LEAVE_ROOM"
                    else tcg_room_manager.apply_action(room_id, user_id, message)
                )
                await tcg_room_manager.broadcast(room["room_id"])
            except ValueError as exc:
                await websocket.send_json({"type": "ERROR", "message": str(exc)})
    except WebSocketDisconnect:
        tcg_room_manager.disconnect(room_id, user_id, websocket)
