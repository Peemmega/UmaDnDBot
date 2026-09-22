BASE_GOLD_RANGE = 20
GOLD_RANGE_MARKER = "✨"
GOLD_LANE_TOLERANCE = 1


def get_player_lane(info: dict) -> int:
    try:
        return int(info.get("current_lane", info.get("entry_number", 1)) or 1)
    except (TypeError, ValueError):
        return 1


def get_gold_range_value(info: dict, base_range: int = BASE_GOLD_RANGE) -> int:
    bonus = int(info.get("gold_range_bonus_this_turn", 0) or 0)
    penalty = abs(int(info.get("enemy_gold_range_penalty_next_turn", 0) or 0))
    return max(1, base_range + bonus - penalty)


def get_gold_lane_tolerance(
    info: dict, base_tolerance: int = GOLD_LANE_TOLERANCE
) -> int:
    bonus = int(info.get("gold_lane_bonus_this_turn", 0) or 0)
    penalty = abs(int(info.get("enemy_gold_lane_penalty_next_turn", 0) or 0))
    return max(0, base_tolerance + bonus - penalty)


def is_in_gold_range_against(
    info: dict,
    other_info: dict,
    *,
    base_range: int = BASE_GOLD_RANGE,
    lane_tolerance: int = GOLD_LANE_TOLERANCE,
) -> bool:
    score = int(info.get("score", 0) or 0)
    other_score = int(other_info.get("score", 0) or 0)
    if abs(score - other_score) > get_gold_range_value(info, base_range):
        return False
    effective_lane_tolerance = get_gold_lane_tolerance(info, lane_tolerance)
    return (
        abs(get_player_lane(info) - get_player_lane(other_info))
        <= effective_lane_tolerance
    )


def count_gold_range_players(
    user_id,
    info: dict,
    ranked_players,
    base_range: int = BASE_GOLD_RANGE,
) -> int:
    return sum(
        1
        for other_id, other_info in ranked_players
        if other_id != user_id
        and is_in_gold_range_against(info, other_info, base_range=base_range)
    )


def is_in_gold_range(
    user_id, info: dict, ranked_players, base_range: int = BASE_GOLD_RANGE
) -> bool:
    return count_gold_range_players(user_id, info, ranked_players, base_range) > 0


def gold_range_marker(user_id, info: dict, ranked_players) -> str:
    if is_in_gold_range(user_id, info, ranked_players):
        return f" {GOLD_RANGE_MARKER}"
    return ""
