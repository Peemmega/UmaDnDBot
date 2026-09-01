import copy
import uuid
import math
import discord
import random
from datetime import datetime, timezone

from utils.race.race_presets import RACE_PRESET
from utils.skill.skill_presets import SKILLS, ICON_URL
from utils.mob.mob_decision import decide_mob_skill_combo, decide_mob_target_lane

from utils.mob.mob_presets import MOB_PRESETS
from utils.database import (
    ensure_player,
    get_player,
    get_player_skill_slots,
)
from utils.race.race_history import ensure_race_history_id, record_race_action, record_turn_snapshot
from utils.profile_images import resolve_player_avatar_url, resolve_public_url
from utils.zone.zone_manager import apply_zone_in_game, get_zone_effects_from_build
from utils.zone.zone_preset import normalize_zone_build
from utils.race.race_presets import (
    get_path_effect,
    get_current_path_type, 
)
from utils.zone.zone_embed import build_zone_used_preview_embed

from utils.race.race_dice import (
    roll_race_dice,
    get_distance_color,
    get_phase_from_turn
)
from utils.race.race_aptitude import (
    build_aptitude_debug_lines,
    calculate_effective_race_stats,
    get_roll_race_stats,
)
from utils.race.runtime_stamina import (
    build_runtime_stamina_note,
    format_runtime_stamina,
    get_runtime_stamina_snapshot,
    runtime_stamina_effect_units,
    runtime_stamina_from_stat,
    set_runtime_stamina,
    sync_runtime_stamina,
)
from utils.race.result_display import format_bonus_display, format_stamina_line
from utils.race.rank_display import get_gold_range_value, get_player_lane, is_in_gold_range_against
from utils.race.race_lane import (
    clamp_lane,
    calculate_lane_block_penalty,
    get_default_lane,
    get_lane_stamina_cost,
    has_drafting_bonus,
)
from utils.race.race_weather import (
    WEATHER_RULE,
    WEATHER_RULE_OPTIONS,
    initialize_race_weather,
    is_sunny,
    is_wet_lane,
)
from utils.race.turn_engine import TurnEngine
from utils.dice.dice_presets import (
    MAX_SPEED_PHASE
)
from utils.in_game_manager import incrase_speed_by_acceleration

from utils.icon_presets import Status_Icon_Type, ICONS

VALID_STYLES = {"Front", "Pace", "Late", "End"}
RACE_STAT_FIELDS = ("speed", "stamina", "power", "gut", "wit")
GAME_RULE_DEFAULTS = {
    "AllowSkill": True,
    "DreamMode": False,
    "NoDebuff": False,
    WEATHER_RULE: "none",
}
games = {}


def _supports_lane_system(game: dict | None) -> bool:
    if not game:
        return False
    return game.get("race_mode", "discord_classic") != "web_timing"


def get_game_rules(game: dict) -> dict[str, bool | str]:
    """Return a room's rules, filling in defaults for rooms created earlier."""
    rules = game.setdefault("game_rules", {})
    for rule_name, default_value in GAME_RULE_DEFAULTS.items():
        rules.setdefault(rule_name, default_value)
    return rules


def get_game_rule(game: dict, rule_name: str) -> bool:
    return bool(get_game_rules(game).get(rule_name, GAME_RULE_DEFAULTS[rule_name]))


def set_game_rule(channel_id: int, rule_name: str, value: bool | str):
    """Change a lobby rule before the race begins."""
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"
    if game.get("started"):
        return False, "ตั้งค่า Game Rule ไม่ได้หลังเริ่มเกมแล้ว"
    if rule_name not in GAME_RULE_DEFAULTS:
        return False, "ไม่พบ Game Rule นี้"

    if rule_name == WEATHER_RULE:
        weather = str(value or "none").strip().lower()
        if weather not in WEATHER_RULE_OPTIONS:
            return False, "Weather ต้องเป็น none, random, warm, rainy หรือ sunny"
        get_game_rules(game)[rule_name] = weather
        return True, weather

    get_game_rules(game)[rule_name] = bool(value)
    return True, bool(value)


def _entry_order_lane(channel_id: int) -> int:
    game = get_game(channel_id)
    player_count = len(game.get("players", {})) if game else 0
    return get_default_lane(player_count + 1)


def _randomize_starting_positions(game: dict) -> list[tuple[object, dict]]:
    shuffled_players = list(game.get("players", {}).items())
    random.shuffle(shuffled_players)

    for index, (_, player) in enumerate(shuffled_players, start=1):
        lane = get_default_lane(index)
        player["entry_number"] = index
        player["current_lane"] = lane
        player["previous_lane"] = lane
        player["pending_lane"] = None
        player["lane_changed"] = False

    return shuffled_players


def _ensure_lane_state(player: dict, entry_number: int | None = None) -> None:
    entry = int(player.get("entry_number") or entry_number or 1)
    player["entry_number"] = entry
    lane = clamp_lane(player.get("current_lane", get_default_lane(entry)))
    player["current_lane"] = lane
    player["previous_lane"] = clamp_lane(player.get("previous_lane", lane))
    player.setdefault("pending_lane", None)
    player.setdefault("lane_changed", False)
    player.setdefault("blocked_count", 0)
    player.setdefault("blocking_penalty", 0.0)
    player.setdefault("drafting_active", False)
    player.setdefault("last_stamina_drain", 0)


def _clone_lane_players_with_scores(game: dict, score_map: dict) -> dict:
    cloned: dict = {}
    for player_id, info in game.get("players", {}).items():
        clone = {
            "score": int(score_map.get(player_id, info.get("score", 0)) or 0),
            "current_lane": info.get("current_lane"),
        }
        cloned[player_id] = clone
    return cloned


def get_stamina_debuff_percent(game_player: dict) -> int:
    race_profile = game_player.get("race_profile") or {}
    gut_stat = int(race_profile.get("gut", 0) or 0)
    return max(0, 25 - gut_stat)


def apply_lane_tactics_to_result(
    *,
    game: dict,
    user_id,
    game_player: dict,
    result: dict,
    path_effect: dict,
    score_map: dict,
    consume_stamina: bool,
    apply_stamina_penalty: bool = True,
) -> dict:
    supports_lane = _supports_lane_system(game)
    _ensure_lane_state(game_player)
    sync_runtime_stamina(game_player)

    base_total = int(result.get("total", 0) or 0)
    final_total = base_total
    blocked_count = 0
    blocking_penalty = 0.0
    drafting_active = False
    lane_cost = 0
    path_stamina_cost = int(path_effect.get("stamina_cost", 0) or 0)
    weather_stamina_cost = 10 if is_sunny(game) else 0
    stamina_drain = path_stamina_cost + weather_stamina_cost
    wet_lane_active = is_wet_lane(game, game_player.get("current_lane"))

    working_players = _clone_lane_players_with_scores(game, score_map)
    temp_player = working_players.get(user_id, {"score": 0, "current_lane": game_player.get("current_lane", 1)})

    race_profile = game_player.get("race_profile") or {}
    effective_stats = game_player.get("effective_race_stats") or {}
    power_stat = int(effective_stats.get("effective_power", race_profile.get("power", 0)) or 0)
    stamina_debuff_percent = get_stamina_debuff_percent(game_player)

    if supports_lane:
        block_info = calculate_lane_block_penalty(
            temp_player,
            working_players,
            base_total,
            power_stat=power_stat,
        )
        blocked_count = int(block_info["blocked_count"])
        blocking_penalty = float(block_info["blocking_penalty"])
        final_total = int(block_info["final_score"])
        lane_base_cost = get_lane_stamina_cost(game_player)
        configured_multiplier = path_effect.get("stamina_multiplier", 1.0)
        lane_stamina_multiplier = float(
            1.0 if configured_multiplier is None else configured_multiplier
        )
        lane_cost = int(round(lane_base_cost * lane_stamina_multiplier))
        stamina_drain = lane_cost + path_stamina_cost + weather_stamina_cost
        drafting_active = has_drafting_bonus(temp_player, working_players)
        temp_player["score"] = int(temp_player.get("score", 0)) + final_total
        if drafting_active:
            stamina_drain = int(round(stamina_drain * 0.90))

    reference_stamina = int(game_player.get("turn_stamina_before_roll", game_player.get("stamina_left", 0)) or 0)
    stamina_penalty_active = (
        apply_stamina_penalty
        and stamina_drain > 0
        and reference_stamina < stamina_drain
    )
    if stamina_penalty_active:
        final_total = int(round(final_total * ((100 - stamina_debuff_percent) / 100)))

    def append_bonus(label: str, *, include_in_preview: bool = True) -> None:
        current = result.get("bonus_display", "-")
        result["bonus_display"] = label if current == "-" else f"{current} {label}"

        if include_in_preview:
            preview_current = result.get("dice_preview_bonus_display", "-")
            result["dice_preview_bonus_display"] = (
                label
                if preview_current == "-"
                else f"{preview_current} {label}"
            )

    if blocking_penalty > 0:
        block_bonus = f"-{int(blocking_penalty * 100)}%BLOCK"
        append_bonus(block_bonus)
    if drafting_active:
        append_bonus("DRAFT", include_in_preview=False)
    if weather_stamina_cost:
        append_bonus("SUN +10STA", include_in_preview=False)
    if stamina_penalty_active and stamina_debuff_percent > 0:
        append_bonus(f"-{stamina_debuff_percent}%STA")

    result["pre_lane_total"] = base_total
    result["total"] = final_total
    result["total_display"] = str(final_total)
    result["blocked_count"] = blocked_count
    result["blocking_penalty"] = blocking_penalty
    result["drafting_active"] = drafting_active
    result["lane_cost"] = lane_cost
    result["stamina_drain"] = stamina_drain
    result["weather_stamina_cost"] = weather_stamina_cost
    result["wet_lane_active"] = wet_lane_active
    result["current_lane"] = game_player.get("current_lane")
    result["previous_lane"] = game_player.get("previous_lane")

    game_player["blocked_count"] = blocked_count
    game_player["blocking_penalty"] = blocking_penalty
    game_player["drafting_active"] = drafting_active
    game_player["last_stamina_drain"] = stamina_drain
    game_player["wet_lane_active"] = wet_lane_active
    game_player["takeStaminaDebuff"] = stamina_penalty_active

    stamina_note = build_runtime_stamina_note(
        game_player,
        drain=stamina_drain,
        penalty=stamina_penalty_active,
        uphill=int(path_effect.get("stamina_cost", 0) or 0) > 100,
    )

    if consume_stamina:
        set_runtime_stamina(
            game_player,
            game_player.get("stamina_stat", 0),
            reference_stamina - stamina_drain,
        )

    return {
        "stamina_note": stamina_note,
        "stamina_penalty_active": stamina_penalty_active,
        "stamina_drain": stamina_drain,
        "drafting_active": drafting_active,
        "blocked_count": blocked_count,
        "blocking_penalty": blocking_penalty,
    }


def refresh_player_profile_snapshot(user_id, player: dict | None) -> dict | None:
    if player is None:
        return None

    if str(user_id).startswith("mob_") or player.get("is_mob"):
        return player

    db_player = get_player(user_id)
    if not db_player:
        return player

    player["username"] = db_player.get("username") or player.get("username")
    player["profile_image_url"] = db_player.get("profile_image_url") or ""
    return player


def format_player_reference(user_id, player: dict | None = None) -> str:
    player = player or {}
    if str(user_id).startswith("mob_") or player.get("is_mob"):
        return (
            player.get("display_name")
            or player.get("username")
            or player.get("name")
            or str(user_id)
        )
    return f"<@{user_id}>"


def _get_rush_stamina_cost(player: dict) -> int:
    snapshot = sync_runtime_stamina(player)
    return max(1, int(round(snapshot["max_stamina"] * 0.05)))


def _get_block_candidates(channel_id: int, user_id: int) -> list[tuple[int, int, dict]]:
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return []

    player = game["players"][user_id]
    my_lane = get_player_lane(player)
    my_score = int(player.get("score", 0) or 0)
    result = []

    for uid, info in game["players"].items():
        if uid == user_id:
            continue
        if abs(get_player_lane(info) - my_lane) > 1:
            continue
        gap = my_score - int(info.get("score", 0) or 0)
        if gap > 0:
            result.append((uid, gap, info))

    return sorted(result, key=lambda item: item[1])


def refresh_player_race_aptitudes(player: dict, race: dict | None) -> dict:
    effective_stats = calculate_effective_race_stats(player, race or {})
    player["effective_race_stats"] = effective_stats
    player["aptitude_bonus"] = {
        "track": {
            "rank": effective_stats["track_rank"],
            "modifier": effective_stats["track_modifier"],
            "percent": effective_stats["track_percent"],
        },
        "distance": {
            "rank": effective_stats["distance_rank"],
            "modifier": effective_stats["distance_modifier"],
            "percent": effective_stats["distance_percent"],
        },
        "style": {
            "rank": effective_stats["style_rank"],
            "modifier": effective_stats["style_modifier"],
            "percent": effective_stats["style_percent"],
        },
        "effective_speed": effective_stats["effective_speed"],
        "effective_power": effective_stats["effective_power"],
        "effective_wit_gain": effective_stats["effective_wit_gain"],
        "effective_wit_requirement": effective_stats["effective_wit_requirement"],
        "lines": build_aptitude_debug_lines(effective_stats),
    }
    return effective_stats


def _race_stat_changes(effect: dict) -> dict[str, int]:
    """Read a race-stat effect while accepting concise and per-stat configs."""
    stats = effect.get("stats", effect.get("stat", "all"))
    if isinstance(stats, dict):
        return {
            stat: int(delta or 0)
            for stat, delta in stats.items()
            if stat in RACE_STAT_FIELDS and int(delta or 0)
        }

    if stats == "all":
        return {stat: int(effect.get("value", 0) or 0) for stat in RACE_STAT_FIELDS}

    if stats in RACE_STAT_FIELDS:
        return {stats: int(effect.get("value", 0) or 0)}

    return {}


def apply_race_stat_changes(player: dict, game: dict, effect: dict) -> dict[str, int]:
    """Apply temporary stat changes to the in-memory race profile only."""
    changes = _race_stat_changes(effect)
    if not changes:
        return {}

    stamina_before = get_runtime_stamina_snapshot(player)
    old_stamina_percent = stamina_before["stamina_percent"]
    race_profile = player.setdefault("race_profile", {})

    for stat, delta in changes.items():
        race_profile[stat] = max(1, int(race_profile.get(stat, 1) or 1) + delta)

    # Keep the same percentage, then grant +100 current Stamina per positive
    # temporary Stamina stat gained.
    new_stamina_stat = int(race_profile.get("stamina", 1) or 1)
    new_stamina_max = runtime_stamina_from_stat(new_stamina_stat)
    stamina_increase = max(0, int(changes.get("stamina", 0) or 0))
    new_stamina_current = (
        round(new_stamina_max * old_stamina_percent / 100)
        + runtime_stamina_effect_units(stamina_increase)
    )
    set_runtime_stamina(player, new_stamina_stat, new_stamina_current)
    refresh_player_race_aptitudes(player, game)
    return changes


def apply_web_timing_player_defaults(player: dict) -> dict:
    defaults = {
        "current_speed": 0,
        "acceleration": 0,
        "zone_active": False,
        "zone_used": False,
        "zone_started_at": None,
        "zone_ends_at": None,
        "tempo_level": "N",
        "tempo_label": "Normal",
        "gauge_speed_multiplier": 1.0,
        "last_distance_gain": 0,
    }
    for field, default in defaults.items():
        player.setdefault(field, default)
    return player


def get_last_corner_index(path: list[int]) -> int:
    for i in range(len(path) - 1, -1, -1):
        if path[i] == 2:
            return i + 1
    return -1

def is_last_corner(game: dict) -> bool:
    path = game["path"]
    turn_index = game["turn"]

    last_corner_index = get_last_corner_index(path)

    return turn_index == last_corner_index

def is_lastspurt(game: dict) -> bool:
    phase = get_phase_from_turn(game["turn"], game["max_turn"])
    path_type = get_current_path_type(game)
    return path_type == 1 and phase == 4

def execute_roll_core(
    *,
    channel_id: int,
    user_id,
    title_prefix: str = "วิ่งในเทิร์นนี้",
    mark_roll: bool = True,
):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ยังไม่มีเกมในห้องนี้"}

    game_player = get_player_in_game(channel_id, user_id)
    if game_player is None:
        return False, {"message": "ไม่พบผู้เล่นในเกม"}

    race_player = game_player.get("race_profile")
    if race_player is None:
        return False, {"message": "ไม่พบข้อมูล stat ตอนเริ่มเกม"}

    roll_stats = get_roll_race_stats(game_player)
    snapshot_scores = game["turn_snapshot_scores"]
    sync_runtime_stamina(game_player)

    pending_effects, merged_stats = build_pending_effects_from_player(game_player)

    path_type = get_current_path_type(game)
    path_effect = get_path_effect(path_type, game_player, race_player)
    game_player["turn_stamina_before_roll"] = int(game_player.get("stamina_left", 0) or 0)

    result = roll_race_dice(
        game_player=game_player,
        player_stats=roll_stats,
        player_id=user_id,
        score_map=snapshot_scores,
        turn=game["turn"],
        max_turn=game["max_turn"],
        path_effect=path_effect,
        skill_effects=pending_effects,
        player_map=game["players"],
    )
    lane_resolution = apply_lane_tactics_to_result(
        game=game,
        user_id=user_id,
        game_player=game_player,
        result=result,
        path_effect=path_effect,
        score_map=snapshot_scores,
        consume_stamina=True,
    )
    stamina_note = lane_resolution["stamina_note"]

    rule = result.get("rule", {})
    rule_text = f"{rule.get('d', 0)}d"
    if rule.get("kh") is not None:
        rule_text += f" kh{rule['kh']}"

    game_player["last_roll_log"] = {
        "phase": result.get("phase"),
        "distance_color": result.get("distance_color"),
        "rule": rule_text,
        "total": result.get("total"),
        "bonus_display": result.get("bonus_display"),
        "stamina": get_runtime_stamina_snapshot(game_player),
        "stamina_note": stamina_note,
        "blocked_count": result.get("blocked_count", 0),
        "blocking_penalty": result.get("blocking_penalty", 0.0),
        "drafting_active": result.get("drafting_active", False),
    }
    if result.get("blocked_count", 0):
        record_race_action(
            game, user_id, "blocked",
            {"blocked_count": result.get("blocked_count"), "penalty": result.get("blocking_penalty", 0.0)},
        )
    if result.get("drafting_active"):
        record_race_action(game, user_id, "draft", {"summary": "Drafting bonus applied"})

    game_player["lastedBuff"] = merged_stats

    game_player["next_roll_flat_bonus"] = 0
    game_player["next_roll_add_d"] = 0
    game_player["next_roll_add_kh"] = 0
    game_player["next_roll_floor_bonus"] = 0
    game_player["next_roll_selected_die_bonus"] = 0
    game_player["next_roll_cap_bonus"] = 0
    game_player["gold_range_bonus_this_turn"] = 0
    game_player["enemy_gold_range_penalty_next_turn"] = 0
    game_player["gold_lane_bonus_this_turn"] = 0
    game_player["enemy_gold_lane_penalty_next_turn"] = 0

    success, new_score = update_player_score(
        channel_id,
        user_id,
        result["total"]
    )
    if not success:
        return False, {"message": "ไม่สามารถอัปเดตคะแนนได้"}

    if mark_roll:
        mark_player_rolled(channel_id, user_id)

    return True, {
        "game": game,
        "game_player": game_player,
        "result": result,
        "new_score": new_score,
        "path_effect": path_effect,
        "stamina_note": stamina_note,
        "title_prefix": title_prefix,
    }

def apply_stamina_debuff(game_player: dict,
                         path_effect: dict,
                         pending_effects: list[dict]
                         ):
    stamina_note = None
    stamina_cost = path_effect.get("stamina_cost", 0)
    stamina_snapshot = sync_runtime_stamina(game_player)
    if stamina_snapshot["current_stamina"] >= stamina_cost:
        return stamina_note, False
    else:
        stamina_debuff_percent = get_stamina_debuff_percent(game_player)
        pending_effects.append({
            "type": "modify_total_percent",
            "value": -stamina_debuff_percent,
            "duration": "this_roll"
        })
        stamina_note = build_runtime_stamina_note(
            game_player,
            drain=stamina_cost,
            penalty=True,
            uphill=stamina_cost > 100,
        )
        return stamina_note, True

def apply_stamina_for_roll(
    game_player: dict,
    path_effect: dict,
) -> tuple[str | None, bool]:
    stamina_note = None
    stamina_gain = path_effect.get("stamina_gain", 0)
    stamina_cost = path_effect.get("stamina_cost", 0)
    sync_runtime_stamina(game_player)

    if stamina_gain > 0:
        set_runtime_stamina(
            game_player,
            game_player.get("stamina_stat", 0),
            game_player.get("stamina_left", 0) + stamina_gain,
        )


    if game_player["stamina_left"] >= stamina_cost:
        set_runtime_stamina(
            game_player,
            game_player.get("stamina_stat", 0),
            game_player.get("stamina_left", 0) - stamina_cost,
        )
        stamina_note = build_runtime_stamina_note(
            game_player,
            gain=stamina_gain,
            drain=stamina_cost,
            uphill=stamina_cost > 100,
        )
    else:
        game_player["takeStaminaDebuff"] = True
        
    return stamina_note

def create_game(channel_id: int, stage_key: str, owner_id: int):
    if channel_id in games:
        return False

    if stage_key not in RACE_PRESET:
        return False

    stage = RACE_PRESET[stage_key]

    games[channel_id] = {
        "channel_id": channel_id,
        "stage_key": stage_key,
        "stage_name": stage['name'],
        "max_turn": stage["turn"],
        "track": stage["track"],
        "distance": stage["distance"],
        "path": stage["path"],
        "owner_id": owner_id,
        "turn": 0,
        "started": False,
        "players": {},
        "turn_snapshot_scores": {},
        "turn_score_logs": [],
        "race_action_logs": [],
        # Results stay out of the official leaderboard unless the room owner
        # explicitly confirms the race as Official before starting it.
        "record_type": "practice",
        "game_rules": GAME_RULE_DEFAULTS.copy(),

        "turn_confirmations": set(),
        "awaiting_turn_confirm": False,
        "turn_confirmation_turn": None,
        "turn_confirmation_token": 0,
        "turn_transition_in_progress": False,
    }

    for preset_key in stage.get("auto_mobs", []):
        add_mob_from_preset(channel_id, preset_key)

    return True

def reset_turn_confirmations(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    TurnEngine.reset_confirmations(game)
    return True

def start_turn_confirmation(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    def revise_mob_lanes(race_game: dict) -> None:
        if not _supports_lane_system(race_game):
            return
        for mob_id, player in race_game.get("players", {}).items():
            if not player.get("is_mob"):
                continue
            target_lane = decide_mob_target_lane(race_game, mob_id)
            if target_lane is not None:
                player["pending_lane"] = clamp_lane(target_lane)

    return TurnEngine.start_confirmation(game, revise_mob_lanes=revise_mob_lanes)

def confirm_turn(
    channel_id: int,
    user_id: int,
    *,
    expected_turn: int | None = None,
    confirmation_token: int | None = None,
):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    result = TurnEngine.confirm(
        game,
        user_id,
        expected_turn=expected_turn,
        confirmation_token=confirmation_token,
    )
    messages = {
        "not_awaiting_confirmation": "ตอนนี้ยังไม่อยู่ในช่วงยืนยันจบเทิร์น",
        "stale_confirmation": "ปุ่มยืนยันนี้หมดอายุแล้ว",
        "stale_turn": "ปุ่มยืนยันนี้เป็นของเทิร์นก่อนหน้า",
        "player_not_found": "คุณไม่ได้อยู่ในเกมนี้",
        "mob_cannot_confirm": "Mob ยืนยันเทิร์นอัตโนมัติ",
        "player_not_rolled": "ต้องทอยก่อนยืนยัน",
    }
    return result.ok, result.payload if result.ok else messages[result.code]

def claim_turn_advance(
    channel_id: int,
    *,
    expected_turn: int | None = None,
    confirmation_token: int | None = None,
    require_all_confirmations: bool = True,
    require_all_rolls: bool = True,
):
    """Atomically reserve a single legal transition to the next turn."""
    game = get_game(channel_id)
    if game is None:
        return False, "ไม่พบเกมนี้แล้ว"

    result = TurnEngine.claim_transition(
        game,
        all_players_rolled=have_all_players_rolled(channel_id),
        expected_turn=expected_turn,
        confirmation_token=confirmation_token,
        require_all_confirmations=require_all_confirmations,
        require_all_rolls=require_all_rolls,
    )
    messages = {
        "race_not_active": "เกมไม่อยู่ในสถานะที่เลื่อนเทิร์นได้",
        "transition_in_progress": "ระบบกำลังเลื่อนเทิร์นนี้อยู่",
        "stale_turn": "คำสั่งนี้เป็นของเทิร์นก่อนหน้า",
        "stale_confirmation": "ช่วงยืนยันนี้หมดอายุแล้ว",
        "pending_rolls": "ยังมีผู้เล่นที่ยังไม่ได้ทอย",
        "pending_confirmations": "ยังยืนยันไม่ครบทุกคน",
    }
    return result.ok, result.payload["turn"] if result.ok else messages[result.code]


def refresh_turn_snapshot(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }
    return True

def get_game(channel_id: int):
    return games.get(channel_id)


def delete_game(channel_id: int) -> bool:
    if channel_id not in games:
        return False

    del games[channel_id]
    return True

def end_game(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    game["ended"] = True
    game["started"] = False
    game["phase"] = "ended"
    return True, "จบเกมแล้ว"

def is_owner(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False
    return game["owner_id"] == user_id


def set_race_record_type(channel_id: int, record_type: str):
    """Set race classification while the lobby has not started yet."""
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"
    if game.get("started"):
        return False, "เปลี่ยนประเภทการแข่งขันไม่ได้หลังเริ่มเกมแล้ว"

    normalized_type = str(record_type).strip().lower()
    if normalized_type not in {"official", "practice"}:
        return False, "ประเภทการแข่งขันต้องเป็น official หรือ practice"

    game["record_type"] = normalized_type
    return True, normalized_type


def is_game_started(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False
    return game["started"]

def have_all_players_rolled(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    players = game["players"]
    if not players:
        return False

    current_turn = game["turn"]
    return all(player["last_roll_turn"] == current_turn for player in players.values())


def start_game(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มไปแล้ว"

    if len(game["players"]) == 0:
        return False, "ยังไม่มีผู้เล่นในเกม"

    game["started"] = True
    game["phase"] = "running"
    game["turn"] = 1
    initialize_race_weather(game)
    ensure_race_history_id(game)
    game.setdefault("race_started_at", datetime.now(timezone.utc).isoformat())

    shuffled_players = _randomize_starting_positions(game)

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }

    
    for index, (user_id, player) in enumerate(shuffled_players, start=1):
        _ensure_lane_state(player, index)
        player["blocked_count"] = 0
        player["blocking_penalty"] = 0.0
        player["drafting_active"] = False
        player["last_stamina_drain"] = 0
        is_mob = player.get("is_mob", False)
        using_mob_preset = player.get("using_mob_preset", False)
        
        if is_mob:
            # mob ใช้ค่า preset ที่มีอยู่ใน player อยู่แล้ว
            base_player = player.get("race_profile", {}).copy()

            if not base_player:
                base_player = {
                    "speed": 1,
                    "stamina": 1,
                    "power": 1,
                    "gut": 1,
                    "wit": 1,
                    "turf": 1,
                    "dirt": 1,
                    "sprint": 1,
                    "mile": 1,
                    "medium": 1,
                    "long": 1,
                    "front": 1,
                    "pace": 1,
                    "late": 1,
                    "end_style": 1,
                }

            player["reroll_left"] = player.get("reroll_left", 0)
            player["wit_reroll_left"] = player.get("wit_reroll_left", 0)
            set_runtime_stamina(player, base_player["stamina"])

            # reset race_profile ใหม่จากฐาน preset
            player["race_profile"] = base_player.copy()
            player["takeStaminaDebuff"] = False

            # mob ใช้ skills จาก preset เดิม ไม่ต้องโหลดจาก DB
            player["skills"] = player.get("skills", {
                1: None,
                2: None,
                3: None,
                4: None,
            })

        elif using_mob_preset:
            base_player = player.get("race_profile", {}).copy()

            player["reroll_left"] = 2
            player["wit_reroll_left"] = 2
            set_runtime_stamina(player, base_player.get("stamina", 1))
            player["race_profile"] = base_player.copy()

            # สำคัญ: ใช้ skills เดิมจาก preset ห้ามทับด้วย DB
            player["skills"] = player.get("skills", {
                1: None,
                2: None,
                3: None,
                4: None,
            })

            player["zone"] = copy.deepcopy(player.get("zone", {}))
        else:
            db_player = get_player(user_id)

            if db_player is None:
                db_player = {
                    "speed": 1,
                    "stamina": 1,
                    "power": 1,
                    "gut": 1,
                    "wit": 1,
                    "turf": 1,
                    "dirt": 1,
                    "sprint": 1,
                    "mile": 1,
                    "medium": 1,
                    "long": 1,
                    "front": 1,
                    "pace": 1,
                    "late": 1,
                    "end_style": 1,
                }

            player["reroll_left"] = 2
            player["wit_reroll_left"] = 2
            set_runtime_stamina(player, db_player["stamina"])

            player["race_profile"] = db_player.copy()

            slots = get_player_skill_slots(user_id) or {
                "slot_1": None,
                "slot_2": None,
                "slot_3": None,
                "slot_4": None,
            }
            player["zone_left"] = 1

            player["skills"] = {
                1: slots["slot_1"],
                2: slots["slot_2"],
                3: slots["slot_3"],
                4: slots["slot_4"],
            }

            # zone ของผู้เล่นจริง ถ้ายังใช้ในเกม
            if "zone" not in player and "zone" in db_player:
                player["zone"] = {
                    "name": db_player["zone"]['name'],
                    "image_url": db_player["zone"]["image_url"],
                    "points": db_player["zone"]["points"],
                    "build": db_player["zone"]["build"],
                }

        # DreamMode standardizes the five core race stats for this race only.
        # Aptitudes remain unchanged, so track/distance/style still matter.
        if get_game_rule(game, "DreamMode"):
            race_profile = player.setdefault("race_profile", {})
            for stat in RACE_STAT_FIELDS:
                race_profile[stat] = 8
            set_runtime_stamina(player, race_profile["stamina"])

        # reset กลางเกม ใช้ร่วมกันทั้ง player จริงและ mob
        player["base_race_stats"] = {
            stat: int((player.get("race_profile") or {}).get(stat, 0) or 0)
            for stat in RACE_STAT_FIELDS
        }
        player["skill_cooldowns"] = {}
        player["skill_use_count"] = 0
        player["activated_passive_skills"] = set()
        player["used_rush"] = False
        player["used_block"] = False
        player["action_locked"] = False

        player["next_roll_flat_bonus"] = 0
        player["next_roll_add_d"] = 0
        player["next_roll_add_kh"] = 0
        player["next_roll_floor_bonus"] = 0
        player["next_roll_selected_die_bonus"] = 0
        player["next_roll_cap_bonus"] = 0
        player["gold_range_bonus_this_turn"] = 0
        player["enemy_gold_range_penalty_next_turn"] = 0
        player["gold_lane_bonus_this_turn"] = 0
        player["enemy_gold_lane_penalty_next_turn"] = 0

        player["no_reroll_this_turn"] = False
        player["no_reroll_next_turn"] = False
        player["last_roll_turn"] = -1
        player["zone_left"] = 1

        refresh_player_race_aptitudes(player, game)

        player["current_max_speed"] = MAX_SPEED_PHASE[player["style"]]["start"]
        player["wit_mana"] = 100 + (player["race_profile"]["wit"] * 10)

    activate_passive_skills(channel_id)
    return True, "เริ่มเกมเรียบร้อยแล้ว"


def build_join_embed(
    *,
    game: dict,
    display_name: str,
    display_image: str,
    style: str,
    aptitude_source: dict,
    title: str = "🏇 ผู้เล่นเข้าร่วม!",
    color: discord.Color = discord.Color.green(),
    name_field: str = "ผู้เล่น",
    name_value: str,
) -> discord.Embed:
    track = game.get("track", "turf")
    distance = game.get("distance", "medium")
    effective_stats = calculate_effective_race_stats(
        {
            "style": style,
            "race_profile": aptitude_source,
        },
        {
            "track": track,
            "distance": distance,
        },
    )

    embed = discord.Embed(
        title=title,
        color=color
    )

    embed.add_field(name=name_field, value=name_value, inline=True)
    embed.add_field(name="Style", value=style, inline=True)

    embed.add_field(
        name="📊 Aptitude Bonus",
        value="\n".join(build_aptitude_debug_lines(effective_stats)),
        inline=False
    )

    embed.set_thumbnail(url=display_image)
    return embed

def build_mob_join_embed(game: dict, mob: dict):
    mob_name = (
        mob.get("display_name")
        or mob.get('username') 
        or mob.get("name")
        or "Mob"
    )

    style = mob.get("style", "Unknown")
    # mob_avatar = mob.get("avatar", "")
    race_profile = mob.get("race_profile", {})

    return build_join_embed(
        game=game,
        display_name=mob_name,
        display_image=resolve_public_url(mob.get("thumnail", "")),
        style=style,
        aptitude_source=race_profile,
        title="🏇 ผู้เล่นเข้าร่วม!",
        color=discord.Color.orange(),
        name_field="ชื่อ",
        name_value=mob_name,
    )

def get_player_skill_cd(channel_id: int, user_id: int, skill_id: str) -> int:
    game = get_game(channel_id)
    if game is None:
        return 0

    player = game["players"].get(user_id)
    if player is None:
        return 0

    return player.get("skill_cooldowns", {}).get(skill_id, 0)


def set_player_skill_cd(channel_id: int, user_id: int, skill_id: str, cooldown: int):
    game = get_game(channel_id)
    if game is None:
        return False

    player = game["players"].get(user_id)
    if player is None:
        return False

    player.setdefault("skill_cooldowns", {})
    player["skill_cooldowns"][skill_id] = cooldown
    return True


def is_skill_on_cooldown(channel_id: int, user_id: int, skill_id: str):
    cd = get_player_skill_cd(channel_id, user_id, skill_id)
    return cd > 0, cd


def tick_skill_cooldowns(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    for player in game["players"].values():
        cooldowns = player.setdefault("skill_cooldowns", {})
        expired = []

        for skill_id, cd in cooldowns.items():
            new_cd = cd - 1
            if new_cd <= 0:
                expired.append(skill_id)
            else:
                cooldowns[skill_id] = new_cd

        for skill_id in expired:
            del cooldowns[skill_id]

    return True


def initialize_player_skills(channel_id: int):
    game = get_game(channel_id)

    for user_id, player in game["players"].items():
        slots = get_player_skill_slots(user_id)

        player["skills"] = {
            1: slots["slot_1"],
            2: slots["slot_2"],
            3: slots["slot_3"],
            4: slots["slot_4"],
        }

        # optional (ไว้ใช้ต่อ)
        player["skill_cooldowns"] = {}

def use_player_stamina(channel_id: int, user_id: int, amount: int = 1):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"

    sync_runtime_stamina(player)
    runtime_amount = runtime_stamina_effect_units(amount)
    if player["stamina_left"] < runtime_amount:
        return False, player["stamina_left"]

    set_runtime_stamina(
        player,
        player.get("stamina_stat", 0),
        player["stamina_left"] - runtime_amount,
    )
    return True, player["stamina_left"]

def apply_stamina_cost(channel_id: int, user_id: int, turn: int):
    game = get_game(channel_id)
    if game is None:
        return {"used": False, "penalty": 0, "stamina_left": None}

    player = game["players"].get(user_id)
    if player is None:
        return {"used": False, "penalty": 0, "stamina_left": None}

    if turn <= 8:
        return {
            "used": False,
            "penalty": 0,
            "stamina_left": player["stamina_left"]
        }

    sync_runtime_stamina(player)
    if player["stamina_left"] > 0:
        set_runtime_stamina(
            player,
            player.get("stamina_stat", 0),
            player["stamina_left"] - 100,
        )
        return {
            "used": True,
            "penalty": 0,
            "stamina_left": player["stamina_left"]
        }

    return {
        "used": False,
        "penalty": 30,
        "stamina_left": player["stamina_left"]
    }

def get_player_stamina_left(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return None

    player = game["players"].get(user_id)
    if player is None:
        return None

    sync_runtime_stamina(player)
    return player["stamina_left"]


def queue_player_lane_change(channel_id: int, user_id: int, target_lane: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"
    if not _supports_lane_system(game):
        return False, "Race mode นี้ยังไม่รองรับ lane system"
    if not game.get("started") or game.get("ended"):
        return False, "Race ยังไม่อยู่ในสถานะที่เปลี่ยนเลนได้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"

    _ensure_lane_state(player)
    lane = clamp_lane(target_lane)
    player["pending_lane"] = lane
    record_race_action(
        game,
        user_id,
        "lane_change_queued",
        {
            "from_lane": player.get("current_lane"),
            "to_lane": lane,
        },
    )
    return True, {
        "current_lane": player["current_lane"],
        "pending_lane": lane,
    }


def apply_pending_lane_change_now(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"
    if not _supports_lane_system(game):
        return False, "Race mode นี้ยังไม่รองรับ lane system"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"

    _ensure_lane_state(player)
    pending_lane = player.get("pending_lane")
    if pending_lane is None:
        return False, "ยังไม่มี Lane ที่รอเปลี่ยน"

    current_lane = clamp_lane(player.get("current_lane"))
    next_lane = clamp_lane(pending_lane)
    player["previous_lane"] = current_lane
    player["current_lane"] = next_lane
    player["pending_lane"] = None
    player["lane_changed"] = next_lane != current_lane
    return True, {
        "previous_lane": current_lane,
        "current_lane": next_lane,
        "lane_changed": player["lane_changed"],
    }

def get_players_ahead(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return []

    my_score = game["players"][user_id]["score"]

    result = []
    for uid, info in game["players"].items():
        if uid == user_id:
            continue
        gap = info["score"] - my_score
        if gap > 0:
            result.append((uid, gap, info))

    return sorted(result, key=lambda x: x[1])

def get_players_behind(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return []

    my_score = game["players"][user_id]["score"]

    result = []
    for uid, info in game["players"].items():
        if uid == user_id:
            continue
        gap = my_score - info["score"]
        if gap > 0:
            result.append((uid, gap, info))

    return sorted(result, key=lambda x: x[1])

def apply_next_roll_effects_to_player(player: dict, effects: list[dict]):
    for effect in effects:
        effect_type = effect.get("type")
        value = effect.get("value", 0)
        duration = effect.get("duration")

        # if duration != "this_roll":
        #     continue

        if effect_type == "modify_velocity":
            player["next_roll_flat_bonus"] = player.get("next_roll_flat_bonus", 0) + value

        elif effect_type == "add_d":
            player["next_roll_add_d"] = player.get("next_roll_add_d", 0) + value

        elif effect_type == "add_kh":
            player["next_roll_add_kh"] = player.get("next_roll_add_kh", 0) + value
            
        elif effect_type == "add_dkh":
            player["next_roll_add_kh"] = player.get("next_roll_add_kh", 0) + value
            player["next_roll_add_d"] = player.get("next_roll_add_d", 0) + value

        elif effect_type == "modify_roll_floor":
            player["next_roll_floor_bonus"] = player.get("next_roll_floor_bonus", 0) + value
            
        elif effect_type == "modify_roll_cap":
            player["next_roll_cap_bonus"] = player.get("next_roll_cap_bonus", 0) + value

        elif effect_type in {"modify_roll_cap_floor", "cap_floor"}:
            player["next_roll_cap_bonus"] = player.get("next_roll_cap_bonus", 0) + effect.get("cap", value)
            player["next_roll_floor_bonus"] = player.get("next_roll_floor_bonus", 0) + effect.get("floor", value)
            
def use_block(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่น"

    if player["used_block"]:
        return False, "คุณใช้ Block ไปแล้วในเทิร์นนี้"

    behind_players = _get_block_candidates(channel_id, user_id)
    if any(is_in_gold_range_against(player, info) for _, _, info in behind_players):
        return False, "คุณอยู่ในระยะ Gold แล้ว"

    gold_range = get_gold_range_value(player)
    valid_targets = [
        (uid, gap, info)
        for uid, gap, info in behind_players
        if gold_range < gap <= gold_range + 20
    ]
    if not valid_targets:
        return False, "ไม่มีเป้าหมายด้านหลังในเลนเดียวกันหรือเลนติดกันที่ถอยเข้า Gold ได้ไม่เกิน 20"

    target_id, gap, target_info = valid_targets[0]
    move_back = gap - gold_range
    player["score"] -= move_back
    player["used_block"] = True
    player["action_locked"] = True

    record_race_action(
        game,
        user_id,
        "Block",
        {
            "move_back": move_back,
            "new_score": player["score"],
            "summary": f"Block moved back {move_back} point(s)",
        },
        target_id=target_id,
    )

    return True, {
        "target_id": target_id,
        "target": target_info,
        "move_back": move_back,
        "new_score": player["score"],
    }


def can_use_rush(channel_id: int, user_id: int) -> tuple[bool, str | None]:
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่น"

    if player["used_rush"]:
        return False, "คุณใช้ Rush ไปแล้วในเกมนี้"

    rush_cost = _get_rush_stamina_cost(player)
    snapshot = get_runtime_stamina_snapshot(player)
    if snapshot["current_stamina"] < rush_cost:
        return False, f"STA ไม่พอสำหรับ Rush (ต้องใช้ {rush_cost})"

    return True, None


def use_rush(channel_id: int, user_id: int):
    ok, reason = can_use_rush(channel_id, user_id)
    if not ok:
        return False, reason

    game = get_game(channel_id)
    player = game["players"].get(user_id)
    rush_cost = _get_rush_stamina_cost(player)
    snapshot = sync_runtime_stamina(player)
    set_runtime_stamina(
        player,
        snapshot["stamina_stat"],
        snapshot["current_stamina"] - rush_cost,
    )

    move_forward = 20
    player["score"] += move_forward
    player["used_rush"] = True
    player["action_locked"] = True

    record_race_action(
        game,
        user_id,
        "Rush",
        {
            "move_forward": move_forward,
            "stamina_cost": rush_cost,
            "stamina_left": player.get("stamina_left", 0),
            "new_score": player["score"],
            "summary": f"Rush +{move_forward} (STA -{rush_cost})",
        },
    )

    return True, {
        "move_forward": move_forward,
        "stamina_cost": rush_cost,
        "stamina_left": player.get("stamina_left", 0),
        "new_score": player["score"],
    }


def can_force_rush_targets(channel_id: int, targets: list[tuple[int, dict]]) -> tuple[bool, str | None]:
    if not targets:
        return False, "ไม่มีเป้าหมายสำหรับบังคับ Rush"

    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    for target_id, _ in targets:
        player = game["players"].get(target_id)
        if player is None or player.get("used_rush"):
            continue

        rush_cost = _get_rush_stamina_cost(player)
        snapshot = get_runtime_stamina_snapshot(player)
        if snapshot["current_stamina"] >= rush_cost:
            return True, None

    return False, "ไม่มีเป้าหมายที่สามารถถูกบังคับใช้ Rush ได้"


def build_aptitude_stat_bonus(att):
    return {
        "power": att["track"],      # Track → Power
        "speed": att["distance"],   # Distance → Speed
        "wit": att["style"],        # Style → Wit
    }

def build_pending_effects_from_player(
    player: dict,
) -> tuple[list[dict], dict]:
    flat = player.get("next_roll_flat_bonus", 0)
    add_d = player.get("next_roll_add_d", 0)
    add_kh = player.get("next_roll_add_kh", 0)
    floor = player.get("next_roll_floor_bonus", 0)
    cap = player.get("next_roll_cap_bonus", 0)
    gold_range = player.get("gold_range_bonus_this_turn", 0)
    enemy_gold_range_penalty = abs(player.get("enemy_gold_range_penalty_next_turn", 0))
    gold_lane_bonus = player.get("gold_lane_bonus_this_turn", 0)
    enemy_gold_lane_penalty = abs(player.get("enemy_gold_lane_penalty_next_turn", 0))

    # รวม lastedBuff
    buff = player.get("lastedBuff", {})
    if buff:
        flat += buff.get("flat", 0)
        add_d += buff.get("add_d", 0)
        add_kh += buff.get("add_kh", 0)
        floor += buff.get("floor", 0)
        cap += buff.get("cap", 0)
        gold_range += buff.get("gold_range", 0)
        gold_lane_bonus += buff.get("gold_lane_bonus", 0)

    pending_effects = []

    if flat != 0:
        pending_effects.append({
            "type": "modify_velocity",
            "value": flat,
            "duration": "this_roll"
        })

    if add_d != 0:
        pending_effects.append({
            "type": "add_d",
            "value": add_d,
            "duration": "this_roll"
        })

    if add_kh != 0:
        pending_effects.append({
            "type": "add_kh",
            "value": add_kh,
            "duration": "this_roll"
        })

    if floor != 0:
        pending_effects.append({
            "type": "modify_roll_floor",
            "value": floor,
            "duration": "this_roll"
        })

    if cap != 0:
        pending_effects.append({
            "type": "modify_roll_cap",
            "value": cap,
            "duration": "this_roll"
        })

    if gold_range != 0:
        pending_effects.append({
            "type": "modify_gold_range",
            "value": gold_range,
            "duration": "this_roll"
        })

    if enemy_gold_range_penalty != 0:
        pending_effects.append({
            "type": "modify_enemy_gold_range",
            "value": enemy_gold_range_penalty,
            "duration": "this_roll"
        })

    if gold_lane_bonus != 0:
        pending_effects.append({
            "type": "modify_gold_lane_range",
            "value": gold_lane_bonus,
            "duration": "this_roll"
        })

    if enemy_gold_lane_penalty != 0:
        pending_effects.append({
            "type": "modify_enemy_gold_lane_range",
            "value": enemy_gold_lane_penalty,
            "duration": "this_roll"
        })

    merged_stats = {
        "flat": flat,
        "add_d": add_d,
        "add_kh": add_kh,
        "floor": floor,
        "cap": cap,
        "gold_range": gold_range,  
        "enemy_gold_range_penalty": enemy_gold_range_penalty,
        "gold_lane_bonus": gold_lane_bonus,
        "enemy_gold_lane_penalty": enemy_gold_lane_penalty,
    }

    return pending_effects, merged_stats


def use_reroll(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"

    if player["reroll_left"] <= 0:
        return False, "คุณไม่มี reroll เหลือแล้ว"

    player["reroll_left"] -= 1
    record_race_action(game, user_id, "reroll", {"rerolls_left": player["reroll_left"]})
    return True, player["reroll_left"]

def build_single_wit_regen_text(game_player: dict) -> str:
    effective_stats = game_player.get("effective_race_stats") or {}
    regen = int(effective_stats.get("effective_wit_gain", 10))
    current_mana = game_player.get("wit_mana", 0)
    return f"{current_mana} → {current_mana + regen}" #{Status_Icon_Type['WIT']} 

def build_run_embed(
    game_player: dict,
    result: dict,
    new_score: int,
    stamina_note: str | None,
    path_effect: dict,
    title_prefix: str = "วิ่งในเทิร์นนี้",
    player_name: str | None = None,
) -> discord.Embed:
    name_part = f"{player_name} | " if player_name else ""

    embed = discord.Embed(
        title=f"{name_part} ช่วงที่ {result['phase']} เทิร์นที่ {result['turn']} : {path_effect['label']} สาย {game_player['style']}",
        color=discord.Color.gold()
    )

    avatar = resolve_player_avatar_url(game_player) or game_player.get("avatar", "0")
    reroll = game_player.get("reroll_left", 0)
    current_max_speed = math.floor(game_player.get("current_max_speed", 0))
    wit_reroll = game_player.get("wit_reroll_left", 0)

    bonus_display = format_bonus_display(result.get("bonus_display", "-"), block_label="🚫")
    embed.add_field(name=f"🏇 ความเร็วปัจจุบัน {current_max_speed} รูปแบบ {result['distance_color']}", value= f"{result['display']} {bonus_display}" , inline=False)
    
    if stamina_note == None:
        stamina_note = format_runtime_stamina(game_player)
    stamina_line = format_stamina_line(
        stamina_note,
        drafting_active=bool(result.get("drafting_active", game_player.get("drafting_active", False))),
    )

    embed.add_field(
        name= f"🏁 Score รวม: **{new_score}** ({result['total']})",
        value=(
            f"{Status_Icon_Type['STA']} : **{stamina_line}**　"
            f"{Status_Icon_Type['WIT']} : **{build_single_wit_regen_text(game_player)}** "
        ),
        inline=False
    )

    embed.add_field(
        name= f"{ICONS['AlarmClock']} : **{reroll}** {Status_Icon_Type['WIT']} Reroll: **{wit_reroll}**",
        value="",
        inline=False
    )

    embed.set_thumbnail(url=avatar)

    return embed

def has_real_player(game: dict) -> bool:
        return any(
            not player.get("is_mob", False)
            for player in game["players"].values()
        )

def next_turn(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return None

    def record_lane_change(race_game: dict, player_id, lane_change: dict) -> None:
        record_race_action(race_game, player_id, "lane_change", lane_change)

    def after_advance() -> None:
        tick_skill_cooldowns(channel_id)
        apply_wit_regen(channel_id)
        incrase_speed_by_acceleration_turn(channel_id)
        activate_passive_skills(channel_id)

    return TurnEngine.advance(
        game,
        lane_system_enabled=_supports_lane_system(game),
        record_lane_change=record_lane_change,
        record_turn_snapshot=record_turn_snapshot,
        after_advance=after_advance,
    )

def incrase_speed_by_acceleration_turn(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return

    for _, player in game["players"].items():
        incrase_speed_by_acceleration(game ,player, 1)


def apply_wit_regen(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return

    for _, player in game["players"].items():
        effective_stats = player.get("effective_race_stats") or refresh_player_race_aptitudes(player, game)
        regen = int(effective_stats.get("effective_wit_gain", 10))
        player["wit_mana"] = player.get("wit_mana", 0) + regen

def get_ranked_players(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return []

    return sorted(
        game["players"].items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )

def add_player(channel_id, user_id, display_name: str, display_avatar: str, style):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มแล้ว ไม่สามารถเข้าร่วมเพิ่มได้"

    if style not in VALID_STYLES:
        return False, "รูปแบบการวิ่งไม่ถูกต้อง"

    if user_id in game["players"]:
        return False, "คุณเข้าร่วมเกมนี้แล้ว"
    
    # A Discord user can open the lobby before visiting the web profile/API.
    # Create the default record here so joining a game never dereferences None.
    db_player = ensure_player(user_id, display_name)
    if db_player is None:
        return False, "Unable to prepare the player profile. Please try again."

    entry_number = len(game["players"]) + 1
    default_lane = get_default_lane(entry_number)
    game["players"][user_id] = {
        "username": db_player.get("username") or display_name,
        "avatar": display_avatar,
        "profile_image_url": db_player.get("profile_image_url") if db_player else "",
        "display_name": display_name,
        "style": style,
        "current_max_speed": MAX_SPEED_PHASE[style]["start"],
        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "stamina_left": 0,
        "max_stamina": 0,
        "stamina_stat": 0,
        "current_stamina": 0,
        "stamina_percent": 0,
        "entry_number": entry_number,
        "current_lane": default_lane,
        "previous_lane": default_lane,
        "pending_lane": None,
        "lane_changed": False,
        "blocked_count": 0,
        "blocking_penalty": 0.0,
        "drafting_active": False,
        "last_stamina_drain": 0,
        "wit_mana": 100,
        "wit_reroll_left": 2,
        "takeStaminaDebuff": False,
        "gold_lane_bonus_this_turn": 0,
        "enemy_gold_lane_penalty_next_turn": 0,
        "skills": {
            1: None,
            2: None,
            3: None,
            4: None,
        },
        "skill_cooldowns": {},
        "race_profile": {},
        "used_rush": False,
        "used_block": False,
        "action_locked": False,
        "next_roll_flat_bonus": 0,
        "next_roll_add_d": 0,
        "next_roll_add_kh": 0,
        "next_roll_floor_bonus": 0,
        "next_roll_selected_die_bonus": 0,
        "next_roll_cap_bonus": 0,
        "no_reroll_this_turn": False,
        "no_reroll_next_turn": False,
        "zone_left": 1,

        "zone": {
            "name": db_player["zone"]['name'],
            "image_url": db_player["zone"]["image_url"],
            "points": db_player["zone"]["points"],
            "build": db_player["zone"]["build"],
        }
    }
    set_runtime_stamina(game["players"][user_id], db_player.get("stamina", 1))
    apply_web_timing_player_defaults(game["players"][user_id])

    return True, "เข้าร่วมเกมสำเร็จ"

def add_player_as_mob_preset(
        channel_id: int, 
        user_id: int, 
        display_name: str, 
        preset_key: str
        ):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มแล้ว ไม่สามารถเข้าร่วมเพิ่มได้"

    if user_id in game["players"]:
        return False, "คุณเข้าร่วมเกมนี้แล้ว"

    preset = MOB_PRESETS.get(preset_key)
    if preset is None:
        return False, "ไม่พบ preset"

    race_profile = copy.deepcopy(preset["race_profile"])
    race_profile = apply_rookie_distance_stats(preset_key, race_profile, game.get("distance"))

    skills = apply_rookie_distance_skills(
        preset_key,
        copy.deepcopy(preset["skills"]),
        game.get("distance"),
    )

    zone = copy.deepcopy(preset["zone"])
    zone["build"] = normalize_zone_build(zone.get("build"))

    game["players"][user_id] = {
        "username": preset['name'],
        "display_name": preset['name'],
        "avatar": preset["avatar"],
        "thumnail": preset["thumnail"],
        "profile_image_url": "",
        "style": preset["style"],
        "current_max_speed": MAX_SPEED_PHASE[preset["style"]]["start"],
        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "stamina_left": 0,
        "max_stamina": 0,
        "stamina_stat": 0,
        "current_stamina": 0,
        "stamina_percent": 0,
        "entry_number": entry_number,
        "current_lane": default_lane,
        "previous_lane": default_lane,
        "pending_lane": None,
        "lane_changed": False,
        "blocked_count": 0,
        "blocking_penalty": 0.0,
        "drafting_active": False,
        "last_stamina_drain": 0,
        "wit_mana": 100,
        "wit_reroll_left": 2,
        "takeStaminaDebuff": False,
        "gold_lane_bonus_this_turn": 0,
        "enemy_gold_lane_penalty_next_turn": 0,
        "skills": skills,
        "zone": zone,
        "zone_left": 1,
        "is_mob": False,
        "using_mob_preset": True,
        "mob_preset_key": preset_key,
        "race_profile": race_profile,
        "skill_cooldowns": {},
        "used_rush": False,
        "used_block": False,
        "action_locked": False,
        "next_roll_flat_bonus": 0,
        "next_roll_add_d": 0,
        "next_roll_add_kh": 0,
        "next_roll_floor_bonus": 0,
        "next_roll_selected_die_bonus": 0,
        "next_roll_cap_bonus": 0,
        "no_reroll_this_turn": False,
        "no_reroll_next_turn": False,
    }
    apply_web_timing_player_defaults(game["players"][user_id])

    return True, "เข้าร่วมสำเร็จ"

def apply_mob_level(race_profile: dict, level: int):
    level = max(1, min(level, 8))

    bonus = level - 1

    aptitude_fields = [
        "turf", "dirt",
        "sprint", "mile", "medium", "long",
        "front", "pace", "late", "end_style",
    ]

    for field in aptitude_fields:
        race_profile[field] = min(8, race_profile.get(field, 1) + bonus)

    return race_profile


ROOKIE_DISTANCE_STAT_SHIFTS = {
    "sprint": {
        "stamina": -2,
        "speed": 1,
        "power": 1,
    },
    "mile": {
        "stamina": -2,
        "power": 1,
        "wit": 1,
    },
    "long": {
        "speed": -1,
        "power": -1,
        "stamina": 2,
    },
}


ROOKIE_DISTANCE_SKILL_LOADOUTS = {
    "rookie_front": {
        "sprint": {
            1: "s033",  # Runaway
            2: "s016",  # Turbo Sprint
            3: "s051",  # Escape Artist
            4: "s049",  # Homestretch Haste
        },
        "mile": {
            1: "s033",  # Runaway
            2: "s015",  # Beeline Burst
            3: "s051",  # Escape Artist
            4: "s049",  # Homestretch Haste
        },
    },
}


def apply_rookie_distance_stats(preset_key: str, race_profile: dict, distance: str | None):
    if not preset_key.startswith("rookie_"):
        return race_profile

    shifts = ROOKIE_DISTANCE_STAT_SHIFTS.get((distance or "").lower())
    if not shifts:
        return race_profile

    points_to_move = 0
    for stat, delta in shifts.items():
        if delta >= 0:
            continue

        current = race_profile.get(stat, 1)
        reduction = min(-delta, max(0, current - 1))
        race_profile[stat] = current - reduction
        points_to_move += reduction

    for stat, delta in shifts.items():
        if delta <= 0 or points_to_move <= 0:
            continue

        current = race_profile.get(stat, 1)
        increase = min(delta, points_to_move, max(0, 8 - current))
        race_profile[stat] = current + increase
        points_to_move -= increase

    return race_profile


def apply_rookie_distance_skills(preset_key: str, skills: dict, distance: str | None):
    if not preset_key.startswith("rookie_"):
        return skills

    distance_key = (distance or "").lower()
    loadout = ROOKIE_DISTANCE_SKILL_LOADOUTS.get(preset_key, {}).get(distance_key)
    if not loadout:
        return skills

    return copy.deepcopy(loadout)


def add_mob_from_preset(channel_id: int, preset_key: str, level: int = 1):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มแล้ว ไม่สามารถเพิ่ม mob ได้"

    preset = MOB_PRESETS.get(preset_key)
    if preset is None:
        return False, "ไม่พบ preset mob"

    level = max(1, min(level, 8))

    mob_id = f"mob_{uuid.uuid4().hex[:8]}"

    race_profile = copy.deepcopy(preset["race_profile"])
    race_profile = apply_mob_level(race_profile, level)
    race_profile = apply_rookie_distance_stats(preset_key, race_profile, game.get("distance"))

    zone = copy.deepcopy(preset["zone"])
    zone["build"] = normalize_zone_build(zone.get("build"))
    skills = apply_rookie_distance_skills(
        preset_key,
        copy.deepcopy(preset["skills"]),
        game.get("distance"),
    )

    entry_number = len(game["players"]) + 1
    default_lane = get_default_lane(entry_number)
    game["players"][mob_id] = {
        "username": preset['name'],
        "display_name": f"{preset['name']} Lv.{level}",
        "avatar": preset["avatar"],
        "thumnail": preset.get("thumnail", preset.get("avatar")),
        "profile_image_url": "",
        "is_mob": True,
        "mob_level": level,
        "ai_level": level,
        "mob_preset_key": preset_key,
        "style": preset["style"],

        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "wit_reroll_left": 0,
        "stamina_left": 0,
        "max_stamina": 0,
        "stamina_stat": 0,
        "current_stamina": 0,
        "stamina_percent": 0,
        "entry_number": entry_number,
        "current_lane": default_lane,
        "previous_lane": default_lane,
        "pending_lane": None,
        "lane_changed": False,
        "blocked_count": 0,
        "blocking_penalty": 0.0,
        "drafting_active": False,
        "last_stamina_drain": 0,
        "gold_lane_bonus_this_turn": 0,
        "enemy_gold_lane_penalty_next_turn": 0,
        "wit_mana": 100,

        "skills": skills,
        "skill_cooldowns": {},
        "race_profile": race_profile,

        "used_rush": False,
        "used_block": False,
        "action_locked": False,
        "takeStaminaDebuff": False,

        "next_roll_flat_bonus": 0,
        "next_roll_add_d": 0,
        "next_roll_add_kh": 0,
        "next_roll_floor_bonus": 0,
        "next_roll_selected_die_bonus": 0,
        "next_roll_cap_bonus": 0,
        "no_reroll_this_turn": False,
        "no_reroll_next_turn": False,
        "zone_left": 1,

        "zone": zone,
    }
    set_runtime_stamina(game["players"][mob_id], race_profile.get("stamina", 1))
    apply_web_timing_player_defaults(game["players"][mob_id])

    return True, f"เพิ่ม mob `{preset['name']}` Lv.{level} เรียบร้อย"

def grant_start_rerolls(channel_id: int, amount: int = 2):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    for _, player in game["players"].items():
        player["reroll_left"] = 2

    return True, f"แจก reroll คนละ {amount} ครั้งแล้ว"

def get_player_in_game(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return None
    return game["players"].get(user_id)


def get_players(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return None
    return game["players"]


def update_player_score(channel_id: int, user_id: int, amount: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ผู้เล่นนี้ไม่ได้อยู่ในเกม"

    player["score"] += amount
    return True, player["score"]

def can_use_wit_reroll(game_player: dict, base_total: int) -> bool:
    effective_stats = game_player.get("effective_race_stats") or {}
    threshold = int(effective_stats.get("effective_wit_requirement", 0))

    if game_player.get("wit_reroll_left", 0) <= 0:
        return False

    return base_total < threshold

def can_player_roll(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if not game["started"]:
        return False, "เกมยังไม่เริ่ม"

    player = game["players"].get(user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    if player["last_roll_turn"] == game["turn"]:
        return False, "คุณทอยไปแล้วในเทิร์นนี้"

    return True, "สามารถทอยได้"


def mark_player_rolled(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    player["last_roll_turn"] = game["turn"]
    return True, "บันทึกการทอยแล้ว"

#----------------------------------------------------------------------
# SKILL SYSTEM
#----------------------------------------------------------------------
def has_position(position_groups, *targets):
    return any(t in position_groups for t in targets)

def get_position_groups(channel_id: int, user_id: int) -> set[str]:
    game = get_game(channel_id)
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

def _get_score_map(game: dict) -> dict:
    return game.get("turn_snapshot_scores") or {
        uid: p["score"]
        for uid, p in game["players"].items()
    }


def _distance_bounds(min_distance, max_distance):
    lower = float("-inf") if min_distance is None else min_distance
    upper = float("inf") if max_distance is None else max_distance
    if lower > upper:
        lower, upper = upper, lower
    return lower, upper


def _distance_in_bounds(distance: int, min_distance, max_distance) -> bool:
    lower, upper = _distance_bounds(min_distance, max_distance)
    return lower <= distance <= upper


def _iter_target_distances(game: dict, user_id):
    scores = _get_score_map(game)
    if user_id not in scores:
        return []

    player_score = scores[user_id]
    distances = []

    for other_id in game["players"]:
        if other_id == user_id or other_id not in scores:
            continue
        distances.append((other_id, scores[other_id] - player_score))

    return distances


def get_nearest_target_distance(game, user_id):
    if game["players"].get(user_id) is None:
        return None

    distances = [distance for _, distance in _iter_target_distances(game, user_id)]

    if not distances:
        return None

    return min(distances, key=lambda d: abs(d))


def has_target_in_distance(game, user_id, min_distance, max_distance) -> bool:
    return any(
        _distance_in_bounds(distance, min_distance, max_distance)
        for _, distance in _iter_target_distances(game, user_id)
    )


def is_front_blocked(game, user_id):
    player = game["players"].get(user_id)
    if not player:
        return False

    player_score = player.get("score", 0)

    for other_id, other in game["players"].items():
        if other_id == user_id:
            continue

        distance = other.get("score", 0) - player_score

        if 0 < distance <= 20:
            return True

    return False

def check_skill_trigger(
    channel_id: int,
    user_id,
    skill: dict,
    *,
    path_type=None,
    phase=None,
):
    game = get_game(channel_id)
    if game is None:
        return False, "ไม่พบเกม"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่น"

    trigger = skill.get("trigger", {})

    if not trigger:
        return True, "ใช้สกิลได้"

    if phase is None:
        phase = get_phase_from_turn(game["turn"], game["max_turn"])

    if path_type is None:
        path_type = get_current_path_type(game)

    # path type
    required_path = trigger.get("path_type")
    if required_path is not None and path_type != required_path:
        return False, "เงื่อนไขเส้นทางไม่ตรง"

    # style
    required_style = trigger.get("style")
    if required_style is not None:
        if player.get("style") != required_style:
            return False, "แผนวิ่งไม่ตรงเงื่อนไข"

    base_stat_requirements = trigger.get("base_stats_min") or {}
    if base_stat_requirements:
        base_stats = player.get("base_race_stats") or player.get("race_profile") or {}
        for stat, minimum in base_stat_requirements.items():
            if stat not in RACE_STAT_FIELDS:
                continue
            if int(base_stats.get(stat, 0) or 0) < int(minimum):
                return False, f"ต้องมี {stat.title()} พื้นฐานอย่างน้อย {minimum}"

    # turn min/max
    turn_min = trigger.get("turn_min")
    if turn_min is not None and game["turn"] < turn_min:
        return False, f"ต้องใช้ตั้งแต่เทิร์น {turn_min}"

    turn_max = trigger.get("turn_max")
    if turn_max is not None and game["turn"] > turn_max:
        return False, f"ใช้ได้ไม่เกินเทิร์น {turn_max}"

    # phase min/max
    phase_min = trigger.get("phase_min")
    if phase_min is not None and phase < phase_min:
        return False, f"ต้องใช้ตั้งแต่ Phase {phase_min}"

    phase_max = trigger.get("phase_max")
    if phase_max is not None and phase > phase_max:
        return False, f"ใช้ได้ไม่เกิน Phase {phase_max}"

    # This is intentionally checked before execute_skill_core increments the
    # counter, so a threshold of 4 means four previous successful skill uses.
    skill_use_count_min = trigger.get("skill_use_count_min")
    if skill_use_count_min is not None:
        skill_use_count = int(player.get("skill_use_count", 0) or 0)
        if skill_use_count < skill_use_count_min:
            return False, (
                f"ต้องใช้สกิลแล้วอย่างน้อย {skill_use_count_min} ครั้งในการแข่งขันนี้"
            )

    # last spurt
    required_lastspurt = trigger.get("lastspurt")
    if required_lastspurt is not None:
        on_lastspurt = is_lastspurt(game)
        if on_lastspurt != required_lastspurt:
            return False, "ยังไม่เข้า Last Spurt"

    # last corner
    required_last_corner = trigger.get("last_corner")
    if required_last_corner is not None:
        on_last_corner = is_last_corner(game)
        if on_last_corner != required_last_corner:
            return False, "ยังไม่ใช่โค้งสุดท้าย"

    # distance color
    required_distance_color = trigger.get("distance_color")
    if required_distance_color is not None:
        score_map = _get_score_map(game)
        skill_effects, _ = build_pending_effects_from_player(player)
        distance_color, _ = get_distance_color(
            user_id,
            score_map,
            skill_effects or [],
            game.get("players", {}),
        )
        if distance_color != required_distance_color:
            return False, "สีระยะไม่ตรงเงื่อนไข"

    # position group
    required_position_group = trigger.get("position_group")
    if required_position_group is not None:
        position_group = get_position_groups(channel_id, user_id)
        if required_position_group not in position_group:
            return False, f"ตำแหน่งกลุ่มไม่ตรงเงื่อนไข {required_position_group}"

    # distance type
    required_distance_type = trigger.get("distance_type")
    if required_distance_type is not None:
        distance_type = game.get("distance_type") or game.get("distance")
        if str(distance_type).lower() != str(required_distance_type).lower():
            return False, "ประเภทระยะไม่ตรงเงื่อนไข"

    # track
    required_track = trigger.get("track")
    if required_track is not None:
        track = game.get("track")
        if str(track or "").lower() != str(required_track).lower():
            return False, "พื้นสนามไม่ตรงเงื่อนไข"

    # target distance
    target_distance_min = trigger.get("target_distance_min")
    target_distance_max = trigger.get("target_distance_max")

    if target_distance_min is not None or target_distance_max is not None:
        if not has_target_in_distance(
            game,
            user_id,
            target_distance_min,
            target_distance_max,
        ):
            return False, "No target in range"

    # front blocked
    required_front_blocked = trigger.get("front_blocked")
    if required_front_blocked is not None:
        is_blocked = is_front_blocked(game, user_id)
        if is_blocked != required_front_blocked:
            return False, "เงื่อนไขถูกบล็อกด้านหน้าไม่ตรง"

    # nearby uma count
    required_nearby_count = trigger.get("nearby_uma_count")
    if required_nearby_count is not None:
        score_map = _get_score_map(game)
        skill_effects, _ = build_pending_effects_from_player(player)

        _, nearby_count = get_distance_color(
            user_id,
            score_map,
            skill_effects or [],
            game.get("players", {}),
        )

        if nearby_count < required_nearby_count:
            return False, (
                f"ต้องมีคนในระยะทองอย่างน้อย "
                f"{required_nearby_count} คน"
            )

    return True, "ใช้สกิลได้"

def get_mob_usable_skills(channel_id: int, game: dict, user_id: str):
    player = game["players"].get(user_id)
    if not player:
        return []

    equipped = player.get("skills", {})
    cooldowns = player.get("skill_cooldowns", {})
    wit_mana = player.get("wit_mana", 0)

    path_type = get_current_path_type(game)
    phase = get_phase_from_turn(game["turn"], game["max_turn"])

    usable = []

    for _, skill_id in equipped.items():
        if not skill_id:
            continue

        skill = SKILLS.get(skill_id)
        if not skill:
            continue

        # Passive skills are activated by activate_passive_skills(), not by AI.
        if skill.get("activation") == "passive":
            continue

        if cooldowns.get(skill_id, 0) > 0:
            continue

        if wit_mana < skill.get("cost", 0):
            continue

        trigger_result = check_skill_trigger(
            channel_id,
            user_id,
            skill,
            path_type=path_type,
            phase=phase,
        )

        if not isinstance(trigger_result, tuple):
            continue

        ok, _reason = trigger_result

        if not ok:
            continue

        usable.append((skill_id, skill))

    return usable

def run_bot_race_test(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ยังไม่มีเกมในห้องนี้"}

    if not game.get("started"):
        success, message = start_game(channel_id)
        if not success:
            return False, {"message": message}

    game = get_game(channel_id)

    mob_ids = [
        user_id
        for user_id, player in game["players"].items()
        if player.get("is_mob")
    ]

    if not mob_ids:
        return False, {"message": "ไม่มี mob สำหรับทดสอบ"}

    while game and game["turn"] <= game["max_turn"]:
        current_turn = game["turn"]

        for user_id, player in list(game["players"].items()):
            if not player.get("is_mob"):
                continue

            if player.get("last_roll_turn") == current_turn:
                continue

            process_mob_turn(channel_id, user_id)

        if game["turn"] >= game["max_turn"]:
            break

        next_turn(channel_id)
        game = get_game(channel_id)

    ranked_players = get_ranked_players(channel_id)

    return True, {
        "game": game,
        "ranked_players": ranked_players,
        "turn_score_logs": game.get("turn_score_logs", []),
    }


def should_mob_use_endgame_zone(game: dict, user_id, player: dict, phase: int) -> bool:
    """Let Pace/Late Mobs spend a valuable Zone during their endgame windows."""
    style = player.get("style")
    eligible_phase = (
        (style == "Late" and phase in {3, 4})
        or (style == "Pace" and phase == 4)
    )
    if not eligible_phase:
        return False
    if player.get("zone_left", 0) <= 0:
        return False

    zone = player.get("zone") or {}
    effects = get_zone_effects_from_build(zone.get("build", {}))
    snapshot = get_runtime_stamina_snapshot(player)
    max_stamina = max(1, int(snapshot.get("max_stamina", 0) or 0))
    stamina_ratio = int(snapshot.get("current_stamina", 0) or 0) / max_stamina

    # Values approximate the immediate impact of the one-use Zone.  Healing is
    # valuable only when the runner actually needs Stamina, so a full-Stamina
    # Mob does not spend a recovery-only Zone early in the final phase.
    value = (
        int(effects.get("flat", 0) or 0)
        + int(effects.get("add_dkh", 0) or 0) * 40
        + (int(effects.get("floor", 0) or 0) + int(effects.get("cap", 0) or 0)) * 5
        + int(effects.get("modify_current_speed", 0) or 0) * 24
        + int(effects.get("race_speed", 0) or 0) * 20
    )
    if stamina_ratio < 0.65:
        value += int(effects.get("self_heal_stamina", 0) or 0) * 30

    if value < 20:
        return False

    turns_remaining = max(1, int(game.get("max_turn", 1) or 1) - int(game.get("turn", 1) or 1))
    chance = min(0.85, 0.18 + min(0.42, value / 180) + (0.15 if turns_remaining <= 1 else 0))

    # Keep the chance stable for this Mob and turn, while giving each eligible
    # endgame turn a distinct opportunity to use the Zone.
    seed = f"zone:{game.get('channel_id', '')}:{user_id}:{game.get('turn', 0)}"
    return random.Random(seed).random() < chance

def process_mob_turn(channel_id: int, user_id: str):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ยังไม่มีเกมในห้องนี้"}

    player = game["players"].get(user_id)
    if player is None:
        return False, {"message": "ไม่พบ mob"}

    if not player.get("is_mob"):
        return False, {"message": "ผู้เล่นนี้ไม่ใช่ mob"}

    # This function can be reached from both the turn-start flow and the
    # after-player-roll flow.  Discord sends await between mob results, so a
    # player can roll while the turn-start loop is still in progress.  Make
    # the mob turn idempotent to prevent a second score roll in that case.
    if player.get("last_roll_turn") == game.get("turn"):
        return False, {"message": "Mob already rolled this turn", "already_rolled": True}

    if _supports_lane_system(game):
        target_lane = decide_mob_target_lane(game, user_id)
        if target_lane is not None:
            player["pending_lane"] = clamp_lane(target_lane)

    zone_success = False
    used_skill_payloads = []
    skill_embeds = []

    phase = get_phase_from_turn(
        game["turn"],
        game["max_turn"]
    )

    turn_trigger = (
        game["turn"] == game["max_turn"]
        or (
            game["turn"] == 1
            and player.get("style", "Front") == "Front"
        )
        or (
            phase == 4
            and player.get("style") == "End"
        )
        or should_mob_use_endgame_zone(game, user_id, player, phase)
    )

    if turn_trigger and player.get("zone_left", 0) > 0:
        zone_success, _zone_message = apply_zone_in_game(game, player)

    usable_skills = get_mob_usable_skills(
        channel_id=channel_id,
        game=game,
        user_id=user_id,
    )

    skill_ids_to_use = decide_mob_skill_combo(
        game=game,
        user_id=user_id,
        usable_skills=usable_skills,
        debug=False,
    )

    for skill_id in skill_ids_to_use:
        success, skill_payload = execute_skill_core(
            channel_id=channel_id,
            user_id=user_id,
            skill_id=skill_id,
            consume_cost=True,
        )

        if not success:
            continue

        used_skill_payloads.append(skill_payload)

        skill = skill_payload.get("skill") or SKILLS.get(skill_id)

        if skill:
            skill_embeds.append(
                build_skill_use_embed(
                    player_name=player.get("display_name")
                    or player.get("username")
                    or "Mob",
                    player=player,
                    skill=skill,
                    payload=skill_payload,
                )
            )

    success, payload = execute_roll_core(
        channel_id=channel_id,
        user_id=user_id,
        title_prefix="วิ่งอัตโนมัติ",
        mark_roll=True,
    )

    if not success:
        return False, payload

    if zone_success:
        payload["zone_preview"] = build_zone_used_preview_embed(player)

    if used_skill_payloads:
        payload["used_skills"] = used_skill_payloads
        payload["used_skill_ids"] = [
            item["skill_id"] for item in used_skill_payloads
        ]

    if skill_embeds:
        payload["skill_embeds"] = skill_embeds

    return True, payload

def execute_skill_core(
    channel_id: int,
    user_id,
    skill_id: str,
    *,
    consume_cost: bool = True,
    ignore_cooldown: bool = False,
    ignore_trigger: bool = False,
    apply_cooldown: bool = True,
):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ไม่พบเกม"}

    player = game["players"].get(user_id)
    if player is None:
        return False, {"message": "ไม่พบผู้เล่น"}

    skill = SKILLS.get(skill_id)
    if not skill:
        return False, {"message": "ไม่พบข้อมูลสกิล"}

    if not get_game_rule(game, "AllowSkill"):
        return False, {"message": "ห้องนี้ปิดการใช้ Skill และ Zone"}

    if get_game_rule(game, "NoDebuff") and "debuff" in skill.get("tags", []):
        return False, {"message": "ห้องนี้ห้ามใช้สกิล Debuff"}

    # =====================================
    # Cooldown
    # =====================================

    on_cd, cd_left = is_skill_on_cooldown(
        channel_id,
        user_id,
        skill_id
    )

    if on_cd and not ignore_cooldown:
        return False, {
            "message": f"สกิลติด cooldown {cd_left}"
        }

    # =====================================
    # Trigger
    # =====================================

    path_type = get_current_path_type(game)

    phase = get_phase_from_turn(
        game["turn"],
        game["max_turn"]
    )

    ok, reason = check_skill_trigger(
        channel_id,
        user_id,
        skill,
        path_type=path_type,
        phase=phase
    )

    if not ok and not ignore_trigger:
        return False, {"message": reason}

    # =====================================
    # Cost
    # =====================================

    cost = skill.get("cost", 0)

    if consume_cost:
        if player.get("wit_mana", 0) < cost:
            return False, {
                "message": f"Wit ไม่พอ ({cost})"
            }

    # =====================================
    # Split effects
    # =====================================

    instant_effects = []
    queued_effects = []
    random_activations = []
    race_stat_changes = []

    for effect in skill.get("effects", []):

        effect_condition = effect.get("condition")
        if effect_condition:
            condition_skill = {"trigger": effect_condition}
            condition_met, _ = check_skill_trigger(
                channel_id,
                user_id,
                condition_skill,
                path_type=path_type,
                phase=phase,
            )
            if not condition_met:
                continue

        effect_type = effect.get("type")
        duration = effect.get("duration")

        if (
            effect_type in [
                "modify_velocity",
                "modify_roll_floor",
                "modify_roll_cap",
                "modify_roll_cap_floor",
                "cap_floor",
                "add_d",
                "add_kh",
                "add_dkh",
            ]
            or duration == "this_roll"
        ):
            queued_effects.append(effect)

        else:
            instant_effects.append(effect)

    result_texts = []

    # =====================================
    # Instant
    # =====================================

    if instant_effects:

        temp_skill = skill.copy()
        temp_skill["effects"] = instant_effects

        success, result_text = apply_skill(
            channel_id,
            user_id,
            temp_skill
        )

        if not success:
            return False, {"message": result_text}

        result_texts.append(result_text)
        random_activations.extend(temp_skill.pop("_random_activations", []))
        race_stat_changes.extend(temp_skill.pop("_race_stat_changes", []))

    # =====================================
    # Queued
    # =====================================

    if queued_effects:
        for effect in queued_effects:
            effect_target = effect.get("target")
            target_skill = skill
            if effect_target:
                target_skill = skill.copy()
                target_skill["target"] = {
                    **skill.get("target", {}),
                    **effect_target,
                }

            queued_targets = resolve_skill_targets(channel_id, user_id, target_skill)
            for _, target_player in queued_targets:
                apply_next_roll_effects_to_player(target_player, [effect])

        result_texts.append(
            "บัฟถูกสะสมไว้สำหรับการวิ่งครั้งถัดไป"
        )

    if not instant_effects and not queued_effects:
        return False, {
            "message": "ยังไม่มี effect รองรับ"
        }

    # =====================================
    # Consume resource
    # =====================================

    if consume_cost:
        player["wit_mana"] -= cost

    player.setdefault("used_skills_this_turn", [])
    player["used_skills_this_turn"].append({
        "id": skill_id,
        "name": skill.get("name", skill_id),
    })
    player["skill_use_count"] = int(player.get("skill_use_count", 0) or 0) + 1
    record_race_action(
        game,
        user_id,
        "skill",
        {"skill_id": skill_id, "skill_name": skill.get("name", skill_id), "cost": cost},
    )

    # =====================================
    # Cooldown
    # =====================================

    if apply_cooldown:
        set_player_skill_cd(
            channel_id,
            user_id,
            skill_id,
            skill.get("cooldown", 0)
        )

    return True, {
        "skill_id": skill_id,
        "skill_name": skill["name"],
        "skill": skill,
        "result_texts": result_texts,
        "random_activations": random_activations,
        "race_stat_changes": race_stat_changes,
        "cost": cost,
        "show_lane_preview": any(
            effect.get("type") == "resolve_pending_lane_now"
            for effect in instant_effects
        ),
    }


def activate_passive_skills(channel_id: int) -> list[dict]:
    """Activate each equipped passive once, at the first turn that matches it."""
    game = get_game(channel_id)
    if game is None or not game.get("started"):
        return []

    activations = []
    for user_id, player in game.get("players", {}).items():
        activated_ids = player.setdefault("activated_passive_skills", set())
        for skill_id in set((player.get("skills") or {}).values()):
            skill = SKILLS.get(skill_id)
            if (
                not skill_id
                or not skill
                or skill.get("activation") != "passive"
                or skill_id in activated_ids
            ):
                continue

            success, payload = execute_skill_core(
                channel_id,
                user_id,
                skill_id,
                consume_cost=True,
            )
            if success:
                activated_ids.add(skill_id)
                payload["user_id"] = str(user_id)
                activations.append(payload)

    if activations:
        game.setdefault("pending_passive_skill_activations", []).extend(activations)
    return activations


def drain_pending_passive_skill_embeds(channel_id: int) -> list[discord.Embed]:
    """Build normal skill-use embeds for automatic Passive activations."""
    game = get_game(channel_id)
    if game is None:
        return []

    embeds = []
    players = game.get("players", {})
    for payload in game.pop("pending_passive_skill_activations", []):
        user_id = payload.get("user_id")
        player = next(
            (
                candidate
                for candidate_id, candidate in players.items()
                if str(candidate_id) == str(user_id)
            ),
            None,
        )
        skill = payload.get("skill") or SKILLS.get(payload.get("skill_id"))
        if not player or not skill:
            continue

        embeds.append(
            build_skill_use_embed(
                player_name=player.get("display_name") or player.get("username") or "Player",
                player=player,
                skill=skill,
                payload=payload,
            )
        )

    return embeds

def apply_skill(channel_id: int, user_id: int, skill: dict):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = get_player_in_game(channel_id, user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    targets = resolve_skill_targets(channel_id, user_id, skill)

    for effect in skill.get("effects", []):
        if effect.get("type") == "force_rush":
            ok, reason = can_force_rush_targets(channel_id, targets)
            if not ok:
                return False, reason

    applied_texts = []

    for effect in skill.get("effects", []):
        effect_type = effect.get("type")
        value = effect.get("value", 0)

        if effect_type == "recover_stamina":
            sync_runtime_stamina(player)
            stamina_gain = max(1, int(round(player.get("max_stamina", 0) * 0.10 * float(value or 0))))
            set_runtime_stamina(
                player,
                player.get("stamina_stat", 0),
                player["stamina_left"] + stamina_gain,
            )
            applied_texts.append(f"ฟื้นฟู STA ตัวเอง +{stamina_gain}")

        elif effect_type == "modify_current_speed":

            incrase_speed_by_acceleration(game, player, effect["value"])
            applied_texts.append(f"เร่งความเร็วขึ้น {value} ระดับ")

        elif effect_type == "modify_race_stats":
            if not targets:
                targets = [(user_id, player)]

            for target_id, target_info in targets:
                stamina_before = get_runtime_stamina_snapshot(target_info)
                changes = apply_race_stat_changes(target_info, game, effect)
                if not changes:
                    continue
                stamina_after = get_runtime_stamina_snapshot(target_info)
                change_text = ", ".join(
                    f"{stat.title()} {delta:+}" for stat, delta in changes.items()
                )
                target_name = (
                    "ตัวเอง"
                    if target_id == user_id
                    else format_player_reference(target_id, target_info)
                )
                stamina_text = ""
                if "stamina" in changes:
                    stamina_text = (
                        f" | Stamina {stamina_before['current_stamina']}/"
                        f"{stamina_before['max_stamina']} → "
                        f"{stamina_after['current_stamina']}/"
                        f"{stamina_after['max_stamina']}"
                    )
                applied_texts.append(f"ปรับ Stats ของ{target_name}: {change_text}{stamina_text}")
                skill.setdefault("_race_stat_changes", []).append({
                    "target_id": str(target_id),
                    "target_name": target_name,
                    "changes": changes,
                    "stamina_before": stamina_before,
                    "stamina_after": stamina_after,
                })

        elif effect_type == "self_heal_stamina":
            sync_runtime_stamina(player)
            stamina_gain = max(1, int(round(player.get("max_stamina", 0) * 0.10 * float(value or 0))))
            set_runtime_stamina(
                player,
                player.get("stamina_stat", 0),
                player["stamina_left"] + stamina_gain,
            )
            applied_texts.append(f"ฟื้นฟู STA ตัวเอง +{stamina_gain}")

        elif effect_type == "flat_total":
            # ถ้า target เป็น self ก็ลงตัวเอง ถ้าไม่ใช่ก็ลง target
            if not targets:
                success, _ = update_player_score(channel_id, user_id, value)
                if success:
                    sign = "+" if value >= 0 else ""
                    applied_texts.append(f"ปรับคะแนนตัวเองทันที {sign}{value}")
            else:
                for target_id, _ in targets:
                    success, _ = update_player_score(channel_id, target_id, value)
                    if success:
                        sign = "+" if value >= 0 else ""
                        if target_id == user_id:
                            applied_texts.append(f"ปรับคะแนนตัวเองทันที {sign}{value}")
                        else:
                            applied_texts.append(f"ปรับคะแนน {format_player_reference(target_id, target_info)} ทันที {sign}{value}")

        elif effect_type == "reduce_stamina":
            if not targets:
                continue

            for target_id, target_info in targets:
                sync_runtime_stamina(target_info)
                before = target_info.get("stamina_left", 0)
                stamina_loss = max(1, int(round(target_info.get("max_stamina", 0) * 0.10 * float(value or 0))))
                set_runtime_stamina(
                    target_info,
                    target_info.get("stamina_stat", 0),
                    before - stamina_loss,
                )
                applied_texts.append(f"ลด STA ของ {format_player_reference(target_id, target_info)} -{stamina_loss}")

        elif effect_type == "resolve_pending_lane_now":
            lane_success, lane_result = apply_pending_lane_change_now(channel_id, user_id)
            if not lane_success:
                return False, lane_result

            previous_lane = lane_result["previous_lane"]
            current_lane = lane_result["current_lane"]
            if lane_result.get("lane_changed"):
                applied_texts.append(f"เปลี่ยน Lane ทันที {previous_lane} -> {current_lane}")
            else:
                applied_texts.append(f"ยืนยัน Lane {current_lane} ทันที")

        elif effect_type == "activate_random_equipped_skills":
            max_cost = effect.get("max_cost", 80)
            count = effect.get("count", 2)
            equipped_skill_ids = list(dict.fromkeys(
                skill_id
                for skill_id in player.get("skills", {}).values()
                if skill_id
            ))
            eligible_skill_ids = [
                skill_id
                for skill_id in equipped_skill_ids
                if skill_id in SKILLS
                and SKILLS[skill_id].get("cost", 0) <= max_cost
                and not any(
                    candidate_effect.get("type") == "activate_random_equipped_skills"
                    for candidate_effect in SKILLS[skill_id].get("effects", [])
                )
            ]
            selected_skill_ids = random.sample(
                eligible_skill_ids,
                min(count, len(eligible_skill_ids)),
            )

            if not selected_skill_ids:
                applied_texts.append(
                    f"ไม่มีสกิลติดตั้งที่ใช้สุ่มได้ (Cost ไม่เกิน {max_cost})"
                )
                continue

            activated_skills = []
            for selected_skill_id in selected_skill_ids:
                activated, payload = execute_skill_core(
                    channel_id,
                    user_id,
                    selected_skill_id,
                    consume_cost=False,
                    ignore_cooldown=True,
                    ignore_trigger=True,
                    apply_cooldown=False,
                )
                if activated:
                    activated_skills.append({
                        "skill_id": selected_skill_id,
                        "name": payload["skill_name"],
                        "result_texts": payload.get("result_texts", []),
                    })

            if activated_skills:
                skill.setdefault("_random_activations", []).extend(activated_skills)
                applied_texts.append("สุ่มใช้สกิลทันที:")
                for activated_skill in activated_skills:
                    applied_texts.append(f"• {activated_skill['name']}")
                    for result_text in activated_skill["result_texts"]:
                        applied_texts.append(f"  └ {result_text}")

        elif effect_type == "apply_debuff_next_turn":
            if not targets:
                continue

            stat = effect.get("stat", "flat_total")

            for target_id, target_info in targets:
                value = effect.get("value", 0)

                if stat == "flat_total":
                    target_info.setdefault("next_roll_flat_bonus", 0)
                    target_info["next_roll_flat_bonus"] += value
                    applied_texts.append(
                        f"ใส่ดีบัฟให้ {format_player_reference(target_id, target_info)} เทิร์นหน้า Flat {value}"
                    )

                elif stat == "cap":
                    target_info.setdefault("next_roll_cap_bonus", 0)
                    target_info["next_roll_cap_bonus"] += value
                    applied_texts.append(
                        f"ใส่ดีบัฟให้ {format_player_reference(target_id, target_info)} เทิร์นหน้า Cap {value}"
                    )

        elif effect_type == "force_rush":
            if not targets:
                continue
                
            for effect in skill.get("effects", []):
                if effect.get("type") == "force_rush":
                    ok, reason = can_force_rush_targets(channel_id, targets)
                    if not ok:
                        return False, reason

            for target_id, target_info in targets:
                rush_success, rush_payload = use_rush(channel_id, target_id)

                if rush_success:
                    applied_texts.append(
                        f"บังคับ {format_player_reference(target_id, target_info)} ใช้ Rush สำเร็จ"
                    )
                else:
                    applied_texts.append(
                        f"บังคับ {format_player_reference(target_id, target_info)} ใช้ Rush ไม่สำเร็จ ({rush_payload})"
                    )

        elif effect_type == "modify_gold_range":
            player.setdefault("gold_range_bonus_this_turn", 0)
            player["gold_range_bonus_this_turn"] += value
            applied_texts.append(f"เพิ่มระยะตรวจ Gold +{value}")

        elif effect_type == "modify_gold_lane_range":
            player.setdefault("gold_lane_bonus_this_turn", 0)
            player["gold_lane_bonus_this_turn"] += value
            applied_texts.append(f"เพิ่มระยะตรวจเลน Gold +{value}")

        elif effect_type == "modify_enemy_gold_range":
            if not targets:
                continue

            value = abs(value)
            for target_id, target_info in targets:
                target_info.setdefault("enemy_gold_range_penalty_next_turn", 0)
                target_info["enemy_gold_range_penalty_next_turn"] += value
                applied_texts.append(f"ลดระยะตรวจ Gold ของ {format_player_reference(target_id, target_info)} {value}")

        elif effect_type == "modify_enemy_gold_lane_range":
            if not targets:
                continue

            value = abs(value)
            for target_id, target_info in targets:
                target_info.setdefault("enemy_gold_lane_penalty_next_turn", 0)
                target_info["enemy_gold_lane_penalty_next_turn"] += value
                applied_texts.append(f"ลดระยะตรวจเลน Gold ของ {format_player_reference(target_id, target_info)} {value}")

    if not applied_texts:
        return False, "สกิลนี้ยังไม่มีผลที่รองรับในระบบตอนนี้"

    return True, "\n".join(applied_texts)

def resolve_skill_targets(channel_id: int, user_id: int, skill: dict) -> list[tuple[int, dict]]:
    game = get_game(channel_id)
    if game is None or user_id not in game["players"]:
        return []

    scores = game.get("turn_snapshot_scores") or {
        uid: p["score"] for uid, p in game["players"].items()
    }

    player = game["players"][user_id]
    my_score = scores[user_id]

    target_cfg = skill.get("target", {})
    scope = target_cfg.get("scope", "self")
    limit = target_cfg.get("limit", 1)
    trigger = skill.get("trigger", {})
    target_distance_min = trigger.get("target_distance_min")
    target_distance_max = trigger.get("target_distance_max")

    if scope == "self":
        return [(user_id, player)]

    front = []
    back = []

    for target_id, info in game["players"].items():
        if target_id == user_id:
            continue

        target_score = scores[target_id]

        gap_front = target_score - my_score
        gap_back = my_score - target_score

        if gap_front > 0 and _distance_in_bounds(
            gap_front,
            target_distance_min,
            target_distance_max,
        ):
            front.append((gap_front, target_id, info))
        elif gap_back > 0 and _distance_in_bounds(
            -gap_back,
            target_distance_min,
            target_distance_max,
        ):
            back.append((gap_back, target_id, info))

    front.sort(key=lambda x: x[0])
    back.sort(key=lambda x: x[0])

    def _same_lane_only(candidates):
        my_lane = clamp_lane(player.get("current_lane"))
        return [
            item
            for item in candidates
            if clamp_lane(item[2].get("current_lane")) == my_lane
        ]

    restrict_same_lane = target_cfg.get(
        "same_lane_only", "debuff" in set(skill.get("tags", []))
    )
    if restrict_same_lane:
        front = _same_lane_only(front)
        back = _same_lane_only(back)

    def _target_pairs(candidates):
        return [
            (tid, info)
            for _, tid, info in candidates
        ]

    if scope == "nearest_front":
        return _target_pairs(front[:1])

    if scope == "nearest_back":
        return _target_pairs(back[:1])

    if scope == "all_front":
        return _target_pairs(front[:limit])

    if scope == "all_back":
        return _target_pairs(back[:limit])

    if scope == "random_enemy":
        enemies = _target_pairs(front + back)
        random.shuffle(enemies)
        return enemies[:limit]

    return []

def build_skill_use_embed(
    *,
    player_name: str,
    player,
    skill,
    payload,
):
    icon_url = ICON_URL.get(skill.get("icon"))

    activation_suffix = " (Passive)" if skill.get("activation") == "passive" else ""
    embed = discord.Embed(
        title=f"{player_name} ใช้สกิล {skill['name']}{activation_suffix}",
        description="\n".join(
            payload.get("result_texts", [])
        ),
        color=discord.Color.green()
    )
    if icon_url:
        embed.set_thumbnail(url=icon_url)

    embed.add_field(
        name=f"{Status_Icon_Type['WIT']} คงเหลือ",
        value=str(player.get("wit_mana", 0)),
        inline=True
    )

    embed.add_field(
        name="⏳ Cooldown",
        value=f"{skill.get('cooldown', 0)} เทิร์น",
        inline=True
    )

    embed.add_field(
        name="✨ บัพรวมทั้งหมด",
        value=build_next_roll_buff_text(player),
        inline=False
    )

    return embed

def build_next_roll_buff_text(player: dict) -> str:
    lines = []

    flat = player.get("next_roll_flat_bonus", 0)
    if flat:
        lines.append(f"เพิ่มผลรวม +{flat}")

    add_d = player.get("next_roll_add_d", 0)
    if add_d:
        lines.append(f"เพิ่มลูกเต๋า +{add_d}")

    add_kh = player.get("next_roll_add_kh", 0)
    if add_kh:
        lines.append(f"เพิ่มจำนวนลูกที่เลือก +{add_kh}")

    floor = player.get("next_roll_floor_bonus", 0)
    if floor:
        lines.append(f"เพิ่มแต้มขั้นต่ำ +{floor}")

    gold_range = player.get("gold_range_bonus_this_turn", 0)
    if gold_range:
        lines.append(f"เพิ่มระยะในการนับโรล Gold +{gold_range}")
    gold_lane_bonus = player.get("gold_lane_bonus_this_turn", 0)
    if gold_lane_bonus:
        lines.append(f"เพิ่มระยะตรวจเลน Gold +{gold_lane_bonus}")

    selected = player.get("next_roll_selected_die_bonus", 0)
    if selected:
        lines.append(f"เพิ่มแต้มลูกที่เลือก +{selected}")

    cap = player.get("next_roll_cap_bonus", 0)
    if cap:
        sign = "+" if cap > 0 else ""
        lines.append(f"ปรับแต้มสูงสุดลูกเต๋า {sign}{cap}")

    return "\n".join(lines) if lines else "ไม่มีบัฟค้าง"
