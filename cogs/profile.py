import discord
from discord.ext import commands
import io

from utils.database import ensure_player, update_player_username,set_player_zone_name,set_player_zone_image_url,set_all_aptitude
from views.profile_stat_view import ProfileStatView, build_stat_embed
from utils.player_card import create_stats_card
from utils.icon_presets import STAT_EMOJIS, Status_Icon_Type, GRADE_TEXT
from views.zone_manage_view import ZoneManageView
from utils.zone.zone_embed import build_zone_manage_embed, build_zone_used_preview_embed

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


    @discord.ui.button(label="Zone Manager", emoji="🌌", style=discord.ButtonStyle.primary)
    async def open_zone_manager(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_zone_manage_embed(
            self.user_id,
            interaction.user.display_name
        )

        await interaction.response.send_message(
            embed=embed,
            view=ZoneManageView(self.user_id),
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

    @discord.app_commands.command(name="zone_manage", description="เปิดหน้าอัป Zone")
    async def zone_manage(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ensure_player(interaction.user.id, interaction.user.name)

        embed = build_zone_manage_embed(
            interaction.user.id,
            interaction.user.display_name
        )

        await interaction.followup.send(
            embed=embed,
            view=ZoneManageView(interaction.user.id),
            ephemeral=True
        )

        

    @discord.app_commands.command(name="zone_preview", description="ดูตัวอย่างผลของ Zone")
    async def zone_preview_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = ensure_player(interaction.user.id, interaction.user.name)

        embed = build_zone_used_preview_embed(player)
        embed.set_footer(
            text="สำหรับโชว์ผลลัพท์เท่านั้น สำหรับโชว์ผลลัพท์เท่านั้น สำหรับโชว์ผลลัพท์เท่านั้น"
        )
        await interaction.followup.send(embed=embed, ephemeral=False)

    @discord.app_commands.command(name="zone_set", description="ตั้งค่า Zone (ชื่อ / รูป)")
    @discord.app_commands.describe(
        mode="เลือกว่าจะตั้งชื่อหรือรูป",
        value="ชื่อ Zone หรือ URL ของรูป"
    )
    @discord.app_commands.choices(mode=[
        discord.app_commands.Choice(name="ตั้งชื่อ", value="name"),
        discord.app_commands.Choice(name="ตั้งรูป", value="image"),
    ])
    async def zone_set(
        self,
        interaction: discord.Interaction,
        mode: discord.app_commands.Choice[str],
        value: str
    ):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        ensure_player(user_id, interaction.user.name)

        if mode.value == "name":
            if len(value) > 50:
                await interaction.followup.send(
                    "ชื่อ Zone ยาวเกินไป (ไม่เกิน 50 ตัวอักษร)",
                    ephemeral=True
                )
                return

            set_player_zone_name(user_id, value)

            await interaction.followup.send(
                f"✅ ตั้งชื่อ Zone เป็น **{value}** สำเร็จ",
                ephemeral=True
            )
            return

        if mode.value == "image":
            # เช็คง่าย ๆ ว่าเป็น URL ไหม
            if not (value.startswith("http://") or value.startswith("https://")):
                await interaction.followup.send(
                    "กรุณาใส่ URL ที่ถูกต้อง",
                    ephemeral=True
                )
                return

            set_player_zone_image_url(user_id, value)

            embed = discord.Embed(
                title="🌌 ตั้งค่า Zone Image สำเร็จ",
                description="ภาพ Zone ถูกเปลี่ยนแล้ว",
                color=discord.Color.purple()
            )
            embed.set_image(url=value)

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

    @discord.app_commands.command(name="set_name", description="เปลี่ยนชื่อโปรไฟล์")
    async def setname(self, interaction: discord.Interaction, new_name: str):
        await interaction.response.defer(ephemeral=True)
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

        update_player_username(str(interaction.user.id), new_name.strip())

        await interaction.followup.send(
            f"เปลี่ยนชื่อโปรไฟล์เป็น **{new_name.strip()}** เรียบร้อยแล้ว",
            ephemeral=True
        )


    @discord.app_commands.command(name="set_all_att", description="ตั้งค่า aptitude ทั้งหมด (สำหรับทดสอบ)")
    @discord.app_commands.describe(value="ระดับ 1-8")
    @discord.app_commands.choices(value=[
        discord.app_commands.Choice(name="1", value=1),
        discord.app_commands.Choice(name="2", value=2),
        discord.app_commands.Choice(name="3", value=3),
        discord.app_commands.Choice(name="4", value=4),
        discord.app_commands.Choice(name="5", value=5),
        discord.app_commands.Choice(name="6", value=6),
        discord.app_commands.Choice(name="7", value=7),
        discord.app_commands.Choice(name="8", value=8),
    ])
    async def set_all_att(self, interaction: discord.Interaction, value: discord.app_commands.Choice[int]):
        await interaction.response.defer(ephemeral=True)
        ensure_player(interaction.user.id, interaction.user.name)

        set_all_aptitude(interaction.user.id, value.value)

        grade = GRADE_TEXT.get(value.value, str(value.value))

        await interaction.followup.send(
            f"📊 ตั้งค่า Aptitude ทั้งหมดเป็นระดับ {grade} ({value.value})",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ProfileCog(bot))