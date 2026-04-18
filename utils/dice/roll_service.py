import discord
from utils.game_manager import (
    get_game,
    get_player_in_game,
    update_player_score,
    mark_player_rolled,
    build_pending_effects_from_player,
    can_use_wit_reroll
)
from utils.icon_presets import Status_Icon_Type
from utils.dice.race_presets import (
    get_path_effect,
    get_current_path_type, 
)

from utils.dice.race_dice import (
    roll_race_dice,
)

def build_single_wit_regen_text(game_player: dict) -> str:
    race_profile = game_player.get("race_profile", {})
    wit_stat = race_profile.get("wit", 0)
    regen = 10 + (wit_stat * 1)
    current_mana = game_player.get("wit_mana", 0)
    return f"{Status_Icon_Type['WIT']} {current_mana} → {current_mana + regen}"

def build_run_embed(
    interaction: discord.Interaction,
    game: dict,
    game_player: dict,
    result: dict,
    new_score: int,
    stamina_note: str | None,
    path_effect: dict,
    title_prefix: str = "วิ่งในเทิร์นนี้",
) -> discord.Embed:
    embed = discord.Embed(
        title=f"{interaction.user.display_name} {title_prefix}",
        color=discord.Color.gold()
    )

    embed.add_field(name="Phase", value=result["phase"], inline=True)
    embed.add_field(name="Style", value=game_player["style"], inline=True)
    embed.add_field(name="Path", value=path_effect["label"], inline=True)

    embed.add_field(name="🎲 Dice", value=result["display"], inline=False)
    embed.add_field(name="📈 Stats Bonus", value=result["bonus_display"], inline=False)

    embed.add_field(name="✨ Total", value=str(result["total"]), inline=True)
    embed.add_field(name="🏁 Score ใหม่", value=str(new_score), inline=True)
    embed.add_field(name=f"{Status_Icon_Type['STA']} คงเหลือ", value=str(game_player["stamina_left"]), inline=True)

    if stamina_note:
        embed.add_field(name="Stamina", value=stamina_note, inline=False)

    embed.add_field(
        name=f"{Status_Icon_Type["WIT"]} ฟื้นฟูจากค่า stats",
        value=build_single_wit_regen_text(game_player),
        inline=False
    )

    embed.add_field(
        name="Reroll คงเหลือ",
        value=f"{game_player['reroll_left']}",
        inline=True
    )

    embed.add_field(
        name=f"{Status_Icon_Type["WIT"]} Reroll",
        value=str(game_player.get("wit_reroll_left", 0)),
        inline=True
    )

    return embed


async def execute_player_roll(
    interaction: discord.Interaction,
    *,
    title_prefix: str = "วิ่งในเทิร์นนี้",
    mark_roll: bool = True,
    allow_reroll_view: bool = True,
) -> tuple[bool, dict]:
    game = get_game(interaction.channel_id)
    if game is None:
        return False, {"message": "ยังไม่มีเกมในห้องนี้"}

    game_player = get_player_in_game(interaction.channel_id, interaction.user.id)
    if game_player is None:
        return False, {"message": "คุณยังไม่ได้เข้าร่วมเกมนี้"}

    race_player = game_player.get("race_profile")
    if race_player is None:
        return False, {"message": "ไม่พบข้อมูล stat ตอนเริ่มเกม"}
    snapshot_scores = game["turn_snapshot_scores"]


    # Buff
    pending_effects,merged_stats = build_pending_effects_from_player(game_player)

    # path effect
    path_type = get_current_path_type(game)
    path_effect = get_path_effect(path_type, race_player)

    result = roll_race_dice(
        style=game_player["style"],
        player=race_player,
        player_id=interaction.user.id,
        score_map=snapshot_scores,
        turn=game["turn"],
        max_turn=game["max_turn"],
        path_effect=path_effect,
        skill_effects=pending_effects,
    )

    flat = merged_stats["flat"]
    if flat != 0:
        sign = "+" if flat > 0 else ""
        if result["bonus_display"] == "-":
            result["bonus_display"] = f"NEXT{sign}{flat}"
        else:
            result["bonus_display"] += f" NEXT{sign}{flat}"

    ## Clear Debuff -----------------------------------------------
    game_player["lastedBuff"] = merged_stats

    game_player["next_roll_flat_bonus"] = 0
    game_player["next_roll_add_d"] = 0
    game_player["next_roll_add_kh"] = 0
    game_player["next_roll_floor_bonus"] = 0
    game_player["next_roll_selected_die_bonus"] = 0
    game_player["next_roll_cap_bonus"] = 0
    ## Clear Debuff -----------------------------------------------

    # stamina -----------------------------------------------------------------------
    stamina_note = None
    stamina_gain = path_effect.get("stamina_gain", 0)
    stamina_cost = path_effect.get("stamina_cost", 0)

    if stamina_gain > 0:
        game_player["stamina_left"] += stamina_gain

    if game_player["stamina_left"] >= stamina_cost:
        game_player["stamina_left"] -= stamina_cost
        if stamina_gain > 0:
            stamina_note = f"+{stamina_gain} / -{stamina_cost} เหลือ {game_player['stamina_left']}"
        else:
            stamina_note = f"-{stamina_cost} เหลือ {game_player['stamina_left']}"
    else:
        result["total"] -= 30
        if result["bonus_display"] == "-":
            result["bonus_display"] = f"{Status_Icon_Type['STA']}-30"
        else:
            result["bonus_display"] += f" {Status_Icon_Type['STA']}-30"
        result["total_display"] = str(result["total"])
        stamina_note = f"STA ไม่พอ (ต้องใช้ {stamina_cost}) โดนหัก 30"
    # stamina -----------------------------------------------------------------------


    # score
    success, new_score = update_player_score(
        interaction.channel_id,
        interaction.user.id,
        result["total"]
    )
    if not success:
        return False, {"message": "ไม่สามารถอัปเดตคะแนนได้"}

    if mark_roll:
        mark_player_rolled(interaction.channel_id, interaction.user.id)

    embed = build_run_embed(
        interaction=interaction,
        game=game,
        game_player=game_player,
        result=result,
        new_score=new_score,
        stamina_note=stamina_note,
        path_effect=path_effect,
        title_prefix=title_prefix,
    )

    view = None
    if allow_reroll_view and not game_player.get("no_reroll_this_turn", False):
        from views.run_reroll_view import RunRerollView
        wit_reroll_ok = can_use_wit_reroll(game_player, result["base_total"])

        view = RunRerollView(
            owner_id=interaction.user.id,
            channel_id=interaction.channel_id,
            old_total=result["total"],
            base_total=result["base_total"],
            wit_reroll_ok=wit_reroll_ok,
        )

    return True, {
        "game": game,
        "game_player": game_player,
        "result": result,
        "new_score": new_score,
        "embed": embed,
        "view": view,
        "path_effect": path_effect,
    }