import discord
from discord.ext import commands
from discord import app_commands

from utils.music_manager import join_user_voice, leave_voice, play_bgm, stop_bgm


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="music_play", description="เล่นเพลงในห้องเสียง")
    @app_commands.choices(
        music=[
            app_commands.Choice(name="Last Spurt", value="lastspurt"),
            app_commands.Choice(name="Arima Kinen", value="arima_kinen"),
            app_commands.Choice(name="G1 Race", value="g1_race"),
            app_commands.Choice(name="Girl Legend U", value="girl_legend_u"),
            app_commands.Choice(name="L'Arc", value="l_arc"),
            app_commands.Choice(name="Glorious Moment", value="glorious_moment"),
            app_commands.Choice(name="Cingrey OST", value="cingrey_ost_01"),
            app_commands.Choice(name="Japan cup Special week", value="SpecialWeekAura"),
        ]
    )
    async def music_play(
        self,
        interaction: discord.Interaction,
        music: app_commands.Choice[str]
    ):
        await interaction.response.defer(ephemeral=True)

        ok, msg = await join_user_voice(interaction)
        if not ok:
            await interaction.followup.send(msg, ephemeral=True)
            return

        ok, msg = play_bgm(interaction.guild, music.value)
        await interaction.followup.send(msg, ephemeral=True)

    # @app_commands.command(name="joinvc", description="ให้บอทเข้าห้องเสียงของคุณ")
    # async def joinvc(self, interaction: discord.Interaction):
    #     ok, msg = await join_user_voice(interaction)
    #     await interaction.response.send_message(msg, ephemeral=True)

    # @app_commands.command(name="leavevc", description="ให้บอทออกจากห้องเสียง")
    # async def leavevc(self, interaction: discord.Interaction):
    #     ok, msg = await leave_voice(interaction.guild)
    #     await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="music_stop", description="หยุดเพลง")
    async def music_stop(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        ok, msg = stop_bgm(interaction.guild)
        ok, msg = await leave_voice(interaction.guild)
        await interaction.followup.send(msg, ephemeral=True)    


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))