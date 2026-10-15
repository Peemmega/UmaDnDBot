from types import SimpleNamespace

import discord
from discord.ext import commands

from utils.music_manager import (
    get_music_choices,
    join_user_voice,
    leave_voice,
    play_bgm,
    stop_bgm,
)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _is_server_admin(self, ctx: commands.Context) -> bool:
        return bool(ctx.guild and ctx.author.guild_permissions.administrator)

    @commands.group(name="music", invoke_without_command=True)
    async def music_group(self, ctx: commands.Context):
        await ctx.send("ใช้ `!music play <music_key>` หรือ `!music stop`")

    @music_group.command(name="play")
    async def music_play(self, ctx: commands.Context, music_key: str):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return

        matching_key = next(
            (key for key in get_music_choices() if key.lower() == music_key.lower()),
            None,
        )
        if matching_key is None:
            await ctx.send("ไม่พบเพลง ใช้ key เหล่านี้ได้: `" + "`, `".join(get_music_choices()) + "`")
            return

        adapter = SimpleNamespace(guild=ctx.guild, user=ctx.author)
        ok, message = await join_user_voice(adapter)
        if not ok:
            await ctx.send(message)
            return

        ok, message = play_bgm(ctx.guild, matching_key)
        await ctx.send(message)

    @music_group.command(name="stop")
    async def music_stop(self, ctx: commands.Context):
        if not self._is_server_admin(ctx):
            await ctx.send("คำสั่งนี้ใช้ได้เฉพาะ Admin ของเซิร์ฟเวอร์")
            return

        stop_bgm(ctx.guild)
        _ok, message = await leave_voice(ctx.guild)
        await ctx.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
