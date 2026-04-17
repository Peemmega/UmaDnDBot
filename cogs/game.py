import discord
from discord.ext import commands
from discord import app_commands

from views.confirmDeleteGameView import ConfirmDeleteView
from views.join_view import LobbyView

from utils.dice.race_presets import RACE_PRESET
from utils.dice.roll_service import (
    execute_player_roll
)
from views.use_skill_view import UseSkillView
from utils.database import ensure_player, get_player_skill_slots
from utils.skill.skill_presets import SKILLS, ICON
from utils.icon_presets import Status_Icon_Type
from utils.dice.race_presets import (
    get_current_path_type, 
    build_path_effect_text, 
    get_path_effect,
    PATH_TYPE_TEXT
)

from utils.dice.race_dice import (
    roll_race_dice,
    get_phase_from_turn,
)

from utils.game_manager import (
    create_game,
    get_game,
    is_owner,
    next_turn,
    get_player_in_game,
    get_players,
    delete_game,
    can_player_roll, 
    mark_player_rolled,
    update_player_score,
    get_ranked_players,
    have_all_players_rolled,
    start_turn_confirmation,
    get_player_skill_cd
)

PATH_EMOJI = {
    1: "➡️",  # ทางตรง
    2: "⤵️",  # โค้ง
    3: "↗️",  # เนินขึ้น
    4: "↘️",  # เนินลง
}

def render_path(path: list[int]) -> str:
    return "".join(PATH_EMOJI.get(x, "⬜") for x in path)

def build_game_end_embed(ranked_players):
        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            rank_lines.append(
                f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
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

        embed.set_image(
            url="https://media.discordapp.net/attachments/1493575422007447622/1493676112952426629/i-won-taurus-cup-with-tm-opera-o-v0-w2a0zxpycglf1.gif"
        )
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1493575422007447622/1493678180702355568/utx_txt_order_00.png"
        )

        return embed

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
                    rank_lines.append(
                        f"#{index} <@{user_id}> | {info['style']} | Score: {info['score']}"
                    )

                if not rank_lines:
                    rank_lines.append("ยังไม่มีผู้เล่น")

                confirm_embed = discord.Embed(
                    title=f"📊 จบเทิร์น {game['turn']}",
                    color=discord.Color.blurple(),
                    description=(
                        f"Phase: {phase}\n\n"
                        f"อันดับคะแนน:\n" + "\n".join(rank_lines)
                    )
                )
                confirm_embed.set_footer(text="ทุกคนต้องกดยืนยันก่อนจะไปเทิร์นถัดไป")

                from views.turn_confirm_view import TurnConfirmView
                view = TurnConfirmView(self, interaction.channel_id)
                msg = await interaction.followup.send(embed=confirm_embed, view=view)
                view.message = msg

    @app_commands.command(name="create", description="สร้างเกมใหม่")
    @app_commands.describe(stage="เลือกสนาม")
    @app_commands.choices(stage=[
        app_commands.Choice(name=RACE_PRESET["NHK"]["name"], value="NHK"),
        app_commands.Choice(name=RACE_PRESET["TakarazukaKinen"]["name"], value="TakarazukaKinen"),
        app_commands.Choice(name=RACE_PRESET["TennoShoSpring"]["name"], value="TennoShoSpring"),
    ])
    async def create(self, interaction: discord.Interaction, stage: app_commands.Choice[str]):
        channel_id = interaction.channel_id
        owner_id = interaction.user.id
        stage_key = stage.value

        success = create_game(channel_id, stage_key, owner_id)
        if not success:
            await interaction.response.send_message(
                "ห้องนี้มีเกมอยู่แล้ว หรือสนามไม่ถูกต้อง",
                ephemeral=True
            )
            return

        stage_data = RACE_PRESET[stage_key]

        embed = discord.Embed(
            title="สนาม: " + stage_data["name"],
            description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
            color=discord.Color.green()

        )

        embed.set_thumbnail(url=stage_data["thumnail"])

        embed.add_field(name="👑 ผู้ดูแล", value=interaction.user.mention, inline=False)
        embed.add_field(name="จำนวนเทิร์น", value=f"⏱️ {stage_data['turn']}", inline=False)
        embed.add_field(
            name="🗺️ เส้นทาง",
            value=render_path(stage_data["path"]),
            inline=False
        )

        embed.set_image(
            url=stage_data["image"]
        )

        embed.add_field(
            name="📢 วิธีเล่น",
            value=(
                "กดปุ่ม Join เพื่อเข้าร่วม\n"
                "ผู้สร้างใช้กดปุ่ม Start เพื่อเริ่มเกม"
            ),
            inline=False
        )
        
        embed.set_footer(text="Game Status: Waiting for players")

        await interaction.response.send_message(
            embed=embed,
            view=LobbyView(channel_id)
        )

    async def process_next_turn(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.followup.send("ยังไม่มีเกมในห้องนี้", ephemeral=True)
            return

        new_turn = next_turn(interaction.channel_id)

        if new_turn > game["max_turn"]:
            ranked_players = get_ranked_players(interaction.channel_id)
            embed = build_game_end_embed(ranked_players)

            await interaction.followup.send(embed=embed)
            delete_game(interaction.channel_id)
            return

        phase = get_phase_from_turn(new_turn, game["max_turn"])
        ranked_players = get_ranked_players(interaction.channel_id)

        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            rank_lines.append(
                f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
            )

        if not rank_lines:
            rank_lines.append("ยังไม่มีผู้เล่น")


        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

        embed = discord.Embed(
            title=f"เข้าสู่เทิร์น {new_turn}",
            color=discord.Color.green(),
            description=(
                f"Phase: {phase}\n"
                f"เส้นทางเทิร์นนี้: {path_label}\n\n"
                f"อันดับคะแนน:\n" + "\n".join(rank_lines)
            )
        )

        embed.add_field(name="Effect", value=build_path_effect_text(path_type), inline=False)

        await interaction.followup.send(embed=embed)

    async def process_next_turn_from_timeout(self, channel: discord.TextChannel):
        game = get_game(channel.id)
        if game is None:
            return

        new_turn = next_turn(channel.id)

        # 🏁 เกมจบ
        if new_turn > game["max_turn"]:
            ranked_players = get_ranked_players(channel.id)
            embed = build_game_end_embed(ranked_players)

            await channel.send(embed=embed)
            delete_game(channel.id)
            return

        # 👉 เทิร์นถัดไป
        phase = get_phase_from_turn(new_turn, game["max_turn"])
        ranked_players = get_ranked_players(channel.id)

        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            rank_lines.append(
                f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
            )

        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

        embed = discord.Embed(
            title=f"เข้าสู่เทิร์น {new_turn} (Auto)",
            color=discord.Color.green(),
            description=(
                f"Phase: {phase}\n"
                f"เส้นทางเทิร์นนี้: {path_label}\n\n"
                f"อันดับคะแนน:\n" + "\n".join(rank_lines)
            )
        )

        embed.add_field(name="Effect", value=build_path_effect_text(path_type), inline=False)


        await channel.send(embed=embed)


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

        send_kwargs = {
            "content": f"🎯 <@{interaction.user.id}> กำลังวิ่ง!",
            "embed": payload["embed"],
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

        slots = None
        wit_mana = "ยังไม่อยู่ในเกม"

        if playerInGame:
            game_skills = playerInGame.get("skills", {})
            has_any_skill = any(game_skills.get(i) for i in (1, 2, 3))

            if has_any_skill:
                slots = {
                    "slot_1": game_skills.get(1),
                    "slot_2": game_skills.get(2),
                    "slot_3": game_skills.get(3),
                }
                wit_mana = playerInGame.get("wit_mana", 0)

        if slots is None:
            slots = get_player_skill_slots(interaction.user.id)

        if not slots:
            await interaction.response.send_message(
                "ไม่พบข้อมูลสกิลของคุณ",
                ephemeral=True
            )
            return

        def format_slot(skill_id: str | None) -> str:
            if not skill_id:
                return "➖ ว่าง"

            skill = SKILLS.get(skill_id)
            if not skill:
                return f"❓ `{skill_id}`"

            emoji = ICON.get(skill.get("icon"), "❓")

            if playerInGame:
                cd_left = get_player_skill_cd(
                    interaction.channel_id,
                    interaction.user.id,
                    skill_id
                )
                if cd_left > 0:
                    return f"{emoji} `{skill_id}` **{skill['name']}** ⏳ {cd_left}"

            return f"{emoji} `{skill_id}` **{skill['name']}** ✅"

        embed = discord.Embed(
            title=f"สกิลของ {interaction.user.display_name}",
            description=(
                f"**1** • {format_slot(slots['slot_1'])}\n"
                f"**2** • {format_slot(slots['slot_2'])}\n"
                f"**3** • {format_slot(slots['slot_3'])}\n\n"
                f"กดปุ่มด้านล่างเพื่อใช้สกิล"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name=f"{Status_Icon_Type.get('WIT', '🔮')} skill pt",
            value=f"{wit_mana}",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            view=UseSkillView(self, interaction.user.id, interaction.channel_id),
            ephemeral=True
        )
   
async def setup(bot: commands.Bot):
    await bot.add_cog(GameCog(bot))