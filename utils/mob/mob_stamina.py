"""Forecast remaining Mob stamina using the race's real cost rules."""

from utils.race.race_lane import has_drafting_bonus
from utils.race.race_tracks import get_path_effect
from utils.race.race_weather import is_sunny
from utils.race.runtime_stamina import runtime_stamina_from_stat
from utils.race.stamina_rules import calculate_roll_stamina_cost


def forecast_stamina(game, user_id, next_lane=None):
    """Project the race on inner lane 2, allowing for the next lane choice.

    Current and next-turn Draft use observed positions. Later Draft, healing,
    and opponent actions are uncertain and are not assumed by this forecast.
    """
    player = game["players"][user_id]
    current_turn = int(game.get("turn", 1))
    last_turn = int(game.get("max_turn", 1))
    rolled = player.get("last_roll_turn") == current_turn
    first_turn = current_turn + int(rolled)
    path = game.get("path") or []
    uses_lane = game.get("race_mode", "discord_classic") != "web_timing"
    current_lane = int(player.get("current_lane", 1) or 1)
    if next_lane is None:
        next_lane = player.get("pending_lane") or 2
    next_lane = int(next_lane)
    stats = player.get("race_profile") or {}
    maximum = int(player.get("max_stamina", 0) or 0)
    if maximum <= 0:
        maximum = runtime_stamina_from_stat(int(stats.get("stamina", 0) or 0))
    starting_stamina = max(0, int(player.get("stamina_left", maximum)))
    remaining = starting_stamina
    total_cost = 0
    shortage_turns = []
    turns = []

    for turn in range(first_turn, last_turn + 1):
        lane = current_lane if turn == current_turn else next_lane if turn == current_turn + 1 else 2
        path_type = path[min(turn - 1, len(path) - 1)] if path else 1
        path_effect = get_path_effect(path_type, dict(player), stats)
        draft = False
        if uses_lane and turn in (current_turn, current_turn + 1):
            # The current roll uses the turn snapshot. For the next roll use
            # latest observed scores and queued lanes as a provisional estimate.
            snapshot = (game.get("turn_snapshot_scores") or {}) if turn == current_turn else {}
            predicted = {
                pid: {
                    **other,
                    "score": snapshot.get(pid, other.get("score", 0)),
                    "current_lane": (other.get("current_lane", 1) if turn == current_turn else other.get("pending_lane") or other.get("current_lane", 1)),
                }
                for pid, other in game["players"].items()
            }
            predicted[user_id]["current_lane"] = lane
            draft = has_drafting_bonus(predicted[user_id], predicted)
        cost = calculate_roll_stamina_cost(
            {**player, "current_lane": lane}, path_effect,
            uses_lane_system=uses_lane, is_sunny=is_sunny(game),
            has_drafting_bonus=draft, turn=turn,
        ).total
        before = remaining
        if cost > remaining:
            shortage_turns.append(turn)
        remaining = max(0, remaining - cost)
        total_cost += cost
        turns.append({"turn": turn, "lane": lane, "path_type": path_type, "draft": draft, "cost": cost, "stamina_before": before})

    return {
        "start_turn": first_turn,
        "starting_stamina": starting_stamina,
        "estimated_cost": total_cost,
        "estimated_remaining": remaining,
        "shortfall": max(0, total_cost - starting_stamina),
        "can_finish": not shortage_turns,
        "shortage_turns": shortage_turns,
        "turns": turns,
    }
