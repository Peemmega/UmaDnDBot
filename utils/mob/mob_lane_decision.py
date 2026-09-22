"""Lane-choice strategy for race Mobs."""

from __future__ import annotations

import random

from utils.mob.mob_board_state import get_current_path_type
from utils.mob.mob_profiles import get_ai_profile
from utils.race.race_dice import get_phase_from_turn
from utils.race.rank_display import get_gold_range_value
from utils.race.race_weather import is_raining

MOB_LANE_NON_TACTICAL_CROWDING_PENALTY = 42
MOB_WET_LANE_PENALTY = 180

def _player_lane(player: dict) -> int:
    try:
        return int(player.get("current_lane", player.get("entry_number", 1)) or 1)
    except (TypeError, ValueError):
        return 1


def _planned_lane(player: dict) -> int:
    """Use queued lane changes when predicting where competitors will be."""
    try:
        pending_lane = player.get("pending_lane")
        if pending_lane is not None:
            return int(pending_lane)
    except (TypeError, ValueError):
        pass
    return _player_lane(player)


def _planned_lane_occupancy(players: dict, target_lane: int, *, user_id) -> int:
    return sum(
        1
        for other_id, other in players.items()
        if other_id != user_id and _planned_lane(other) == target_lane
    )


def _gold_count_for_lane(player: dict, players: dict, target_lane: int, *, user_id) -> int:
    my_score = int(player.get("score", 0) or 0)
    gold_range = get_gold_range_value(player)
    count = 0
    for other_id, other in players.items():
        if other_id == user_id:
            continue
        if abs(int(other.get("score", 0) or 0) - my_score) > gold_range:
            continue
        if abs(_planned_lane(other) - target_lane) > 1:
            continue
        count += 1
    return count


def _front_gaps_for_lane(player: dict, players: dict, target_lane: int, *, user_id) -> list[int]:
    my_score = int(player.get("score", 0) or 0)
    gaps: list[int] = []
    for other_id, other in players.items():
        if other_id == user_id:
            continue
        if _planned_lane(other) != target_lane:
            continue
        other_score = int(other.get("score", 0) or 0)
        if other_score > my_score:
            gaps.append(other_score - my_score)
    gaps.sort()
    return gaps


def _immediate_push_score(player: dict) -> int:
    return (
        int(player.get("next_roll_flat_bonus", 0) or 0)
        + int(player.get("next_roll_floor_bonus", 0) or 0)
        + int(player.get("next_roll_cap_bonus", 0) or 0)
        + (int(player.get("next_roll_add_d", 0) or 0) * 24)
        + (int(player.get("next_roll_add_kh", 0) or 0) * 28)
    )


def decide_mob_target_lane(game, user_id) -> int | None:
    player = game["players"].get(user_id)
    if not player:
        return None

    players = game.get("players", {})
    current_lane = _player_lane(player)
    phase = get_phase_from_turn(game.get("turn", 1), game.get("max_turn", 20))
    path_type = get_current_path_type(game)
    style = str(player.get("style", "Pace"))
    estimated_gain = max(80, int(player.get("current_max_speed", 0) or 0))
    immediate_push = _immediate_push_score(player)
    gold_range = get_gold_range_value(player)
    current_gold_count = _gold_count_for_lane(player, players, current_lane, user_id=user_id)
    current_front_gaps = _front_gaps_for_lane(player, players, current_lane, user_id=user_id)
    current_likely_blockers = sum(1 for gap in current_front_gaps if gap <= estimated_gain)
    preview_wet_lanes = {
        int(lane)
        for lane in (game.get("next_wet_lanes") or [])
        if str(lane).isdigit() and 1 <= int(lane) <= 6
    } if is_raining(game) else set()

    lane_scores: list[tuple[int, int]] = []

    for target_lane in range(1, 7):
        gold_count = _gold_count_for_lane(player, players, target_lane, user_id=user_id)
        front_gaps = _front_gaps_for_lane(player, players, target_lane, user_id=user_id)
        same_lane_front = len(front_gaps)
        same_lane_front_in_gold = sum(1 for gap in front_gaps if gap <= gold_range)
        likely_blockers = sum(1 for gap in front_gaps if gap <= estimated_gain)
        planned_occupancy = _planned_lane_occupancy(
            players,
            target_lane,
            user_id=user_id,
        )
        nearest_front_gap = front_gaps[0] if front_gaps else None

        score = 0
        blocker_relief = current_likely_blockers - likely_blockers
        lane_shift = abs(target_lane - current_lane)
        downhill = path_type == 4
        uphill = path_type == 3

        # Base preference: stay lower to conserve stamina, especially lane 1.
        score -= (target_lane - 1) * 22
        if target_lane == 1:
            score += 26
        elif target_lane == 2:
            score += 10

        # A Mob can choose a lane after the rain preview appears in turn
        # confirmation.  Avoid lanes that will be wet on the next turn, where
        # they would halve acceleration, unless the tactical tradeoff is large.
        if target_lane in preview_wet_lanes:
            score -= MOB_WET_LANE_PENALTY

        # Only move out when there is a concrete payoff.
        score += blocker_relief * 34
        score += gold_count * 10
        score += same_lane_front_in_gold * 18
        score -= likely_blockers * 24
        score -= max(0, same_lane_front - likely_blockers) * 7

        # Keep anti-clumping as a tie-breaker.  A lane with a runner ahead is
        # strategically meaningful: it can provide Draft or must be assessed
        # for a Block.  Do not let population alone override those calculations.
        if planned_occupancy and same_lane_front == 0:
            score -= planned_occupancy * MOB_LANE_NON_TACTICAL_CROWDING_PENALTY

        if same_lane_front == 0:
            score += 14 if phase >= 3 else 6

        if nearest_front_gap is not None and nearest_front_gap <= 25:
            score -= 12

        if downhill:
            score += blocker_relief * 16
            score -= likely_blockers * 12
            if same_lane_front == 0:
                score += 18
            if target_lane >= 4 and likely_blockers == 0:
                score += 10

        if uphill:
            score -= max(0, target_lane - 1) * 16
            score -= lane_shift * 8
            if target_lane >= 4:
                score -= 20
            if target_lane > current_lane:
                score -= 10
            if blocker_relief >= 2:
                score += 10

        # Leaving the pack can be good if the current lane is crowded and target lane goes white.
        if current_gold_count > 0 and gold_count == 0:
            score += 16
        elif current_gold_count == 0 and gold_count > 0:
            score += 6

        if style in {"Front", "Pace"}:
            if phase <= 2:
                score += gold_count * 8
            else:
                score -= likely_blockers * 8
            if target_lane > 2 and blocker_relief <= 0:
                score -= 18

        if style in {"Late", "End"}:
            if phase >= 3 and same_lane_front == 0:
                score += 24
            if phase >= 3 and likely_blockers > 0:
                score -= 10
            if gold_count == 0 and blocker_relief > 0:
                score += 12

        if phase >= 3:
            score += max(0, 3 - target_lane) * 8
        if phase >= 4:
            score += max(0, 2 - target_lane) * 10

        score -= lane_shift * 5
        if target_lane == current_lane:
            score += 8

        # Hard discourage climbing outward without enough upside.
        if target_lane > current_lane and blocker_relief <= 0 and gold_count >= current_gold_count:
            score -= 20
        if target_lane >= 4 and blocker_relief < 2:
            score -= 22

        safe_to_press = (
            likely_blockers == 0
            and (nearest_front_gap is None or nearest_front_gap > estimated_gain + gold_range)
        )
        if style in {"Front", "Pace"} and safe_to_press:
            score += 14
            if immediate_push >= 20:
                score += 14
            if downhill:
                score += 8
        elif style in {"Late", "End"} and uphill and lane_shift > 0 and blocker_relief <= 0:
            score -= 10

        lane_scores.append((score, target_lane))

    lane_scores.sort(reverse=True)
    profile = get_ai_profile(player)
    candidate_count = min(profile["lane_candidates"], len(lane_scores))
    # Lower levels deliberately pick among good-enough lanes, while high levels
    # always take the best evaluated lane.
    return random.choice(lane_scores[:candidate_count])[1]

# =========================================================
# FUTURE DICE EVALUATION
# =========================================================


