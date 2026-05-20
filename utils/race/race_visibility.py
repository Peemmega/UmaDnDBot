from __future__ import annotations

from utils.race.race_dice import get_phase_from_turn
from utils.race.race_presets import (
    PATH_TYPE_ICON,
    PATH_TYPE_TEXT,
    RACE_PRESET,
    get_current_path_type,
)
from utils.skill.skill_presets import SKILLS


def _player_name(user_id, player: dict) -> str:
    return (
        player.get("display_name")
        or player.get("username")
        or player.get("name")
        or str(user_id)
    )


def serialize_player(user_id, player: dict, rank: int | None = None) -> dict:
    skill_slots = player.get("skills") or {}
    skills = []
    for slot in (1, 2, 3, 4):
        skill_id = skill_slots.get(slot) or skill_slots.get(str(slot))
        skill = SKILLS.get(skill_id) if skill_id else None
        cooldowns = player.get("skill_cooldowns") or {}
        skills.append({
            "slot": slot,
            "id": skill_id,
            "name": skill.get("name") if skill else None,
            "icon": skill.get("icon") if skill else None,
            "cost": skill.get("cost", 0) if skill else 0,
            "cooldown": cooldowns.get(skill_id, 0) if skill_id else 0,
        })

    return {
        "id": str(user_id),
        "name": _player_name(user_id, player),
        "username": player.get("username"),
        "avatar": player.get("avatar") or player.get("thumnail"),
        "style": player.get("style"),
        "score": player.get("score", 0),
        "rank": rank,
        "is_mob": bool(player.get("is_mob")),
        "mob_level": player.get("mob_level"),
        "last_roll_turn": player.get("last_roll_turn", -1),
        "has_rolled": player.get("last_roll_turn") == player.get("_current_turn"),
        "stamina_left": player.get("stamina_left", 0),
        "wit_mana": player.get("wit_mana", 0),
        "current_max_speed": player.get("current_max_speed", 0),
        "zone_left": player.get("zone_left", 0),
        "used_block": bool(player.get("used_block")),
        "used_rush": bool(player.get("used_rush")),
        "action_locked": bool(player.get("action_locked")),
        "zone": player.get("zone"),
        "skills": skills,
        "last_roll": player.get("last_roll_log"),
        "buffs": {
            "flat": player.get("next_roll_flat_bonus", 0),
            "dice": player.get("next_roll_add_d", 0),
            "keep_highest": player.get("next_roll_add_kh", 0),
            "floor": player.get("next_roll_floor_bonus", 0),
            "selected": player.get("next_roll_selected_die_bonus", 0),
            "cap": player.get("next_roll_cap_bonus", 0),
        },
    }


def serialize_room(game: dict, room_id: str | None = None, user_id: str | None = None) -> dict:
    ranked = sorted(
        game.get("players", {}).items(),
        key=lambda item: item[1].get("score", 0),
        reverse=True,
    )
    rank_by_id = {player_id: index for index, (player_id, _) in enumerate(ranked, start=1)}

    players = []
    for player_id, player in game.get("players", {}).items():
        player["_current_turn"] = game.get("turn", 0)
        players.append(serialize_player(player_id, player, rank_by_id.get(player_id)))
        player.pop("_current_turn", None)

    stage_key = game.get("stage_key")
    preset = RACE_PRESET.get(stage_key, {})
    turn = game.get("turn", 0)
    max_turn = game.get("max_turn", 0)
    current_path_type = get_current_path_type(game) if turn else None
    owner_id = str(game.get("owner_id"))
    phase = game.get("phase")
    if game.get("ended"):
        phase = "ended"
    elif game.get("started"):
        phase = "running"
    else:
        phase = "waiting"

    return {
        "room_id": room_id or str(game.get("room_id") or ""),
        "room_code": (room_id or str(game.get("room_id") or ""))[-6:].upper(),
        "owner_id": owner_id,
        "my_player_id": str(user_id) if user_id else None,
        "stage_key": stage_key,
        "race_name": game.get("stage_name"),
        "track": game.get("track"),
        "distance": game.get("distance"),
        "image": preset.get("image"),
        "thumbnail": preset.get("thumnail"),
        "turn": turn,
        "max_turn": max_turn,
        "race_phase": get_phase_from_turn(turn, max_turn) if turn else 0,
        "phase": phase,
        "status": "ended" if game.get("ended") else ("running" if game.get("started") else "waiting"),
        "path": [
            {
                "turn": index,
                "type": path_type,
                "label": PATH_TYPE_TEXT.get(path_type, "Straight"),
                "icon": PATH_TYPE_ICON.get(path_type, "->"),
                "active": index == turn,
            }
            for index, path_type in enumerate(game.get("path", []), start=1)
        ],
        "current_path": {
            "type": current_path_type,
            "label": PATH_TYPE_TEXT.get(current_path_type, "Waiting") if current_path_type else "Waiting",
            "icon": PATH_TYPE_ICON.get(current_path_type, "-") if current_path_type else "-",
        },
        "players": players,
        "scoreboard": sorted(players, key=lambda item: item["score"], reverse=True),
        "action_logs": game.get("web_action_logs", [])[-80:],
        "turn_score_logs": game.get("turn_score_logs", [])[-80:],
        "result": game.get("result"),
    }


def serialize_room_summary(game: dict, room_id: str) -> dict:
    return {
        "room_id": room_id,
        "room_code": room_id[-6:].upper(),
        "phase": "ended" if game.get("ended") else ("running" if game.get("started") else "waiting"),
        "race_name": game.get("stage_name"),
        "stage_key": game.get("stage_key"),
        "thumbnail": RACE_PRESET.get(game.get("stage_key"), {}).get("thumnail"),
        "turn": game.get("turn", 0),
        "max_turn": game.get("max_turn", 0),
        "player_count": len(game.get("players", {})),
        "human_count": len([
            player for player in game.get("players", {}).values()
            if not player.get("is_mob")
        ]),
        "mob_count": len([
            player for player in game.get("players", {}).values()
            if player.get("is_mob")
        ]),
        "max_players": 18,
    }
