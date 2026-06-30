import copy
import uuid
import math
import discord
import random

from utils.race.race_presets import RACE_PRESET
from utils.skill.skill_presets import SKILLS, ICON
from utils.mob.mob_decision import decide_mob_skill_combo

from utils.mob.mob_presets import MOB_PRESETS
from utils.database import get_player, get_player_skill_slots
from utils.profile_images import resolve_player_avatar_url
from utils.zone.zone_manager import apply_zone_in_game
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
from utils.dice.dice_presets import (
    MAX_SPEED_PHASE
)
from utils.in_game_manager import incrase_speed_by_acceleration

from utils.icon_presets import Status_Icon_Type, ICONS

VALID_STYLES = {"Front", "Pace", "Late", "End"}
games = {}


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

    pending_effects, merged_stats = build_pending_effects_from_player(game_player)

    path_type = get_current_path_type(game)
    path_effect = get_path_effect(path_type, game_player, race_player)

    stamina_note, stamina_penalty_active = apply_stamina_debuff(game_player,path_effect,pending_effects)
    new_stamina_note = apply_stamina_for_roll(game_player,path_effect)

    if (new_stamina_note != None):
        stamina_note = new_stamina_note

    result = roll_race_dice(
        game_player=game_player,
        player_stats=roll_stats,
        player_id=user_id,
        score_map=snapshot_scores,
        turn=game["turn"],
        max_turn=game["max_turn"],
        path_effect=path_effect,
        skill_effects=pending_effects,
    )

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
    }

    game_player["lastedBuff"] = merged_stats

    game_player["next_roll_flat_bonus"] = 0
    game_player["next_roll_add_d"] = 0
    game_player["next_roll_add_kh"] = 0
    game_player["next_roll_floor_bonus"] = 0
    game_player["next_roll_selected_die_bonus"] = 0
    game_player["next_roll_cap_bonus"] = 0
    game_player["gold_range_bonus_this_turn"] = 0
    game_player["enemy_gold_range_penalty_next_turn"] = 0

    if stamina_penalty_active:
        if result['bonus_display'] == "-":
            result['bonus_display'] = "-20CAP"
        else:
            result['bonus_display'] += " -20CAP"
            
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
    if game_player["stamina_left"] >= stamina_cost:
        return stamina_note, False
    else:
        pending_effects.append({
            "type": "modify_roll_cap",
            "value": -20,
            "duration": "this_roll"
        })
        stamina_note = f"ไม่พอ Cap ลูกเต๋า -20"
        return stamina_note, True

def apply_stamina_for_roll(
    game_player: dict,
    path_effect: dict,
) -> tuple[str | None, bool]:
    stamina_note = None
    stamina_gain = path_effect.get("stamina_gain", 0)
    stamina_cost = path_effect.get("stamina_cost", 0)

    if stamina_gain > 0:
        game_player["stamina_left"] += stamina_gain


    if game_player["stamina_left"] >= stamina_cost:
        game_player["stamina_left"] -= stamina_cost
        
        if stamina_cost == 0 and stamina_gain == 0:
            stamina_note = f"{game_player['stamina_left']}"
        else:
            if stamina_gain > 0:
                stamina_note = f"+{stamina_gain} / -{stamina_cost} เหลือ {game_player['stamina_left']}"
            else:
                stamina_note = f"{game_player['stamina_left'] + stamina_cost} → {game_player['stamina_left']}"
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

        "turn_confirmations": set(),
        "awaiting_turn_confirm": False,
    }

    for preset_key in stage.get("auto_mobs", []):
        add_mob_from_preset(channel_id, preset_key)

    return True

def reset_turn_confirmations(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    game["turn_confirmations"] = set()
    game["awaiting_turn_confirm"] = False
    return True

def start_turn_confirmation(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    game["turn_confirmations"] = set()
    game["awaiting_turn_confirm"] = True
    return True

def confirm_turn(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if not game["awaiting_turn_confirm"]:
        return False, "ตอนนี้ยังไม่อยู่ในช่วงยืนยันจบเทิร์น"

    if user_id not in game["players"]:
        return False, "คุณไม่ได้อยู่ในเกมนี้"

    game["turn_confirmations"].add(user_id)

    confirmed_count = len(game["turn_confirmations"])
    total_players = len(game["players"])

    for user_id, player in game["players"].items():
        if player.get("is_mob"):
            confirmed_count += 1

    all_confirmed = confirmed_count >= total_players

    return True, {
        "confirmed_count": confirmed_count,
        "total_players": total_players,
        "all_confirmed": all_confirmed,
    }

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

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }

    
    for user_id, player in game["players"].items():
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
            player["stamina_left"] = 8 + base_player["stamina"]

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
            player["stamina_left"] = 8 + base_player.get("stamina", 1)
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
            player["stamina_left"] = 8 + db_player["stamina"]

            player["race_profile"] = db_player.copy()

            slots = get_player_skill_slots(user_id) or {
                "slot_1": None,
                "slot_2": None,
                "slot_3": None,
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

        # reset กลางเกม ใช้ร่วมกันทั้ง player จริงและ mob
        player["skill_cooldowns"] = {}
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

        player["no_reroll_this_turn"] = False
        player["no_reroll_next_turn"] = False
        player["last_roll_turn"] = -1
        player["zone_left"] = 1

        refresh_player_race_aptitudes(player, game)

        player["current_max_speed"] = MAX_SPEED_PHASE[player["style"]]["start"]
        player["wit_mana"] = 100 + (player["race_profile"]["wit"] * 10)

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
    surface = game.get("track") or game.get("surface", "turf")
    distance = game.get("distance", "medium")
    effective_stats = calculate_effective_race_stats(
        {
            "style": style,
            "race_profile": aptitude_source,
        },
        {
            "track": surface,
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
        display_image=mob.get("thumnail", ""),
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

    if player["stamina_left"] < amount:
        return False, player["stamina_left"]

    player["stamina_left"] -= amount
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

    if player["stamina_left"] > 0:
        player["stamina_left"] -= 1
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

    return player["stamina_left"]

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
            
def use_block(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่น"

    if player["used_block"]:
        return False, "คุณใช้ Block ไปแล้ว"

    behind_players = get_players_behind(channel_id, user_id)
    valid_targets = [(uid, gap, info) for uid, gap, info in behind_players if gap > 20]

    if not valid_targets:
        return False, "ไม่มีคนด้านหลังที่ห่างเกิน 20"

    target_id, gap, target_info = valid_targets[0]

    move_back = gap - 20
    player["score"] -= move_back

    target_info["next_roll_flat_bonus"] -= 20
    player["used_block"] = True
    player["action_locked"] = True

    return True, {
        "target_id": target_id,
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
        return False, "คุณใช้ Rush ไปแล้ว"

    ahead_players = get_players_ahead(channel_id, user_id)
    valid_targets = [(uid, gap, info) for uid, gap, info in ahead_players if gap <= 30]

    if not valid_targets:
        return False, "ไม่มีคนด้านหน้าที่อยู่ในระยะ 30"

    return True, None

def use_rush(channel_id: int, user_id: int):
    ok, reason = can_use_rush(channel_id, user_id)
    if not ok:
        return False, reason

    game = get_game(channel_id)
    player = game["players"].get(user_id)

    ahead_players = get_players_ahead(channel_id, user_id)
    valid_targets = [(uid, gap, info) for uid, gap, info in ahead_players if gap <= 30]

    target_id, gap, target_info = valid_targets[0]

    move_forward = max(gap - 10, 0)
    player["score"] += move_forward

    player["next_roll_flat_bonus"] -= 20
    player["no_reroll_this_turn"] = True
    player["used_rush"] = True
    player["action_locked"] = True

    return True, {
        "target_id": target_id,
        "move_forward": move_forward,
        "new_score": player["score"],
    }

def can_force_rush_targets(channel_id: int, targets: list[tuple[int, dict]]) -> tuple[bool, str | None]:
    if not targets:
        return False, "ไม่มีเป้าหมายสำหรับบังคับ Rush"

    for target_id, _ in targets:
        game = get_game(channel_id)
        if game is None:
            return False, "ยังไม่มีเกมในห้องนี้"

        player = game["players"].get(target_id)
        if player is None:
            continue

        if player.get("used_rush"):
            continue

        ahead_players = get_players_ahead(channel_id, target_id)
        valid_targets = [(uid, gap, info) for uid, gap, info in ahead_players if gap <= 30]

        if valid_targets:
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

    # รวม lastedBuff
    buff = player.get("lastedBuff", {})
    if buff:
        flat += buff.get("flat", 0)
        add_d += buff.get("add_d", 0)
        add_kh += buff.get("add_kh", 0)
        floor += buff.get("floor", 0)
        cap += buff.get("cap", 0)
        gold_range += buff.get("gold_range", 0)

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

    merged_stats = {
        "flat": flat,
        "add_d": add_d,
        "add_kh": add_kh,
        "floor": floor,
        "cap": cap,
        "gold_range": gold_range,  
        "enemy_gold_range_penalty": enemy_gold_range_penalty,
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

    embed.add_field(name=f"🏇 ความเร็วปัจจุบัน {current_max_speed} รูปแบบ {result['distance_color']}", value= f"{result['display']} {result['bonus_display']}" , inline=False)
    
    if stamina_note == None:
        stamina_note = str(game_player["stamina_left"])

    embed.add_field(
        name= f"🏁 Score รวม: **{new_score}** ({result['total']})",
        value=(
            f"{Status_Icon_Type['STA']} : **{stamina_note}**　"
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

    current_turn = game["turn"]
    snapshot_scores = game.get("turn_snapshot_scores", {})

    game.setdefault("turn_score_logs", [])

    for user_id, info in game["players"].items():
        before_score = snapshot_scores.get(user_id, 0)
        current_score = info.get("score", 0)
        gain = current_score - before_score

        display_name = (
            info.get("display_name")
            or info.get("username")
            or str(user_id)
        )

        game["turn_score_logs"].append({
            "turn": current_turn,
            "player_id": str(user_id),
            "name": display_name,
            "style": info.get("style"),
            "gain": gain,
            "score_before": before_score,
            "score_after": current_score,
            "roll": info.get("last_roll_log"),
            "skills": info.get("used_skills_this_turn", []),
        })

    game["turn"] += 1

    tick_skill_cooldowns(channel_id)

    for player in game["players"].values():
        player["no_reroll_this_turn"] = player.get("no_reroll_next_turn", False)
        player["no_reroll_next_turn"] = False
        player["action_locked"] = False
        player["takeStaminaDebuff"] = False
        if player.get("debuffPower"):
            player["debuffPower"] = False
        player.pop("lastedBuff", None)
        player.pop("last_roll_log", None)
        player["used_skills_this_turn"] = []

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }

    apply_wit_regen(channel_id)
    incrase_speed_by_acceleration_turn(channel_id)

    return game["turn"]

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
    player_data = get_player(user_id)
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มแล้ว ไม่สามารถเข้าร่วมเพิ่มได้"

    if style not in VALID_STYLES:
        return False, "รูปแบบการวิ่งไม่ถูกต้อง"

    if user_id in game["players"]:
        return False, "คุณเข้าร่วมเกมนี้แล้ว"
    
    db_player = get_player(user_id)

    game["players"][user_id] = {
        "username": player_data.get('username') ,
        "avatar": display_avatar,
        "profile_image_url": db_player.get("profile_image_url") if db_player else "",
        "display_name": display_name,
        "style": style,
        "current_max_speed": MAX_SPEED_PHASE[style]["start"],
        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "stamina_left": 0,
        "wit_mana": 100,
        "wit_reroll_left": 2,
        "takeStaminaDebuff": False,
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
        "wit_mana": 100,
        "wit_reroll_left": 2,
        "takeStaminaDebuff": False,
        "skills": skills,
        "zone": copy.deepcopy(preset["zone"]),
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
    skills = apply_rookie_distance_skills(
        preset_key,
        copy.deepcopy(preset["skills"]),
        game.get("distance"),
    )

    game["players"][mob_id] = {
        "username": preset['name'],
        "display_name": f"{preset['name']} Lv.{level}",
        "avatar": preset["avatar"],
        "thumnail": preset.get("thumnail", preset.get("avatar")),
        "profile_image_url": "",
        "is_mob": True,
        "mob_level": level,
        "mob_preset_key": preset_key,
        "style": preset["style"],

        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "wit_reroll_left": 0,
        "stamina_left": 8 + race_profile.get("stamina", 1),
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

    # surface
    required_surface = trigger.get("surface")
    if required_surface is not None:
        surface = game.get("surface")
        if surface != required_surface:
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
            skill_effects or []
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

def process_mob_turn(channel_id: int, user_id: str):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ยังไม่มีเกมในห้องนี้"}

    player = game["players"].get(user_id)
    if player is None:
        return False, {"message": "ไม่พบ mob"}

    if not player.get("is_mob"):
        return False, {"message": "ผู้เล่นนี้ไม่ใช่ mob"}

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
        ) or (
            phase == 3
            and player.get("style") == "Late"
        )
        or (
            phase == 4
            and player.get("style") == "End"
        )
    )

    if turn_trigger and player.get("zone_left", 0) > 0:
        zone_success = apply_zone_in_game(game, player)
        if zone_success:
            player["zone_left"] -= 1

    usable_skills = get_mob_usable_skills(
        channel_id=channel_id,
        game=game,
        user_id=user_id,
    )

    skill_ids_to_use = decide_mob_skill_combo(
        game=game,
        user_id=user_id,
        usable_skills=usable_skills,
        max_skill_per_turn=3,
        min_combo_score=45,
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

    # =====================================
    # Cooldown
    # =====================================

    on_cd, cd_left = is_skill_on_cooldown(
        channel_id,
        user_id,
        skill_id
    )

    if on_cd:
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

    if not ok:
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

    for effect in skill.get("effects", []):

        effect_type = effect.get("type")
        duration = effect.get("duration")

        if (
            effect_type in [
                "modify_velocity",
                "modify_roll_floor",
                "modify_roll_cap",
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

    # =====================================
    # Queued
    # =====================================

    if queued_effects:
        apply_next_roll_effects_to_player(
            player,
            queued_effects
        )

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

    # =====================================
    # Cooldown
    # =====================================

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
        "cost": cost,
    }

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
            player["stamina_left"] += value
            applied_texts.append(f"ฟื้นฟู STA ตัวเอง +{value}")

        elif effect_type == "modify_current_speed":

            incrase_speed_by_acceleration(game, player, effect["value"])
            applied_texts.append(f"เร่งความเร็วขึ้น {value} ระดับ")

        elif effect_type == "self_heal_stamina":
            player["stamina_left"] += value
            applied_texts.append(f"ฟื้นฟู STA ตัวเอง +{value}")

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
                            applied_texts.append(f"ปรับคะแนน <@{target_id}> ทันที {sign}{value}")

        elif effect_type == "reduce_stamina":
            if not targets:
                continue

            for target_id, target_info in targets:
                before = target_info.get("stamina_left", 0)
                target_info["stamina_left"] = max(0, before - value)
                applied_texts.append(f"ลด STA ของ <@{target_id}> -{value}")

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
                        f"ใส่ดีบัฟให้ <@{target_id}> เทิร์นหน้า Flat {value}"
                    )

                elif stat == "cap":
                    target_info.setdefault("next_roll_cap_bonus", 0)
                    target_info["next_roll_cap_bonus"] += value
                    applied_texts.append(
                        f"ใส่ดีบัฟให้ <@{target_id}> เทิร์นหน้า Cap {value}"
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
                        f"บังคับ <@{target_id}> ใช้ Rush สำเร็จ"
                    )
                else:
                    applied_texts.append(
                        f"บังคับ <@{target_id}> ใช้ Rush ไม่สำเร็จ ({rush_payload})"
                    )

        elif effect_type == "modify_gold_range":
            player.setdefault("gold_range_bonus_this_turn", 0)
            player["gold_range_bonus_this_turn"] += value
            applied_texts.append(f"เพิ่มระยะตรวจ Gold +{value}")

        elif effect_type == "modify_enemy_gold_range":
            if not targets:
                continue

            value = abs(value)
            for target_id, target_info in targets:
                target_info.setdefault("enemy_gold_range_penalty_next_turn", 0)
                target_info["enemy_gold_range_penalty_next_turn"] += value
                applied_texts.append(f"ลดระยะตรวจ Gold ของ <@{target_id}> {value}")

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

    if scope == "nearest_front":
        return [(tid, info) for _, tid, info in front[:1]]

    if scope == "nearest_back":
        return [(tid, info) for _, tid, info in back[:1]]

    if scope == "all_front":
        return [(tid, info) for _, tid, info in front[:limit]]

    if scope == "all_back":
        return [(tid, info) for _, tid, info in back[:limit]]

    if scope == "random_enemy":
        enemies = [(tid, info) for _, tid, info in front + back]
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
    emoji = ICON.get(skill.get("icon"), "❓")

    embed = discord.Embed(
        title=f"{emoji} {player_name} ใช้สกิล {skill['name']}",
        description="\n".join(
            payload.get("result_texts", [])
        ),
        color=discord.Color.green()
    )

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

    selected = player.get("next_roll_selected_die_bonus", 0)
    if selected:
        lines.append(f"เพิ่มแต้มลูกที่เลือก +{selected}")

    cap = player.get("next_roll_cap_bonus", 0)
    if cap:
        sign = "+" if cap > 0 else ""
        lines.append(f"ปรับแต้มสูงสุดลูกเต๋า {sign}{cap}")

    return "\n".join(lines) if lines else "ไม่มีบัฟค้าง"
