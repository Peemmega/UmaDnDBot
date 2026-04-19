import discord

from utils.zone.zone_manager import (
    upgrade_zone_stat,
    downgrade_zone_stat,
)
from utils.zone.zone_embed import build_zone_manage_embed

ZONE_OPTIONS = [
    discord.SelectOption(label="Flat Total", value="flat", description="เพิ่มผลรวมโดยตรง"),
    discord.SelectOption(label="Add Dice", value="add_d", description="เพิ่มจำนวนลูกเต๋า"),
    discord.SelectOption(label="Keep High", value="add_kh", description="เพิ่มจำนวนลูกที่เลือก"),
    discord.SelectOption(label="Floor", value="floor", description="เพิ่มแต้มขั้นต่ำ"),
    discord.SelectOption(label="Selected Die", value="selected_die", description="เพิ่มแต้มลูกที่เลือก"),
    discord.SelectOption(label="Cap", value="cap", description="เพิ่มแต้มสูงสุด"),
]


class ZoneFieldSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="เลือกค่าสำหรับอัป Zone",
            min_values=1,
            max_values=1,
            options=ZONE_OPTIONS
        )

    async def callback(self, interaction: discord.Interaction):
        view: ZoneManageView = self.view
        view.selected_field = self.values[0]

        embed = build_zone_manage_embed(view.user_id, interaction.user.display_name)
        embed.add_field(
            name="เลือกอยู่ตอนนี้",
            value=f"`{view.selected_field}`",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=view)


class ZoneManageView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.selected_field = "flat"
        self.add_item(ZoneFieldSelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("ปุ่มนี้ไม่ใช่ของคุณ", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="➕ เพิ่ม", style=discord.ButtonStyle.success)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, msg = upgrade_zone_stat(self.user_id, self.selected_field, 1)
        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        embed = build_zone_manage_embed(self.user_id, interaction.user.display_name)
        embed.add_field(name="ผลล่าสุด", value=msg, inline=False)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="➖ ลด", style=discord.ButtonStyle.danger)
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, msg = downgrade_zone_stat(self.user_id, self.selected_field, 1)
        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        embed = build_zone_manage_embed(self.user_id, interaction.user.display_name)
        embed.add_field(name="ผลล่าสุด", value=msg, inline=False)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="ปิด", style=discord.ButtonStyle.secondary)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        embed = build_zone_manage_embed(self.user_id, interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()