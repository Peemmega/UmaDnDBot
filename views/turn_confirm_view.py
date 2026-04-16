import discord
from utils.game_manager import (
    get_game,
    confirm_turn,
    reset_turn_confirmations,
)

class TurnConfirmView(discord.ui.View):
    def __init__(self, cog, channel_id: int):
        super().__init__(timeout=120)
        self.cog = cog
        self.channel_id = channel_id

    @discord.ui.button(label="ยืนยัน", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ไม่พบเกมนี้แล้ว",
                ephemeral=True
            )
            return

        success, result = confirm_turn(self.channel_id, interaction.user.id)
        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        confirmed_count = result["confirmed_count"]
        total_players = result["total_players"]

        if result["all_confirmed"]:
            for item in self.children:
                item.disabled = True

            await interaction.response.edit_message(
                content=f"✅ ยืนยันครบแล้ว ({confirmed_count}/{total_players}) กำลังไปเทิร์นถัดไป",
                view=self
            )

            reset_turn_confirmations(self.channel_id)

            await interaction.followup.send("ทุกคนยืนยันครบแล้ว กำลังเข้าสู่เทิร์นถัดไป")
            await self.cog.process_next_turn(interaction)
            self.stop()
            return

        await interaction.response.send_message(
            f"ยืนยันแล้ว ({confirmed_count}/{total_players})",
            ephemeral=True
        )