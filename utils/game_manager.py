import copy
import uuid
import discord

from utils.dice.race_presets import RACE_PRESET
from utils.database import get_player, get_player_skill_slots
from utils.mob.mob_presets import MOB_PRESETS
from utils.zone.zone_manager import apply_zone_in_game
from utils.dice.race_presets import (
    get_path_effect,
    get_current_path_type, 
)
from utils.zone.zone_embed import build_zone_used_preview_embed

from utils.dice.race_dice import (
    roll_race_dice,
)

from utils.icon_presets import Status_Icon_Type

VALID_STYLES = {"Front", "Pace", "Late", "End"}
games = {}


def execute_roll_core(
    *,
    channel_id: int,
    user_id,
    title_prefix: str = "วิ่งในเทิร์นนี้",
    mark_roll: bool = True,
    build_embed: bool = False,
    build_reroll_view: bool = False,
    owner_id: int | None = None,
    player_name: str | None = None,
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

    snapshot_scores = game["turn_snapshot_scores"]

    pending_effects, merged_stats = build_pending_effects_from_player(game_player)

    path_type = get_current_path_type(game)
    path_effect = get_path_effect(path_type, race_player)

    result = roll_race_dice(
        style=game_player["style"],
        player=race_player,
        player_id=user_id,
        score_map=snapshot_scores,
        turn=game["turn"],
        max_turn=game["max_turn"],
        path_effect=path_effect,
        skill_effects=pending_effects,
    )

    game_player["lastedBuff"] = merged_stats

    game_player["next_roll_flat_bonus"] = 0
    game_player["next_roll_add_d"] = 0
    game_player["next_roll_add_kh"] = 0
    game_player["next_roll_floor_bonus"] = 0
    game_player["next_roll_selected_die_bonus"] = 0
    game_player["next_roll_cap_bonus"] = 0
    game_player["gold_range_bonus_this_turn"] = 0
    game_player["enemy_gold_range_penalty_next_turn"] = 0

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
        result["total"] -= 30
        if result["bonus_display"] == "-":
            result["bonus_display"] = f"-30{Status_Icon_Type['STA']}"
        else:
            result["bonus_display"] += f" -30{Status_Icon_Type['STA']}"
        result["total_display"] = str(result["total"])
        stamina_note = f"{Status_Icon_Type['STA']} ไม่พอ โดนหัก 30 แต้ม"

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

def create_game(channel_id: int, stage_key: str, owner_id: int):
    if channel_id in games:
        return False

    if stage_key not in RACE_PRESET:
        return False

    stage = RACE_PRESET[stage_key]

    games[channel_id] = {
        "stage_key": stage_key,
        "stage_name": stage["name"],
        "max_turn": stage["turn"],
        "track": stage["track"],
        "distance": stage["distance"],
        "path": stage["path"],
        "owner_id": owner_id,
        "turn": 0,
        "started": False,
        "players": {},
        "turn_snapshot_scores": {},

        "turn_confirmations": set(),
        "awaiting_turn_confirm": False,
    }

    return True

def have_all_players_rolled(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    players = game["players"]
    if not players:
        return False

    current_turn = game["turn"]
    return all(player["last_roll_turn"] == current_turn for player in players.values())

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

            # mob ใช้ skills จาก preset เดิม ไม่ต้องโหลดจาก DB
            player["skills"] = player.get("skills", {
                1: None,
                2: None,
                3: None,
            })

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
            }

            # zone ของผู้เล่นจริง ถ้ายังใช้ในเกม
            if "zone" not in player and "zone" in db_player:
                player["zone"] = {
                    "name": db_player["zone"]["name"],
                    "image_url": db_player["zone"]["image_url"],
                    "points": db_player["zone"]["points"],
                    "build": db_player["zone"]["build"],
                }

        # reset กลางเกม ใช้ร่วมกันทั้ง player จริงและ mob
        player["skill_cooldowns"] = {}
        player["wit_mana"] = 100
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

        # ===== attitude bonus =====
        att_source = player["race_profile"]

        att = get_attitude_values(
            att_source,
            game["track"],
            game["distance"],
            player["style"]
        )

        att_bonus = build_attitude_stat_bonus(att)

        player["race_profile"]["power"] += att_bonus["power"]
        player["race_profile"]["speed"] += att_bonus["speed"]
        player["race_profile"]["wit"] += att_bonus["wit"]

        # optional: เก็บไว้ดูใน UI
        player["attitude_bonus"] = att_bonus

    return True, "เริ่มเกมเรียบร้อยแล้ว"


def build_mob_join_embed(game: dict, player: dict):
    surface = game.get("surface", "Turf")
    distance = game.get("distance", "Medium")

    mob_name = (
        player.get("display_name")
        or player.get("username")
        or player.get("name")
        or "Mob"
    )

    style = player.get("style", "Unknown")

    embed = discord.Embed(
        title="🤖 Mob เข้าร่วม!",
        color=discord.Color.orange()
    )

    embed.add_field(name="ชื่อ", value=mob_name, inline=True)
    embed.add_field(name="Style", value=style, inline=True)

    # 🔥 ใช้ race_profile แทน db_player
    race_profile = player.get("race_profile", {})

    att = get_attitude_values(race_profile, surface, distance, style)
    att_bonus = build_attitude_stat_bonus(att)

    embed.add_field(
        name="📊 Attitude Bonus",
        value=(
            f"{Status_Icon_Type['POW']} +{att_bonus['power']}\n"
            f"{Status_Icon_Type['SPD']} +{att_bonus['speed']}\n"
            f"{Status_Icon_Type['WIT']} +{att_bonus['wit']}"
        ),
        inline=False
    )

    return embed

def get_attitude_values(db_player, surface, distance, style):
    surface_key = "turf" if surface == "Turf" else "dirt"

    style_map = {
        "Front": "front",
        "Pace": "pace",
        "Late": "late",
        "End": "end_style",
    }

    return {
        "track": db_player.get(surface_key, 1),
        "distance": db_player.get(distance.lower(), 1),
        "style": db_player.get(style_map.get(style, "pace"), 1),
    }


def build_attitude_stat_bonus(att):
    return {
        "power": max(0, att["track"] - 1),
        "speed": max(0, att["distance"] - 1),
        "wit": max(0, att["style"] - 1),
    }

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

        if duration != "this_roll":
            continue

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

        elif effect_type == "modify_selected_die":
            player["next_roll_selected_die_bonus"] = player.get("next_roll_selected_die_bonus", 0) + value

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
    valid_targets = [(uid, gap, info) for uid, gap, info in behind_players if gap > 10]

    if not valid_targets:
        return False, "ไม่มีคนด้านหลังที่ห่างเกิน 10"

    target_id, gap, target_info = valid_targets[0]

    move_back = gap - 10
    player["score"] -= move_back

    target_info["next_roll_flat_bonus"] -= 10
    player["used_block"] = True
    player["action_locked"] = True

    return True, {
        "target_id": target_id,
        "move_back": move_back,
        "new_score": player["score"],
    }

def use_rush(channel_id: int, user_id: int):
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

    target_id, gap, target_info = valid_targets[0]

    move_forward = max(gap - 10, 0)
    player["score"] += move_forward

    player["next_roll_flat_bonus"] -= 10
    player["no_reroll_this_turn"] = True
    player["used_rush"] = True
    player["action_locked"] = True

    return True, {
        "target_id": target_id,
        "move_forward": move_forward,
        "new_score": player["score"],
    }

def get_attitude_values(db_player, surface, distance, style):
    surface_key = "turf" if surface == "Turf" else "dirt"

    style_map = {
        "Front": "front",
        "Pace": "pace",
        "Late": "late",
        "End": "end_style",
    }

    return {
        "track": db_player.get(surface_key, 1),
        "distance": db_player.get(distance.lower(), 1),
        "style": db_player.get(style_map.get(style, "pace"), 1),
    }

def build_attitude_stat_bonus(att):
    return {
        "power": att["track"],      # Track → Power
        "speed": att["distance"],   # Distance → Speed
        "wit": att["style"],        # Style → Wit
    }

def build_pending_effects_from_player(player: dict) -> tuple[list[dict], dict]:
    flat = player.get("next_roll_flat_bonus", 0)
    add_d = player.get("next_roll_add_d", 0)
    add_kh = player.get("next_roll_add_kh", 0)
    floor = player.get("next_roll_floor_bonus", 0)
    sel = player.get("next_roll_selected_die_bonus", 0)
    cap = player.get("next_roll_cap_bonus", 0)

    # รวม lastedBuff
    buff = player.get("lastedBuff", {})
    if buff:
        flat += buff.get("flat", 0)
        add_d += buff.get("add_d", 0)
        add_kh += buff.get("add_kh", 0)
        floor += buff.get("floor", 0)
        sel += buff.get("sel", 0)
        cap += buff.get("cap", 0)

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

    if sel != 0:
        pending_effects.append({
            "type": "modify_selected_die",
            "value": sel,
            "duration": "this_roll"
        })

    if cap != 0:
        pending_effects.append({
            "type": "modify_roll_cap",
            "value": cap,
            "duration": "this_roll"
        })

    merged_stats = {
        "flat": flat,
        "add_d": add_d,
        "add_kh": add_kh,
        "floor": floor,
        "sel": sel,
        "cap": cap,
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

def process_mob_turn(channel_id: int, user_id: str):
    game = get_game(channel_id)
    if game is None:
        return False, {"message": "ยังไม่มีเกมในห้องนี้"}

    player = game["players"].get(user_id)
    if player is None:
        return False, {"message": "ไม่พบ mob"}

    # ✅ ใช้ zone_left
    zone_success = False
    
    
    if (
        player.get("is_mob")
        and game["turn"] == game["max_turn"]  # 🔥 เทิร์นสุดท้าย
        and player.get("zone_left", 0) > 0
    ):
        zone_success, zone_text = apply_zone_in_game(player)
        if zone_success:
            player["zone_left"] -= 1   # 🔥 สำคัญ

    success, payload = execute_roll_core(
        channel_id=channel_id,
        user_id=user_id,
        title_prefix="วิ่งอัตโนมัติ",
        mark_roll=True,
    )

    if not success:
        return False, payload

    # ✅ สร้าง embed เอง
    mob_name = (
        player.get("display_name")
        or player.get("username")
        or player.get("name")
        or "Mob"
    )

    embed = build_run_embed(
        game_player=payload["game_player"],
        result=payload["result"],
        new_score=payload["new_score"],
        stamina_note=payload["stamina_note"],
        path_effect=payload["path_effect"],
        player_name=f"🤖 {mob_name}",
    )

    payload["embed"] = embed
    if zone_success:
        payload["zone_preview"] = build_zone_used_preview_embed(player)
    
    # print(player.get("is_mob"), game["turn"] == game["max_turn"], player.get("zone_left", 0) > 0 ,game["turn"], game["max_turn"])
        
    return True, payload

def build_single_wit_regen_text(game_player: dict) -> str:
    race_profile = game_player.get("race_profile", {})
    wit_stat = race_profile.get("wit", 0)
    regen = 10 + (wit_stat * 1)
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
        title=f"{name_part}Phase {result['phase']} {path_effect['label']} สาย {game_player['style']}",
        color=discord.Color.gold()
    )

    embed.add_field(name=f"🏇 ความเร็ว {result["distance_color"]}", value= f"{result["display"]} {result["bonus_display"]}" , inline=False)
    reroll = game_player.get("reroll_left", 0)
    wit_reroll = game_player.get("wit_reroll_left", 0)

    if stamina_note == None:
        stamina_note = str(game_player["stamina_left"])

    embed.add_field(
        name="📊 สรุปผล",
        value=(
            f"🏁 Score รวม: **{new_score}** ({result['total']})　"
            f"{Status_Icon_Type['STA']} : **{stamina_note}**　"
            f"{Status_Icon_Type['WIT']} : **{build_single_wit_regen_text(game_player)}**"
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 Reroll",
        value=(
            f"Reroll คงเหลือ: **{reroll}**　"
            f"{Status_Icon_Type['WIT']} Reroll: **{wit_reroll}**"
        ),
        inline=False
    )

    return embed


def next_turn(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return None

    game["turn"] += 1

    tick_skill_cooldowns(channel_id)

    for player in game["players"].values():
        player["no_reroll_this_turn"] = player.get("no_reroll_next_turn", False)
        player["no_reroll_next_turn"] = False
        player["action_locked"] = False
        player.pop("lastedBuff", None)

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }

    apply_wit_regen(channel_id)

    return game["turn"]

def apply_wit_regen(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return

    for _, player in game["players"].items():
        race_profile = player.get("race_profile", {})
        wit_stat = race_profile.get("wit", 0)
        regen = 10 + (wit_stat * 1)
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

def add_player(channel_id, user_id, display_name: str, style):
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
        "username": player_data.get("username"),
        "display_name": display_name,
        "style": style,
        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "stamina_left": 0,
        "wit_mana": 100,
        "wit_reroll_left": 2,
        "skills": {
            1: None,
            2: None,
            3: None,
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
            "name": db_player["zone"]["name"],
            "image_url": db_player["zone"]["image_url"],
            "points": db_player["zone"]["points"],
            "build": db_player["zone"]["build"],
        }
    }

    return True, "เข้าร่วมเกมสำเร็จ"

def add_mob_from_preset(channel_id: int, preset_key: str):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มแล้ว ไม่สามารถเพิ่ม mob ได้"

    preset = MOB_PRESETS.get(preset_key)
    if preset is None:
        return False, "ไม่พบ preset mob"

    mob_id = f"mob_{uuid.uuid4().hex[:8]}"

    race_profile = copy.deepcopy(preset["race_profile"])
    zone = copy.deepcopy(preset["zone"])
    skills = copy.deepcopy(preset["skills"])

    game["players"][mob_id] = {
        "username": preset["name"],
        "display_name": preset["name"],
        "is_mob": True,
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

    

    return True, f"เพิ่ม mob `{preset['name']}` เรียบร้อย"


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
    race_profile = game_player.get("race_profile", {})
    wit_stat = race_profile.get("wit", 0)
    threshold = wit_stat * 5

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