from __future__ import annotations

from typing import Any


APTITUDE_MODIFIER = {
    "G": 0.90,
    "F": 0.95,
    "E": 1.00,
    "D": 1.05,
    "C": 1.10,
    "B": 1.15,
    "A": 1.20,
    "S": 1.25,
}

APTITUDE_ORDER = ("G", "F", "E", "D", "C", "B", "A", "S")
NUMERIC_TO_APTITUDE_RANK = {
    index: rank for index, rank in enumerate(APTITUDE_ORDER, start=1)
}
STYLE_FIELD_MAP = {
    "Front": "front",
    "Pace": "pace",
    "Late": "late",
    "End": "end_style",
}


def normalize_aptitude_rank(rank: Any) -> str:
    if isinstance(rank, str):
        normalized = rank.strip().upper()
        if normalized in APTITUDE_MODIFIER:
            return normalized
        if normalized.isdigit():
            return NUMERIC_TO_APTITUDE_RANK.get(int(normalized), "E")
        return "E"

    if isinstance(rank, (int, float)):
        return NUMERIC_TO_APTITUDE_RANK.get(int(rank), "E")

    return "E"


def get_aptitude_modifier(rank: Any) -> float:
    return APTITUDE_MODIFIER.get(normalize_aptitude_rank(rank), 1.0)


def get_aptitude_percent(rank: Any) -> int:
    return int(round((get_aptitude_modifier(rank) - 1.0) * 100))


def format_aptitude_percent(rank: Any) -> str:
    percent = get_aptitude_percent(rank)
    return f"{percent:+d}%"


def get_aptitude_values(source: dict | None, surface: str | None, distance: str | None, style: str | None) -> dict:
    source = source or {}
    surface_key = "dirt" if str(surface or "").lower() == "dirt" else "turf"
    distance_key = str(distance or "medium").lower()
    style_key = STYLE_FIELD_MAP.get(style or "Pace", "pace")

    track_rank = normalize_aptitude_rank(source.get(surface_key, "E"))
    distance_rank = normalize_aptitude_rank(source.get(distance_key, "E"))
    style_rank = normalize_aptitude_rank(source.get(style_key, "E"))

    return {
        "track_field": surface_key,
        "distance_field": distance_key,
        "style_field": style_key,
        "track_rank": track_rank,
        "distance_rank": distance_rank,
        "style_rank": style_rank,
        "track_modifier": get_aptitude_modifier(track_rank),
        "distance_modifier": get_aptitude_modifier(distance_rank),
        "style_modifier": get_aptitude_modifier(style_rank),
    }


def _resolve_race_context(player: dict, race: dict | None) -> tuple[str, str, str]:
    race = race or {}
    track = race.get("track") or race.get("surface") or "turf"
    distance = race.get("distance") or "medium"
    style = player.get("style") or race.get("style") or "Pace"
    return str(track), str(distance), str(style)


def calculate_effective_race_stats(player: dict, race: dict | None) -> dict:
    race_profile = (player or {}).get("race_profile") or {}
    track, distance, style = _resolve_race_context(player or {}, race)
    aptitude = get_aptitude_values(race_profile, track, distance, style)

    base_speed = int(race_profile.get("speed", 0))
    base_power = int(race_profile.get("power", 0))
    base_wit = int(race_profile.get("wit", 0))
    base_wit_gain = 10 + base_wit * 2
    base_wit_requirement = base_wit * 25

    effective_speed = int(round(base_speed * aptitude["distance_modifier"]))
    effective_power = int(round(base_power * aptitude["track_modifier"]))
    effective_wit_gain = int(round(base_wit_gain * aptitude["style_modifier"]))
    effective_wit_requirement = int(round(base_wit_requirement * aptitude["style_modifier"]))
    return {
        "track_rank": aptitude["track_rank"],
        "distance_rank": aptitude["distance_rank"],
        "style_rank": aptitude["style_rank"],
        "track_modifier": aptitude["track_modifier"],
        "distance_modifier": aptitude["distance_modifier"],
        "style_modifier": aptitude["style_modifier"],
        "track_percent": get_aptitude_percent(aptitude["track_rank"]),
        "distance_percent": get_aptitude_percent(aptitude["distance_rank"]),
        "style_percent": get_aptitude_percent(aptitude["style_rank"]),
        "base_speed": base_speed,
        "base_power": base_power,
        "base_wit": base_wit,
        "base_wit_gain": base_wit_gain,
        "base_wit_requirement": base_wit_requirement,
        "effective_speed": effective_speed,
        "effective_power": effective_power,
        "effective_wit_gain": effective_wit_gain,
        "effective_wit_requirement": effective_wit_requirement,
    }


def build_aptitude_debug_lines(effective_stats: dict | None) -> list[str]:
    effective_stats = effective_stats or {}
    return [
        (
            f"Track Aptitude {effective_stats.get('track_rank', 'E')} "
            f"({effective_stats.get('track_percent', 0):+d}% Power)"
        ),
        (
            f"Distance Aptitude {effective_stats.get('distance_rank', 'E')} "
            f"({effective_stats.get('distance_percent', 0):+d}% Total)"
        ),
        (
            f"Style Aptitude {effective_stats.get('style_rank', 'E')} "
            f"({effective_stats.get('style_percent', 0):+d}% Wit)"
        ),
    ]


def get_roll_race_stats(player: dict) -> dict:
    race_profile = ((player or {}).get("race_profile") or {}).copy()
    effective_stats = (player or {}).get("effective_race_stats") or {}
    race_profile["power"] = int(effective_stats.get("effective_power", race_profile.get("power", 0)))
    return race_profile
