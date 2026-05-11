BASE_GOLD_RANGE = 20
GOLD_RANGE_MARKER = "✨"


def is_in_gold_range(user_id, info: dict, ranked_players, base_range: int = BASE_GOLD_RANGE) -> bool:
    score = info.get("score", 0)
    other_scores = [
        other_info.get("score", 0)
        for other_id, other_info in ranked_players
        if other_id != user_id
    ]

    if not other_scores:
        return False

    bonus = info.get("gold_range_bonus_this_turn", 0)
    penalty = info.get("enemy_gold_range_penalty_next_turn", 0)
    gold_range = max(1, base_range + bonus - penalty)

    return min(abs(score - other_score) for other_score in other_scores) <= gold_range


def gold_range_marker(user_id, info: dict, ranked_players) -> str:
    if is_in_gold_range(user_id, info, ranked_players):
        return f" {GOLD_RANGE_MARKER}"
    return ""
