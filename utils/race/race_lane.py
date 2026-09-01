from __future__ import annotations

from typing import Iterable
from utils.race.rank_display import is_in_gold_range_against

LANE_MIN = 1
LANE_MAX = 6
LANE_DRAFT_FACTOR = 0.90
LANE_BLOCK_PENALTY_STEP = 0.10
LANE_BLOCK_PENALTY_CAP = 0.20
LANE_STAMINA_BASE_COSTS = {
    1: 90,
    2: 100,
    3: 110,
    4: 120,
    5: 130,
    6: 140,
}


def clamp_lane(lane: int | None) -> int:
    try:
        value = int(lane or LANE_MIN)
    except (TypeError, ValueError):
        value = LANE_MIN
    return max(LANE_MIN, min(LANE_MAX, value))


def get_default_lane(entry_number: int | None) -> int:
    try:
        entry = int(entry_number or LANE_MIN)
    except (TypeError, ValueError):
        entry = LANE_MIN
    return clamp_lane(((max(1, entry) - 1) // 2) + 1)


def get_lane_stamina_base_cost(player: dict) -> int:
    lane = clamp_lane(player.get("current_lane"))
    return LANE_STAMINA_BASE_COSTS[lane]


def get_lane_stamina_cost(player: dict, additional_drain: int = 0) -> int:
    """Return the lane's fixed base cost plus path/weather costs."""
    return get_lane_stamina_base_cost(player) + max(0, int(additional_drain or 0))


def get_player_lane(player: dict) -> int:
    return clamp_lane(player.get("current_lane"))


def _iter_players(players: dict | Iterable[dict]) -> Iterable[tuple[str | None, dict]]:
    if isinstance(players, dict):
        return players.items()
    return ((None, player) for player in players)


def calculate_lane_block_penalty(
    player: dict,
    players: dict | Iterable[dict],
    base_score: int,
    power_stat: int = 0,
) -> dict:
    my_lane = get_player_lane(player)
    my_position = int(player.get("score", 0) or 0)
    projected_position = my_position + int(base_score or 0)

    blocked_count = 0
    blocked_runner_ids: list[str] = []

    for player_id, target in _iter_players(players):
        if target is player:
            continue
        if get_player_lane(target) != my_lane:
            continue

        target_position = int(target.get("score", 0) or 0)
        if target_position <= my_position:
            continue
        if projected_position > target_position:
            blocked_count += 1
            if player_id is not None:
                blocked_runner_ids.append(str(player_id))

    raw_blocking_penalty = min(
        LANE_BLOCK_PENALTY_CAP, blocked_count * LANE_BLOCK_PENALTY_STEP
    )
    power_reduction = max(0.0, float(power_stat) / 100.0)
    blocking_penalty = max(0.0, raw_blocking_penalty - power_reduction)
    final_score = int(round(int(base_score or 0) * (1 - blocking_penalty)))

    return {
        "blocked_count": blocked_count,
        "raw_blocking_penalty": raw_blocking_penalty,
        "blocking_penalty": blocking_penalty,
        "final_score": final_score,
        "blocked_runner_ids": blocked_runner_ids,
    }


def has_drafting_bonus(player: dict, players: dict | Iterable[dict]) -> bool:
    my_lane = get_player_lane(player)
    my_position = int(player.get("score", 0) or 0)
    for _, target in _iter_players(players):
        if target is player:
            continue
        if get_player_lane(target) != my_lane:
            continue
        if int(target.get("score", 0) or 0) > my_position and is_in_gold_range_against(
            player, target
        ):
            return True
    return False


def resolve_pending_lane_changes(players: dict | Iterable[dict]) -> list[dict]:
    changed_players: list[dict] = []
    for _, player in _iter_players(players):
        current_lane = clamp_lane(player.get("current_lane"))
        pending_lane = player.get("pending_lane")
        player["previous_lane"] = current_lane
        player["lane_changed"] = False
        if pending_lane is None:
            player["current_lane"] = current_lane
            continue

        next_lane = clamp_lane(pending_lane)
        player["current_lane"] = next_lane
        player["pending_lane"] = None
        player["lane_changed"] = next_lane != current_lane
        if player["lane_changed"]:
            changed_players.append(player)
    return changed_players
