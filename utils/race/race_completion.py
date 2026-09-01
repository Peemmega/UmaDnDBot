"""Shared, transport-neutral race completion state transition."""

from __future__ import annotations


def rank_race_players(game: dict) -> list[tuple[object, dict]]:
    """Return final standings using the active race mode's progress metric."""
    timing_mode = game.get("race_mode") == "web_timing"
    return sorted(
        game.get("players", {}).items(),
        key=lambda item: int(
            item[1].get("web_distance", item[1].get("score", 0))
            if timing_mode
            else item[1].get("score", 0)
        ),
        reverse=True,
    )


def serialize_race_standing(item: tuple[object, dict], rank: int = 1) -> dict:
    player_id, player = item
    distance = int(player.get("web_distance", player.get("score", 0)) or 0)
    return {
        "rank": rank,
        "id": str(player_id),
        "name": player.get("display_name") or player.get("username") or str(player_id),
        "style": player.get("style"),
        "score": int(player.get("score", 0) or 0),
        "distance": distance,
        "is_mob": bool(player.get("is_mob")),
    }


def complete_race(
    game: dict,
    *,
    ranked_players: list[tuple[object, dict]] | None = None,
    winner_id: object | None = None,
) -> tuple[list[tuple[object, dict]], dict]:
    """Finalize state exactly once and return standings plus a serializable result.

    Persistence, messaging, and socket broadcasts deliberately remain with
    their transports. This function only applies the race rule/state change.
    """
    ranked = ranked_players if ranked_players is not None else rank_race_players(game)
    if winner_id is None and ranked:
        winner_id = ranked[0][0]

    winner = next(
        (item for item in ranked if str(item[0]) == str(winner_id)),
        ranked[0] if ranked else None,
    )
    result = {
        "winner": serialize_race_standing(winner) if winner else None,
        "rankings": [
            serialize_race_standing(item, rank)
            for rank, item in enumerate(ranked, start=1)
        ],
    }
    game["winner_id"] = str(winner_id) if winner_id is not None else None
    game["result"] = result
    game["ended"] = True
    game["started"] = False
    game["phase"] = "ended"
    return ranked, result


def finalize_race(
    game: dict,
    *,
    ranked_players: list[tuple[object, dict]] | None = None,
    winner_id: object | None = None,
) -> tuple[list[tuple[object, dict]], dict, str]:
    """Complete the race and persist its final snapshot through one pathway."""
    # Imported lazily so the state transition stays usable for an admin abort
    # even when the history database is unavailable.
    from utils.race.race_history import save_completed_race

    ranked, result = complete_race(
        game, ranked_players=ranked_players, winner_id=winner_id
    )
    return ranked, result, save_completed_race(game, ranked)
