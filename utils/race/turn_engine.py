"""Race turn lifecycle independent from Discord and Web transports.

The engine owns the mutable confirmation and turn-transition state.  The
callers retain their existing public APIs and provide callbacks for external
effects such as history persistence, cooldowns, and speed progression.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from utils.race.race_lane import resolve_pending_lane_changes
from utils.race.race_weather import (
    advance_weather_turn,
    is_raining,
    schedule_next_wet_lanes,
)


@dataclass(frozen=True)
class TurnEngineResult:
    ok: bool
    code: str
    payload: dict[str, Any] | None = None


class TurnEngine:
    """Coordinates confirmation and deterministic transition between turns."""

    @staticmethod
    def reset_confirmations(game: dict) -> None:
        game["turn_confirmations"] = set()
        game["awaiting_turn_confirm"] = False
        game["turn_confirmation_turn"] = None
        game["turn_confirmation_token"] = int(game.get("turn_confirmation_token", 0)) + 1

    @classmethod
    def start_confirmation(
        cls,
        game: dict,
        *,
        revise_mob_lanes: Callable[[dict], None] | None = None,
    ) -> bool:
        if game.get("turn_transition_in_progress"):
            return False

        game["turn_confirmations"] = set()
        game["awaiting_turn_confirm"] = True
        game["turn_confirmation_turn"] = game.get("turn")
        game["turn_confirmation_token"] = int(game.get("turn_confirmation_token", 0)) + 1
        schedule_next_wet_lanes(game)

        if game.get("next_wet_lanes") and revise_mob_lanes is not None:
            revise_mob_lanes(game)
        return True

    @staticmethod
    def confirm(
        game: dict,
        user_id,
        *,
        expected_turn: int | None = None,
        confirmation_token: int | None = None,
    ) -> TurnEngineResult:
        if not game.get("awaiting_turn_confirm"):
            return TurnEngineResult(False, "not_awaiting_confirmation")

        current_turn = game.get("turn")
        if game.get("turn_confirmation_turn") != current_turn:
            return TurnEngineResult(False, "stale_confirmation")
        if expected_turn is not None and expected_turn != current_turn:
            return TurnEngineResult(False, "stale_turn")
        if (
            confirmation_token is not None
            and confirmation_token != game.get("turn_confirmation_token")
        ):
            return TurnEngineResult(False, "stale_confirmation")

        player = game.get("players", {}).get(user_id)
        if player is None:
            return TurnEngineResult(False, "player_not_found")
        if player.get("is_mob"):
            return TurnEngineResult(False, "mob_cannot_confirm")
        if player.get("last_roll_turn") != current_turn:
            return TurnEngineResult(False, "player_not_rolled")

        game["turn_confirmations"].add(user_id)
        required_confirmations = {
            player_id
            for player_id, info in game.get("players", {}).items()
            if not info.get("is_mob")
        }
        confirmed_count = len(game["turn_confirmations"] & required_confirmations)
        return TurnEngineResult(
            True,
            "ok",
            {
                "confirmed_count": confirmed_count,
                "total_players": len(required_confirmations),
                "all_confirmed": confirmed_count == len(required_confirmations),
            },
        )

    @classmethod
    def claim_transition(
        cls,
        game: dict,
        *,
        all_players_rolled: bool,
        expected_turn: int | None = None,
        confirmation_token: int | None = None,
        require_all_confirmations: bool = True,
        require_all_rolls: bool = True,
    ) -> TurnEngineResult:
        if not game.get("started") or game.get("ended"):
            return TurnEngineResult(False, "race_not_active")
        if game.get("turn_transition_in_progress"):
            return TurnEngineResult(False, "transition_in_progress")

        current_turn = game.get("turn")
        if expected_turn is not None and expected_turn != current_turn:
            return TurnEngineResult(False, "stale_turn")

        if confirmation_token is not None and (
            not game.get("awaiting_turn_confirm")
            or game.get("turn_confirmation_turn") != current_turn
            or game.get("turn_confirmation_token") != confirmation_token
        ):
            return TurnEngineResult(False, "stale_confirmation")

        if require_all_rolls and not all_players_rolled:
            return TurnEngineResult(False, "pending_rolls")

        if require_all_confirmations:
            required_confirmations = {
                player_id
                for player_id, info in game.get("players", {}).items()
                if not info.get("is_mob")
            }
            if (
                not game.get("awaiting_turn_confirm")
                or game.get("turn_confirmation_turn") != current_turn
                or not required_confirmations.issubset(game.get("turn_confirmations", set()))
            ):
                return TurnEngineResult(False, "pending_confirmations")

        # Claim before callers await on rendering or transport work.
        game["turn_transition_in_progress"] = True
        cls.reset_confirmations(game)
        return TurnEngineResult(True, "ok", {"turn": current_turn})

    @staticmethod
    def advance(
        game: dict,
        *,
        lane_system_enabled: bool,
        record_lane_change: Callable[[dict, object, dict], None],
        record_turn_snapshot: Callable[[dict, int], None],
        after_advance: Callable[[], None],
    ) -> int:
        """Record a completed turn, reset transient state, and enter the next one."""
        current_turn = int(game.get("turn", 0))
        snapshot_scores = game.get("turn_snapshot_scores", {})
        players = game.get("players", {})
        position_by_player = {
            player_id: position
            for position, (player_id, _) in enumerate(
                sorted(
                    players.items(),
                    key=lambda item: int(item[1].get("score", 0) or 0),
                    reverse=True,
                ),
                start=1,
            )
        }

        game.setdefault("turn_score_logs", [])
        for user_id, player in players.items():
            before_score = int(snapshot_scores.get(user_id, 0) or 0)
            current_score = int(player.get("score", 0) or 0)
            game["turn_score_logs"].append(
                {
                    "turn": current_turn,
                    "player_id": str(user_id),
                    "name": player.get("display_name") or player.get("username") or str(user_id),
                    "style": player.get("style"),
                    "gain": current_score - before_score,
                    "score_before": before_score,
                    "score_after": current_score,
                    "position": position_by_player.get(user_id),
                    "roll": player.get("last_roll_log"),
                    "skills": player.get("used_skills_this_turn", []),
                }
            )

        if lane_system_enabled:
            resolve_pending_lane_changes(players)
            for player_id, player in players.items():
                if not player.get("lane_changed"):
                    continue
                lane_change = {
                    "from": player.get("previous_lane"),
                    "to": player.get("current_lane"),
                }
                game["turn_score_logs"].append(
                    {
                        "turn": current_turn,
                        "player_id": str(player_id),
                        "name": player.get("display_name") or player.get("username") or str(player_id),
                        "style": player.get("style"),
                        "gain": 0,
                        "score_before": player.get("score", 0),
                        "score_after": player.get("score", 0),
                        "position": position_by_player.get(player_id),
                        "roll": {"lane_change": lane_change},
                        "skills": [],
                    }
                )
                record_lane_change(
                    game,
                    player_id,
                    {"from_lane": lane_change["from"], "to_lane": lane_change["to"]},
                )

        record_turn_snapshot(game, current_turn)
        if is_raining(game) and not game.get("next_wet_lanes"):
            schedule_next_wet_lanes(game)
        advance_weather_turn(game)

        game["turn"] = current_turn + 1
        game["turn_transition_in_progress"] = False
        TurnEngine.reset_confirmations(game)

        for player in players.values():
            player["used_block"] = False
            player["no_reroll_this_turn"] = player.get("no_reroll_next_turn", False)
            player["no_reroll_next_turn"] = False
            player["action_locked"] = False
            player["takeStaminaDebuff"] = False
            if player.get("debuffPower"):
                player["debuffPower"] = False
            player.pop("lastedBuff", None)
            player.pop("last_roll_log", None)
            player.pop("turn_stamina_before_roll", None)
            player["used_skills_this_turn"] = []
            player["blocked_count"] = 0
            player["blocking_penalty"] = 0.0
            player["drafting_active"] = False
            player["last_stamina_drain"] = 0
            if not player.get("lane_changed"):
                player["previous_lane"] = player.get(
                    "current_lane", player.get("previous_lane", 1)
                )

        game["turn_snapshot_scores"] = {
            user_id: player.get("score", 0) for user_id, player in players.items()
        }
        after_advance()
        return game["turn"]
