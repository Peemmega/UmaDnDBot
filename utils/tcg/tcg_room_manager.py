import secrets
import time
from typing import Any

from fastapi import WebSocket

from .tcg_decks import DECKS_BY_ID
from .tcg_state import add_carrot, draw_cards, move_card, setup_game_state, shuffle_deck, tap_card, untap_all
from .tcg_trainers import get_trainer
from .tcg_visibility import sanitize_room


class TcgRoomManager:
    def __init__(self):
        self.rooms: dict[str, dict[str, Any]] = {}
        self.connections: dict[str, dict[str, WebSocket]] = {}

    def _now(self) -> int:
        return int(time.time())

    def _new_room_id(self) -> str:
        return secrets.token_hex(4)

    def _room_players(self, room: dict) -> list[dict]:
        players = []
        seen_user_ids = set()
        for player in room["players"].values():
            if not player:
                continue
            user_id = str(player["user_id"])
            if user_id in seen_user_ids:
                continue
            seen_user_ids.add(user_id)
            players.append(player)
        return players

    def _log_room_players(self, action: str, room: dict) -> None:
        players = [
            f"{slot}={player['user_id']}"
            for slot, player in room["players"].items()
            if player
        ]
        print(
            f"[tcg] {action} room_id={room['room_id']} "
            f"players=[{', '.join(players) or 'empty'}]"
        )

    def _find_active_room_for_user(self, user_id: str) -> dict | None:
        user_id = str(user_id)
        for room in self.rooms.values():
            if room["phase"] != "ended" and user_id in room["player_slots"]:
                return room
        return None

    def _cleanup_room_if_empty(self, room_id: str) -> bool:
        room = self.rooms.get(room_id)
        if not room:
            return False
        if self._room_players(room):
            return False
        self.rooms.pop(room_id, None)
        self.connections.pop(room_id, None)
        print(f"[tcg] cleanup empty room room_id={room_id}")
        return True

    def clear_rooms(self) -> int:
        count = len(self.rooms)
        self.rooms.clear()
        self.connections.clear()
        print(f"[tcg] clear rooms count={count}")
        return count

    def list_rooms(self) -> list[dict]:
        for room_id in list(self.rooms):
            self._cleanup_room_if_empty(room_id)
        return [
            {
                "room_id": room["room_id"],
                "room_code": room["room_code"],
                "host_id": room["host_id"],
                "phase": room["phase"],
                "player_count": len(self._room_players(room)),
                "max_players": 2,
                "players": room["players"],
                "created_at": room["created_at"],
                "updated_at": room["updated_at"],
            }
            for room in sorted(self.rooms.values(), key=lambda item: item["updated_at"], reverse=True)
            if room["phase"] != "ended"
        ]

    def create_room(self, user_id: str, username: str, avatar_url: str = "") -> dict:
        user_id = str(user_id)
        existing_room = self._find_active_room_for_user(user_id)
        if existing_room:
            print(f"[tcg] create room existing user_id={user_id} room_id={existing_room['room_id']}")
            self._log_room_players("create-existing", existing_room)
            return existing_room

        room_id = self._new_room_id()
        room = {
            "room_id": room_id,
            "room_code": room_id.upper(),
            "host_id": user_id,
            "phase": "waiting",
            "players": {
                "player1": {"user_id": user_id, "username": username, "avatar_url": avatar_url, "is_host": True},
                "player2": None,
            },
            "player_slots": {user_id: "player1"},
            "deck_confirmed": {"player1": None, "player2": None},
            "trainer_confirmed": {"player1": None, "player2": None},
            "loadouts": {"player1": None, "player2": None},
            "game_state": None,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        self.rooms[room_id] = room
        print(f"[tcg] create room user_id={user_id} room_id={room_id}")
        self._log_room_players("create", room)
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
            print(f"[tcg] join room existing user_id={user_id} room_id={room_id}")
            self._log_room_players("join-existing", room)
            return room
        if room["players"]["player2"] is not None:
            raise ValueError("Room is full")
        if room["phase"] != "waiting":
            raise ValueError("Room already started")
        room["players"]["player2"] = {"user_id": user_id, "username": username, "avatar_url": avatar_url, "is_host": False}
        room["player_slots"][user_id] = "player2"
        room["updated_at"] = self._now()
        print(f"[tcg] join room user_id={user_id} room_id={room_id}")
        self._log_room_players("join", room)
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
        print(f"[tcg] leave room user_id={user_id} room_id={room_id}")
        self._log_room_players("leave", room)
        self._cleanup_room_if_empty(room_id)
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
        deck = DECKS_BY_ID.get(deck_id)
        if not deck:
            raise ValueError("Invalid deck")
        return self.confirm_loadout(room_id, user_id, deck_id, deck.get("trainer"))

    def confirm_loadout(self, room_id: str, user_id: str, deck_id: str, trainer_id: str) -> dict:
        room = self.get_room(room_id)
        if room["phase"] != "deck_select":
            raise ValueError("Room is not in deck select")
        if deck_id not in DECKS_BY_ID:
            raise ValueError("Invalid deck")
        if not get_trainer(trainer_id):
            raise ValueError("Invalid trainer")
        slot = room["player_slots"].get(str(user_id))
        if not slot:
            raise ValueError("Player not in room")

        loadout = {"deck_id": deck_id, "trainer_id": trainer_id, "ready": True}
        room["loadouts"][slot] = loadout
        room["deck_confirmed"][slot] = deck_id
        room["trainer_confirmed"][slot] = trainer_id

        player1 = room["loadouts"].get("player1")
        player2 = room["loadouts"].get("player2")
        if player1 and player2 and player1.get("ready") and player2.get("ready"):
            room["game_state"] = setup_game_state(player1, player2)
            room["phase"] = "in_game"
        room["updated_at"] = self._now()
        return room

    async def connect(self, room_id: str, user_id: str, websocket: WebSocket) -> None:
        room = self.get_room(room_id)
        user_id = str(user_id)
        if user_id not in room["player_slots"]:
            await websocket.close(code=1008)
            raise ValueError("Player not in room")
        await websocket.accept()
        connections = self.connections.setdefault(room_id, {})
        old_socket = connections.get(user_id)
        if old_socket is not None and old_socket is not websocket:
            try:
                await old_socket.close(code=1000)
            except Exception:
                pass
        connections[user_id] = websocket
        print(f"[tcg] websocket connect room_id={room_id} user_id={user_id}")
        self._log_room_players("websocket-connect", room)

    def disconnect(self, room_id: str, user_id: str, websocket: WebSocket | None = None) -> None:
        user_id = str(user_id)
        connections = self.connections.get(room_id, {})
        if websocket is not None and connections.get(user_id) is not websocket:
            return
        connections.pop(user_id, None)
        if not connections:
            self.connections.pop(room_id, None)
        print(f"[tcg] websocket disconnect room_id={room_id} user_id={user_id}")

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
