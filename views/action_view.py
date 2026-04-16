import discord

class ActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Test", style=discord.ButtonStyle.grey, emoji="👟")
    async def run_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("วิ่งไปหาคนถาม")

    @discord.ui.button(label="Test 2", style=discord.ButtonStyle.grey, emoji="❤️")
    async def love_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("โอกุริเกรับทั้งใจ")

    @discord.ui.button(label="Test 3", style=discord.ButtonStyle.grey, emoji="💪")
    async def pose_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("โอกุริเกรับทำฟอม")