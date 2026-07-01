from __future__ import annotations

from typing import Iterable

LANE_MIN = 1
LANE_MAX = 6
LANE_BASE_DRAIN = 100
LANE_COST_STEP = 5
LANE_DRAFT_FACTOR = 0.90
LANE_BLOCK_PENALTY_STEP = 0.10
LANE_BLOCK_PENALTY_CAP = 0.50


def clamp_lane(lane: int | None) -> int:
    try:
        value = int(lane or LANE_MIN)
    except (TypeError, ValueError):
        value = LANE_MIN
    return max(LANE_MIN, min(LANE_MAX, value))


def get_default_lane(entry_number: int | None) -> int:
    return clamp_lane(entry_number or LANE_MIN)


def get_lane_stamina_cost(player: dict) -> int:
    lane = clamp_lane(player.get("current_lane"))
    return (lane - 1) * LANE_COST_STEP


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

    blocking_penalty = min(LANE_BLOCK_PENALTY_CAP, blocked_count * LANE_BLOCK_PENALTY_STEP)
    final_score = int(round(int(base_score or 0) * (1 - blocking_penalty)))

    return {
        "blocked_count": blocked_count,
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
        if int(target.get("score", 0) or 0) > my_position:
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
