"""Web timing race rules with no WebSocket or HTTP dependencies."""

from __future__ import annotations

import time
from typing import Callable

from utils.race.race_presets import get_web_race_finish_distance
from utils.race.web_timing_balance import (
    get_web_timing_snapshot,
    initialize_web_timing_player,
    refresh_web_timing_player,
    roll_web_timing_distance_gain,
)


def initialize_web_timing_race(
    game: dict,
    stage: dict,
    *,
    refresh_player: Callable[[dict, dict], object],
    start_delay_seconds: float,
    bot_half_cycle_seconds: Callable[[dict], float],
    timing_now: float | None = None,
    schedule_now: float | None = None,
) -> list[object]:
    """Initialize timing-race state and return players whose Zone activated."""
    timing_now = time.time() if timing_now is None else timing_now
    schedule_now = time.monotonic() if schedule_now is None else schedule_now
    game["finish_distance"] = get_web_race_finish_distance(stage)
    game["winner_id"] = None
    entered_zone: list[object] = []

    for player_id, player in game.get("players", {}).items():
        refresh_player(player, game)
        player.update(
            {
                "web_distance": 0,
                "score": 0,
                "web_timing_last_cycle": 0,
                "web_timing_submitted_cycles": set(),
                "web_latest_timing_result": None,
                "web_last_distance_gain": 0,
                "last_distance_gain": 0,
            }
        )
        if initialize_web_timing_player(
            player, game["finish_distance"], timing_now + start_delay_seconds
        ):
            entered_zone.append(player_id)
        if player.get("is_mob"):
            player["web_timing_next_auto_submit_at"] = (
                schedule_now + start_delay_seconds + bot_half_cycle_seconds(player)
            )
    return entered_zone


def apply_web_timing_gain(
    game: dict,
    user_id: object,
    *,
    cycle_id: int,
    timing_score: float,
    timing_offset: float,
) -> dict:
    """Apply one timing input and return transport-ready event data."""
    player = game.get("players", {}).get(str(user_id))
    if player is None:
        raise ValueError("Player is not in this race room")

    finish_distance = int(game.get("finish_distance") or 2000)
    zone_before = refresh_web_timing_player(player, finish_distance)
    base_gain, raw_distance_gain, timing_tier = roll_web_timing_distance_gain(
        player, timing_score
    )
    multiplier = raw_distance_gain / base_gain if base_gain else 0.0
    distance_gain = max(1, round(raw_distance_gain))
    distance = min(
        finish_distance, int(player.get("web_distance", 0) or 0) + distance_gain
    )
    player["web_distance"] = distance
    player["score"] = distance
    player["web_last_distance_gain"] = distance_gain
    player["last_distance_gain"] = distance_gain
    zone_after = refresh_web_timing_player(player, finish_distance, increase_speed=False)
    snapshot = get_web_timing_snapshot(player, finish_distance)

    result = {
        "base_gain": round(base_gain, 2),
        "timing_multiplier": round(multiplier, 3),
        "timing_score": round(timing_score, 3),
        "timing_offset": round(timing_offset, 3),
        "timing_tier": timing_tier,
        "total": distance_gain,
    }
    latest = {
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
    player["web_latest_timing_result"] = latest
    return {
        "player": player,
        "result": result,
        "latest": latest,
        "distance": distance,
        "distance_gain": distance_gain,
        "finished": distance >= finish_distance,
        "entered_zone": zone_before or zone_after,
    }
