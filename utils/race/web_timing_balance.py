from __future__ import annotations

import random
import time

from utils.dice.dice_presets import MAX_SPEED_PHASE


WEB_TIMING_TEMPO_TABLE = {
    "Front": {1: "H", 2: "N", 3: "N", 4: "M"},
    "Pace": {1: "M", 2: "M", 3: "M", 4: "M"},
    "Late": {1: "N", 2: "N", 3: "H", 4: "M"},
    "End": {1: "N", 2: "N", 3: "M", 4: "H"},
}

WEB_TIMING_TEMPO_CONFIG = {
    "N": {
        "label": "Normal",
        "speed_multiplier": 1.00,
        "acceleration_multiplier": 1.00,
        "gauge_speed_multiplier": 1.00,
    },
    "M": {
        "label": "Medium",
        "speed_multiplier": 1.12,
        "acceleration_multiplier": 1.10,
        "gauge_speed_multiplier": 1.12,
    },
    "H": {
        "label": "High",
        "speed_multiplier": 1.28,
        "acceleration_multiplier": 1.25,
        "gauge_speed_multiplier": 1.28,
    },
}

WEB_TIMING_ZONE_EFFECT = {
    "duration_seconds": 10.0,
    "speed_bonus": 1.20,
    "acceleration_bonus": 1.25,
    "gauge_speed_bonus": 1.10,
}

TIMING_RESULT_MULTIPLIERS = {
    "Perfect": 1.20,
    "Great": 1.05,
    "Good": 0.90,
    "Bad": 0.65,
    "Miss": 0.35,
}

MAX_WEB_TIMING_SPEED = 40.0
MAX_WEB_TIMING_ACCELERATION = 4.0
MAX_ACCELERATION_ELAPSED_SECONDS = 3.0


def get_web_timing_phase(distance: float, finish_distance: int) -> int:
    progress = max(0.0, float(distance)) / max(1, int(finish_distance))
    return min(4, max(1, int(progress * 4) + 1))


def get_tempo(style: str, phase: int) -> dict:
    level = WEB_TIMING_TEMPO_TABLE.get(style, WEB_TIMING_TEMPO_TABLE["Pace"]).get(phase, "N")
    return {"tempo_level": level, **WEB_TIMING_TEMPO_CONFIG[level]}


def get_zone_trigger_phase(style: str) -> int:
    return 4 if style == "Pace" else {"Front": 1, "Late": 3, "End": 4}.get(style, 4)


def get_timing_tier(score: float) -> str:
    if score >= 0.92:
        return "Perfect"
    if score >= 0.78:
        return "Great"
    if score >= 0.55:
        return "Good"
    if score >= 0.30:
        return "Bad"
    return "Miss"


def initialize_web_timing_player(player: dict, finish_distance: int, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    style = player.get("style") or "Pace"
    style_rule = MAX_SPEED_PHASE.get(style, MAX_SPEED_PHASE["Pace"])
    race_profile = player.get("race_profile") or {}
    player["web_timing_current_speed"] = max(0.0, float(style_rule["start"]))
    player["web_timing_base_acceleration"] = min(
        MAX_WEB_TIMING_ACCELERATION,
        max(0.1, 0.3 + (0.1 * float(race_profile.get("power", 1)))),
    )
    player["web_timing_speed_updated_at"] = now
    player["web_timing_phase"] = get_web_timing_phase(player.get("web_distance", 0), finish_distance)
    player["zone_active"] = False
    player["zone_started_at"] = None
    player["zone_ends_at"] = None
    player["active_zone_until"] = None
    player["zone_used"] = False
    player["zone_source"] = None
    activated = _activate_zone_if_ready(player, now)
    _sync_public_state(player, now)
    return activated


def refresh_web_timing_player(
    player: dict,
    finish_distance: int,
    now: float | None = None,
    *,
    increase_speed: bool = True,
) -> bool:
    now = time.time() if now is None else now
    _expire_zone(player, now)
    if increase_speed:
        previous_update = float(player.get("web_timing_speed_updated_at", now))
        elapsed = min(MAX_ACCELERATION_ELAPSED_SECONDS, max(0.0, now - previous_update))
        current_speed = max(0.0, float(player.get("web_timing_current_speed", 0.0)))
        current_speed += _effective_acceleration(player) * elapsed
        player["web_timing_current_speed"] = min(MAX_WEB_TIMING_SPEED, current_speed)
    player["web_timing_speed_updated_at"] = now

    old_phase = int(player.get("web_timing_phase", 1))
    new_phase = get_web_timing_phase(player.get("web_distance", 0), finish_distance)
    player["web_timing_phase"] = new_phase
    activated = old_phase != new_phase and _activate_zone_if_ready(player, now)
    _sync_public_state(player, now)
    return activated


def get_web_timing_snapshot(player: dict, finish_distance: int, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    _expire_zone(player, now)
    player["web_timing_phase"] = get_web_timing_phase(player.get("web_distance", 0), finish_distance)
    _sync_public_state(player, now)
    return {
        "phase": player.get("web_timing_phase", 1),
        "tempo_level": player.get("tempo_level", "N"),
        "tempo_label": player.get("tempo_label", "Normal"),
        "speed_multiplier": player.get("speed_multiplier", 1.0),
        "acceleration_multiplier": player.get("acceleration_multiplier", 1.0),
        "gauge_speed_multiplier": player.get("gauge_speed_multiplier", 1.0),
        "current_speed": player.get("current_speed", 0),
        "acceleration": player.get("acceleration", 0),
        "zone_active": player.get("zone_active", False),
        "zone_started_at": player.get("zone_started_at"),
        "zone_ends_at": player.get("zone_ends_at"),
        "active_zone_until": player.get("active_zone_until"),
        "zone_remaining_seconds": player.get("zone_remaining_seconds", 0),
        "zone_used": player.get("zone_used", False),
        "zone_name": player.get("zone_name"),
        "zone_source": player.get("zone_source"),
    }


def roll_web_timing_distance_gain(player: dict, timing_score: float) -> tuple[float, float, str]:
    current_speed = max(0.0, float(player.get("current_speed", 0.0)))
    base_gain = random.uniform(current_speed / 2.0, current_speed)
    tier = get_timing_tier(timing_score)
    return base_gain, base_gain * TIMING_RESULT_MULTIPLIERS[tier], tier


def _activate_zone_if_ready(player: dict, now: float) -> bool:
    style = player.get("style") or "Pace"
    if player.get("zone_used") or int(player.get("web_timing_phase", 1)) != get_zone_trigger_phase(style):
        return False
    ends_at = now + WEB_TIMING_ZONE_EFFECT["duration_seconds"]
    player["zone_active"] = True
    player["zone_started_at"] = now
    player["zone_ends_at"] = ends_at
    player["active_zone_until"] = ends_at
    player["zone_used"] = True
    player["zone_name"] = (player.get("zone") or {}).get("name") or f"{style} Zone"
    player["zone_source"] = f"{style} Phase {player['web_timing_phase']}"
    return True


def _expire_zone(player: dict, now: float) -> None:
    if player.get("zone_active") and now >= float(player.get("zone_ends_at") or 0):
        player["zone_active"] = False


def _effective_acceleration(player: dict) -> float:
    phase = int(player.get("web_timing_phase", 1))
    tempo = get_tempo(player.get("style") or "Pace", phase)
    zone_bonus = WEB_TIMING_ZONE_EFFECT["acceleration_bonus"] if player.get("zone_active") else 1.0
    return min(
        MAX_WEB_TIMING_ACCELERATION,
        max(0.0, float(player.get("web_timing_base_acceleration", 0.1)) * tempo["acceleration_multiplier"] * zone_bonus),
    )


def _sync_public_state(player: dict, now: float) -> None:
    tempo = get_tempo(player.get("style") or "Pace", int(player.get("web_timing_phase", 1)))
    zone_active = bool(player.get("zone_active"))
    speed_bonus = WEB_TIMING_ZONE_EFFECT["speed_bonus"] if zone_active else 1.0
    gauge_bonus = WEB_TIMING_ZONE_EFFECT["gauge_speed_bonus"] if zone_active else 1.0
    player["tempo_level"] = tempo["tempo_level"]
    player["tempo_label"] = tempo["label"]
    player["speed_multiplier"] = tempo["speed_multiplier"]
    player["acceleration_multiplier"] = tempo["acceleration_multiplier"]
    player["gauge_speed_multiplier"] = round(tempo["gauge_speed_multiplier"] * gauge_bonus, 3)
    player["current_speed"] = round(
        min(MAX_WEB_TIMING_SPEED, max(0.0, float(player.get("web_timing_current_speed", 0.0)) * tempo["speed_multiplier"] * speed_bonus)),
        2,
    )
    player["acceleration"] = round(_effective_acceleration(player), 2)
    player["zone_remaining_seconds"] = round(
        max(0.0, float(player.get("zone_ends_at") or 0.0) - now) if zone_active else 0.0,
        1,
    )
