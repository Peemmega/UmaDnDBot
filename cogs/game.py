import discord
from discord.ext import commands
from discord import app_commands

from io import BytesIO
import discord
from utils.race_dice_preview import create_race_dice_preview

from views.confirmDeleteGameView import ConfirmDeleteView
from views.use_skill_view import UseSkillView
from views.create_game_view import CreateGameView

from utils.icon_presets import Status_Icon_Type
from utils.skill.skill_presets import SKILLS, ICON
from utils.narrater import (
    generate_commentary,
    build_narrator_players_from_ranked,
    generate_finish_commentary,
)
from utils.music_manager import play_bgm, stop_bgm

from utils.race.race_presets import RACE_PRESET, render_path, build_track_progress_text, build_current_track_text
from utils.dice.roll_service import (execute_player_roll)


from utils.database import ensure_player
from utils.race.race_presets import (
    get_current_path_type, 
    build_path_effect_text, 
    PATH_TYPE_TEXT
)

from utils.skill.skill_manager import build_skill_card_text
from utils.race.race_dice import (get_phase_from_turn,)
from utils.mob.mob_presets import (MOB_PRESETS)

from utils.game_manager import (
    create_game,
    get_game,
    is_owner,
    next_turn,
    get_player_in_game,
    get_players,
    delete_game,
    can_player_roll, 
    get_ranked_players,
    have_all_players_rolled,
    start_turn_confirmation,
    is_skill_on_cooldown,
    add_mob_from_preset,
    add_player_as_mob_preset,
    build_mob_join_embed,
    process_mob_turn
)



def build_game_end_embed(ranked_players, commentary_text: str | None = None):
    rank_lines = []
    for index, (user_id, info) in enumerate(ranked_players, start=1):
        if str(user_id).startswith("mob_"):
            display_name = info.get("display_name") or info.get("username") or "Mob"
        else:
            display_name = f"<@{user_id}>"

        rank_lines.append(
            f"{index}. {display_name} | {info['style']} | Score: {info['score']}"
        )
        

    if not rank_lines:
        rank_lines.append("ยังไม่มีผู้เล่น")

    winner_text = "ไม่มีผู้ชนะ"
    if ranked_players:
        winner_id, winner_info = ranked_players[0]
        winner_text = (
            f"🏆 ผู้ชนะ: <@{winner_id}>\n"
            f"Style: {winner_info['style']}\n"
            f"Score: {winner_info['score']}"
        )

    embed = discord.Embed(
        title="🏁 เกมจบแล้ว",
        color=discord.Color.red(),
        description=(
            f"{winner_text}\n\n"
            f"อันดับสุดท้าย:\n" + "\n".join(rank_lines)
        )
    )

    if commentary_text:
        embed.add_field(
            name="📢 Narrator",
            value=commentary_text[:1000],
            inline=False
        )

    embed.set_image(
        url="https://media.discordapp.net/attachments/1493575422007447622/1493676112952426629/i-won-taurus-cup-with-tm-opera-o-v0-w2a0zxpycglf1.gif"
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
    name = skill["name"]
    
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
            name=data["name"],   # ชื่อโชว์
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
        stage_name = data["name"]

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

async def mob_preset_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    return [
        app_commands.Choice(name=data["name"], value=key)
        for key, data in MOB_PRESETS.items()
        if current.lower() in data["name"].lower()
    ][:25]

class GameCog(commands.GroupCog, name="game"):
    def __init__(self, bot):
        self.bot = bot

    def can_use_roll_skill(self, channel_id: int, user_id: int):
        from utils.game_manager import can_player_roll
        can_roll, message = can_player_roll(channel_id, user_id)
        if not can_roll:
            return False, "คุณใช้สิทธิ์ทอยในเทิร์นนี้ไปแล้ว จึงใช้สกิลประเภท Active Roll ไม่ได้"
        return True, None

    async def handle_after_roll(self, interaction: discord.Interaction, game: dict):
        if have_all_players_rolled(interaction.channel_id):
            if not game["awaiting_turn_confirm"]:
                start_turn_confirmation(interaction.channel_id)

                ranked_players = get_ranked_players(interaction.channel_id)
                phase = get_phase_from_turn(game["turn"], game["max_turn"])

                rank_lines = []
                for index, (user_id, info) in enumerate(ranked_players, start=1):
                    if str(user_id).startswith("mob_"):
                        display_name = info.get("display_name") or info.get("username") or "Mob"
                    else:
                        display_name = info.get("username") or f"<@{user_id}>"

                    rank_lines.append(
                        f"ลำดับที่ {index}: {display_name} | Score: {info['score']} ({info['style']})"
                    )

                if not rank_lines:
                    rank_lines.append("ยังไม่มีผู้เล่น")

                confirm_embed = discord.Embed(
                    title=f"📊ผลสรุป ช่วงที่ {phase} เทิร์นที่ {game['turn']}",
                    color=discord.Color.blurple(),
                    description=(
                        f"อันดับคะแนน:🏆\n" + "\n".join(rank_lines)
                    )
                )
                confirm_embed.set_footer(text="ทุกคนต้องกดยืนยันก่อนจะไปเทิร์นถัดไป")

                from views.turn_confirm_view import TurnConfirmView
                view = TurnConfirmView(self, interaction.channel_id)
                msg = await interaction.followup.send(embed=confirm_embed, view=view)
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

    @discord.app_commands.command(name="skip_turn", description="ข้ามไปเทิร์นถัดไปทันที (เฉพาะเจ้าของห้อง)")
    async def skip_turn(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)

        if game is None:
            await interaction.response.send_message("ยังไม่มีเกมในห้องนี้", ephemeral=True)
            return

        if not game["started"]:
            await interaction.response.send_message("เกมยังไม่เริ่ม", ephemeral=True)
            return

        if not is_owner(interaction.channel_id, interaction.user.id):
            await interaction.response.send_message("มีแค่เจ้าของห้องเท่านั้นที่ข้ามเทิร์นได้", ephemeral=True)
            return

        await interaction.response.defer()
        await interaction.followup.send(f"⏭️ <@{interaction.user.id}> ข้ามเทิร์น {game['turn']}")
        await self.process_next_turn(interaction)

    @app_commands.command(name="add_mob", description="เพิ่ม mob preset")
    @app_commands.autocomplete(preset=mob_preset_autocomplete)
    async def add_mob(
        self,
        interaction: discord.Interaction,
        preset: str
    ):
        success, message = add_mob_from_preset(interaction.channel_id, preset)

        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.response.send_message("ไม่พบข้อมูลเกม", ephemeral=True)
            return

        # หา mob ที่เพิ่งเพิ่มล่าสุด
        mob_players = [
            info for uid, info in game["players"].items()
            if str(uid).startswith("mob_")
        ]

        if not mob_players:
            await interaction.response.send_message("เพิ่ม mob สำเร็จ แต่ไม่พบข้อมูล mob", ephemeral=True)
            return

        mob = mob_players[-1]
        embed = build_mob_join_embed(game, mob)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="join_as_mob", description="เข้าร่วมโดยใช้ mob preset")
    @app_commands.autocomplete(preset=mob_preset_autocomplete)
    async def join_as_mob(
        self,
        interaction: discord.Interaction,
        preset: str
    ):
        success, message = add_player_as_mob_preset(
            interaction.channel_id,
            interaction.user.id,
            interaction.user.display_name,
            preset
        )

        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.response.send_message("ไม่พบข้อมูลเกม", ephemeral=True)
            return

        player = game["players"].get(interaction.user.id)
        if player is None:
            await interaction.response.send_message("เข้าร่วมสำเร็จ แต่ไม่พบข้อมูลผู้เล่นในเกม", ephemeral=True)
            return

        embed = build_mob_join_embed(game, player)
        embed.title = "🏇 ผู้เล่นเข้าร่วมด้วย Mob Preset!"
        embed.add_field(name="ผู้เล่น", value=interaction.user.mention, inline=True)
        embed.add_field(name="Preset", value=MOB_PRESETS[preset]["name"], inline=True)

        await interaction.response.send_message(embed=embed)

    async def _process_next_turn_core(
        self,
        *,
        channel_id: int,
        send_func,
        guild,
        title_suffix: str = "",
    ):
        game = get_game(channel_id)
        if game is None:
            return

        previous_ranked_players = get_ranked_players(channel_id)
        previous_players = build_narrator_players_from_ranked(previous_ranked_players)

        new_turn = next_turn(channel_id)

        if new_turn > game["max_turn"]:
            ranked_players = get_ranked_players(channel_id)

            commentary_text = None
            try:
                final_players = build_narrator_players_from_ranked(ranked_players)
                commentary_text = await generate_finish_commentary(
                    final_players,
                    stage_name=game.get("stage_name")
                )
            except Exception as e:
                print("Finish narrator error:", e)

            embed = build_game_end_embed(ranked_players, commentary_text=commentary_text)
            await send_func(embed=embed)

            ok, msg = stop_bgm(guild)
            print(f"[Music] stop on turn end: {msg}")

            delete_game(channel_id)
            return

        game = get_game(channel_id)

        phase = get_phase_from_turn(new_turn, game["max_turn"])
        ranked_players = get_ranked_players(channel_id)
        current_players = build_narrator_players_from_ranked(ranked_players)

        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            if str(user_id).startswith("mob_"):
                display_name = (
                    info.get("display_name")
                    or info.get("username")
                    or info.get("name")
                    or "Mob"
                )
            else:
                display_name = info.get("username") or f"<@{user_id}>"

            rank_lines.append(
                f"ลำดับที่ {index}: {display_name} | Score: {info['score']} ({info['style']})"
            )

        if not rank_lines:
            rank_lines.append("ยังไม่มีผู้เล่น")

        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

        track_preview = build_track_progress_text(game["path"], new_turn)
        current_track_text = build_current_track_text(game["path"], new_turn)

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
                f"เส้นทางเทิร์นนี้:\n{track_preview}\n{current_track_text}\n\n"
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

        if commentary_text:
            embed.add_field(
                name="📢 Narrator",
                value=commentary_text[:1000],
                inline=False
            )

        await send_func(embed=embed)

        game = get_game(channel_id)
        for user_id, player in game["players"].items():
            if player.get("is_mob"):
                success, payload = process_mob_turn(channel_id, user_id)
                if success and payload.get("zone_preview"):
                    await send_func(embed=payload["zone_preview"])
                if success and payload.get("embed"):
                    await send_func(embed=payload["embed"])

    async def process_next_turn(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.followup.send("เกมยังไม่เข้าร่วม race", ephemeral=True)
            return

        await self._process_next_turn_core(
            channel_id=interaction.channel_id,
            send_func=interaction.followup.send,
            guild=interaction.guild,
            title_suffix=""
        )

    async def process_next_turn_from_timeout(self, channel: discord.TextChannel):
        game = get_game(channel.id)
        if game is None:
            return

        await self._process_next_turn_core(
            channel_id=channel.id,
            send_func=channel.send,
            guild=channel.guild,
            title_suffix="(Auto)"
    )

    @app_commands.command(name="myinfo", description="ดูข้อมูลของตัวเองในเกม")
    async def myinfo(self, interaction: discord.Interaction):
        player = get_player_in_game(interaction.channel_id, interaction.user.id)
        if player is None:
            await interaction.response.send_message(
                "คุณยังไม่ได้เข้าร่วมเกมนี้",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"ข้อมูลของ {interaction.user.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Style", value=player["style"], inline=True)
        embed.add_field(name="Score", value=player["score"], inline=True)
        embed.add_field(name="Reroll คงเหลือ", value=player["reroll_left"], inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="ดูข้อมูลเกมในห้องนี้")
    async def info(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return
        
        status_text = "Started" if game["started"] else "Waiting"
        players = get_players(interaction.channel_id)
        player_lines = []

        if players:
            for user_id, info in players.items():
                player_lines.append(
                    f"<@{user_id}> | Style: {info['style']} | Score: {info['score']}"
                )
        else:
            player_lines.append("ยังไม่มีผู้เล่น")

        embed = discord.Embed(
            title=f"Race: {game['stage_name']}",
            color=discord.Color.green(),
            description=(
                f"เจ้าของเกม: <@{game['owner_id']}>\n"
                f"สถานะ: {status_text}\n"
                f"เทิร์น: {game['turn']}\n\n"
                f"ผู้เล่น:\n" + "\n".join(player_lines)
            )
        )

        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/697810514448744448/1493624841989914714/utx_ico_itemlist_dailyrace_00.png"
        )

        await interaction.response.send_message(embed=embed)

    

    @app_commands.command(name="close", description="ลบหรือจบเกมในห้องนี้")
    async def close(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)

        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return

        if not is_owner(interaction.channel_id, interaction.user.id):
            await interaction.response.send_message(
                "มีแค่ผู้สร้างเกมเท่านั้นที่ลบเกมได้",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "คุณแน่ใจหรือไม่ว่าจะลบเกมนี้?",
            view=ConfirmDeleteView(interaction.channel_id),
            ephemeral=True
        )

    # @app_commands.command(name="run", description="ทอยเต๋าเดินในเทิร์นนี้")
    # async def run(self, interaction: discord.Interaction):
    #     await interaction.response.defer()

    #     can_roll, message = can_player_roll(interaction.channel_id, interaction.user.id)
    #     if not can_roll:
    #         await interaction.followup.send(message, ephemeral=True)
    #         return

    #     success, payload = await execute_player_roll(
    #         interaction,
    #         title_prefix="วิ่งในเทิร์นนี้",
    #         mark_roll=True,
    #         allow_reroll_view=True,
    #     )

    #     if not success:
    #         await interaction.followup.send(payload["message"], ephemeral=True)
    #         return

    #     send_kwargs = {
    #         "content": f"<@{interaction.user.id}>",
    #         "embed": payload["embed"],
    #     }
    #     if payload["view"] is not None:
    #         send_kwargs["view"] = payload["view"]

    #     await interaction.followup.send(**send_kwargs)

    #     game = payload["game"]
    #     await self.handle_after_roll(interaction, game)

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

        avatar_url = interaction.user.display_avatar.url


        card = await create_race_dice_preview(
            game_player=game_player,
            result=result,
            payload=payload,
            path_label=path_effect["label"],
            character_image_url=avatar_url,
        )

        buffer = BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)

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

    @discord.app_commands.command(name="skill", description="เปิดเมนูใช้สกิล")
    async def skill(self, interaction: discord.Interaction):
        ensure_player(interaction.user.id, interaction.user.name)

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
            name=f"{Status_Icon_Type['WIT']} Skill pt",
            value=str(wit_mana),
            inline=True
        )

        embed.set_footer(text="กดปุ่ม 1 / 2 / 3 เพื่อใช้สกิล หรือกด 🌌 เพื่อใช้ Zone")

        await interaction.response.send_message(
            embed=embed,
            view=UseSkillView(self, interaction.user.id, interaction.channel_id),
            ephemeral=True
        )
   
async def setup(bot: commands.Bot):
    await bot.add_cog(GameCog(bot))