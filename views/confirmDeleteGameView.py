import discord
from utils.game_manager import delete_game, get_game


class ConfirmDeleteView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=30)
        self.channel_id = channel_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ไม่พบเกมนี้แล้ว",
                ephemeral=True
            )
            return False

        if interaction.user.id != game["owner_id"]:
            await interaction.response.send_message(
                "มีแค่ผู้สร้างเกมเท่านั้นที่ลบเกมได้",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="ยืนยันลบ", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = delete_game(self.channel_id)

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🛑 ลบเกมเรียบร้อยแล้ว",
            view=self
        )

        if success:
            embed = discord.Embed(
                title="🛑 Game Closed",
                description=(
                    f"เกมในห้องนี้ถูกปิดโดย {interaction.user.mention}\n"
                    f"ห้องถูกรีเซ็ตเรียบร้อยแล้ว"
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

        self.stop()

    @discord.ui.button(label="ยกเลิก", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="ยกเลิกการลบเกม",
            view=self
        )

        self.stop()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True