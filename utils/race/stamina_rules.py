"""Canonical stamina calculations used by race rolls and skill effects."""

from __future__ import annotations

from dataclasses import dataclass

from utils.race.race_lane import get_lane_stamina_cost


SUNNY_STAMINA_COST = 10
DRAFTING_STAMINA_FACTOR = 0.90


@dataclass(frozen=True)
class RollStaminaCost:
    """Breakdown of the stamina consumed by one race roll."""

    lane_cost: int
    path_cost: int
    weather_cost: int
    total: int


def calculate_roll_stamina_cost(
    player: dict,
    path_effect: dict | None,
    *,
    uses_lane_system: bool,
    is_sunny: bool,
    has_drafting_bonus: bool,
) -> RollStaminaCost:
    """Return the single authoritative stamina formula for a race roll.

    Lane cost is included only for the Discord lane mode. Path and sunny
    weather costs apply in every mode. Drafting reduces the final drain by 10%.
    """
    effect = path_effect or {}
    path_cost = int(effect.get("stamina_cost", 0) or 0)
    weather_cost = SUNNY_STAMINA_COST if is_sunny else 0
    lane_cost = 0

    if uses_lane_system:
        base_lane_cost = get_lane_stamina_cost(player)
        configured_multiplier = effect.get("stamina_multiplier", 1.0)
        multiplier = float(1.0 if configured_multiplier is None else configured_multiplier)
        lane_cost = int(round(base_lane_cost * multiplier))

    total = lane_cost + path_cost + weather_cost
    if uses_lane_system and has_drafting_bonus:
        total = int(round(total * DRAFTING_STAMINA_FACTOR))

    return RollStaminaCost(
        lane_cost=lane_cost,
        path_cost=path_cost,
        weather_cost=weather_cost,
        total=total,
    )


def calculate_percent_stamina_amount(
    max_stamina: int | float,
    value: int | float,
    *,
    minimum: int = 1,
) -> int:
    """Convert a skill's 10%-unit stamina value into runtime STA units."""
    return max(
        minimum,
        int(round(max(0, float(max_stamina or 0)) * 0.10 * float(value or 0))),
    )
