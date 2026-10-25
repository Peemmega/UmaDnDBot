import discord
import os
from discord.ext import commands
from discord import app_commands
import random
from types import SimpleNamespace

from utils.race_dice_preview import create_race_dice_preview
from utils.image_encoding import encode_png
from utils.mob.mob_fast_output import build_mob_fast_roll_text

from views.confirmDeleteGameView import ConfirmDeleteView
from views.use_skill_view import UseSkillView
from views.create_game_view import (
    CreateGameView,
    TrainingTrackSelectView,
    build_training_track_menu_embed,
)

from utils.icon_presets import Status_Icon_Type
from utils.channel_config import RACE_LOG_CHANNEL_ID
from utils.skill.skill_presets import SKILLS, ICON
from utils.narrater import (
    generate_commentary,
    build_narrator_players_from_ranked,
    generate_finish_commentary,
)
from utils.music_manager import play_bgm, stop_bgm

from utils.race.race_presets import RACE_PRESET, render_path, build_track_progress_text, build_current_track_text
from utils.race.race_log_embed import build_race_log_file
from utils.race.result_display import format_pack_status
from utils.race.rank_display import gold_range_marker
from utils.dice.roll_service import (execute_player_roll)
from utils.turn_result_image import create_turn_result_card

WIN_IMAGE = [
    "https://media.discordapp.net/attachments/1493575422007447622/1493676112952426629/i-won-taurus-cup-with-tm-opera-o-v0-w2a0zxpycglf1.gif",
    "https://cdn.discordapp.com/attachments/697810514448744448/1501846522877317130/-tamamocross.gif",
    "https://cdn.discordapp.com/attachments/697810514448744448/1501846523393081456/-uma.gif",
    "https://cdn.discordapp.com/attachments/697810514448744448/1501846523833487360/uma-uma-musume.gif",
    "https://cdn.discordapp.com/attachments/697810514448744448/1501846524420821103/uma-musume-pretty-derby-jungle-pocket-roar.gif"
]

MOB_RENDER_MODE = os.getenv("MOB_RENDER_MODE", "detailed").strip().lower()


def should_render_mob_preview(game: dict | None = None) -> bool:
    """Compact mode avoids per-mob image attachments and Discord rate limits."""
    mode = (game or {}).get("mob_render_mode", MOB_RENDER_MODE)
    return str(mode).strip().lower() != "compact"


async def build_turn_result_discord_file(game: dict, ranked_players):
    result_card = await create_turn_result_card(game, ranked_players)
    buffer = await encode_png(result_card)
    return discord.File(buffer, filename="turn_result.png")


from utils.database import ensure_player
from utils.race.race_completion import complete_race, finalize_race
from utils.profile_images import resolve_player_avatar_url, resolve_player_render_image
from utils.race.race_presets import (
    get_current_path_type, 
    build_path_effect_text, 
    PATH_TYPE_TEXT
)

from utils.skill.skill_manager import build_skill_card_text
from utils.race.race_dice import (get_phase_from_turn,)
from utils.mob.mob_presets import (MOB_PRESETS)

from utils.game_manager import (
    get_game,
    get_unconfirmed_turn_players,
    is_owner,
    claim_turn_advance,
    next_turn,
    get_player_in_game,
    get_players,
    delete_game,
    can_player_roll, 
    get_ranked_players,
    have_all_players_rolled,
    start_turn_confirmation,
    drain_pending_passive_skill_embeds,
    is_skill_on_cooldown,
    add_player_as_mob_preset,
    build_mob_join_embed,
    process_mob_turn,
    has_real_player,
    queue_player_lane_change,
    run_bot_race_test,
    refresh_player_profile_snapshot,
    format_player_reference,
    get_game_rule,
    add_player,
)

def build_race_log_embed(game: dict, ranked_players):
    rank_lines = []

    for index, (user_id, info) in enumerate(ranked_players, start=1):
        name = (
            info.get("display_name")
            or info.get("username")
            or str(user_id)
        )

        marker = gold_range_marker(user_id, info, ranked_players)
        rank_lines.append(
            f"**{index}. {name}{marker}** | {info.get('style')} | Score: **{info.get('score', 0)}**"
        )

    turn_logs = game.get("turn_score_logs", [])

    # =========================
    # group by player
    # =========================
    player_logs = {}

    for log in turn_logs:
        player_name = log["name"]

        if player_name not in player_logs:
            player_logs[player_name] = {
                "style": log.get("style"),
                "logs": []
            }

        player_logs[player_name]["logs"].append(log)

    # =========================
    # build compact text
    # =========================
    log_lines = []

    for player_name, data in player_logs.items():
        style = data["style"]

        log_lines.append(f"\n**{player_name}** ({style})")

        for item in data["logs"]:
            detail_parts = []
            roll = item.get("roll") or {}

            if roll:
                phase = roll.get("phase")
                color = roll.get("distance_color")
                rule = roll.get("rule")
                detail_parts.append(f"P{phase} {format_pack_status(color)} {rule}")

            skills = item.get("skills") or []
            if skills:
                skill_ids = ", ".join(skill.get("id", "?") for skill in skills)
                detail_parts.append(f"skills: {skill_ids}")

            detail = f" | {' | '.join(detail_parts)}" if detail_parts else ""
            log_lines.append(
                f"{item['turn']} {item['score_after']} (+{item['gain']}){detail}"
            )

    description = (
        f"สนาม: **{game.get('stage_name', 'Unknown')}**\n\n"
        f"🏆 **อันดับสุดท้าย**\n"
        + "\n".join(rank_lines)
        + "\n\n📜 **Turn Score Log**\n"
        + "\n".join(log_lines)
    )

    if len(description) > 3900:
        description = description[:3900] + "\n...log ยาวเกินไป ถูกตัดบางส่วน"

    embed = discord.Embed(
        title="📘 Race Result Log",
        description=description,
        color=discord.Color.blue(),
    )

    return embed


def _format_rank_line(index: int, user_id, info: dict, ranked_players) -> str:
    display_name = format_player_reference(user_id, info)

    marker = gold_range_marker(user_id, info, ranked_players)
    current_lane = int(info.get("current_lane", info.get("entry_number", 1)) or 1)
    return (
        f"ลำดับที่ {index}: {display_name}{marker} | "
        f"Lane {current_lane} | Score: {info['score']} ({info['style']})"
    )

def build_game_end_embed(ranked_players, commentary_text: str | None = None):
    rank_lines = []
    for index, (user_id, info) in enumerate(ranked_players, start=1):
        display_name = format_player_reference(user_id, info)

        marker = gold_range_marker(user_id, info, ranked_players)
        rank_lines.append(
            f"{index}. {display_name}{marker} | {info['style']} | Score: {info['score']}"
        )
        

    if not rank_lines:
        rank_lines.append("ยังไม่มีผู้เล่น")

    winner_text = "ไม่มีผู้ชนะ"
    if ranked_players:
        winner_id, winner_info = ranked_players[0]
        winner_text = (
            f"🏆 ผู้ชนะ: {format_player_reference(winner_id, winner_info)}\n"
            f"Style: {winner_info['style']}\n"
            f"Score: {winner_info['score']}"
        )

    embed = discord.Embed(
        title="🏁 เกมจบแล้ว",
        color=discord.Color.red(),
        description=(
            f"{winner_text}\n\n"
            f"📢 Narrator\n{commentary_text[:1000]}\n\n"
            f"อันดับ:\n" + "\n".join(rank_lines)
        )
    )

    embed.set_image(
        url=random.choice(WIN_IMAGE)
    )
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1493575422007447622/1493678180702355568/utx_txt_order_00.png"
    )

    return embed

def build_slot_display(skill_id: str | None, channel_id: int, user_id: int) -> str:
    if not skill_id:
        return "➖ ว่าง"

    on_cd, cd_left = is_skill_on_cooldown(channel_id, user_id, skill_id)

    skill = SKILLS.get(skill_id)
    emoji = ICON.get(skill.get("icon"), "❓")
    name = skill['name']
    
    if on_cd:
        return (
            f"{emoji} `{skill_id}` **{name}**\n"
            f"⏳ **คูลดาวน์ {cd_left} เทิร์น**\n"
            f"--------------------------------------"
        )

    return build_skill_card_text(skill_id)

def get_mob_preset_choices():
    return [
        app_commands.Choice(
            name=data['name'],   # ชื่อโชว์
            value=key            # key ใช้จริง
        )
        for key, data in MOB_PRESETS.items()
    ]

async def stage_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    results = []

    for key, data in RACE_PRESET.items():
        stage_name = data['name']

        if (
            current.lower() in key.lower()
            or current.lower() in stage_name.lower()
        ):
            results.append(
                app_commands.Choice(
                    name=stage_name,
                    value=key
                )
            )

    # ถ้ามี Random อยากให้ติดมาด้วยเสมอ
    if "random".startswith(current.lower()) or current == "":
        results.append(app_commands.Choice(name="Random", value="Random"))

    return results[:25]

class GameCog(commands.GroupCog, name="game"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="game", invoke_without_command=True)
    async def game_admin_group(self, ctx: commands.Context):
        await ctx.send("ใช้ `!game join_as_mob`, `!game skil_turn` หรือ `!game test_bot_race`")

    @game_admin_group.command(name="join_as_mob")
    async def join_as_mob_admin(
        self,
        ctx: commands.Context,
        target: discord.Member,
        preset: str,
    ):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return

        if preset not in MOB_PRESETS:
            await ctx.send("ไม่พบ preset นี้ กรุณาใช้ preset key เช่น `rookie_front`")
            return

        success, message = add_player_as_mob_preset(
            ctx.channel.id,
            target.id,
            target.display_name,
            preset,
        )
        if not success:
            await ctx.send(message)
            return

        game = get_game(ctx.channel.id)
        player = (game or {}).get("players", {}).get(target.id)
        if player is None:
            await ctx.send("เพิ่มผู้เล่นแล้ว แต่ไม่พบข้อมูลผู้เล่นในห้อง")
            return

        embed = build_mob_join_embed(game, player)
        embed.title = "🏇 เพิ่มผู้เล่นด้วย Mob Preset แล้ว"
        embed.add_field(name="ผู้เล่น", value=target.mention, inline=True)
        embed.add_field(name="Preset", value=MOB_PRESETS[preset]["name"], inline=True)
        await ctx.send(embed=embed)

    @game_admin_group.command(name="skil_turn", aliases=["skip_turn"])
    async def skil_turn_admin(self, ctx: commands.Context):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return

        game = get_game(ctx.channel.id)
        if game is None:
            await ctx.send("ห้องนี้ยังไม่มีเกม")
            return
        if not game.get("started"):
            await ctx.send("เกมยังไม่เริ่ม")
            return

        await ctx.send(f"⏭️ Admin ข้ามเทิร์น {game.get('turn')}")
        advanced = await self._process_next_turn_core(
            channel_id=ctx.channel.id,
            send_func=ctx.send,
            guild=ctx.guild,
            title_suffix="(Admin)",
            require_all_confirmations=False,
            require_all_rolls=False,
        )
        if not advanced:
            await ctx.send("ข้ามเทิร์นไม่สำเร็จ อาจมีคำสั่งข้ามเทิร์นอื่นกำลังทำงาน")

    @game_admin_group.command(name="test_bot_race")
    async def test_bot_race_admin(self, ctx: commands.Context):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return

        async def send_response(content=None, **kwargs):
            kwargs.pop("ephemeral", None)
            return await ctx.send(content, **kwargs)

        adapter = SimpleNamespace(
            channel_id=ctx.channel.id,
            guild=ctx.guild,
            user=ctx.author,
            followup=SimpleNamespace(send=send_response),
        )
        await self.run_test_bot_race_command_logic(adapter)

    async def run_test_bot_race_command_logic(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        game = get_game(channel_id)

        if game is None:
            await interaction.followup.send("ยังไม่มีเกมในห้องนี้", ephemeral=True)
            return

        is_server_admin = bool(
            interaction.guild
            and interaction.user.guild_permissions.administrator
        )
        if not is_owner(channel_id, interaction.user.id) and not is_server_admin:
            await interaction.followup.send(
                "มีแค่เจ้าของห้องเท่านั้นที่ใช้คำสั่งนี้ได้",
                ephemeral=True
            )
            return

        success, payload = run_bot_race_test(channel_id)

        if not success:
            await interaction.followup.send(payload["message"], ephemeral=True)
            return

        game = payload["game"]
        game["record_type"] = "practice"
        ranked_players = payload["ranked_players"]
        try:
            ranked_players, _result, _history_id = finalize_race(
                game, ranked_players=ranked_players
            )
        except Exception as exc:
            print(f"Practice Race History save error: {exc}")

        log_channel_id = RACE_LOG_CHANNEL_ID
        log_channel = interaction.guild.get_channel(log_channel_id)

        if log_channel is None:
            await interaction.followup.send(
                "ทดสอบจบแล้ว แต่ไม่พบห้อง log ที่กำหนด",
                ephemeral=True
            )
            delete_game(channel_id)
            return

        log_file = build_race_log_file(game, ranked_players)
        await log_channel.send(file=log_file)

        delete_game(channel_id)

        await interaction.followup.send(
            "✅ ทดสอบบอทจบแล้ว ส่ง log และปิดห้องแข่งเรียบร้อย",
            ephemeral=True
        )
        
    def can_use_roll_skill(self, channel_id: int, user_id: int):
        from utils.game_manager import can_player_roll
        can_roll, message = can_player_roll(channel_id, user_id)
        if not can_roll:
            return False, "คุณใช้สิทธิ์ทอยในเทิร์นนี้ไปแล้ว จึงใช้สกิลประเภท Active Roll ไม่ได้"
        return True, None

    async def _process_pending_mobs_after_player_roll(
        self,
        interaction: discord.Interaction,
        game: dict,
    ) -> None:
        """Finish unrolled Mobs so the player's roll can close the turn."""
        current_turn = game.get("turn")
        for user_id, player in list(game.get("players", {}).items()):
            if not (player.get("is_mob") or player.get("bot_auto")) or player.get("last_roll_turn") == current_turn:
                continue

            success, payload = process_mob_turn(interaction.channel_id, user_id)
            if not success:
                print(f"Mob turn failed for {user_id}: {payload.get('message', payload)}")
                continue

            if payload.get("zone_preview"):
                await interaction.followup.send(embed=payload["zone_preview"])
            for skill_embed in payload.get("skill_embeds", []):
                await interaction.followup.send(embed=skill_embed)

            if should_render_mob_preview(game):
                card = await create_race_dice_preview(
                    game_player=player,
                    result=payload["result"],
                    payload=payload,
                    path_label=payload["path_effect"]["label"],
                    character_image_url=resolve_player_render_image(player),
                )
                buffer = await encode_png(card)
                await interaction.followup.send(
                    content=f"{player.get('username')}",
                    file=discord.File(buffer, filename="race_dice_preview.png"),
                )
            else:
                await interaction.followup.send(
                    build_mob_fast_roll_text(
                        game_player=player,
                        result=payload["result"],
                        payload=payload,
                        path_label=payload["path_effect"]["label"],
                    )
                )

    async def _send_automated_roll_result(
        self,
        interaction: discord.Interaction,
        user_id,
        player: dict,
        payload: dict,
    ) -> None:
        if payload.get("zone_preview"):
            await interaction.followup.send(embed=payload["zone_preview"])
        for skill_embed in payload.get("skill_embeds", []):
            await interaction.followup.send(embed=skill_embed)

        game = get_game(interaction.channel_id)
        if should_render_mob_preview(game):
            card = await create_race_dice_preview(
                game_player=player,
                result=payload["result"],
                payload=payload,
                path_label=payload["path_effect"]["label"],
                character_image_url=resolve_player_render_image(player),
            )
            await interaction.followup.send(
                content=f"Admin ทอยแทน <@{user_id}>",
                file=discord.File(await encode_png(card), filename="race_dice_preview.png"),
            )
        else:
            await interaction.followup.send(
                f"Admin ทอยแทน <@{user_id}>\n" + build_mob_fast_roll_text(
                    game_player=player,
                    result=payload["result"],
                    payload=payload,
                    path_label=payload["path_effect"]["label"],
                )
            )

    async def handle_after_roll(self, interaction: discord.Interaction, game: dict):
        if not game.get("awaiting_turn_confirm"):
            await self._process_pending_mobs_after_player_roll(interaction, game)

        if have_all_players_rolled(interaction.channel_id):
            if not game["awaiting_turn_confirm"]:
                start_turn_confirmation(interaction.channel_id)

                ranked_players = get_ranked_players(interaction.channel_id)
                phase = get_phase_from_turn(game["turn"], game["max_turn"])
                track_preview = build_track_progress_text(game["path"], game["turn"])

                rank_lines = []
                for index, (user_id, info) in enumerate(ranked_players, start=1):
                    display_name = format_player_reference(user_id, info)

                    marker = gold_range_marker(user_id, info, ranked_players)
                    rank_lines.append(
                        f"ลำดับที่ {index}: {display_name}{marker} | Score: {info['score']} ({info['style']})"
                    )

                rank_lines = [
                    _format_rank_line(index, user_id, info, ranked_players)
                    for index, (user_id, info) in enumerate(ranked_players, start=1)
                ]

                if not rank_lines:
                    rank_lines.append("ยังไม่มีผู้เล่น")

                confirm_embed = discord.Embed(
                    title=f"📊ผลสรุป ช่วงที่ {phase} เทิร์นที่ {game['turn']}",
                    color=discord.Color.blurple(),
                    description=(
                        f"อันดับคะแนน:🏆\n" + "\n".join(rank_lines)
                    )
                )
                confirm_embed.add_field(
                    name="🗺️ เส้นทางทั้งสนาม",
                    value=track_preview,
                    inline=False,
                )
                confirm_embed.set_footer(text="ทุกคนต้องกดยืนยันก่อนจะไปเทิร์นถัดไป")
                confirm_embed.add_field(
                    name="🛣️ เปลี่ยนเลนเทิร์นถัดไป",
                    value="ก่อนกดยืนยัน สามารถใช้ `/game lane target_lane:1-6` เพื่อเลือกเลนของเทิร์นถัดไปได้",
                    inline=False,
                )

                from views.turn_confirm_view import TurnConfirmView
                view = TurnConfirmView(self, interaction.channel_id)
                send_kwargs = {
                    "embed": confirm_embed,
                    "view": view,
                }

                try:
                    result_file = await build_turn_result_discord_file(game, ranked_players)
                    confirm_embed.set_image(url="attachment://turn_result.png")
                    send_kwargs["file"] = result_file
                except Exception as exc:
                    print("Turn result image error:", exc)

                msg = await interaction.followup.send(**send_kwargs)
                view.message = msg

    @app_commands.command(name="create", description="สร้างเกมใหม่")
    async def create(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        owner_id = interaction.user.id

        if get_game(channel_id) is not None:
            await interaction.response.send_message(
                "ห้องนี้มีเกมอยู่แล้ว",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🏟️ Create Game",
            description=(
                "เลือกระยะของสนามก่อน\n\n"
                "ปุ่มด้านล่าง:\n"
                "• Sprint\n"
                "• Mile\n"
                "• Medium\n"
                "• Long"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="เลือกระยะเพื่อดูรายชื่อสนาม")

        await interaction.response.send_message(
            embed=embed,
            view=CreateGameView(channel_id, owner_id),
            ephemeral=True
        )

    @app_commands.command(
        name="create_training_track",
        description="สร้างเกมด้วยสนาม Training Track",
    )
    async def create_training_track(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        owner_id = interaction.user.id

        if get_game(channel_id) is not None:
            await interaction.response.send_message(
                "ห้องนี้มีเกมอยู่แล้ว",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            embed=build_training_track_menu_embed(),
            view=TrainingTrackSelectView(channel_id, owner_id),
            ephemeral=True,
        )

    def _is_server_admin(self, ctx: commands.Context) -> bool:
        return bool(ctx.guild and ctx.author.guild_permissions.administrator)

    def _prefix_interaction_adapter(self, ctx: commands.Context):
        return SimpleNamespace(
            channel_id=ctx.channel.id,
            followup=SimpleNamespace(send=ctx.send),
        )

    @commands.command(name="race_add", aliases=["raceadd"])
    async def race_add(self, ctx: commands.Context, target: discord.Member, style: str):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return
        style = style.strip().capitalize()
        if style not in {"Front", "Pace", "Late", "End"}:
            await ctx.send("ระบุสายวิ่งเป็น Front, Pace, Late หรือ End เช่น `!race_add @สมาชิก Pace`")
            return
        success, message = add_player(ctx.channel.id, target.id, target.display_name, target.display_avatar.url, style)
        if not success:
            await ctx.send(message)
            return
        game = get_game(ctx.channel.id)
        await ctx.send(f"เพิ่ม {target.mention} ลงทะเบียนลำดับที่ {len(game['players'])} แล้ว (สาย {style})")

    @commands.command(name="race_auto", aliases=["raceauto"])
    async def race_auto(self, ctx: commands.Context, target: discord.Member, mode: str):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return
        mode = mode.strip().lower()
        if mode not in {"on", "off", "legend", "\u0e40\u0e1b\u0e34\u0e14", "\u0e1b\u0e34\u0e14"}:
            await ctx.send("Use on, off, or legend; example: `!race_auto @member legend`.")
            return
        enabled = mode in {"on", "legend", "\u0e40\u0e1b\u0e34\u0e14"}
        game = get_game(ctx.channel.id)
        player = game.get("players", {}).get(target.id) if game else None
        if player is None or player.get("is_mob"):
            await ctx.send("ไม่พบผู้เข้าแข่งขันคนนี้ในห้อง")
            return
        player["bot_auto"] = enabled
        if mode == "legend":
            player["ai_level"] = 8
            player["bot_auto_mode"] = "legend"
        else:
            player.pop("ai_level", None)
            player["bot_auto_mode"] = "on" if enabled else "off"
        if enabled and game.get("started") and player.get("last_roll_turn") != game.get("turn"):
            player["auto_control_turn"] = game.get("turn")
            success, payload = process_mob_turn(ctx.channel.id, target.id)
            if not success:
                await ctx.send(payload.get("message", "บอทเล่นแทนไม่สำเร็จ"))
                return
            adapter = self._prefix_interaction_adapter(ctx)
            await self._send_automated_roll_result(adapter, target.id, player, payload)
            await self.handle_after_roll(adapter, game)
            return
        mode_label = "Legend (Lv.8)" if mode == "legend" else ("ON" if enabled else "OFF")
        await ctx.send(f"Auto race for {target.mention}: **{mode_label}**")


    @commands.command(name="race_roll", aliases=["raceroll", "roll_for"])
    async def race_roll(self, ctx: commands.Context, target: discord.Member):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return
        game = get_game(ctx.channel.id)
        player = game.get("players", {}).get(target.id) if game else None
        if player is None or player.get("is_mob"):
            await ctx.send("ไม่พบผู้เข้าแข่งขันคนนี้ในห้อง")
            return
        if not game.get("started"):
            await ctx.send("เกมยังไม่เริ่ม")
            return
        player["auto_control_turn"] = game.get("turn")
        success, payload = process_mob_turn(ctx.channel.id, target.id)
        if not success:
            await ctx.send(payload.get("message", "ทอยแทนไม่สำเร็จ"))
            return
        adapter = self._prefix_interaction_adapter(ctx)
        await self._send_automated_roll_result(adapter, target.id, player, payload)
        await self.handle_after_roll(adapter, game)

    @app_commands.command(name="roster", description="แสดงรายชื่อและลำดับผู้เข้าแข่งขันในห้องนี้")
    async def roster(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.response.send_message("ห้องนี้ยังไม่มีเกม", ephemeral=True)
            return
        lines = []
        current_turn = game.get("turn")
        for number, (user_id, player) in enumerate(game.get("players", {}).items(), start=1):
            if player.get("is_mob"):
                name = player.get("display_name") or player.get("username") or "Mob"
                status = "Mob"
            else:
                name = f"<@{user_id}>"
                status = "เล่นอัตโนมัติ" if player.get("bot_auto") else "ผู้เล่น"
                if game.get("started"):
                    status += " · ทอยแล้ว" if player.get("last_roll_turn") == current_turn else " · รอทอย"
            lines.append(f"**{number}.** {name} — {player.get('style', '-')}, {status}")
        await interaction.response.send_message(
            f"**รายชื่อผู้เข้าแข่งขัน · {game.get('stage_name', 'สนาม')}**\n" + ("\n".join(lines) or "ยังไม่มีผู้เข้าแข่งขัน")
        )

    @app_commands.command(
        name="unconfirmed",
        description="ดูว่าใครยังไม่ยืนยันเทิร์นปัจจุบัน",
    )
    async def unconfirmed(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ห้องนี้ยังไม่มีเกม",
                ephemeral=True,
            )
            return
        if (
            not game.get("awaiting_turn_confirm")
            or game.get("turn_confirmation_turn") != game.get("turn")
        ):
            await interaction.response.send_message(
                "ตอนนี้ยังไม่อยู่ในช่วงยืนยันเทิร์น",
                ephemeral=True,
            )
            return

        pending_players = get_unconfirmed_turn_players(interaction.channel_id) or []
        if not pending_players:
            await interaction.response.send_message(
                f"✅ ผู้เล่นยืนยันครบแล้วสำหรับเทิร์น {game.get('turn')}",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        lines = []
        for user_id, player in pending_players:
            roll_status = (
                "ทอยแล้ว · รอยืนยัน"
                if player.get("last_roll_turn") == game.get("turn")
                else "ยังไม่ทอย"
            )
            lines.append(f"• <@{user_id}> — {roll_status}")

        await interaction.response.send_message(
            f"**ผู้เล่นที่ยังไม่ยืนยันเทิร์น {game.get('turn')}**\n"
            + "\n".join(lines),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(name="race_remove", aliases=["raceremove", "remove_player"])
    async def race_remove(self, ctx: commands.Context, number: int):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return
        game = get_game(ctx.channel.id)
        if game is None:
            await ctx.send("ห้องนี้ยังไม่มีเกม")
            return
        if game.get("started"):
            await ctx.send("นำผู้เล่นออกได้เฉพาะก่อนเริ่มแข่ง")
            return
        if number < 1:
            await ctx.send("ลำดับต้องเริ่มที่ 1")
            return
        roster = list(game.get("players", {}).items())
        if number > len(roster):
            await ctx.send("ไม่มีผู้เข้าแข่งขันตามลำดับนี้")
            return
        user_id, player = roster[number - 1]
        if player.get("is_mob"):
            await ctx.send("ลำดับนี้เป็น Mob; ใช้คำสั่งลบ Mob ที่เกี่ยวข้องแทน")
            return
        game["players"].pop(user_id, None)
        await ctx.send(f"นำ <@{user_id}> (ลำดับ {number}) ออกจากห้องแล้ว")

    async def _process_next_turn_core(
        self,
        *,
        channel_id: int,
        send_func,
        guild,
        title_suffix: str = "",
        expected_turn: int | None = None,
        confirmation_token: int | None = None,
        require_all_confirmations: bool = True,
        require_all_rolls: bool = True,
    ):
        game = get_game(channel_id)
        if game is None:
            return False

        claimed, _reason = claim_turn_advance(
            channel_id,
            expected_turn=expected_turn,
            confirmation_token=confirmation_token,
            require_all_confirmations=require_all_confirmations,
            require_all_rolls=require_all_rolls,
        )
        if not claimed:
            return False

        previous_ranked_players = get_ranked_players(channel_id)
        previous_players = build_narrator_players_from_ranked(
            previous_ranked_players,
            score_overrides=game.get("turn_snapshot_scores", {}),
        )

        new_turn = next_turn(channel_id)

        if new_turn > game["max_turn"]:
            # Finish the shared race state before rendering or persistence, so
            # late interactions cannot enter the end path a second time.
            ranked_players = get_ranked_players(channel_id)
            race_history_id = None
            try:
                ranked_players, _result, race_history_id = finalize_race(
                    game, ranked_players=ranked_players
                )
            except Exception as exc:
                print(f"Race History save error: {exc}")

            commentary_text = None
            try:
                final_players = build_narrator_players_from_ranked(ranked_players)
                commentary_text = await generate_finish_commentary(
                    final_players,
                    stage_name=game.get("stage_name")
                )
            except Exception as e:
                print("Finish narrator error:", e)

            embed = build_game_end_embed(
                ranked_players,
                commentary_text=commentary_text
            )
            if race_history_id:
                embed.add_field(
                    name="Race History",
                    value=f"Saved completed race `{race_history_id[:8]}`.",
                    inline=False,
                )
            await send_func(embed=embed)

            log_channel_id = RACE_LOG_CHANNEL_ID

            log_channel = None
            if guild:
                log_channel = guild.get_channel(log_channel_id)

            if log_channel:
                log_file = build_race_log_file(game, ranked_players)
                await log_channel.send(file=log_file)

            ok, msg = stop_bgm(guild)

            delete_game(channel_id)
            return True

        game = get_game(channel_id)

        phase = get_phase_from_turn(new_turn, game["max_turn"])
        ranked_players = get_ranked_players(channel_id)
        current_players = build_narrator_players_from_ranked(ranked_players)

        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            display_name = format_player_reference(user_id, info)

            marker = gold_range_marker(user_id, info, ranked_players)
            rank_lines.append(
                f"ลำดับที่ {index}: {display_name}{marker} | Score: {info['score']} ({info['style']})"
            )

        rank_lines = [
            _format_rank_line(index, user_id, info, ranked_players)
            for index, (user_id, info) in enumerate(ranked_players, start=1)
        ]

        if not rank_lines:
            rank_lines.append("ยังไม่มีผู้เล่น")

        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

        track_preview = build_track_progress_text(game["path"], new_turn)
        # current_track_text = build_current_track_text(game["path"], new_turn)

        commentary_text = None
        try:
            commentary_text = await generate_commentary(
                previous_players,
                current_players,
                turn=new_turn,
                max_turn=game["max_turn"],
                event_text=f"เริ่มเทิร์น {new_turn} เส้นทางเป็น {path_label}"
            )
        except Exception as e:
            print("Narrator error:", e)

        title = f"เข้าสู่เทิร์น {new_turn}"
        if title_suffix:
            title += f" {title_suffix}"

     

        embed = discord.Embed(
            title=title,
            color=discord.Color.green(),
            description=(
                f"Phase: {phase}\n"
                f"เส้นทางเทิร์นนี้:\n{track_preview}\n\n"
                f"📢 Narrator:\n{commentary_text[:1000]}\n\n"
                f"อันดับคะแนน:🏆\n" + "\n".join(rank_lines)
            )
        )
        
        embed.add_field(
            name="Effect",
            value=build_path_effect_text(path_type),
            inline=False
        )

        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1494733536656097340/1495342542470778983/utx_ico_itemlist_roommatch_00.png?ex=69e5e5c4&is=69e49444&hm=8dcadb111d4f0a7cd59d85e3c2023bc491ba78c8edd65ba2ac3f1471e89d0656&=&format=webp&quality=lossless&width=228&height=200"
        )

        send_kwargs = {"embed": embed}
        try:
            result_file = await build_turn_result_discord_file(game, ranked_players)
            embed.set_image(url="attachment://turn_result.png")
            send_kwargs["file"] = result_file
        except Exception as exc:
            print("Next turn result image error:", exc)

        await send_func(**send_kwargs)

        for passive_embed in drain_pending_passive_skill_embeds(channel_id):
            await send_func(embed=passive_embed)

        game = get_game(channel_id)
        for user_id, player in game["players"].items():
            if player.get("is_mob") or player.get("bot_auto"):
                success, payload = process_mob_turn(channel_id, user_id)
                if not success:
                    print(f"Mob turn failed for {user_id}: {payload.get('message', payload)}")
                    continue
                if success and payload.get("zone_preview"):
                    await send_func(embed=payload["zone_preview"])

                if payload.get("skill_embeds"):
                    for skill_embed in payload["skill_embeds"]:
                        await send_func(embed=skill_embed)
                
                if should_render_mob_preview(game):
                    card = await create_race_dice_preview(
                        game_player=player,
                        result= payload["result"],
                        payload=payload,
                        path_label=payload["path_effect"]["label"],
                        character_image_url=resolve_player_render_image(player),
                    )
                    buffer = await encode_png(card)
                    file = discord.File(buffer, filename="race_dice_preview.png")
                    await send_func(content=f"{player.get('username') }", file=file)
                else:
                    await send_func(
                        content=build_mob_fast_roll_text(
                            game_player=player,
                            result=payload["result"],
                            payload=payload,
                            path_label=payload["path_effect"]["label"],
                        )
                    )

        if game and game["started"] and not has_real_player(game):
            await self._process_next_turn_core(
                channel_id=channel_id,
                send_func=send_func,
                guild=guild,
                title_suffix="(Auto Mob)",
                require_all_confirmations=False,
            )

        return True

    async def process_next_turn(
        self,
        interaction: discord.Interaction,
        *,
        expected_turn: int | None = None,
        confirmation_token: int | None = None,
        require_all_confirmations: bool = True,
        require_all_rolls: bool = True,
    ):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.followup.send("เกมยังไม่เข้าร่วม race", ephemeral=True)
            return

        return await self._process_next_turn_core(
            channel_id=interaction.channel_id,
            send_func=interaction.followup.send,
            guild=interaction.guild,
            title_suffix="",
            expected_turn=expected_turn,
            confirmation_token=confirmation_token,
            require_all_confirmations=require_all_confirmations,
            require_all_rolls=require_all_rolls,
        )

    async def process_next_turn_from_timeout(
        self,
        channel: discord.TextChannel,
        *,
        expected_turn: int,
        confirmation_token: int,
    ):
        game = get_game(channel.id)
        if game is None:
            return

        return await self._process_next_turn_core(
            channel_id=channel.id,
            send_func=channel.send,
            guild=channel.guild,
            title_suffix="(Auto)",
            expected_turn=expected_turn,
            confirmation_token=confirmation_token,
            require_all_confirmations=False,
        )

    # @app_commands.command(name="myinfo", description="ดูข้อมูลของตัวเองในเกม")
    # async def myinfo(self, interaction: discord.Interaction):
    #     player = get_player_in_game(interaction.channel_id, interaction.user.id)
    #     if player is None:
    #         await interaction.response.send_message(
    #             "คุณยังไม่ได้เข้าร่วมเกมนี้",
    #             ephemeral=True
    #         )
    #         return

    #     embed = discord.Embed(
    #         title=f"ข้อมูลของ {interaction.user.display_name}",
    #         color=discord.Color.blurple()
    #     )
    #     embed.add_field(name="Style", value=player["style"], inline=True)
    #     embed.add_field(name="Score", value=player["score"], inline=True)
    #     embed.add_field(name="Reroll คงเหลือ", value=player["reroll_left"], inline=True)

    #     await interaction.response.send_message(embed=embed)

    # @app_commands.command(name="info", description="ดูข้อมูลเกมในห้องนี้")
    # async def info(self, interaction: discord.Interaction):
    #     game = get_game(interaction.channel_id)
    #     if game is None:
    #         await interaction.response.send_message(
    #             "ยังไม่มีเกมในห้องนี้",
    #             ephemeral=True
    #         )
    #         return
        
    #     status_text = "Started" if game["started"] else "Waiting"
    #     players = get_players(interaction.channel_id)
    #     player_lines = []

    #     if players:
    #         for user_id, info in players.items():
    #             player_lines.append(
    #                 f"<@{user_id}> | Style: {info['style']} | Score: {info['score']}"
    #             )
    #     else:
    #         player_lines.append("ยังไม่มีผู้เล่น")

    #     embed = discord.Embed(
    #         title=f"Race: {game['stage_name']}",
    #         color=discord.Color.green(),
    #         description=(
    #             f"เจ้าของเกม: <@{game['owner_id']}>\n"
    #             f"สถานะ: {status_text}\n"
    #             f"เทิร์น: {game['turn']}\n\n"
    #             f"ผู้เล่น:\n" + "\n".join(player_lines)
    #         )
    #     )

    #     embed.set_thumbnail(
    #         url="https://media.discordapp.net/attachments/697810514448744448/1493624841989914714/utx_ico_itemlist_dailyrace_00.png"
    #     )

    #     await interaction.response.send_message(embed=embed)


    @app_commands.command(name="close", description="ลบหรือจบเกมในห้องนี้")
    async def close(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)

        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return

        is_game_owner = is_owner(interaction.channel_id, interaction.user.id)
        is_admin = interaction.user.guild_permissions.administrator

        if not (is_game_owner or is_admin):
            await interaction.response.send_message(
                "มีแค่ผู้สร้างเกมหรือผู้ดูแลเซิร์ฟเวอร์เท่านั้นที่ลบเกมได้",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "คุณแน่ใจหรือไม่ว่าจะลบเกมนี้?",
            view=ConfirmDeleteView(interaction.channel_id),
            ephemeral=True
        )

    @app_commands.command(name="run", description="ทอยเต๋าเดินในเทิร์นนี้")
    async def run(self, interaction: discord.Interaction):
        await interaction.response.defer()

        can_roll, message = can_player_roll(interaction.channel_id, interaction.user.id)
        if not can_roll:
            await interaction.followup.send(message, ephemeral=True)
            return

        success, payload = await execute_player_roll(
            interaction,
            title_prefix="วิ่งในเทิร์นนี้",
            mark_roll=True,
            allow_reroll_view=True,
        )

        if not success:
            await interaction.followup.send(payload["message"], ephemeral=True)
            return

        game_player = payload["game_player"]
        result = payload["result"]
        path_effect = payload["path_effect"]
        refresh_player_profile_snapshot(interaction.user.id, game_player)

        avatar_url = resolve_player_avatar_url(game_player, interaction.user.display_avatar.url)


        card = await create_race_dice_preview(
            game_player=game_player,
            result=result,
            payload=payload,
            path_label=path_effect["label"],
            character_image_url=resolve_player_render_image(game_player, avatar_url),
        )

        buffer = await encode_png(card)

        file = discord.File(buffer, filename="race_dice_preview.png")

        send_kwargs = {
            "content": f"<@{interaction.user.id}>",
            "file": file,
        }

        if payload["view"] is not None:
            send_kwargs["view"] = payload["view"]

        await interaction.followup.send(**send_kwargs)

        game = payload["game"]
        await self.handle_after_roll(interaction, game)

    @app_commands.command(name="lane", description="เลือกเลนสำหรับเทิร์นถัดไป")
    @app_commands.describe(target_lane="เลนที่ต้องการ 1-6")
    async def lane(self, interaction: discord.Interaction, target_lane: int):
        success, result = queue_player_lane_change(interaction.channel_id, interaction.user.id, target_lane)
        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await interaction.response.send_message(
            f"ตั้งเลนถัดไปเป็น Lane {result['pending_lane']} แล้ว (ตอนนี้ Lane {result['current_lane']})",
            ephemeral=True,
        )

    @discord.app_commands.command(name="skill", description="เปิดเมนูใช้สกิล")
    async def skill(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is not None and not get_game_rule(game, "AllowSkill"):
            await interaction.response.send_message(
                "ห้องนี้ปิดการใช้ Skill และ Zone",
                ephemeral=True,
            )
            return

        playerInGame = get_player_in_game(
            interaction.channel_id,
            interaction.user.id
        )

        if playerInGame is None:
            await interaction.response.send_message(
                "เกมยังไม่เข้าร่วม race",
                ephemeral=True
            )
            return

        slots = playerInGame.get("skills", {
            1: None,
            2: None,
            3: None,
            4: None,
        })

        wit_mana = playerInGame.get("wit_mana", 0)

        embed = discord.Embed(
            title=f"📘 Skill Menu: {interaction.user.display_name}",
            color=discord.Color.blurple()
        )

        zone = playerInGame.get("zone")
        if not zone:
            await interaction.response.send_message(
                "ไม่พบข้อมูล Zone",
                ephemeral=True
            )
            return

        zone_name = zone.get("name", "Default Zone")
        zone_left = playerInGame.get("zone_left", 0)
        zone_text = f"{zone_name}\nคงเหลือ: {zone_left}"

        embed.add_field(
            name="🌌 Zone",
            value=zone_text,
            inline=False
        )

        embed.add_field(
            name="🎯 Skill Slot 1",
            value=build_slot_display(slots.get(1), interaction.channel_id, interaction.user.id),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 2",
            value=build_slot_display(slots.get(2), interaction.channel_id, interaction.user.id),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 3",
            value=build_slot_display(slots.get(3), interaction.channel_id, interaction.user.id),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 4",
            value=build_slot_display(slots.get(4), interaction.channel_id, interaction.user.id),
            inline=False
        )
        
        embed.add_field(
            name=f"{Status_Icon_Type['WIT']} Skill pt",
            value=str(wit_mana),
            inline=True
        )

        embed.set_footer(text="กดปุ่ม 1 / 2 / 3 / 4 เพื่อใช้สกิล หรือกด 🌌 เพื่อใช้ Zone")

        await interaction.response.send_message(
            embed=embed,
            view=UseSkillView(self, interaction.user.id, interaction.channel_id),
            ephemeral=True
        )
   
async def setup(bot: commands.Bot):
    await bot.add_cog(GameCog(bot))
