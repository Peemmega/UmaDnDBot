from __future__ import annotations

import time

from utils.database import get_player
from utils.dice.dice_presets import DICE_PRESET, MAX_SPEED_PHASE
from utils.profile_images import (
    is_local_filesystem_path,
    resolve_player_avatar_url,
    resolve_public_url,
)
from utils.race.race_dice import get_phase_from_turn
from utils.race.race_presets import (
    PATH_TYPE_ICON,
    PATH_TYPE_TEXT,
    RACE_PRESET,
    get_current_path_type,
    get_web_race_finish_distance,
)
from utils.race.runtime_stamina import get_runtime_stamina_snapshot
from utils.skill.skill_presets import SKILLS
from utils.race.web_timing_balance import get_web_timing_phase, get_web_timing_snapshot
from utils.race.web_timing_config import (
    DEFAULT_GAUGE_HALF_CYCLE_MS,
    WEB_TIMING_GAUGE_HALF_CYCLE_MS,
    get_web_timing_ui_config,
)


def _player_name(user_id, player: dict) -> str:
    return (
        player.get("display_name")
        or player.get("username")
        or player.get("name")
        or str(user_id)
    )


def serialize_player(
    user_id,
    player: dict,
    rank: int | None = None,
    finish_distance: int | None = None,
    viewer_id: str | None = None,
) -> dict:
    if not str(user_id).startswith("mob_") and not player.get("is_mob"):
        db_player = get_player(user_id)
        if db_player:
            player["username"] = db_player.get("username") or player.get("username")
            player["profile_image_url"] = db_player.get("profile_image_url") or ""

    skill_slots = player.get("skills") or {}
    skills = []
    for slot in (1, 2, 3, 4):
        skill_id = skill_slots.get(slot) or skill_slots.get(str(slot))
        skill = SKILLS.get(skill_id) if skill_id else None
        cooldowns = player.get("skill_cooldowns") or {}
        skills.append(
            {
                "slot": slot,
                "id": skill_id,
                "name": skill.get("name") if skill else None,
                "icon": skill.get("icon") if skill else None,
                "cost": skill.get("cost", 0) if skill else 0,
                "cooldown": cooldowns.get(skill_id, 0) if skill_id else 0,
            }
        )

    player_avatar = resolve_player_avatar_url(player)
    raw_thumbnail = player.get("thumnail") or player.get("thumbnail") or ""
    player_thumbnail = (
        ""
        if is_local_filesystem_path(raw_thumbnail)
        else resolve_public_url(raw_thumbnail)
    )
    if not player_thumbnail:
        player_thumbnail = str(player_avatar) if player_avatar else ""

    distance = int(player.get("web_distance", player.get("score", 0)))
    distance_limit = max(1, int(finish_distance or 1))
    progress_ratio = (
        min(1.0, max(0.0, distance / distance_limit)) if finish_distance else 0.0
    )
    timing_state = (
        get_web_timing_snapshot(player, distance_limit) if finish_distance else {}
    )

    stamina_snapshot = get_runtime_stamina_snapshot(player)
    return {
        "id": str(user_id),
        "user_id": str(user_id),
        "name": _player_name(user_id, player),
        "username": player.get("username"),
        "avatar": str(player_avatar) if player_avatar else "",
        "profile_image_url": resolve_public_url(player.get("profile_image_url")),
        "thumbnail": player_thumbnail,
        "style": player.get("style"),
        "display_number": int(player.get("entry_number", rank or 1) or 1),
        "score": player.get("score", 0),
        "distance": distance,
        "distance_left": max(0, distance_limit - distance) if finish_distance else None,
        "progress_ratio": round(progress_ratio, 4),
        "progress_percent": round(progress_ratio * 100, 1),
        "phase": timing_state.get("phase") if finish_distance else None,
        "tempo_level": timing_state.get("tempo_level"),
        "tempo_label": timing_state.get("tempo_label"),
        "speed_multiplier": timing_state.get("speed_multiplier"),
        "acceleration_multiplier": timing_state.get("acceleration_multiplier"),
        "gauge_speed_multiplier": timing_state.get("gauge_speed_multiplier"),
        "current_speed": timing_state.get("current_speed"),
        "acceleration": timing_state.get("acceleration"),
        "zone_active": timing_state.get("zone_active", False),
        "zone_started_at": timing_state.get("zone_started_at"),
        "zone_ends_at": timing_state.get("zone_ends_at"),
        "active_zone_until": timing_state.get("active_zone_until"),
        "zone_remaining_seconds": timing_state.get("zone_remaining_seconds", 0),
        "zone_used": timing_state.get("zone_used", False),
        "zone_name": timing_state.get("zone_name"),
        "zone_source": timing_state.get("zone_source"),
        "last_distance_gain": player.get(
            "last_distance_gain", player.get("web_last_distance_gain", 0)
        ),
        "last_timing_result": player.get("web_latest_timing_result"),
        "rank": rank,
        "is_mob": bool(player.get("is_mob")),
        "mob_level": player.get("mob_level"),
        "ai_level": player.get("ai_level"),
        "mob_preset_key": player.get("mob_preset_key"),
        "last_roll_turn": player.get("last_roll_turn", -1),
        "has_rolled": player.get("last_roll_turn") == player.get("_current_turn"),
        "stamina_left": stamina_snapshot["current_stamina"],
        "current_stamina": stamina_snapshot["current_stamina"],
        "max_stamina": stamina_snapshot["max_stamina"],
        "stamina_stat": stamina_snapshot["stamina_stat"],
        "stamina_percent": stamina_snapshot["stamina_percent"],
        "current_lane": int(
            player.get("current_lane", player.get("entry_number", 1)) or 1
        ),
        "previous_lane": int(
            player.get("previous_lane", player.get("current_lane", 1)) or 1
        ),
        "pending_lane": (
            int(player.get("pending_lane", 0) or 0)
            if str(viewer_id or "") == str(user_id)
            and player.get("pending_lane") is not None
            else None
        ),
        "lane_changed": bool(player.get("lane_changed")),
        "blocked_count": int(player.get("blocked_count", 0) or 0),
        "blocking_penalty": float(player.get("blocking_penalty", 0.0) or 0.0),
        "drafting_active": bool(player.get("drafting_active")),
        "last_stamina_drain": int(player.get("last_stamina_drain", 0) or 0),
        "wit_mana": player.get("wit_mana", 0),
        "current_max_speed": player.get("current_max_speed", 0),
        "zone_left": player.get("zone_left", 0),
        "reroll_left": player.get("reroll_left", 0),
        "wit_reroll_left": player.get("wit_reroll_left", 0),
        "aptitude_bonus": player.get("aptitude_bonus"),
        "effective_race_stats": player.get("effective_race_stats"),
        "no_reroll_this_turn": bool(player.get("no_reroll_this_turn")),
        "used_block": bool(player.get("used_block")),
        "used_rush": bool(player.get("used_rush")),
        "action_locked": bool(player.get("action_locked")),
        "zone": player.get("zone"),
        "skills": skills,
        "last_roll": player.get("last_roll_log"),
        "latest_timing_result": player.get("web_latest_timing_result"),
        # Keep the client-side Gold indicator on the same rules as the race engine.
        "gold_range_bonus_this_turn": player.get("gold_range_bonus_this_turn", 0),
        "enemy_gold_range_penalty_next_turn": player.get(
            "enemy_gold_range_penalty_next_turn", 0
        ),
        "gold_lane_bonus_this_turn": player.get("gold_lane_bonus_this_turn", 0),
        "enemy_gold_lane_penalty_next_turn": player.get(
            "enemy_gold_lane_penalty_next_turn", 0
        ),
        "buffs": {
            "flat": player.get("next_roll_flat_bonus", 0),
            "dice": player.get("next_roll_add_d", 0),
            "keep_highest": player.get("next_roll_add_kh", 0),
            "floor": player.get("next_roll_floor_bonus", 0),
            "selected": player.get("next_roll_selected_die_bonus", 0),
            "cap": player.get("next_roll_cap_bonus", 0),
        },
    }


def serialize_room(
    game: dict, room_id: str | None = None, user_id: str | None = None
) -> dict:
    race_mode = game.get("race_mode", "discord_classic")
    is_web_timing = race_mode == "web_timing"
    stage_key = game.get("stage_key")
    preset = RACE_PRESET.get(stage_key, {})
    finish_distance = (
        int(game.get("finish_distance") or get_web_race_finish_distance(preset))
        if is_web_timing
        else None
    )
    ranked = sorted(
        game.get("players", {}).items(),
        key=lambda item: (
            item[1].get("web_distance", 0) if is_web_timing else item[1].get("score", 0)
        ),
        reverse=True,
    )
    rank_by_id = {
        player_id: index for index, (player_id, _) in enumerate(ranked, start=1)
    }

    players = []
    for player_id, player in game.get("players", {}).items():
        player["_current_turn"] = game.get("turn", 0)
        players.append(
            serialize_player(
                player_id,
                player,
                rank_by_id.get(player_id),
                finish_distance,
                str(user_id) if user_id else None,
            )
        )
        player.pop("_current_turn", None)

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
    leader_player = ranked[0][1] if ranked else {}
    leader_distance = (
        int(leader_player.get("web_distance", 0)) if is_web_timing else None
    )
    leader_ratio = (
        leader_distance / max(1, finish_distance or 1) if is_web_timing else 0
    )
    leader_phase = (
        get_web_timing_phase(leader_distance, finish_distance)
        if is_web_timing
        else None
    )
    path = game.get("path", [])
    leader_path_index = (
        min(len(path) - 1, max(0, int(leader_ratio * len(path))))
        if path and is_web_timing
        else None
    )
    display_path_type = (
        path[leader_path_index] if leader_path_index is not None else current_path_type
    )
    timing_phase = (
        leader_phase
        if is_web_timing
        else _timing_phase(turn, max_turn, current_path_type)
    )

    return {
        "room_id": room_id or str(game.get("room_id") or ""),
        "room_code": (room_id or str(game.get("room_id") or ""))[-6:].upper(),
        "updated_at": int(game.get("updated_at") or time.time()),
        "owner_id": owner_id,
        "my_player_id": str(user_id) if user_id else None,
        "stage_key": stage_key,
        "race_history_id": game.get("race_history_id"),
        "record_type": game.get("record_type", "practice"),
        "race_name": game.get("stage_name"),
        "track": game.get("track"),
        "distance": game.get("distance"),
        "image": preset.get("image"),
        "thumbnail": preset.get("thumnail"),
        "turn": turn,
        "max_turn": max_turn,
        "race_phase": get_phase_from_turn(turn, max_turn) if turn else 0,
        "timing_phase": timing_phase,
        "timing_config": get_web_timing_ui_config() if is_web_timing else None,
        "gameplay_mode": game.get("web_gameplay_mode", "manual"),
        "race_mode": race_mode,
        "lane_system_enabled": not is_web_timing,
        "cycle_id": 0,
        "finish_distance": finish_distance,
        "leader_distance": leader_distance,
        "leader_phase": leader_phase,
        "winner_id": game.get("winner_id"),
        "timing_gauge": build_timing_gauge_config(game, current_player),
        "timing_gauges": {
            str(player_id): build_timing_gauge_config(game, player)
            for player_id, player in game.get("players", {}).items()
        },
        "phase": phase,
        "status": (
            "ended"
            if game.get("ended")
            else ("running" if game.get("started") else "waiting")
        ),
        "awaiting_turn_confirm": bool(game.get("awaiting_turn_confirm")),
        "turn_confirmations": [
            str(user_id) for user_id in game.get("turn_confirmations", set())
        ],
        "path": [
            {
                "turn": index,
                "type": path_type,
                "label": PATH_TYPE_TEXT.get(path_type, "Straight"),
                "icon": PATH_TYPE_ICON.get(path_type, "->"),
                "active": index
                == ((leader_path_index + 1) if leader_path_index is not None else turn),
            }
            for index, path_type in enumerate(path, start=1)
        ],
        "current_path": {
            "type": display_path_type,
            "label": (
                PATH_TYPE_TEXT.get(display_path_type, "Waiting")
                if display_path_type
                else "Waiting"
            ),
            "icon": (
                PATH_TYPE_ICON.get(display_path_type, "-") if display_path_type else "-"
            ),
        },
        "dice_presets": DICE_PRESET,
        "players": players,
        "scoreboard": sorted(
            players,
            key=lambda item: item["distance"] if is_web_timing else item["score"],
            reverse=True,
        ),
        "logs": game.get("web_action_logs", [])[-80:],
        "action_logs": game.get("web_action_logs", [])[-80:],
        "turn_score_logs": game.get("turn_score_logs", [])[-80:],
        "result": game.get("result"),
    }


def serialize_room_summary(game: dict, room_id: str) -> dict:
    race_mode = game.get("race_mode", "discord_classic")
    stage = RACE_PRESET.get(game.get("stage_key"), {})
    return {
        "room_id": room_id,
        "room_code": room_id[-6:].upper(),
        "updated_at": int(game.get("updated_at") or time.time()),
        "phase": (
            "ended"
            if game.get("ended")
            else ("running" if game.get("started") else "waiting")
        ),
        "race_name": game.get("stage_name"),
        "stage_key": game.get("stage_key"),
        "race_history_id": game.get("race_history_id"),
        "record_type": game.get("record_type", "practice"),
        "thumbnail": stage.get("thumnail"),
        "turn": game.get("turn", 0),
        "max_turn": game.get("max_turn", 0),
        "player_count": len(game.get("players", {})),
        "human_count": len(
            [
                player
                for player in game.get("players", {}).values()
                if not player.get("is_mob")
            ]
        ),
        "mob_count": len(
            [
                player
                for player in game.get("players", {}).values()
                if player.get("is_mob")
            ]
        ),
        "max_players": 18,
        "gameplay_mode": game.get("web_gameplay_mode", "manual"),
        "race_mode": race_mode,
        "finish_distance": game.get("finish_distance")
        or (get_web_race_finish_distance(stage) if race_mode == "web_timing" else None),
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


def _web_player_phase(progress_ratio: float) -> str:
    if progress_ratio >= 1.0:
        return "Finished"
    if progress_ratio < 0.15:
        return "Start"
    if progress_ratio < 0.40:
        return "Early"
    if progress_ratio < 0.70:
        return "Middle"
    if progress_ratio < 0.90:
        return "Final Corner"
    return "Final Straight"


def build_timing_gauge_config(game: dict, player: dict | None) -> dict:
    player = player or {}
    style = player.get("style") or "Pace"
    style_rule = MAX_SPEED_PHASE.get(style, MAX_SPEED_PHASE["Pace"])
    turn = int(game.get("turn", 0))
    max_turn = max(1, int(game.get("max_turn", 1)))
    is_web_timing = game.get("race_mode") == "web_timing"
    finish_distance = max(1, int(game.get("finish_distance") or 2000))
    progress_ratio = float(player.get("web_distance", 0)) / finish_distance
    path = game.get("path") or [1]
    path_index = min(len(path) - 1, max(0, int(progress_ratio * len(path))))
    path_type = (
        path[path_index]
        if is_web_timing
        else (get_current_path_type(game) if turn else None)
    )
    timing_state = (
        get_web_timing_snapshot(player, finish_distance) if is_web_timing else {}
    )
    phase = (
        timing_state.get("phase")
        if is_web_timing
        else _timing_phase(turn, max_turn, path_type)
    )
    current_speed = float(
        timing_state.get("current_speed")
        or player.get("current_max_speed")
        or style_rule["start"]
    )
    acceleration = float(
        timing_state.get("acceleration")
        or max(0.0, current_speed - float(style_rule["start"]))
    )

    phase_factor = {
        "Start": 0.92,
        "Early": 1.0,
        "Middle": 1.08,
        "Final Corner": 1.16,
        "Final Straight": 1.24,
    }.get(phase, 1.0)
    style_factor = (
        {
            "Front": {"Start": 0.94, "Early": 0.98, "Final Straight": 1.12},
            "Pace": {},
            "Late": {
                "Start": 0.92,
                "Early": 0.96,
                "Final Corner": 1.1,
                "Final Straight": 1.14,
            },
            "End": {
                "Start": 0.88,
                "Early": 0.92,
                "Final Corner": 1.14,
                "Final Straight": 1.22,
            },
        }
        .get(style, {})
        .get(phase, 1.0)
    )
    segment_factor = {1: 1.0, 2: 1.06, 3: 1.1, 4: 0.96}.get(path_type, 1.0)
    speed_factor = min(
        1.35, max(0.85, current_speed / max(1.0, float(style_rule["start"])))
    )
    marker_speed = (
        float(timing_state.get("gauge_speed_multiplier", 1.0))
        if is_web_timing
        else phase_factor * style_factor * segment_factor * speed_factor
    )

    return {
        "phase": phase,
        "style": style,
        "track_segment": (
            PATH_TYPE_TEXT.get(path_type, "Waiting") if path_type else "Waiting"
        ),
        "current_speed": round(current_speed, 2),
        "acceleration": round(acceleration, 2),
        "tempo_level": timing_state.get("tempo_level"),
        "tempo_label": timing_state.get("tempo_label"),
        "speed_multiplier": timing_state.get("speed_multiplier"),
        "acceleration_multiplier": timing_state.get("acceleration_multiplier"),
        "gauge_speed_multiplier": timing_state.get("gauge_speed_multiplier", 1.0),
        "zone_active": timing_state.get("zone_active", False),
        "zone_remaining_seconds": timing_state.get("zone_remaining_seconds", 0),
        "zone_used": timing_state.get("zone_used", False),
        "zone_name": timing_state.get("zone_name"),
        "last_distance_gain": player.get(
            "last_distance_gain", player.get("web_last_distance_gain", 0)
        ),
        "last_timing_result": player.get("web_latest_timing_result"),
        "marker_speed": round(marker_speed, 3),
        "half_cycle_ms": round(
            (
                WEB_TIMING_GAUGE_HALF_CYCLE_MS
                if is_web_timing
                else DEFAULT_GAUGE_HALF_CYCLE_MS
            )
            / marker_speed
        ),
    }
