import discord
from discord.ext import commands
from utils.dice.dice_presets import DICE_PRESET, MAX_DICE_VALUE
from utils.race.race_dice import (
    build_dice_table_grid
)

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="dice_table", description="ดูตารางเต๋า")
    async def dice_table(self, interaction: discord.Interaction):

        white_text = build_dice_table_grid(DICE_PRESET, "White")
        gold_text = build_dice_table_grid(DICE_PRESET, "Gold")

        embed = discord.Embed(
            title="🎲 Dice Table",
            description="ตารางการทอยเต๋าตาม Style และ Phase",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="⚪ White Roll",
            value=f"```{white_text}```",
            inline=False
        )

        embed.add_field(
            name="🟡 Gold Roll",
            value=f"```{gold_text}```",
            inline=False
        )

        embed.add_field(
            name="📘 คำอธิบาย",
            value=(
                f"d = สุ่มค่า 1 ถึง {MAX_DICE_VALUE} ต่อ 1 ลูกเต๋า\n"
                "kh = เลือกค่าที่มากที่สุดตามจำนวน"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    cog = GeneralCog(bot)
    await bot.add_cog(cog)