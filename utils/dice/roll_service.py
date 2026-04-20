import discord
from utils.game_manager import (
    can_use_wit_reroll,
    execute_roll_core,
    build_run_embed
)
from utils.icon_presets import Status_Icon_Type

async def execute_player_roll(
    interaction: discord.Interaction,
    *,
    title_prefix: str = "วิ่งในเทิร์นนี้",
    mark_roll: bool = True,
    allow_reroll_view: bool = True,
) -> tuple[bool, dict]:
    success, payload = execute_roll_core(
        channel_id=interaction.channel_id,
        user_id=interaction.user.id,
        title_prefix=title_prefix,
        mark_roll=mark_roll,
    )
    if not success:
        return False, payload

    game_player = payload["game_player"]
    result = payload["result"]
    new_score = payload["new_score"]
    path_effect = payload["path_effect"]
    stamina_note = payload["stamina_note"]

    embed = build_run_embed(
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

    payload["embed"] = embed
    payload["view"] = view
    return True, payload