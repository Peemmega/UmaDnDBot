import discord
from discord.ext import commands
import io

from utils.database import ensure_player, update_player_username
from views.profile_stat_view import ProfileStatView, build_stat_embed
from utils.player_card import create_stats_card
from utils.icon_presets import STAT_EMOJIS, Status_Icon_Type

def get_stat_emoji(value: int) -> str:
    value = max(1, min(value, 8))
    return STAT_EMOJIS[value]

def get_stat_icon(value: str) -> str:
    return Status_Icon_Type[value]


class OpenStatMenuView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "มีแค่เจ้าของโปรไฟล์เท่านั้นที่ใช้ปุ่มนี้ได้",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="เพิ่ม Stats", style=discord.ButtonStyle.success, emoji="📈")
    async def open_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = ensure_player(interaction.user.id, interaction.user.name)
        embed = build_stat_embed(interaction.user, player, "จัดการค่าสเตตัส")

        view = ProfileStatView(interaction.user.id,player)
        view.refresh_button_state(player)

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="profile_card", description="สร้างการ์ดโปรไฟล์เป็นรูป")
    async def profile_card(self, interaction: discord.Interaction):
        await interaction.response.defer()

        player = ensure_player(interaction.user.id, interaction.user.name)
        avatar_url = interaction.user.display_avatar.url

        image = await create_stats_card(player, avatar_url)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(fp=buffer, filename="profile_card.png")
        await interaction.followup.send(
            file=file,
            view=OpenStatMenuView(interaction.user.id),
            ephemeral=True
        )      

    @discord.app_commands.command(name="set_name", description="เปลี่ยนชื่อโปรไฟล์")
    async def setname(self, interaction: discord.Interaction, new_name: str):
        if len(new_name.strip()) == 0:
            await interaction.response.send_message(
                "ชื่อห้ามว่าง",
                ephemeral=True
            )
            return

        if len(new_name) > 30:
            await interaction.response.send_message(
                "ชื่อต้องไม่เกิน 30 ตัวอักษร",
                ephemeral=True
            )
            return

        update_player_username(interaction.user.id, new_name.strip())

        await interaction.response.send_message(
            f"เปลี่ยนชื่อโปรไฟล์เป็น **{new_name.strip()}** เรียบร้อยแล้ว"
        )



    # @discord.app_commands.command(name="profile", description="ดูข้อมูลผู้เล่น")
    # async def profile(self, interaction: discord.Interaction):
    #     player = ensure_player(interaction.user.id, interaction.user.name)

    #     embed = discord.Embed(
    #         title=f"โปรไฟล์ของ {player['username']}",
    #         color=discord.Color.green()
    #     )

    #     embed.set_thumbnail(url=interaction.user.display_avatar.url)

    #     embed.set_author(
    #         name="Profile",
    #         icon_url="https://media.discordapp.net/attachments/697810514448744448/1493591350535389194/utx_ico_directory_01.png"
    #     )

    #     embed.add_field(
    #         name="ค่าสเตตัส",
    #         value=(
    #             f"{get_stat_icon('SPD')} : {get_stat_emoji(player['speed'])}   "
    #             f"{get_stat_icon('STA')} : {get_stat_emoji(player['stamina'])}   "
    #             f"{get_stat_icon('POW')} : {get_stat_emoji(player['power'])}   "
    #             f"{get_stat_icon('GUT')} : {get_stat_emoji(player['gut'])}   "
    #             f"{get_stat_icon('WIT')} : {get_stat_emoji(player['wit'])}\n"
    #             f"🗺️    "
    #             f"**Turf** : {get_stat_emoji(player['turf'])}   "
    #             f"**Dirt** : {get_stat_emoji(player['dirt'])}\n"
    #             f"📏    "
    #             f"**Sprint** : {get_stat_emoji(player['sprint'])}   "
    #             f"**Mile** : {get_stat_emoji(player['mile'])}   "
    #             f"**Medium** : {get_stat_emoji(player['medium'])}   "
    #             f"**Long** : {get_stat_emoji(player['long'])}\n"
    #             f"🏇    "
    #             f"**Front** : {get_stat_emoji(player['front'])}   "
    #             f"**Pace** : {get_stat_emoji(player['pace'])}   "
    #             f"**Late** : {get_stat_emoji(player['late'])}   "
    #             f"**End** : {get_stat_emoji(player['end_style'])}"
    #         ),
    #         inline=False
    #     )

    #     embed.add_field(
    #         name="ETC",
    #         value=(
    #             f"**Uma Coin** : {player['uma_coin']}\n"
    #             f"**Stats Point** : {player['stats_point']}   "
    #             f"**Skill Point** : {player['skill_point']}"
    #         ),
    #         inline=False
    #     )

    #     embed.set_footer(text="Eclipse first, the rest nowhere")

    #     await interaction.response.send_message(
    #         embed=embed,
    #         view=OpenStatMenuView(interaction.user.id)
    #     )


async def setup(bot):
    await bot.add_cog(ProfileCog(bot))