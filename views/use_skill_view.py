import discord
from utils.game_manager import (
    get_game,execute_skill_core
)

from utils.zone.zone_manager import apply_zone_in_game
from utils.zone.zone_embed import build_zone_used_preview_embed

class UseSkillView(discord.ui.View):
    def __init__(self, cog, owner_id: int, channel_id: int):
        super().__init__(timeout=60)
        self.cog = cog
        self.owner_id = owner_id
        self.channel_id = channel_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "เมนูนี้เป็นของคุณคนเดียว",
                ephemeral=True
            )
            return False
        return True
    
    async def use_slot(self, interaction: discord.Interaction, slot: int):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message("ไม่พบเกม", ephemeral=True)
            return

        player = game["players"].get(interaction.user.id)
        if player is None:
            await interaction.response.send_message("ไม่พบผู้เล่น", ephemeral=True)
            return

        skills = player.get("skills")
        if not skills:
            await interaction.response.send_message(
                "ยังไม่มีข้อมูลสกิลในเกมนี้ กรุณาเริ่มเกมใหม่อีกครั้ง",
                ephemeral=True
            )
            return

        skill_id = skills.get(slot)
        if not skill_id:
            await interaction.response.send_message(f"Slot {slot} ว่าง", ephemeral=True)
            return

        success, payload = execute_skill_core(
            self.channel_id,
            interaction.user.id,
            skill_id,
        )

        if not success:
            await interaction.response.send_message(
                payload["message"],
                ephemeral=True
            )
            return

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def slot1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def slot2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def slot3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 3)

    @discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def slot4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 4)

    @discord.ui.button(label="Zone", style=discord.ButtonStyle.success, emoji="🌌")
    async def use_zone_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message("ไม่พบเกม", ephemeral=True)
            return

        player = game["players"].get(interaction.user.id)
        if player is None:
            await interaction.response.send_message("ไม่พบผู้เล่น", ephemeral=True)
            return

        if player.get("zone_left", 0) <= 0:
            await interaction.response.send_message("Zone ถูกใช้ไปแล้ว", ephemeral=True)
            return

        success, result_text = apply_zone_in_game(game, player)
        if not success:
            await interaction.response.send_message(result_text, ephemeral=True)
            return
    
        embed = build_zone_used_preview_embed(player)

        await interaction.response.send_message(embed=embed, ephemeral=False)