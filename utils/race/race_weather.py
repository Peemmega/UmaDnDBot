from __future__ import annotations

import random


WEATHER_RULE = "Weather"
WEATHER_NONE = "none"
WEATHER_RANDOM = "random"
WEATHER_WARM = "warm"
WEATHER_SUNNY = "sunny"
WEATHER_RAIN = "rainy"
WEATHER_TYPES = (WEATHER_WARM, WEATHER_SUNNY, WEATHER_RAIN)
WEATHER_RULE_OPTIONS = (WEATHER_NONE, WEATHER_RANDOM, *WEATHER_TYPES)
WEATHER_LABELS = {
    WEATHER_NONE: "ไม่มีสภาพอากาศ",
    WEATHER_WARM: "อบอุ่น",
    WEATHER_SUNNY: "แดดจัด",
    WEATHER_RAIN: "ฝนตก",
}
LANE_COUNT = 6


def initialize_race_weather(game: dict) -> str:
    """Choose the race weather once, after the room rules have been locked."""
    rules = game.get("game_rules") or {}
    selection = str(rules.get(WEATHER_RULE, WEATHER_NONE) or WEATHER_NONE).lower()
    weather = random.choice(WEATHER_TYPES) if selection == WEATHER_RANDOM else selection
    if weather not in WEATHER_TYPES:
        weather = WEATHER_NONE
    game["weather"] = weather
    game["wet_lanes"] = []
    game["next_wet_lanes"] = []
    return weather


def weather_label(game: dict) -> str:
    return WEATHER_LABELS.get(game.get("weather"), WEATHER_LABELS[WEATHER_NONE])


def is_sunny(game: dict) -> bool:
    return game.get("weather") == WEATHER_SUNNY


def is_raining(game: dict) -> bool:
    return game.get("weather") == WEATHER_RAIN


def schedule_next_wet_lanes(game: dict) -> list[int]:
    """Pick the lanes that will be wet on the next non-final turn."""
    if not is_raining(game) or int(game.get("turn", 0) or 0) >= int(game.get("max_turn", 0) or 0):
        game["next_wet_lanes"] = []
        return []

    lane_count = random.randint(1, 2)
    lanes = sorted(random.sample(range(1, LANE_COUNT + 1), k=lane_count))
    game["next_wet_lanes"] = lanes
    return lanes


def advance_weather_turn(game: dict) -> list[int]:
    """Activate the lanes previewed at the end of the previous turn."""
    active_lanes = list(game.get("next_wet_lanes") or []) if is_raining(game) else []
    game["wet_lanes"] = active_lanes
    game["next_wet_lanes"] = []
    return active_lanes


def display_wet_lanes(game: dict) -> list[int]:
    """Use the next-turn preview during confirmation, otherwise active lanes."""
    if game.get("awaiting_turn_confirm"):
        return list(game.get("next_wet_lanes") or [])
    return list(game.get("wet_lanes") or [])


def is_wet_lane(game: dict, lane: int) -> bool:
    return is_raining(game) and int(lane or 0) in set(game.get("wet_lanes") or [])
