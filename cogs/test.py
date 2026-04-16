import discord
from discord.ext import commands

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="test", description="สุ่มพลังเกโหด")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("โอกุริเป็นเกรับ")

    @discord.app_commands.command(name="test2", description="ส่งข้อความ")
    async def test2(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

async def setup(bot):
    cog = GeneralCog(bot)
    await bot.add_cog(cog)