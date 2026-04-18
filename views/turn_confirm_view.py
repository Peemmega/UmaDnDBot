import discord
from utils.game_manager import (
    get_game,
    confirm_turn,
    use_block,
    use_rush,
    reset_turn_confirmations,
)

class TurnConfirmView(discord.ui.View):
    def __init__(self, cog, channel_id: int):
        super().__init__(timeout=30)
        self.cog = cog
        self.channel_id = channel_id
        self.message = None

    async def on_timeout(self):
        game = get_game(self.channel_id)
        if game is None:
            return

        reset_turn_confirmations(self.channel_id)

        channel = self.cog.bot.get_channel(self.channel_id)
        if channel is None:
            return

        if self.message:
            try:
                await self.message.delete()
            except:
                pass

        await channel.send("⏳ หมดเวลา ยืนยันไม่ครบ → ข้ามเทิร์นอัตโนมัติ")

        await self.cog.process_next_turn_from_timeout(channel)

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
                content=f"✅ ยืนยันครบแล้ว ({confirmed_count}/{total_players})",
                view=self
            )

            reset_turn_confirmations(self.channel_id)

            # 🔥 ลบ message เก่า
            if self.message:
                await self.message.delete()

            await self.cog.process_next_turn(interaction)
            self.stop()
            return

        await interaction.response.send_message(
            f"ยืนยันแล้ว ({confirmed_count}/{total_players})",
            ephemeral=True
        )

    @discord.ui.button(label="Block", style=discord.ButtonStyle.danger, emoji="🛡️")
    async def block_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, result = use_block(self.channel_id, interaction.user.id)
        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await interaction.response.send_message(
            f"ใช้ Block ใส่ <@{result['target_id']}> สำเร็จ\n"
            f"ถอยหลัง {result['move_back']} แต้ม",
        )
    @discord.ui.button(label="Rush", style=discord.ButtonStyle.primary, emoji="⚡")
    async def rush_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, result = use_rush(self.channel_id, interaction.user.id)
        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await interaction.response.send_message(
            f"ใช้ Rush เข้าหา <@{result['target_id']}> สำเร็จ\n"
            f"ขยับไป {result['move_forward']} แต้ม",
         )     