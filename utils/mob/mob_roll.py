import discord
from utils.dice.race_presets import (
    get_path_effect,
    get_current_path_type, 
)

from utils.dice.race_dice import (
    roll_race_dice,
)
from utils.game_manager import (
    get_game,
    get_player_in_game,
    update_player_score,
    mark_player_rolled,
    build_pending_effects_from_player,
)
from utils.icon_presets import Status_Icon_Type

def execute_roll_core(
    *,
    channel_id: int,
    user_id,
    title_prefix: str = "วิ่งในเทิร์นนี้",
    mark_roll: bool = True,
    game
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

def build_mob_run_embed(
    *,
    game: dict,
    game_player: dict,
    result: dict,
    new_score: int,
    stamina_note: str | None,
    path_effect: dict,
    title_prefix: str = "วิ่งในเทิร์นนี้",
):
    mob_name = (
        game_player.get("display_name")
        or game_player.get("username")
        or game_player.get("name")
        or "Mob"
    )

    embed = discord.Embed(
        title=f"🤖 {mob_name} {title_prefix}",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="🎲 Roll",
        value=(
            f"Base: **{result['base_total']}**\n"
            f"โบนัส: {result['bonus_display']}\n"
            f"รวม: **{result['total_display']}**"
        ),
        inline=True
    )

    embed.add_field(
        name="🏁 Score",
        value=f"**{new_score}**",
        inline=True
    )

    embed.add_field(
        name="❤️ STA",
        value=stamina_note or "-",
        inline=True
    )

    if result.get("selected"):
        embed.add_field(
            name="🎯 Selected Dice",
            value=", ".join(str(x) for x in result["selected"]),
            inline=False
        )

    if result.get("all_rolls"):
        embed.add_field(
            name="🎲 All Dice",
            value=", ".join(str(x) for x in result["all_rolls"]),
            inline=False
        )

    if path_effect:
        effect_lines = []
        if path_effect.get("flat_bonus", 0):
            effect_lines.append(f"Flat {path_effect['flat_bonus']:+}")
        if path_effect.get("stamina_cost", 0):
            effect_lines.append(f"STA Cost -{path_effect['stamina_cost']}")
        if path_effect.get("stamina_gain", 0):
            effect_lines.append(f"STA Gain +{path_effect['stamina_gain']}")

        if effect_lines:
            embed.add_field(
                name="🛤️ Path Effect",
                value="\n".join(effect_lines),
                inline=False
            )

    return embed