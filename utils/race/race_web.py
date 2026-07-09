from __future__ import annotations

import asyncio
import random
import time
import uuid
from typing import Any

from fastapi import WebSocket

from utils.database import ensure_player
from utils.dice.dice_presets import MAX_SPEED_PHASE
from utils.game_manager import (
    add_mob_from_preset,
    apply_lane_tactics_to_result,
    add_player,
    build_pending_effects_from_player,
    can_use_wit_reroll,
    can_player_roll,
    confirm_turn,
    create_game,
    execute_roll_core,
    execute_skill_core,
    games,
    get_stamina_debuff_percent,
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
    refresh_player_profile_snapshot,
    refresh_player_race_aptitudes,
    queue_player_lane_change,
    use_reroll,
    use_rush,
)
from utils.race.race_aptitude import get_roll_race_stats
from utils.race.runtime_stamina import (
    format_runtime_stamina,
    get_runtime_stamina_snapshot,
)
from utils.race_dice_preview import create_race_dice_preview
from utils.mob.mob_presets import MOB_PRESETS
from utils.race.race_dice import roll_race_dice
from utils.race.race_presets import PATH_TYPE_TEXT, RACE_PRESET
from utils.race.race_presets import get_current_path_type, get_path_effect, get_web_race_finish_distance
from utils.race.race_visibility import build_timing_gauge_config, serialize_room, serialize_room_summary
from utils.race.web_timing_config import (
    BOT_TIMING_POLL_INTERVAL_SECONDS,
    DEFAULT_GAUGE_HALF_CYCLE_MS,
    TIMING_MIN_INTERVAL_SECONDS,
    WEB_TIMING_MIN_HALF_CYCLE_MS,
    get_web_timing_start_delay_seconds,
)
from utils.zone.zone_manager import apply_zone_in_game
from utils.race.web_timing_balance import (
    get_web_timing_snapshot,
    initialize_web_timing_player,
    refresh_web_timing_player,
    roll_web_timing_distance_gain,
)
from utils.profile_images import resolve_player_render_image


WEB_ROOM_PREFIX = "web_race_"
DEFAULT_STAGE_KEY = "Debut"


class RaceWebManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = {}
        self.web_timing_bot_tasks: dict[str, asyncio.Task] = {}
        self.preview_png_cache: dict[tuple[str, str, int], bytes] = {}

    def _now(self) -> int:
        return int(time.time())

    def _touch(self, game: dict) -> int:
        updated_at = self._now()
        game["updated_at"] = updated_at
        return updated_at

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
        self._touch(game)
        log_payload = dict(payload or {})
        log_payload.setdefault("updated_at", game.get("updated_at"))
        game.setdefault("web_action_logs", []).append({
            "id": uuid.uuid4().hex[:8],
            "turn": game.get("turn", 0),
            "message": message,
            "payload": log_payload,
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

    def _build_lane_order_summary(self, game: dict) -> str:
        ranked_players = get_ranked_players(game.get("room_id"))
        if not ranked_players:
            return "No players"

        parts = []
        for index, (player_id, player) in enumerate(ranked_players, start=1):
            lane = int(player.get("current_lane", player.get("entry_number", 1)) or 1)
            parts.append(f"{index}. {self._player_label(player_id, player)} L{lane}")
        return " | ".join(parts)

    def _find_player_entry(self, game: dict, user_id: str) -> tuple[Any, dict] | tuple[None, None]:
        for player_id, player in game.get("players", {}).items():
            if str(player_id) == str(user_id):
                return player_id, player
        return None, None

    def _store_roll_preview_context(self, player: dict, payload: dict) -> None:
        path_effect = payload.get("path_effect") or {}
        player["web_last_roll_preview"] = {
            "new_score": payload.get("new_score", player.get("score", 0)),
            "path_label": path_effect.get("label") or "Straight",
        }

    def _prune_preview_cache(self, room_id: str, user_id: str, keep_version: int) -> None:
        stale_keys = [
            key for key in self.preview_png_cache
            if key[0] == str(room_id) and key[1] == str(user_id) and key[2] != int(keep_version)
        ]
        for key in stale_keys:
            self.preview_png_cache.pop(key, None)

    def _encode_preview_png(self, card) -> bytes:
        import io

        # Palette PNG is much smaller than raw RGBA for this mostly-flat preview card.
        encoded = card.convert("P", palette=Image.ADAPTIVE, colors=256)
        buffer = io.BytesIO()
        encoded.save(buffer, format="PNG", optimize=True, compress_level=9)
        return buffer.getvalue()

    async def build_player_preview_png(self, room_id: str, user_id: str) -> bytes:
        game = self._get_room(room_id)
        player_id, player = self._find_player_entry(game, str(user_id))
        if player is None:
            raise ValueError("Player is not in this race room")

        result = player.get("web_last_roll_result") or {}
        if not result:
            raise ValueError("No race roll preview available for this player")

        preview = player.get("web_last_roll_preview") or {}
        preview_version = int(game.get("updated_at") or self._now())
        cache_key = (str(room_id), str(user_id), preview_version)
        cached = self.preview_png_cache.get(cache_key)
        if cached is not None:
            return cached

        card = await create_race_dice_preview(
            game_player=player,
            result=result,
            payload={
                "new_score": preview.get("new_score", player.get("score", 0)),
            },
            path_label=preview.get("path_label") or PATH_TYPE_TEXT.get(get_current_path_type(game), "Straight"),
            character_image_url=resolve_player_render_image(player),
        )
        png_bytes = self._encode_preview_png(card)
        self.preview_png_cache[cache_key] = png_bytes
        self._prune_preview_cache(room_id, user_id, preview_version)
        return png_bytes

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
        gameplay_mode: str = "timing",
    ) -> dict:
        if stage_key not in RACE_PRESET:
            raise ValueError("Race stage not found")
        if gameplay_mode not in {"timing", "manual"}:
            raise ValueError("Race gameplay mode must be timing or manual")

        room_id = self._new_room_id()
        ensure_player(owner_id, username)

        if not create_game(room_id, stage_key, str(owner_id)):
            raise ValueError("Could not create race room")

        game = self._get_room(room_id)
        game["room_id"] = room_id
        game["phase"] = "waiting"
        game["web_gameplay_mode"] = gameplay_mode
        game["race_mode"] = "web_timing" if gameplay_mode == "timing" else "discord_classic"
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
        existing_player_id, existing_player = self._find_player_entry(game, user_id)
        if existing_player and not mob_preset:
            refresh_player_profile_snapshot(existing_player_id, existing_player)
            existing_player["display_name"] = username or existing_player.get("display_name")
            existing_player["username"] = username or existing_player.get("username")
            if avatar_url:
                existing_player["avatar"] = avatar_url
            self._log(game, f"{self._player_label(existing_player_id, existing_player)} rejoined")
            return serialize_room(game, room_id, str(existing_player_id))

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
        game.setdefault("web_gameplay_mode", "timing")
        game.setdefault("race_mode", "web_timing" if game["web_gameplay_mode"] == "timing" else "discord_classic")
        if game["race_mode"] == "web_timing":
            self._initialize_web_timing_race(game)
            self._start_web_timing_bot_loop(room_id)
        self._log(game, "Race started")
        if game["race_mode"] != "web_timing":
            self._process_mobs(room_id)
            self._advance_if_ready(room_id, require_confirmation=True)
        return serialize_room(self._get_room(room_id), room_id, str(user_id))

    def run(self, room_id: str, user_id: str) -> dict:
        game = self._get_room(room_id)
        if game.get("web_gameplay_mode") == "timing":
            raise ValueError("This web race uses the timing gauge")
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
                "player_id": str(user_id),
                "result": result,
                "roll_summary": _roll_summary_payload(payload),
            },
        )
        player["web_last_roll_result"] = result
        self._store_roll_preview_context(player, payload)
        self._advance_if_ready(room_id)
        return serialize_room(self._get_room(room_id), room_id, str(user_id))

    def timing(
        self,
        room_id: str,
        user_id: str,
        cycle_id: int,
        timing_score: float,
        timing_offset: float = 0.0,
        phase: str | None = None,
    ) -> dict:
        game = self._get_room(room_id)
        if game.get("race_mode") != "web_timing":
            raise ValueError("This web race uses manual Run")
        if not game.get("started") or game.get("ended"):
            raise ValueError("Race is not running")

        player_id, player = self._find_player_entry(game, str(user_id))
        if player is None:
            raise ValueError("Player is not in this race room")
        if player.get("is_mob"):
            raise ValueError("Bot timing is controlled by the server")

        current_cycle = int(cycle_id)
        if current_cycle < 1:
            raise ValueError("Timing cycle must be positive")

        submitted_cycles = player.setdefault("web_timing_submitted_cycles", set())
        if current_cycle in submitted_cycles:
            raise ValueError("Timing already submitted for this cycle")
        last_cycle = int(player.get("web_timing_last_cycle", 0))
        if current_cycle <= last_cycle:
            raise ValueError("Timing cycle is older than the latest submission")

        now = time.time()
        last_submit_at = float(player.get("web_timing_last_submit_at", 0.0))
        if last_submit_at and now - last_submit_at < TIMING_MIN_INTERVAL_SECONDS:
            raise ValueError("Timing submission is too fast")

        score = _clamp(float(timing_score), 0.0, 1.0)
        offset = _clamp(float(timing_offset), -1.0, 1.0)
        self._execute_web_timing_gain(
            room_id,
            str(player_id),
            cycle_id=current_cycle,
            timing_score=score,
            timing_offset=offset,
            client_phase=phase,
        )
        player["web_timing_last_submit_at"] = now
        player["web_timing_last_cycle"] = current_cycle
        submitted_cycles.add(current_cycle)
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

        success, payload = self._execute_reroll_core(
            room_id,
            str(user_id),
            old_total,
            minimum_total=old_total if use_wit else None,
        )
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
                "player_id": str(user_id),
                "result": result,
                "roll_summary": _roll_summary_payload(payload),
                "reroll_type": "wit" if use_wit else "normal",
            },
        )
        self._store_roll_preview_context(player, payload)
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
        if game.get("race_mode") == "web_timing":
            raise ValueError("Zone activates automatically in web timing races")
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
                "stamina": get_runtime_stamina_snapshot(player),
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

        self._log(
            game,
            f"{self._player_label(user_id, player)} used Rush +{result.get('move_forward', 0)}",
            result,
        )
        return serialize_room(game, room_id, str(user_id))

    def change_lane(self, room_id: str, user_id: str, target_lane: int) -> dict:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        success, result = queue_player_lane_change(room_id, str(user_id), target_lane)
        if not success:
            raise ValueError(result)

        self._log(
            game,
            f"{self._player_label(user_id, player)} queued lane {result.get('pending_lane')}",
            {
                "current_lane": result.get("current_lane"),
                "pending_lane": result.get("pending_lane"),
            },
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
                        "player_id": str(player_id),
                        "result": result,
                        "used_skill_ids": payload.get("used_skill_ids", []),
                        "roll_summary": _roll_summary_payload(payload),
                    },
                )
                player["web_last_roll_result"] = result
                self._store_roll_preview_context(player, payload)
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
            self._log(game, f"Turn {game.get('turn')} started | {self._build_lane_order_summary(game)}")
            self._process_mobs(room_id)
            game = self._get_room(room_id)

    def _initialize_web_timing_race(self, game: dict) -> None:
        stage = RACE_PRESET.get(game.get("stage_key"), {})
        game["finish_distance"] = get_web_race_finish_distance(stage)
        game["winner_id"] = None
        timing_now = time.time()
        schedule_now = time.monotonic()
        start_delay_seconds = get_web_timing_start_delay_seconds()
        for player_id, player in game.get("players", {}).items():
            refresh_player_race_aptitudes(player, game)
            player["web_distance"] = 0
            player["score"] = 0
            player["web_timing_last_cycle"] = 0
            player["web_timing_submitted_cycles"] = set()
            player["web_latest_timing_result"] = None
            player["web_last_distance_gain"] = 0
            player["last_distance_gain"] = 0
            if initialize_web_timing_player(player, game["finish_distance"], timing_now + start_delay_seconds):
                self._log(game, f"{self._player_label(player_id, player)} entered Zone!")
            if player.get("is_mob"):
                player["web_timing_next_auto_submit_at"] = (
                    schedule_now
                    + start_delay_seconds
                    + self._get_bot_timing_half_cycle_seconds(game, player)
                )

    def _start_web_timing_bot_loop(self, room_id: str) -> None:
        game = self._get_room(room_id)
        if not any(player.get("is_mob") for player in game.get("players", {}).values()):
            return
        existing_task = self.web_timing_bot_tasks.get(room_id)
        if existing_task and not existing_task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        task = loop.create_task(self._run_web_timing_bot_loop(room_id))
        self.web_timing_bot_tasks[room_id] = task
        task.add_done_callback(lambda finished_task: self._clear_web_timing_bot_task(room_id, finished_task))

    def _clear_web_timing_bot_task(self, room_id: str, finished_task: asyncio.Task) -> None:
        if self.web_timing_bot_tasks.get(room_id) is finished_task:
            self.web_timing_bot_tasks.pop(room_id, None)

    async def _run_web_timing_bot_loop(self, room_id: str) -> None:
        while True:
            try:
                game = self._get_room(room_id)
            except ValueError:
                return
            if game.get("race_mode") != "web_timing" or not game.get("started") or game.get("ended"):
                return
            if self._process_due_web_timing_mobs(room_id):
                await self.broadcast(room_id)
            await asyncio.sleep(BOT_TIMING_POLL_INTERVAL_SECONDS)

    def _get_bot_timing_half_cycle_seconds(self, game: dict, player: dict) -> float:
        gauge = build_timing_gauge_config(game, player)
        return max(
            WEB_TIMING_MIN_HALF_CYCLE_MS,
            float(gauge.get("half_cycle_ms") or DEFAULT_GAUGE_HALF_CYCLE_MS),
        ) / 1000.0

    def _process_due_web_timing_mobs(self, room_id: str) -> bool:
        game = self._get_room(room_id)
        now = time.monotonic()
        changed = False
        for player_id, player in list(game.get("players", {}).items()):
            if game.get("ended"):
                return changed
            if not player.get("is_mob"):
                continue
            next_submit_at = float(player.get("web_timing_next_auto_submit_at") or 0.0)
            if not next_submit_at:
                player["web_timing_next_auto_submit_at"] = now + self._get_bot_timing_half_cycle_seconds(game, player)
                continue
            if now < next_submit_at:
                continue
            cycle_id = int(player.get("web_timing_last_cycle", 0)) + 1
            submitted_cycles = player.setdefault("web_timing_submitted_cycles", set())
            _timing_tier, timing_score = roll_bot_timing_result()
            self._execute_web_timing_gain(
                room_id,
                str(player_id),
                cycle_id=cycle_id,
                timing_score=timing_score,
                timing_offset=round(random.uniform(-1.0, 1.0) * (1.0 - timing_score), 3),
                client_phase=None,
                is_bot=True,
            )
            player["web_timing_last_cycle"] = cycle_id
            submitted_cycles.add(cycle_id)
            player["web_timing_next_auto_submit_at"] = now + self._get_bot_timing_half_cycle_seconds(game, player)
            changed = True
        return changed

    def _execute_web_timing_gain(
        self,
        room_id: str,
        user_id: str,
        *,
        cycle_id: int,
        timing_score: float,
        timing_offset: float,
        client_phase: str | None,
        is_bot: bool = False,
    ) -> None:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        if player is None:
            raise ValueError("Player is not in this race room")

        finish_distance = int(game.get("finish_distance") or 2000)
        if refresh_web_timing_player(player, finish_distance):
            self._log(game, f"{self._player_label(user_id, player)} entered Zone!")
        base_gain, raw_distance_gain, timing_tier = roll_web_timing_distance_gain(player, timing_score)
        multiplier = raw_distance_gain / base_gain if base_gain else 0.0
        distance_gain = max(1, round(raw_distance_gain))
        distance = min(finish_distance, int(player.get("web_distance", 0)) + distance_gain)
        player["web_distance"] = distance
        player["score"] = distance
        player["web_last_distance_gain"] = distance_gain
        player["last_distance_gain"] = distance_gain
        if refresh_web_timing_player(player, finish_distance, increase_speed=False):
            self._log(game, f"{self._player_label(user_id, player)} entered Zone!")
        snapshot = get_web_timing_snapshot(player, finish_distance)

        result = {
            "base_gain": round(base_gain, 2),
            "timing_multiplier": round(multiplier, 3),
            "timing_score": round(timing_score, 3),
            "timing_offset": round(timing_offset, 3),
            "timing_tier": timing_tier,
            "total": distance_gain,
        }
        player["web_latest_timing_result"] = {
            "cycle_id": cycle_id,
            "score": result["timing_score"],
            "timing_score": result["timing_score"],
            "offset": result["timing_offset"],
            "tier": result["timing_tier"],
            "distance_gain": distance_gain,
            "total": distance_gain,
            "phase": snapshot["phase"],
            "tempo_level": snapshot["tempo_level"],
        }
        self._log(
            game,
            f"{self._player_label(user_id, player)} timed {result['timing_tier']} +{distance_gain}m",
            {
                "timing": player["web_latest_timing_result"],
                "effective_stats": player.get("effective_race_stats"),
                "aptitude_bonus": player.get("aptitude_bonus"),
                "client_phase": client_phase,
                "is_bot": is_bot,
            },
        )
        if distance >= finish_distance:
            self._finish_web_timing_race(game, str(user_id))

    def _finish_web_timing_race(self, game: dict, winner_id: str) -> None:
        ranked = sorted(
            game.get("players", {}).items(),
            key=lambda item: item[1].get("web_distance", 0),
            reverse=True,
        )
        game["winner_id"] = winner_id
        game["result"] = {
            "winner": _serialize_winner(next(item for item in ranked if str(item[0]) == winner_id)),
            "rankings": [_serialize_winner(item, index) for index, item in enumerate(ranked, start=1)],
        }
        game["ended"] = True
        game["started"] = False
        game["phase"] = "ended"
        self._log(game, "Race finished", game["result"])

    def _execute_reroll_core(
        self,
        room_id: str,
        user_id: str,
        old_total: int,
        minimum_total: int | None = None,
    ) -> tuple[bool, dict]:
        game = self._get_room(room_id)
        player = game.get("players", {}).get(str(user_id))
        if player is None:
            return False, {"message": "Player is not in this race room"}

        race_player = player.get("race_profile")
        if race_player is None:
            return False, {"message": "Race profile is missing"}
        roll_stats = get_roll_race_stats(player)

        success, _ = update_player_score(room_id, str(user_id), -old_total)
        if not success:
            return False, {"message": "Could not remove old score"}

        pending_effects, merged_stats = build_pending_effects_from_player(player)
        if player.get("takeStaminaDebuff", False):
            pending_effects.append({
                "type": "modify_total_percent",
                "value": -get_stamina_debuff_percent(player),
                "duration": "this_roll",
            })
        path_type = get_current_path_type(game)
        path_effect = get_path_effect(path_type, player, race_player)
        result = roll_race_dice(
            game_player=player,
            player_stats=roll_stats,
            player_id=str(user_id),
            score_map=game.get("turn_snapshot_scores", {}),
            turn=game["turn"],
            max_turn=game["max_turn"],
            path_effect=path_effect,
            skill_effects=pending_effects,
            minimum_total=minimum_total,
            player_map=game.get("players", {}),
        )
        lane_resolution = apply_lane_tactics_to_result(
            game=game,
            user_id=str(user_id),
            game_player=player,
            result=result,
            path_effect=path_effect,
            score_map=game.get("turn_snapshot_scores", {}),
            consume_stamina=False,
            apply_stamina_penalty=False,
        )

        player["lastedBuff"] = merged_stats
        player["next_roll_flat_bonus"] = 0
        player["next_roll_add_d"] = 0
        player["next_roll_add_kh"] = 0
        player["next_roll_floor_bonus"] = 0
        player["next_roll_selected_die_bonus"] = 0
        player["next_roll_cap_bonus"] = 0
        player["gold_range_bonus_this_turn"] = 0
        player["enemy_gold_range_penalty_next_turn"] = 0
        player["gold_lane_bonus_this_turn"] = 0
        player["enemy_gold_lane_penalty_next_turn"] = 0

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
            "stamina_note": lane_resolution["stamina_note"],
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
    distance = int(player.get("web_distance", player.get("score", 0)))
    return {
        "rank": rank,
        "id": str(player_id),
        "name": player.get("display_name") or player.get("username") or str(player_id),
        "style": player.get("style"),
        "score": player.get("score", 0),
        "distance": distance,
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


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _timing_tier(score: float) -> str:
    if score >= 0.92:
        return "Perfect"
    if score >= 0.78:
        return "Great"
    if score >= 0.55:
        return "Good"
    if score >= 0.30:
        return "Bad"
    return "Miss"


def _timing_phase(game: dict) -> str:
    turn = max(1, int(game.get("turn", 1)))
    max_turn = max(1, int(game.get("max_turn", 1)))
    progress = turn / max_turn
    path_label = str(PATH_TYPE_TEXT.get(get_current_path_type(game), "")).lower()
    if progress <= 0.1:
        return "Start"
    if progress <= 0.4:
        return "Early"
    if progress <= 0.7:
        return "Middle"
    if "corner" in path_label:
        return "Final Corner"
    return "Final Straight"


def _web_player_phase(player: dict, finish_distance: int) -> str:
    progress = float(player.get("web_distance", 0)) / max(1, finish_distance)
    if progress >= 1.0:
        return "Finished"
    if progress < 0.15:
        return "Start"
    if progress < 0.40:
        return "Early"
    if progress < 0.70:
        return "Middle"
    if progress < 0.90:
        return "Final Corner"
    return "Final Straight"


def _increase_web_timing_speed(player: dict, finish_distance: int) -> None:
    style = player.get("style") or "Pace"
    style_rule = MAX_SPEED_PHASE.get(style, MAX_SPEED_PHASE["Pace"])
    phase = _web_player_phase(player, finish_distance)
    phase_cap_key = {
        "Start": "start",
        "Early": "mid",
        "Middle": "mid",
        "Final Corner": "late",
        "Final Straight": "last_spurt",
        "Finished": "last_spurt",
    }.get(phase, "mid")
    race_profile = player.get("race_profile") or {}
    effective_stats = player.get("effective_race_stats") or {}
    speed_cap = float(style_rule[phase_cap_key]) + float(effective_stats.get("effective_speed", race_profile.get("speed", 0)))
    acceleration = 0.3 + (0.1 * float(effective_stats.get("effective_power", race_profile.get("power", 1))))
    player["current_max_speed"] = min(speed_cap, float(player.get("current_max_speed", 0)) + acceleration)


def roll_bot_timing_result() -> tuple[str, float]:
    tier = random.choices(
        ["Good", "Great", "Perfect"],
        weights=[10, 60, 30],
        k=1,
    )[0]
    minimum, maximum = {
        "Good": (0.55, 0.77),
        "Great": (0.78, 0.91),
        "Perfect": (0.92, 1.00),
    }[tier]
    return tier, round(random.uniform(minimum, maximum), 3)


def _roll_summary_payload(payload: dict) -> dict:
    player = payload.get("game_player") or {}
    result = payload.get("result") or {}
    path_effect = payload.get("path_effect") or {}
    race_profile = player.get("race_profile") or {}
    aptitude_bonus = player.get("aptitude_bonus") or {}
    effective_stats = player.get("effective_race_stats") or {}
    lasted_buff = player.get("lastedBuff") or {}
    stamina_snapshot = get_runtime_stamina_snapshot(player)
    return {
        "total": result.get("total", 0),
        "raw_total": result.get("raw_total"),
        "timing_score": result.get("timing_score"),
        "timing_tier": result.get("timing_tier"),
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
        "stamina_left": stamina_snapshot["current_stamina"],
        "current_stamina": stamina_snapshot["current_stamina"],
        "max_stamina": stamina_snapshot["max_stamina"],
        "stamina_stat": stamina_snapshot["stamina_stat"],
        "stamina_percent": stamina_snapshot["stamina_percent"],
        "current_lane": int(player.get("current_lane", 1) or 1),
        "previous_lane": int(player.get("previous_lane", player.get("current_lane", 1)) or 1),
        "lane_changed": bool(player.get("lane_changed")),
        "blocked_count": int(result.get("blocked_count", player.get("blocked_count", 0)) or 0),
        "blocking_penalty": float(result.get("blocking_penalty", player.get("blocking_penalty", 0.0)) or 0.0),
        "drafting_active": bool(result.get("drafting_active", player.get("drafting_active", False))),
        "current_max_speed": player.get("current_max_speed", 0),
        "stats": {
            "speed": race_profile.get("speed", 0),
            "stamina": race_profile.get("stamina", 0),
            "power": race_profile.get("power", 0),
            "gut": race_profile.get("gut", 0),
            "wit": race_profile.get("wit", 0),
        },
        "effective_stats": {
            "effective_speed": effective_stats.get("effective_speed"),
            "effective_power": effective_stats.get("effective_power"),
            "effective_wit_gain": effective_stats.get("effective_wit_gain"),
            "effective_wit_requirement": effective_stats.get("effective_wit_requirement"),
            "distance_percent": effective_stats.get("distance_percent"),
        },
        "aptitude_bonus": aptitude_bonus,
        "pending_bonus": lasted_buff,
    }


def add_player_as_web_mob(room_id: str, user_id: str, username: str, preset_key: str):
    from utils.game_manager import add_player_as_mob_preset

    return add_player_as_mob_preset(room_id, user_id, username, preset_key)


race_web_manager = RaceWebManager()
