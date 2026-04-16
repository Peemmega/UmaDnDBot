import discord
from discord.ext import commands
from discord import app_commands

from views.run_reroll_view import RunRerollView
from views.confirmDeleteGameView import ConfirmDeleteView
from views.join_view import LobbyView
from utils.database import ensure_player
from utils.dice_presets import DICE_PRESET
from utils.race_presets import RACE_PRESET

from utils.race_dice import (
    roll_race_dice,
    get_phase_from_turn,
    build_dice_table_text
)

from utils.game_manager import (
    create_game,
    get_game,
    is_owner,
    next_turn,
    get_player_in_game,
    get_players,
    delete_game,
    update_player_score,
    can_player_roll, 
    mark_player_rolled,
    get_ranked_players,
    have_all_players_rolled,
    start_turn_confirmation,
)

PATH_EMOJI = {
    1: "➡️",  # ทางตรง
    2: "⤵️",  # โค้ง
    3: "↗️",  # เนินขึ้น
    4: "↘️",  # เนินลง
}

def render_path(path: list[int]) -> str:
    return "".join(PATH_EMOJI.get(x, "⬜") for x in path)


async def process_next_turn(self, interaction: discord.Interaction):
    game = get_game(interaction.channel_id)
    if game is None:
        await interaction.followup.send("ยังไม่มีเกมในห้องนี้", ephemeral=True)
        return

    new_turn = next_turn(interaction.channel_id)

    if new_turn > game["max_turn"]:
        ranked_players = get_ranked_players(interaction.channel_id)

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

    embed = discord.Embed(
        title=f"เข้าสู่เทิร์น {new_turn}",
        color=discord.Color.green(),
        description=(
            f"Phase: {phase}\n\n"
            f"อันดับคะแนน:\n" + "\n".join(rank_lines)
        )
    )

    await interaction.followup.send(embed=embed)

class GameCog(commands.GroupCog, name="game"):
    def __init__(self, bot):
        self.bot = bot

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
            title="📍Race: " + stage_data["name"],
            description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=stage_data["thumnail"])

        embed.add_field(name="👑 ผู้ดูแล", value=interaction.user.mention, inline=False)
        embed.add_field(name="จำนวนเทิร์น", value= f"⏱️ {stage_data["turn"]}", inline=False)

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

        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.followup.send(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return

        game_player = get_player_in_game(interaction.channel_id, interaction.user.id)
        if game_player is None:
            await interaction.followup.send(
                "คุณยังไม่ได้เข้าร่วมเกมนี้",
                ephemeral=True
            )
            return

        db_player = ensure_player(interaction.user.id, interaction.user.name)

        can_roll, message = can_player_roll(interaction.channel_id, interaction.user.id)
        if not can_roll:
            await interaction.followup.send(message, ephemeral=True)
            return

        snapshot_scores = game["turn_snapshot_scores"]

        # 🎲 roll
        result = roll_race_dice(
            style=game_player["style"],
            player=db_player,
            player_id=interaction.user.id,
            score_map=snapshot_scores,
            turn=game["turn"],
            max_turn=game["max_turn"]
        )

        # 💨 STAMINA SYSTEM
        stamina_note = None
        if game["turn"] > 8:
            if game_player["stamina_left"] > 0:
                game_player["stamina_left"] -= 1
                stamina_note = f"STA -1 เหลือ {game_player['stamina_left']}"
            else:
                result["total"] -= 30
                result["total_display"] += " -30 STA"
                stamina_note = "STA หมด: โดนหัก 30"

        # 🏁 update score
        success, new_score = update_player_score(
            interaction.channel_id,
            interaction.user.id,
            result["total"]
        )

        if not success:
            await interaction.followup.send(
                "ไม่สามารถอัปเดตคะแนนได้",
                ephemeral=True
            )
            return

        # mark ว่ากดแล้ว
        mark_player_rolled(interaction.channel_id, interaction.user.id)

        # 📊 embed แสดงผล
        embed = discord.Embed(
            title=f"{interaction.user.display_name} วิ่งในเทิร์นนี้",
            color=discord.Color.gold()
        )

        embed.add_field(name="Style", value=game_player["style"], inline=True)
        embed.add_field(name="Phase", value=result["phase"], inline=True)
        embed.add_field(name="Distance", value=result["distance_color"], inline=True)

        embed.add_field(name="🎲 Dice", value=result["display"], inline=False)
        embed.add_field(name="✨ Total", value=result["total_display"], inline=True)
        embed.add_field(name="🏁 Score ใหม่", value=new_score, inline=True)

        embed.add_field(name="STA คงเหลือ", value=game_player["stamina_left"], inline=True)
        embed.set_footer(text=f"Reroll คงเหลือ {game_player['reroll_left']}")

        if stamina_note:
            embed.add_field(name="Stamina Effect", value=stamina_note, inline=False)

        # 🎯 reroll view
        view = RunRerollView(
            owner_id=interaction.user.id,
            channel_id=interaction.channel_id,
            old_total=result["total"],
        )

        await interaction.followup.send(
            content=f"🎯 <@{interaction.user.id}> กำลังวิ่ง!",
            embed=embed,
            view=view
        )

        # ===============================
        # 🔥 ถ้าทุกคน roll ครบ → เปิด confirm
        # ===============================
        if have_all_players_rolled(interaction.channel_id):

            if not game["awaiting_turn_confirm"]:
                start_turn_confirmation(interaction.channel_id)

                ranked_players = get_ranked_players(interaction.channel_id)
                phase = get_phase_from_turn(game["turn"], game["max_turn"])

                rank_lines = []
                for index, (user_id, info) in enumerate(ranked_players, start=1):
                    rank_lines.append(
                        f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
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

                confirm_embed.set_footer(
                    text="ทุกคนต้องกดยืนยันก่อนจะไปเทิร์นถัดไป"
                )

                from views.turn_confirm_view import TurnConfirmView

                await interaction.followup.send(
                    embed=confirm_embed,
                    view=TurnConfirmView(self, interaction.channel_id)
                )

    @app_commands.command(name="next_turn", description="ไปเทิร์นถัดไป")
    async def next_turn_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.followup.send("ยังไม่มีเกมในห้องนี้", ephemeral=True)
            return

        if not game["started"]:
            await interaction.followup.send("เกมยังไม่เริ่ม", ephemeral=True)
            return

        if not is_owner(interaction.channel_id, interaction.user.id):
            await interaction.followup.send(
                "มีแค่ผู้สร้างเกมเท่านั้นที่ใช้คำสั่งนี้ได้",
                ephemeral=True
            )
            return

        await self.process_next_turn(interaction)

    @discord.app_commands.command(name="dice_table", description="ดูตารางเต๋า")
    async def dice_table(self, interaction: discord.Interaction):
        table_text = build_dice_table_text(DICE_PRESET)

        await interaction.response.send_message(
            f"```markdown\n{table_text}\n```"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(GameCog(bot))