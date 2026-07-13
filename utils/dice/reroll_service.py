import discord
from utils.game_manager import get_game, get_player_in_game, update_player_score, build_pending_effects_from_player,build_run_embed, apply_lane_tactics_to_result, get_stamina_debuff_percent
from utils.race.race_aptitude import get_roll_race_stats
from utils.race.race_presets import get_current_path_type, get_path_effect
from utils.race.race_dice import roll_race_dice
from utils.race.runtime_stamina import (
    build_runtime_stamina_note,
    format_runtime_stamina,
    get_runtime_stamina_snapshot,
)
from utils.icon_presets import Status_Icon_Type


def can_execute_reroll(channel_id: int, user_id: int, expected_turn: int) -> tuple[bool, str]:
    """Verify that a reroll belongs to the roll that created its UI control."""
    game = get_game(channel_id)
    if game is None:
        return False, "ไม่พบเกมนี้แล้ว"
    if not game.get("started"):
        return False, "เกมยังไม่เริ่มหรือจบแล้ว"
    if game.get("turn") != expected_turn:
        return False, "ปุ่ม reroll นี้หมดอายุแล้ว"

    player = get_player_in_game(channel_id, user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"
    if player.get("last_roll_turn") != expected_turn:
        return False, "ต้องทอยในเทิร์นนี้ก่อนจึงจะ reroll ได้"
    if player.get("no_reroll_this_turn", False):
        return False, "ไม่สามารถ reroll ในเทิร์นนี้ได้"
    return True, ""


async def execute_reroll(
    interaction: discord.Interaction,
    *,
    old_total: int,
    expected_turn: int,
    minimum_total: int | None = None,
    title_prefix: str = "สุ่มใหม่สำเร็จ",
) -> tuple[bool, dict]:
    allowed, message = can_execute_reroll(
        interaction.channel_id,
        interaction.user.id,
        expected_turn,
    )
    if not allowed:
        return False, {"message": message}

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
            "value": -get_stamina_debuff_percent(game_player),
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
        player_map=game["players"],
    )
    lane_resolution = apply_lane_tactics_to_result(
        game=game,
        user_id=interaction.user.id,
        game_player=game_player,
        result=result,
        path_effect=path_effect,
        score_map=score_map,
        consume_stamina=False,
        apply_stamina_penalty=False,
    )

    staminaNote = None
    if game_player.get("takeStaminaDebuff", False):
        staminaNote = lane_resolution["stamina_note"]
   
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
    game_player["gold_lane_bonus_this_turn"] = 0
    game_player["enemy_gold_lane_penalty_next_turn"] = 0
    ## Clear Debuff -----------------------------------------------

    success, new_score = update_player_score(
        interaction.channel_id,
        interaction.user.id,
        result["total"]
    )
    if not success:
        return False, {"message": "ไม่สามารถอัปเดตคะแนนใหม่ได้"}

    rule = result.get("rule", {})
    rule_text = f"{rule.get('d', 0)}d"
    if rule.get("kh") is not None:
        rule_text += f" kh{rule['kh']}"
    game_player["last_roll_log"] = {
        "phase": result.get("phase"),
        "distance_color": result.get("distance_color"),
        "rule": rule_text,
        "total": result.get("total"),
        "base_total": result.get("base_total"),
        "bonus_display": result.get("bonus_display"),
        "stamina": get_runtime_stamina_snapshot(game_player),
        "stamina_note": staminaNote or format_runtime_stamina(game_player),
        "blocked_count": result.get("blocked_count", 0),
        "blocking_penalty": result.get("blocking_penalty", 0.0),
        "drafting_active": result.get("drafting_active", False),
    }

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
