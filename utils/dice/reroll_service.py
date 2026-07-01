import discord
from utils.game_manager import get_game, get_player_in_game, update_player_score, build_pending_effects_from_player,build_run_embed
from utils.race.race_aptitude import get_roll_race_stats
from utils.race.race_presets import get_current_path_type, get_path_effect
from utils.race.race_dice import roll_race_dice
from utils.race.runtime_stamina import build_runtime_stamina_note, format_runtime_stamina
from utils.icon_presets import Status_Icon_Type

async def execute_reroll(
    interaction: discord.Interaction,
    *,
    old_total: int,
    minimum_total: int | None = None,
    title_prefix: str = "สุ่มใหม่สำเร็จ",
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

    roll_stats = get_roll_race_stats(game_player)

    success, _ = update_player_score(
        interaction.channel_id,
        interaction.user.id,
        -old_total
    )
    if not success:
        return False, {"message": "ไม่สามารถลบคะแนนเดิมได้"}

    score_map = game["turn_snapshot_scores"]
    # Buff
    skill_effects = []
    merged_stats = {}

    skill_effects,merged_stats = build_pending_effects_from_player(game_player)
    if game_player.get("takeStaminaDebuff", False):
        skill_effects.append({
            "type": "modify_total_percent",
            "value": -25,
            "duration": "this_roll",
        })

    path_type = get_current_path_type(game)
    path_effect = get_path_effect(path_type, game_player, race_player)
    
  
    result = roll_race_dice(
        game_player=game_player,
        player_stats=roll_stats,
        player_id=interaction.user.id,
        score_map=score_map,
        turn=game["turn"],
        max_turn=game["max_turn"],
        path_effect=path_effect,
        skill_effects=skill_effects,
        minimum_total=minimum_total,
    )

    staminaNote = None
    if game_player.get("takeStaminaDebuff", False):
        staminaNote = build_runtime_stamina_note(game_player, penalty=True)
   
    ## Clear Debuff -----------------------------------------------
    game_player["lastedBuff"] = merged_stats

    game_player["next_roll_flat_bonus"] = 0
    game_player["next_roll_add_d"] = 0
    game_player["next_roll_add_kh"] = 0
    game_player["next_roll_floor_bonus"] = 0
    game_player["next_roll_selected_die_bonus"] = 0
    game_player["next_roll_cap_bonus"] = 0
    game_player["gold_range_bonus_this_turn"] = 0
    game_player["enemy_gold_range_penalty_next_turn"] = 0
    ## Clear Debuff -----------------------------------------------

    success, new_score = update_player_score(
        interaction.channel_id,
        interaction.user.id,
        result["total"]
    )
    if not success:
        return False, {"message": "ไม่สามารถอัปเดตคะแนนใหม่ได้"}

    embed = build_run_embed(
        game_player=game_player,
        result=result,
        new_score=new_score,
        stamina_note= staminaNote or format_runtime_stamina(game_player),
        path_effect=path_effect,
        title_prefix=title_prefix,
    )

    return True, {
        "game": game,
        "game_player": game_player,
        "result": result,
        "new_score": new_score,
        "embed": embed,
    }
