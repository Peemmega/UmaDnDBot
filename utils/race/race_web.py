from __future__ import annotations

import uuid
from typing import Any

from fastapi import WebSocket

from utils.database import ensure_player
from utils.game_manager import (
    add_mob_from_preset,
    add_player,
    build_pending_effects_from_player,
    can_use_wit_reroll,
    can_player_roll,
    confirm_turn,
    create_game,
    execute_roll_core,
    execute_skill_core,
    games,
    get_game,
    get_ranked_players,
    have_all_players_rolled,
    next_turn,
    process_mob_turn,
    reset_turn_confirmations,
    start_game,
    start_turn_confirmation,
    update_player_score,
    use_block,
    use_reroll,
    use_rush,
)
from utils.mob.mob_presets import MOB_PRESETS
from utils.race.race_dice import roll_race_dice
from utils.race.race_presets import RACE_PRESET
from utils.race.race_presets import get_current_path_type, get_path_effect
from utils.race.race_visibility import serialize_room, serialize_room_summary
from utils.zone.zone_manager import apply_zone_in_game


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

    def _player_label(self, player_id, player: dict | None) -> str:
        if not player:
            return str(player_id)
        return (
            player.get("display_name")
            or player.get("username")
            or player.get("name")
            or str(player_id)
        )

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
            {
                "result": result,
                "roll_summary": _roll_summary_payload(payload),
            },
        )
        player["web_last_roll_result"] = result
        self._advance_if_ready(room_id)
        return serialize_room(self._get_room(room_id), room_id, str(user_id))

    def reroll(self, room_id: str, user_id: str, use_wit: bool = False) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        if player is None:
            raise ValueError("Player is not in this race room")
        if not game.get("awaiting_turn_confirm"):
            raise ValueError("Reroll is only available during turn confirmation")
        if player.get("last_roll_turn") != game.get("turn"):
            raise ValueError("You need to run before rerolling")
        if player.get("no_reroll_this_turn"):
            raise ValueError("Reroll is blocked this turn")

        old_result = player.get("web_last_roll_result") or {}
        old_total = int(old_result.get("total") or player.get("last_roll_log", {}).get("total") or 0)
        if old_total <= 0:
            raise ValueError("No roll result available to reroll")

        spent_normal_reroll = False
        if use_wit:
            base_total = int(old_result.get("base_total") or player.get("last_roll_log", {}).get("base_total") or 0)
            if not can_use_wit_reroll(player, base_total):
                raise ValueError("WIT reroll is not available for this roll")
            player["wit_reroll_left"] = max(0, int(player.get("wit_reroll_left", 0)) - 1)
        else:
            success, result = use_reroll(room_id, str(user_id))
            if not success:
                raise ValueError(result)
            spent_normal_reroll = True

        success, payload = self._execute_reroll_core(room_id, str(user_id), old_total)
        if not success:
            if use_wit:
                player["wit_reroll_left"] = int(player.get("wit_reroll_left", 0)) + 1
            elif spent_normal_reroll:
                player["reroll_left"] = int(player.get("reroll_left", 0)) + 1
            raise ValueError(payload.get("message", "Reroll failed"))

        result = payload["result"]
        self._log(
            game,
            f"{self._player_label(user_id, player)} {'WIT ' if use_wit else ''}rerolled +{result.get('total', 0)}",
            {
                "result": result,
                "roll_summary": _roll_summary_payload(payload),
                "reroll_type": "wit" if use_wit else "normal",
            },
        )
        return serialize_room(game, room_id, str(user_id))

    def confirm(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        success, result = confirm_turn(room_id, str(user_id))
        if not success:
            raise ValueError(result)

        self._log(
            game,
            f"{self._player_label(user_id, game.get('players', {}).get(str(user_id)))} confirmed turn",
            result,
        )

        if result.get("all_confirmed"):
            reset_turn_confirmations(room_id)
            self._advance_if_ready(room_id, require_confirmation=False)

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

    def zone(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        if player is None:
            raise ValueError("Player is not in this race room")

        success, result_text = apply_zone_in_game(game, player)
        if not success:
            raise ValueError(result_text)

        self._log(
            game,
            f"{self._player_label(user_id, player)} used Zone",
            {
                "zone": player.get("zone"),
                "result_text": result_text,
                "buffs": _current_buff_payload(player),
                "stamina_left": player.get("stamina_left", 0),
                "current_max_speed": player.get("current_max_speed", 0),
            },
        )
        return serialize_room(game, room_id, str(user_id))

    def block(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        success, result = use_block(room_id, str(user_id))
        if not success:
            raise ValueError(result)

        target = game.get("players", {}).get(result.get("target_id"))
        self._log(
            game,
            f"{self._player_label(user_id, player)} used Block on {self._player_label(result.get('target_id'), target)}",
            result,
        )
        return serialize_room(game, room_id, str(user_id))

    def rush(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        success, result = use_rush(room_id, str(user_id))
        if not success:
            raise ValueError(result)

        target = game.get("players", {}).get(result.get("target_id"))
        self._log(
            game,
            f"{self._player_label(user_id, player)} used Rush toward {self._player_label(result.get('target_id'), target)}",
            result,
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
                    {
                        "result": result,
                        "used_skill_ids": payload.get("used_skill_ids", []),
                        "roll_summary": _roll_summary_payload(payload),
                    },
                )
            else:
                self._log(game, f"Bot turn failed: {payload.get('message', 'unknown error')}")

    def _advance_if_ready(self, room_id: str, require_confirmation: bool = True) -> None:
        game = self._get_room(room_id)
        guard = 0
        while game.get("started") and not game.get("ended") and have_all_players_rolled(room_id):
            guard += 1
            if guard > 80:
                raise ValueError("Race auto-advance guard tripped")

            has_human = any(not player.get("is_mob") for player in game.get("players", {}).values())
            if require_confirmation and has_human:
                if not game.get("awaiting_turn_confirm"):
                    start_turn_confirmation(room_id)
                    self._log(game, "Awaiting turn confirmation")
                break

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

    def _execute_reroll_core(self, room_id: str, user_id: str, old_total: int) -> tuple[bool, dict]:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        if player is None:
            return False, {"message": "Player is not in this race room"}

        race_player = player.get("race_profile")
        if race_player is None:
            return False, {"message": "Race profile is missing"}

        success, _ = update_player_score(room_id, str(user_id), -old_total)
        if not success:
            return False, {"message": "Could not remove old score"}

        pending_effects, merged_stats = build_pending_effects_from_player(player)
        path_type = get_current_path_type(game)
        path_effect = get_path_effect(path_type, player, race_player)
        result = roll_race_dice(
            game_player=player,
            player_stats=race_player,
            player_id=str(user_id),
            score_map=game.get("turn_snapshot_scores", {}),
            turn=game["turn"],
            max_turn=game["max_turn"],
            path_effect=path_effect,
            skill_effects=pending_effects,
        )

        if player.get("takeStaminaDebuff", False):
            if result["bonus_display"] == "-":
                result["bonus_display"] = "-20CAP"
            else:
                result["bonus_display"] += " -20CAP"

        player["lastedBuff"] = merged_stats
        player["next_roll_flat_bonus"] = 0
        player["next_roll_add_d"] = 0
        player["next_roll_add_kh"] = 0
        player["next_roll_floor_bonus"] = 0
        player["next_roll_selected_die_bonus"] = 0
        player["next_roll_cap_bonus"] = 0
        player["gold_range_bonus_this_turn"] = 0
        player["enemy_gold_range_penalty_next_turn"] = 0

        success, new_score = update_player_score(room_id, str(user_id), result["total"])
        if not success:
            update_player_score(room_id, str(user_id), old_total)
            return False, {"message": "Could not apply new score"}

        rule = result.get("rule", {})
        rule_text = f"{rule.get('d', 0)}d"
        if rule.get("kh") is not None:
            rule_text += f" kh{rule['kh']}"

        player["last_roll_log"] = {
            "phase": result.get("phase"),
            "distance_color": result.get("distance_color"),
            "rule": rule_text,
            "total": result.get("total"),
            "base_total": result.get("base_total"),
            "bonus_display": result.get("bonus_display"),
        }
        player["web_last_roll_result"] = result

        return True, {
            "game": game,
            "game_player": player,
            "result": result,
            "new_score": new_score,
            "path_effect": path_effect,
            "stamina_note": player.get("stamina_left", 0),
        }

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


def _current_buff_payload(player: dict) -> dict:
    return {
        "flat": player.get("next_roll_flat_bonus", 0),
        "add_d": player.get("next_roll_add_d", 0),
        "add_kh": player.get("next_roll_add_kh", 0),
        "floor": player.get("next_roll_floor_bonus", 0),
        "cap": player.get("next_roll_cap_bonus", 0),
        "gold_range": player.get("gold_range_bonus_this_turn", 0),
    }


def _roll_summary_payload(payload: dict) -> dict:
    player = payload.get("game_player") or {}
    result = payload.get("result") or {}
    path_effect = payload.get("path_effect") or {}
    race_profile = player.get("race_profile") or {}
    aptitude_bonus = player.get("aptitude_bonus") or {}
    lasted_buff = player.get("lastedBuff") or {}
    return {
        "total": result.get("total", 0),
        "dice": result.get("display"),
        "selected": result.get("selected", []),
        "modified_selected": result.get("modified_selected", []),
        "base_total": result.get("base_total", 0),
        "bonus_display": result.get("bonus_display"),
        "rule": result.get("rule"),
        "phase": result.get("phase"),
        "distance_color": result.get("distance_color"),
        "path": {
            "label": path_effect.get("label"),
            "stamina_cost": path_effect.get("stamina_cost", 0),
            "stamina_gain": path_effect.get("stamina_gain", 0),
            "reduce_dice_value": path_effect.get("reduce_dice_value", 0),
            "spd_multiplier": path_effect.get("spd_multiplier", 1.0),
            "power_total_multiplier": path_effect.get("power_total_multiplier", 1.0),
            "extra_max_from_wit": path_effect.get("extra_max_from_wit", 0),
            "extra_floor_from_wit": path_effect.get("extra_floor_from_wit", 0),
        },
        "stamina_note": payload.get("stamina_note"),
        "stamina_left": player.get("stamina_left", 0),
        "current_max_speed": player.get("current_max_speed", 0),
        "stats": {
            "speed": race_profile.get("speed", 0),
            "stamina": race_profile.get("stamina", 0),
            "power": race_profile.get("power", 0),
            "gut": race_profile.get("gut", 0),
            "wit": race_profile.get("wit", 0),
        },
        "aptitude_bonus": aptitude_bonus,
        "pending_bonus": lasted_buff,
    }


def add_player_as_web_mob(room_id: str, user_id: str, username: str, preset_key: str):
    from utils.game_manager import add_player_as_mob_preset

    return add_player_as_mob_preset(room_id, user_id, username, preset_key)


race_web_manager = RaceWebManager()
