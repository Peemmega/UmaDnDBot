import discord
from utils.game_manager import (
    get_game,
    get_player_in_game,
    use_reroll,
    can_use_wit_reroll,
)
from utils.dice.reroll_service import execute_reroll

class RunRerollView(discord.ui.View):
    def __init__(self, owner_id: int, channel_id: int, old_total: int, base_total: int, wit_reroll_ok: bool):
        super().__init__(timeout=40)
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.old_total = old_total
        self.base_total = base_total
        self.wit_reroll_ok = wit_reroll_ok

        self.refresh_button_states()

    def refresh_button_states(self):
        game_player = get_player_in_game(self.channel_id, self.owner_id)

        normal_left = 0
        wit_left = 0

        if game_player:
            normal_left = game_player.get("reroll_left", 0)
            wit_left = game_player.get("wit_reroll_left", 0)

        for item in self.children:
            if not isinstance(item, discord.ui.Button):
                continue

            if item.label == "สุ่มใหม่":
                item.disabled = normal_left <= 0

            elif item.label == "WIT Reroll":
                item.disabled = (not self.wit_reroll_ok) or (wit_left <= 0)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("ปุ่มนี้ไม่ใช่ของคุณ", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="สุ่มใหม่", style=discord.ButtonStyle.primary, emoji="🎲")
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, reroll_left = use_reroll(self.channel_id, self.owner_id)
        if not success:
            await interaction.response.send_message(reroll_left, ephemeral=True)
            return

        success, payload = await execute_reroll(
            interaction,
            old_total=self.old_total,
            title_prefix="สุ่มใหม่สำเร็จ",
        )
        if not success:
            await interaction.response.send_message(payload["message"], ephemeral=True)
            return

        self.old_total = payload["result"]["total"]
        self.base_total = payload["result"]["base_total"]

        game_player = get_player_in_game(self.channel_id, self.owner_id)
        if game_player:
            self.wit_reroll_ok = can_use_wit_reroll(game_player, self.base_total)

        self.refresh_button_states()

        await interaction.response.edit_message(embed=payload["embed"], view=self)

    @discord.ui.button(label="WIT Reroll", style=discord.ButtonStyle.success, emoji="🔮")
    async def wit_reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message("ไม่พบเกมนี้แล้ว", ephemeral=True)
            return

        game_player = get_player_in_game(self.channel_id, self.owner_id)
        if game_player is None:
            await interaction.response.send_message("ไม่พบผู้เล่นในเกม", ephemeral=True)
            return

        if not can_use_wit_reroll(game_player, self.base_total):
            await interaction.response.send_message("ไม่เข้าเงื่อนไข WIT Reroll", ephemeral=True)
            return

        if game_player.get("wit_reroll_left", 0) <= 0:
            await interaction.response.send_message("WIT Reroll หมดแล้ว", ephemeral=True)
            return

        game_player["wit_reroll_left"] -= 1

        success, payload = await execute_reroll(
            interaction,
            old_total=self.old_total,
            title_prefix="WIT Reroll สำเร็จ",
        )
        if not success:
            game_player["wit_reroll_left"] += 1
            await interaction.response.send_message(payload["message"], ephemeral=True)
            return

        self.old_total = payload["result"]["total"]
        self.base_total = payload["result"]["base_total"]

        self.wit_reroll_ok = can_use_wit_reroll(game_player, self.base_total)

        self.refresh_button_states()

        await interaction.response.edit_message(embed=payload["embed"], view=self)

    # @discord.ui.button(label="ปิด", style=discord.ButtonStyle.secondary)
    # async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     for item in self.children:
    #         if isinstance(item, discord.ui.Button):
    #             item.disabled = True

    #     await interaction.response.edit_message(view=self)
    #     self.stop()