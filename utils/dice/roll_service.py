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
    return f"{current_mana} → {current_mana + regen}" #{Status_Icon_Type['WIT']} 

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
        title=f"Phase {result["phase"]} {path_effect["label"]} สาย {game_player["style"]}",
        color=discord.Color.gold()
    )

    embed.add_field(name=f"🏇 ความเร็ว {result["distance_color"]}", value= f"{result["display"]} {result["bonus_display"]}" , inline=False)

    if stamina_note == None:
        stamina_note = str(game_player["stamina_left"])

    embed.add_field(
        name="📊 สรุปผล",
        value=(
            f"🏁 Score รวม: **{new_score}** ({result['total']})　"
            f"{Status_Icon_Type["STA"]} : **{stamina_note}**　"
            f"{Status_Icon_Type["WIT"]} : **{build_single_wit_regen_text(game_player)}**"
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 Reroll",
        value=(
            f"Reroll คงเหลือ: **{game_player['reroll_left']}**　"
            f"{Status_Icon_Type['WIT']} Reroll: **{str(game_player.get("wit_reroll_left", 0))}**"
        ),
        inline=False
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

    # flat = merged_stats["flat"]
    # if flat != 0:
    #     sign = "+" if flat > 0 else ""
    #     if result["bonus_display"] == "-":
    #         result["bonus_display"] = f"NEXT{sign}{flat}"
    #     else:
    #         result["bonus_display"] += f" NEXT{sign}{flat}"

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