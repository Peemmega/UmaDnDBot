from __future__ import annotations

import uuid
from typing import Any

from fastapi import WebSocket

from utils.database import ensure_player
from utils.game_manager import (
    add_mob_from_preset,
    add_player,
    can_player_roll,
    create_game,
    execute_roll_core,
    execute_skill_core,
    games,
    get_game,
    get_ranked_players,
    have_all_players_rolled,
    next_turn,
    process_mob_turn,
    start_game,
)
from utils.mob.mob_presets import MOB_PRESETS
from utils.race.race_presets import RACE_PRESET
from utils.race.race_visibility import serialize_room, serialize_room_summary


WEB_ROOM_PREFIX = "web_race_"
DEFAULT_STAGE_KEY = "Debut"


class RaceWebManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = {}

    def _room_key(self, room_id: str) -> str:
        return room_id

    def _new_room_id(self) -> str:
        return f"{WEB_ROOM_PREFIX}{uuid.uuid4().hex[:10]}"

    def _get_room(self, room_id: str) -> dict:
        game = get_game(self._room_key(room_id))
        if game is None:
            raise ValueError("Race room not found")
        return game

    def _log(self, game: dict, message: str, payload: dict | None = None) -> None:
        game.setdefault("web_action_logs", []).append({
            "id": uuid.uuid4().hex[:8],
            "turn": game.get("turn", 0),
            "message": message,
            "payload": payload or {},
        })
        game["web_action_logs"] = game["web_action_logs"][-120:]
        safe_message = str(message).encode("ascii", "backslashreplace").decode("ascii")
        print(f"[race-web] {game.get('room_id')} turn={game.get('turn')} {safe_message}")

    def list_rooms(self) -> list[dict]:
        summaries = []
        for room_id, game in games.items():
            if str(room_id).startswith(WEB_ROOM_PREFIX):
                summaries.append(serialize_room_summary(game, str(room_id)))
        return sorted(
            summaries,
            key=lambda item: (item["phase"] != "waiting", item["room_id"]),
        )

    def create_room(
        self,
        owner_id: str,
        username: str,
        avatar_url: str = "",
        stage_key: str = DEFAULT_STAGE_KEY,
        style: str = "Pace",
    ) -> dict:
        if stage_key not in RACE_PRESET:
            raise ValueError("Race stage not found")

        room_id = self._new_room_id()
        ensure_player(owner_id, username)

        if not create_game(room_id, stage_key, str(owner_id)):
            raise ValueError("Could not create race room")

        game = self._get_room(room_id)
        game["room_id"] = room_id
        game["phase"] = "waiting"
        game["web_action_logs"] = []
        self._log(game, f"{username} created {game.get('stage_name')}")
        success, message = add_player(room_id, str(owner_id), username, avatar_url, style)
        if not success:
            raise ValueError(message)
        self._log(game, f"{username} joined as {style}")

        return serialize_room(game, room_id, str(owner_id))

    def join_room(
        self,
        room_id: str,
        user_id: str,
        username: str,
        avatar_url: str = "",
        style: str = "Pace",
        mob_preset: str | None = None,
    ) -> dict:
        game = self._get_room(room_id)

        if mob_preset:
            success, message = add_player_as_web_mob(room_id, str(user_id), username, mob_preset)
        else:
            ensure_player(user_id, username)
            success, message = add_player(room_id, str(user_id), username, avatar_url, style)

        if not success:
            raise ValueError(message)

        self._log(game, f"{username} joined as {style}")
        return serialize_room(game, room_id, str(user_id))

    def leave_room(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).pop(str(user_id), None)
        if player is None:
            raise ValueError("Player is not in this race room")

        self._log(game, f"{player.get('display_name') or player.get('username') or user_id} left")

        if not game["players"]:
            games.pop(room_id, None)
            return {
                "room_id": room_id,
                "phase": "closed",
                "players": [],
                "scoreboard": [],
                "action_logs": [],
            }

        if str(game.get("owner_id")) == str(user_id):
            game["owner_id"] = str(next(iter(game["players"].keys())))

        return serialize_room(game, room_id, str(user_id))

    def add_bot(self, room_id: str, user_id: str, preset_key: str = "rookie_pace", level: int = 1) -> dict:
        game = self._get_room(room_id)
        success, message = add_mob_from_preset(room_id, preset_key, level)
        if not success:
            raise ValueError(message)
        self._log(game, message)
        return serialize_room(game, room_id, str(user_id))

    def start_room(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        if str(game.get("owner_id")) != str(user_id):
            raise ValueError("Only the room owner can start this race")

        success, message = start_game(room_id)
        if not success:
            raise ValueError(message)

        game = self._get_room(room_id)
        self._log(game, "Race started")
        self._process_mobs(room_id)
        self._advance_if_ready(room_id)
        return serialize_room(self._get_room(room_id), room_id, str(user_id))

    def run(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        ok, message = can_player_roll(room_id, str(user_id))
        if not ok:
            raise ValueError(message)

        success, payload = execute_roll_core(
            channel_id=room_id,
            user_id=str(user_id),
            title_prefix="web run",
            mark_roll=True,
        )
        if not success:
            raise ValueError(payload.get("message", "Run failed"))

        player = payload["game_player"]
        result = payload["result"]
        self._log(
            game,
            f"{player.get('display_name') or player.get('username') or user_id} ran +{result.get('total', 0)}",
            {"result": result},
        )
        self._advance_if_ready(room_id)
        return serialize_room(self._get_room(room_id), room_id, str(user_id))

    def skill(self, room_id: str, user_id: str, skill_id: str | None = None, slot: int | None = None) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        if player is None:
            raise ValueError("Player is not in this race room")

        if slot and not skill_id:
            slots = player.get("skills") or {}
            skill_id = slots.get(slot) or slots.get(str(slot))

        if not skill_id:
            return serialize_room(game, room_id, str(user_id))

        success, payload = execute_skill_core(room_id, str(user_id), skill_id, consume_cost=True)
        if not success:
            raise ValueError(payload.get("message", "Skill failed"))

        self._log(
            game,
            f"{player.get('display_name') or player.get('username') or user_id} used {payload.get('skill_name', skill_id)}",
            payload,
        )
        return serialize_room(game, room_id, str(user_id))

    def get_room(self, room_id: str, user_id: str | None = None) -> dict:
        return serialize_room(self._get_room(room_id), room_id, user_id)

    def _process_mobs(self, room_id: str) -> None:
        game = self._get_room(room_id)
        if not game.get("started") or game.get("ended"):
            return

        for player_id, player in list(game.get("players", {}).items()):
            if not player.get("is_mob"):
                continue
            if player.get("last_roll_turn") == game.get("turn"):
                continue

            success, payload = process_mob_turn(room_id, player_id)
            if success:
                result = payload.get("result", {})
                self._log(
                    game,
                    f"{player.get('display_name') or player.get('username') or player_id} auto ran +{result.get('total', 0)}",
                    {"result": result, "used_skill_ids": payload.get("used_skill_ids", [])},
                )
            else:
                self._log(game, f"Bot turn failed: {payload.get('message', 'unknown error')}")

    def _advance_if_ready(self, room_id: str) -> None:
        game = self._get_room(room_id)
        guard = 0
        while game.get("started") and not game.get("ended") and have_all_players_rolled(room_id):
            guard += 1
            if guard > 80:
                raise ValueError("Race auto-advance guard tripped")

            if game.get("turn", 0) >= game.get("max_turn", 0):
                final_turn = game.get("turn", 0)
                next_turn(room_id)
                game["turn"] = final_turn
                ranked = get_ranked_players(room_id)
                game["result"] = {
                    "winner": _serialize_winner(ranked[0]) if ranked else None,
                    "rankings": [
                        _serialize_winner(item, index)
                        for index, item in enumerate(ranked, start=1)
                    ],
                }
                game["ended"] = True
                game["started"] = False
                game["phase"] = "ended"
                self._log(game, "Race finished", game["result"])
                break

            next_turn(room_id)
            self._log(game, f"Turn {game.get('turn')} started")
            self._process_mobs(room_id)
            game = self._get_room(room_id)

    async def connect(self, room_id: str, websocket: WebSocket) -> None:
        self._get_room(room_id)
        await websocket.accept()
        self.connections.setdefault(room_id, set()).add(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket) -> None:
        sockets = self.connections.get(room_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self.connections.pop(room_id, None)

    async def broadcast(self, room_id: str) -> None:
        sockets = list(self.connections.get(room_id, set()))
        if not sockets:
            return

        try:
            payload: dict[str, Any] = {
                "type": "RACE_STATE",
                "room": self.get_room(room_id),
            }
        except ValueError:
            payload = {"type": "RACE_CLOSED", "room_id": room_id}

        stale = []
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)

        for websocket in stale:
            self.disconnect(room_id, websocket)


def _serialize_winner(item, rank: int = 1) -> dict:
    player_id, player = item
    return {
        "rank": rank,
        "id": str(player_id),
        "name": player.get("display_name") or player.get("username") or str(player_id),
        "style": player.get("style"),
        "score": player.get("score", 0),
        "is_mob": bool(player.get("is_mob")),
    }


def add_player_as_web_mob(room_id: str, user_id: str, username: str, preset_key: str):
    from utils.game_manager import add_player_as_mob_preset

    return add_player_as_mob_preset(room_id, user_id, username, preset_key)


race_web_manager = RaceWebManager()
