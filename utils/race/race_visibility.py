from __future__ import annotations

from utils.dice.dice_presets import DICE_PRESET, MAX_SPEED_PHASE
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

    player_avatar = player.get("thumnail") if player.get("is_mob") else player.get("avatar")
    player_avatar = player_avatar or player.get("avatar") or player.get("thumnail")

    return {
        "id": str(user_id),
        "name": _player_name(user_id, player),
        "username": player.get("username"),
        "avatar": str(player_avatar) if player_avatar else "",
        "thumbnail": str(player.get("thumnail") or ""),
        "style": player.get("style"),
        "score": player.get("score", 0),
        "rank": rank,
        "is_mob": bool(player.get("is_mob")),
        "mob_level": player.get("mob_level"),
        "mob_preset_key": player.get("mob_preset_key"),
        "last_roll_turn": player.get("last_roll_turn", -1),
        "has_rolled": player.get("last_roll_turn") == player.get("_current_turn"),
        "stamina_left": player.get("stamina_left", 0),
        "wit_mana": player.get("wit_mana", 0),
        "current_max_speed": player.get("current_max_speed", 0),
        "zone_left": player.get("zone_left", 0),
        "reroll_left": player.get("reroll_left", 0),
        "wit_reroll_left": player.get("wit_reroll_left", 0),
        "no_reroll_this_turn": bool(player.get("no_reroll_this_turn")),
        "used_block": bool(player.get("used_block")),
        "used_rush": bool(player.get("used_rush")),
        "action_locked": bool(player.get("action_locked")),
        "zone": player.get("zone"),
        "skills": skills,
        "last_roll": player.get("last_roll_log"),
        "latest_timing_result": player.get("web_latest_timing_result"),
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
    current_player = game.get("players", {}).get(str(user_id)) if user_id else None
    phase = game.get("phase")
    if game.get("ended"):
        phase = "ended"
    elif game.get("started"):
        phase = "running"
    else:
        phase = "waiting"
    timing_phase = _timing_phase(turn, max_turn, current_path_type)

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
        "timing_phase": timing_phase,
        "gameplay_mode": game.get("web_gameplay_mode", "manual"),
        "cycle_id": turn if game.get("started") else 0,
        "timing_gauge": build_timing_gauge_config(game, current_player),
        "timing_gauges": {
            str(player_id): build_timing_gauge_config(game, player)
            for player_id, player in game.get("players", {}).items()
        },
        "phase": phase,
        "status": "ended" if game.get("ended") else ("running" if game.get("started") else "waiting"),
        "awaiting_turn_confirm": bool(game.get("awaiting_turn_confirm")),
        "turn_confirmations": [str(user_id) for user_id in game.get("turn_confirmations", set())],
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
        "dice_presets": DICE_PRESET,
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
        "gameplay_mode": game.get("web_gameplay_mode", "manual"),
    }


def _timing_phase(turn: int, max_turn: int, path_type) -> str:
    if not turn or not max_turn:
        return "Waiting"
    progress = turn / max_turn
    path_label = str(PATH_TYPE_TEXT.get(path_type, "")).lower()
    if progress <= 0.1:
        return "Start"
    if progress <= 0.4:
        return "Early"
    if progress <= 0.7:
        return "Middle"
    if "corner" in path_label:
        return "Final Corner"
    return "Final Straight"


def build_timing_gauge_config(game: dict, player: dict | None) -> dict:
    player = player or {}
    style = player.get("style") or "Pace"
    style_rule = MAX_SPEED_PHASE.get(style, MAX_SPEED_PHASE["Pace"])
    turn = int(game.get("turn", 0))
    max_turn = max(1, int(game.get("max_turn", 1)))
    path_type = get_current_path_type(game) if turn else None
    phase = _timing_phase(turn, max_turn, path_type)
    current_speed = float(player.get("current_max_speed") or style_rule["start"])
    acceleration = max(0.0, current_speed - float(style_rule["start"]))

    phase_factor = {
        "Start": 0.92,
        "Early": 1.0,
        "Middle": 1.08,
        "Final Corner": 1.16,
        "Final Straight": 1.24,
    }.get(phase, 1.0)
    style_factor = {
        "Front": {"Start": 0.94, "Early": 0.98, "Final Straight": 1.12},
        "Pace": {},
        "Late": {"Start": 0.92, "Early": 0.96, "Final Corner": 1.1, "Final Straight": 1.14},
        "End": {"Start": 0.88, "Early": 0.92, "Final Corner": 1.14, "Final Straight": 1.22},
    }.get(style, {}).get(phase, 1.0)
    segment_factor = {1: 1.0, 2: 1.06, 3: 1.1, 4: 0.96}.get(path_type, 1.0)
    speed_factor = min(1.35, max(0.85, current_speed / max(1.0, float(style_rule["start"]))))
    marker_speed = phase_factor * style_factor * segment_factor * speed_factor

    return {
        "phase": phase,
        "style": style,
        "track_segment": PATH_TYPE_TEXT.get(path_type, "Waiting") if path_type else "Waiting",
        "current_speed": round(current_speed, 2),
        "acceleration": round(acceleration, 2),
        "marker_speed": round(marker_speed, 3),
        "half_cycle_ms": round(1450 / marker_speed),
    }
