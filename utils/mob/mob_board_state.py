"""Read-only race-board helpers for Mob AI."""

from __future__ import annotations

def get_position_groups(game, user_id):
    if game is None:
        return {"middle"}

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"]
        for uid, p in game["players"].items()
    }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    total = len(ranked)

    if total <= 1:
        return {"front"}

    for index, (uid, _) in enumerate(ranked):
        if uid != user_id:
            continue

        # rank เริ่มที่ 1
        rank = index + 1

        groups = set()

        ratio = rank / total

        # =====================
        # FRONT
        # top ~55%
        # =====================
        if ratio <= 0.55:
            groups.add("front")

        # =====================
        # MIDDLE
        # overlap หนัก
        # =====================
        if 0.25 <= ratio <= 0.80:
            groups.add("middle")

        # =====================
        # BACK
        # bottom ~55%
        # =====================
        if ratio >= 0.45:
            groups.add("back")

        return groups

    return {"middle"}


def get_distance_to_front(game, user_id):
    player_score = game["players"][user_id].get("score", 0)

    front_scores = [
        p.get("score", 0)
        for pid, p in game["players"].items()
        if pid != user_id
    ]

    if not front_scores:
        return 0

    front_score = max(front_scores)

    return front_score - player_score


def get_nearby_count(game, user_id):
    player_score = game["players"][user_id].get("score", 0)

    count = 0

    for pid, other in game["players"].items():
        if pid == user_id:
            continue

        if abs(other.get("score", 0) - player_score) <= 20:
            count += 1

    return count


def get_current_path_type(game):
    if game.get("current_path_type") is not None:
        return game["current_path_type"]

    path = game.get("path") or []
    if not path:
        return 1

    turn = game.get("turn", 1)
    index = max(0, min(turn - 1, len(path) - 1))
    return path[index]

