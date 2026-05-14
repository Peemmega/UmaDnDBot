import secrets
import time
from typing import Any

from fastapi import WebSocket

from .tcg_decks import DECKS_BY_ID
from .tcg_state import add_carrot, draw_cards, move_card, setup_game_state, shuffle_deck, tap_card, untap_all
from .tcg_visibility import sanitize_room


class TcgRoomManager:
    def __init__(self):
        self.rooms: dict[str, dict[str, Any]] = {}
        self.connections: dict[str, dict[str, WebSocket]] = {}

    def _now(self) -> int:
        return int(time.time())

    def _new_room_id(self) -> str:
        return secrets.token_hex(4)

    def list_rooms(self) -> list[dict]:
        return [
            {
                "room_id": room["room_id"],
                "room_code": room["room_code"],
                "host_id": room["host_id"],
                "phase": room["phase"],
                "player_count": len(room["players"]),
                "max_players": 2,
                "players": room["players"],
                "created_at": room["created_at"],
                "updated_at": room["updated_at"],
            }
            for room in sorted(self.rooms.values(), key=lambda item: item["updated_at"], reverse=True)
            if room["phase"] != "ended"
        ]

    def create_room(self, user_id: str, username: str, avatar_url: str = "") -> dict:
        room_id = self._new_room_id()
        room = {
            "room_id": room_id,
            "room_code": room_id.upper(),
            "host_id": str(user_id),
            "phase": "waiting",
            "players": {
                "player1": {"user_id": str(user_id), "username": username, "avatar_url": avatar_url, "is_host": True},
                "player2": None,
            },
            "player_slots": {str(user_id): "player1"},
            "deck_confirmed": {"player1": None, "player2": None},
            "game_state": None,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        self.rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> dict:
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError("Room not found")
        return room

    def join_room(self, room_id: str, user_id: str, username: str, avatar_url: str = "") -> dict:
        room = self.get_room(room_id)
        user_id = str(user_id)
        if user_id in room["player_slots"]:
            return room
        if room["players"]["player2"] is not None:
            raise ValueError("Room is full")
        if room["phase"] != "waiting":
            raise ValueError("Room already started")
        room["players"]["player2"] = {"user_id": user_id, "username": username, "avatar_url": avatar_url, "is_host": False}
        room["player_slots"][user_id] = "player2"
        room["updated_at"] = self._now()
        return room

    def leave_room(self, room_id: str, user_id: str) -> dict:
        room = self.get_room(room_id)
        user_id = str(user_id)
        slot = room["player_slots"].pop(user_id, None)
        if slot:
            room["players"][slot] = None
        if user_id == room["host_id"] or not any(room["players"].values()):
            room["phase"] = "ended"
        room["updated_at"] = self._now()
        return room

    def start_deck_select(self, room_id: str, user_id: str) -> dict:
        room = self.get_room(room_id)
        if str(user_id) != room["host_id"]:
            raise ValueError("Only host can start")
        if not room["players"]["player1"] or not room["players"]["player2"]:
            raise ValueError("Need 2 players")
        room["phase"] = "deck_select"
        room["updated_at"] = self._now()
        return room

    def confirm_deck(self, room_id: str, user_id: str, deck_id: str) -> dict:
        room = self.get_room(room_id)
        if room["phase"] != "deck_select":
            raise ValueError("Room is not in deck select")
        if deck_id not in DECKS_BY_ID:
            raise ValueError("Invalid deck")
        slot = room["player_slots"].get(str(user_id))
        if not slot:
            raise ValueError("Player not in room")
        room["deck_confirmed"][slot] = deck_id
        if room["deck_confirmed"]["player1"] and room["deck_confirmed"]["player2"]:
            room["game_state"] = setup_game_state(room["deck_confirmed"]["player1"], room["deck_confirmed"]["player2"])
            room["phase"] = "in_game"
        room["updated_at"] = self._now()
        return room

    async def connect(self, room_id: str, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.setdefault(room_id, {})[str(user_id)] = websocket

    def disconnect(self, room_id: str, user_id: str) -> None:
        self.connections.get(room_id, {}).pop(str(user_id), None)

    async def broadcast(self, room_id: str) -> None:
        room = self.get_room(room_id)
        dead = []
        for user_id, websocket in self.connections.get(room_id, {}).items():
            try:
                await websocket.send_json({"type": "ROOM_STATE", "room": sanitize_room(room, user_id)})
            except Exception:
                dead.append(user_id)
        for user_id in dead:
            self.disconnect(room_id, user_id)

    def apply_action(self, room_id: str, user_id: str, action: dict) -> dict:
        room = self.get_room(room_id)
        if room["phase"] != "in_game" or not room["game_state"]:
            raise ValueError("Game has not started")
        slot = room["player_slots"].get(str(user_id))
        if not slot:
            raise ValueError("Player not in room")
        action_type = action.get("type")
        payload = action.get("payload", {})

        if action_type == "DRAW":
            draw_cards(room["game_state"], slot, 1)
        elif action_type == "DRAW_2":
            draw_cards(room["game_state"], slot, 2)
        elif action_type == "SHUFFLE_DECK":
            shuffle_deck(room["game_state"], slot)
        elif action_type == "ADD_CARROT":
            add_carrot(room["game_state"], slot)
        elif action_type == "TAP_CARD":
            tap_card(room["game_state"], slot, payload["cardId"])
        elif action_type == "UNTAP_ALL":
            untap_all(room["game_state"], slot)
        elif action_type == "MOVE_CARD":
            if payload.get("playerId", slot) != slot:
                raise ValueError("Cannot move opponent cards")
            move_card(
                room["game_state"],
                slot,
                payload["cardId"],
                payload["fromZone"],
                payload["toZone"],
                payload.get("fieldX"),
                payload.get("fieldY"),
            )
        elif action_type == "END_TURN":
            room["game_state"]["turnPlayer"] = "player2" if room["game_state"].get("turnPlayer") == "player1" else "player1"
        else:
            raise ValueError("Unsupported action")

        room["updated_at"] = self._now()
        return room


tcg_room_manager = TcgRoomManager()
