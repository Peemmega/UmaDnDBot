import discord
from discord.ext import commands
from views.action_view import ActionView
from utils.database import ensure_player

class ActionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="action", description="เลือกแอคชั่น")
    async def action(self, interaction: discord.Interaction):
        await interaction.response.send_message("เลือกแอคชั่น", view=ActionView())

async def setup(bot):
    cog = ActionCog(bot)
    await bot.add_cog(cog)