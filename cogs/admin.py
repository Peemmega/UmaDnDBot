import discord
from discord.ext import commands
from utils.database import reset_all_zone_data

ADMIN_IDS = {
    464058883556769793,  # ใส่ Discord user id ของแอดมิน
}

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_user(self, user_id: int) -> bool:
        return user_id in ADMIN_IDS

    @commands.command(name="resetzoneall")
    async def reset_zone_all(self, ctx: commands.Context):
        if ctx.author.id not in ADMIN_IDS:
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        reset_all_zone_data()

        try:
            await ctx.author.send("รีเซ็ต Zone Build + Zone Points ของทุกคนแล้ว")
        except discord.Forbidden:
            await ctx.send("รีเซ็ตเสร็จแล้ว", delete_after=5)

async def setup(bot):
    await bot.add_cog(Admin(bot))