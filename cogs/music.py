import discord
from discord.ext import commands
from discord import app_commands

from utils.music_manager import join_user_voice, leave_voice


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="joinvc", description="ให้บอทเข้าห้องเสียงของคุณ")
    async def joinvc(self, interaction: discord.Interaction):
        ok, msg = await join_user_voice(interaction)
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="leavevc", description="ให้บอทออกจากห้องเสียง")
    async def leavevc(self, interaction: discord.Interaction):
        ok, msg = await leave_voice(interaction.guild)
        await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))