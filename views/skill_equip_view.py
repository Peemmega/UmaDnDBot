import discord

class SkillEquipView(discord.ui.View):
    def __init__(self, skill_id: str, equip_callback):
        super().__init__(timeout=120)
        self.skill_id = skill_id
        self.equip_callback = equip_callback

    @discord.ui.button(label="ติดตั้ง Slot 1", style=discord.ButtonStyle.primary)
    async def equip_slot_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.equip_callback(interaction, slot=1, skill_id=self.skill_id)

    @discord.ui.button(label="ติดตั้ง Slot 2", style=discord.ButtonStyle.primary)
    async def equip_slot_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.equip_callback(interaction, slot=2, skill_id=self.skill_id)

    @discord.ui.button(label="ติดตั้ง Slot 3", style=discord.ButtonStyle.primary)
    async def equip_slot_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.equip_callback(interaction, slot=3, skill_id=self.skill_id)