import discord
from utils.game_manager import delete_game, get_game
from utils.room_bookings import close_booking_for_room


class ConfirmDeleteView(discord.ui.View):
    """Confirm closing a game. ``refund=True`` also returns the booking quota."""

    def __init__(self, channel_id: int, *, refund: bool = False):
        super().__init__(timeout=30)
        self.channel_id = channel_id
        self.refund = refund
        if refund:
            self.confirm.label = "ยืนยันปิดและคืนโควต้า"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ไม่พบเกมนี้แล้ว",
                ephemeral=True
            )
            return False

        is_game_owner = interaction.user.id == game["owner_id"]
        is_admin = bool(
            interaction.guild
            and interaction.user.guild_permissions.administrator
        )
        if not (is_game_owner or is_admin):
            await interaction.response.send_message(
                "มีแค่ผู้สร้างเกมเท่านั้นที่ลบเกมได้",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="ยืนยันลบ", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id) or {}

        # Remove the booking first so the restore worker cannot rebuild the room.
        try:
            booking = close_booking_for_room(
                str(self.channel_id),
                game.get("booking_id"),
                refund=self.refund,
            )
        except ValueError as exc:
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(content=f"❌ {exc}", view=self)
            self.stop()
            return

        if self.refund and booking is None:
            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(
                content="❌ ห้องนี้ไม่ได้สร้างจากระบบจองห้อง จึงไม่มีโควต้าให้คืน",
                view=self
            )
            self.stop()
            return

        success = delete_game(self.channel_id)

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🛑 ลบเกมเรียบร้อยแล้ว",
            view=self
        )

        if success:
            lines = [
                f"เกมในห้องนี้ถูกปิดโดย {interaction.user.mention}",
                "ห้องถูกรีเซ็ตเรียบร้อยแล้ว",
            ]
            if booking is not None:
                lines.append("ลบห้องออกจากระบบจองแล้ว")
            if self.refund:
                lines.append("↩️ คืนโควต้า 1 ครั้งเรียบร้อยแล้ว")
            embed = discord.Embed(
                title="🛑 Game Closed",
                description="\n".join(lines),
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
