import discord
from utils.game_manager import (
    get_game,
    confirm_turn,
    format_player_reference,
    use_block,
    use_rush,
    reset_turn_confirmations,
    process_mob_turn,
)

class TurnConfirmView(discord.ui.View):
    def __init__(self, cog, channel_id: int):
        super().__init__(timeout=30)
        self.cog = cog
        self.channel_id = channel_id
        self.message = None
        game = get_game(channel_id)
        self.turn = game.get("turn") if game else None
        self.confirmation_token = (
            game.get("turn_confirmation_token") if game else None
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        game = get_game(self.channel_id)
        if (
            game is None
            or game.get("turn") != self.turn
            or not game.get("awaiting_turn_confirm")
            or game.get("turn_confirmation_turn") != self.turn
            or game.get("turn_confirmation_token") != self.confirmation_token
        ):
            await interaction.response.send_message(
                "ปุ่มของเทิร์นนี้หมดอายุแล้ว",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        game = get_game(self.channel_id)
        if game is None:
            return

        if (
            game.get("turn") != self.turn
            or not game.get("awaiting_turn_confirm")
            or game.get("turn_confirmation_turn") != self.turn
            or game.get("turn_confirmation_token") != self.confirmation_token
        ):
            return

        channel = self.cog.bot.get_channel(self.channel_id)
        if channel is None:
            return

        players = game.get("players", {})

        # Retry pending Mob turns once before deciding that this turn is not
        # ready. A Mob failure must stall safely; it must never be treated as
        # an optional participant by the timeout path.
        for user_id, player in players.items():
            if player.get("is_mob") and player.get("last_roll_turn") != game.get("turn"):
                success, payload = process_mob_turn(self.channel_id, user_id)
                if not success:
                    print(f"Mob turn retry failed for {user_id}: {payload.get('message', payload)}")

        not_rolled_players = []

        for user_id, player in players.items():
            if player.get("last_roll_turn") != game.get("turn"):
                not_rolled_players.append(player)
                
        if not_rolled_players:
            names = []

            for p in not_rolled_players:
                name = (
                    p.get("display_name")
                    or p.get("name")
                    or p.get("username")
                    or "Unknown Player"
                )
                names.append(name)

            await channel.send(
                "⏳ หมดเวลายืนยันแล้ว แต่ยังมีผู้เล่นที่ยังไม่ได้ทอย\n"
                "ยังไม่ข้ามเทิร์นอัตโนมัติ\n\n"
                + "\n".join(f"• {name}" for name in names)
            )

            reset_turn_confirmations(self.channel_id)
            return

        # =========================
        # ทุกคนทอยแล้ว → ข้ามเทิร์นได้
        # =========================
        advanced = await self.cog.process_next_turn_from_timeout(
            channel,
            expected_turn=self.turn,
            confirmation_token=self.confirmation_token,
        )
        if not advanced:
            return

        if self.message:
            try:
                await self.message.delete()
            except:
                pass

        await channel.send("⏳ หมดเวลา ยืนยันไม่ครบ แต่ทุกคนทอยแล้ว → ข้ามเทิร์นอัตโนมัติ")

    @discord.ui.button(label="ยืนยัน", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ไม่พบเกมนี้แล้ว",
                ephemeral=True
            )
            return

        success, result = confirm_turn(
            self.channel_id,
            interaction.user.id,
            expected_turn=self.turn,
            confirmation_token=self.confirmation_token,
        )
        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        confirmed_count = result["confirmed_count"]
        total_players = result["total_players"]

        if result["all_confirmed"]:
            for item in self.children:
                item.disabled = True

            # Stop the timeout before the Discord edit yields control.
            self.stop()

            await interaction.response.edit_message(
                content=f"✅ ยืนยันครบแล้ว ({confirmed_count}/{total_players})",
                view=self
            )

            # 🔥 ลบ message เก่า
            if self.message:
                await self.message.delete()

            await self.cog.process_next_turn(
                interaction,
                expected_turn=self.turn,
                confirmation_token=self.confirmation_token,
            )
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
            f"ใช้ Block ใส่ {format_player_reference(result['target_id'], result.get('target'))} สำเร็จ\n"
            f"ถอยหลัง {result['move_back']} แต้ม",
        )
    @discord.ui.button(label="Rush", style=discord.ButtonStyle.primary, emoji="⚡")
    async def rush_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, result = use_rush(self.channel_id, interaction.user.id)
        if not success:
            await interaction.response.send_message(result, ephemeral=True)
            return

        await interaction.response.send_message(
            f"ใช้ Rush สำเร็จ\n"
            f"ขยับไป {result['move_forward']} แต้ม และใช้ STA {result['stamina_cost']}",
         )     
