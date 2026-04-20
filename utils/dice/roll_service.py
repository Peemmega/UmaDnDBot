import discord
from utils.game_manager import (
    can_use_wit_reroll
)
from utils.icon_presets import Status_Icon_Type
from utils.mob.mob_roll import execute_roll_core


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
            f"{Status_Icon_Type['STA']} : **{stamina_note}**　"
            f"{Status_Icon_Type['WIT']} : **{build_single_wit_regen_text(game_player)}**"
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
    success, payload = execute_roll_core(
        channel_id=interaction.channel_id,
        user_id=interaction.user.id,
        title_prefix=title_prefix,
        mark_roll=mark_roll,
    )
    if not success:
        return False, payload

    game = payload["game"]
    game_player = payload["game_player"]
    result = payload["result"]
    new_score = payload["new_score"]
    path_effect = payload["path_effect"]
    stamina_note = payload["stamina_note"]

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

    payload["embed"] = embed
    payload["view"] = view
    return True, payload