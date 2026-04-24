import discord
from discord.ext import commands
from utils.database import (
    ensure_player,
    reset_all_zone_data,
    add_player_attitude,
    set_all_attitude,
    add_player_stats_point,
    add_player_skill_point,
)

ADMIN_IDS = {
    464058883556769793,
}

LOG_CHANNEL_ID = 1496060150929166488

VALID_ATTITUDE_FIELDS = {
    "turf", "dirt",
    "sprint", "mile", "medium", "long",
    "front", "pace", "late", "end_style",
}

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_user(self, user_id: int) -> bool:
        return user_id in ADMIN_IDS

    async def silent_delete(self, message: discord.Message):
        try:
            await message.delete()
        except discord.Forbidden:
            pass

    def resolve_target(self, ctx: commands.Context, member: discord.Member | None) -> discord.Member:
        return member or ctx.author

    async def send_result_embed(
        self,
        ctx: commands.Context,
        *,
        title: str,
        description: str,
        color: discord.Color = discord.Color.blurple(),
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        await ctx.send(embed=embed)

    async def send_log_embed(
        self,
        ctx: commands.Context,
        *,
        action_name: str,
        result_text: str,
        target: discord.Member | None = None,
        color: discord.Color = discord.Color.dark_gold(),
    ):
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(LOG_CHANNEL_ID)
            except Exception:
                return

        target_text = target.mention if target else "-"

        embed = discord.Embed(
            title="🛡️ Admin Command Log",
            color=color
        )
        embed.add_field(name="ผู้ใช้คำสั่ง", value=f"{ctx.author.mention}\n`{ctx.author.id}`", inline=True)
        embed.add_field(name="คำสั่ง", value=f"`{ctx.message.content}`", inline=False)
        embed.add_field(name="Action", value=action_name, inline=True)
        embed.add_field(name="Target", value=target_text, inline=True)
        embed.add_field(name="Channel", value=f"{ctx.channel.mention}\n`{ctx.channel.id}`", inline=False)
        embed.add_field(name="Result", value=result_text, inline=False)

        if ctx.guild:
            embed.set_footer(text=f"{ctx.guild.name} | Guild ID: {ctx.guild.id}")
        else:
            embed.set_footer(text="Direct Message")

        try:
            await channel.send(embed=embed)
        except Exception:
            pass

    @commands.command(name="resetzoneall")
    async def reset_zone_all(self, ctx: commands.Context):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="resetzoneall",
                result_text="ปฏิเสธการใช้งาน: ไม่มีสิทธิ์",
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)
        reset_all_zone_data()

        await self.send_result_embed(
            ctx,
            title="♻️ Reset Zone สำเร็จ",
            description="รีเซ็ต Zone Build และ Zone Points ของทุกคนแล้ว",
            color=discord.Color.red()
        )
        await self.send_log_embed(
            ctx,
            action_name="resetzoneall",
            result_text="รีเซ็ต Zone Build และ Zone Points ของทุกคนแล้ว",
            color=discord.Color.red(),
        )

    @commands.command(name="add_att")
    async def add_att(
        self,
        ctx: commands.Context,
        attitude_name: str,
        member: Optional[discord.Member] = None,
    ):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="add_att",
                result_text="ปฏิเสธการใช้งาน: ไม่มีสิทธิ์",
                target=member,
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        target = self.resolve_target(ctx, member)
        ensure_player(target.id, target.name)

        attitude_name = attitude_name.lower().strip()
        if attitude_name not in VALID_ATTITUDE_FIELDS:
            error_text = (
                f"ไม่พบ attitude: `{attitude_name}`\n"
                f"ใช้ได้: {', '.join(sorted(VALID_ATTITUDE_FIELDS))}"
            )
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Attitude ไม่สำเร็จ",
                description=error_text,
                color=discord.Color.red()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_att",
                result_text=error_text,
                target=target,
                color=discord.Color.red(),
            )
            return

        success, msg = add_player_attitude(target.id, attitude_name, 1)

        if success:
            result_text = f"เพิ่ม `{attitude_name}` +1 ให้ {target.display_name}"
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Attitude สำเร็จ",
                description=f"{target.mention}\nเพิ่ม `{attitude_name}` +1 แล้ว",
                color=discord.Color.green()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_att",
                result_text=result_text,
                target=target,
                color=discord.Color.green(),
            )
        else:
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Attitude ไม่สำเร็จ",
                description=msg,
                color=discord.Color.red()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_att",
                result_text=msg,
                target=target,
                color=discord.Color.red(),
            )

    @commands.command(name="set_all_att")
    async def set_all_att(
        self,
        ctx: commands.Context,
        value: int,
        member: Optional[discord.Member] = None,
    ):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="set_all_att",
                result_text="ปฏิเสธการใช้งาน: ไม่มีสิทธิ์",
                target=member,
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        if value < 1 or value > 8:
            error_text = "ค่าต้องอยู่ระหว่าง `1-8`"
            await self.send_result_embed(
                ctx,
                title="ตั้งค่า Attitude ไม่สำเร็จ",
                description=error_text,
                color=discord.Color.red()
            )
            await self.send_log_embed(
                ctx,
                action_name="set_all_att",
                result_text=error_text,
                target=member,
                color=discord.Color.red(),
            )
            return

        target = self.resolve_target(ctx, member)
        ensure_player(target.id, target.name)

        set_all_attitude(target.id, value)

        result_text = f"ตั้งค่า Attitude ทั้งหมดของ {target.display_name} เป็น {value}"
        await self.send_result_embed(
            ctx,
            title="ตั้งค่า Attitude สำเร็จ",
            description=f"{target.mention}\nตั้งค่า Attitude ทั้งหมดเป็น `{value}` แล้ว",
            color=discord.Color.green()
        )
        await self.send_log_embed(
            ctx,
            action_name="set_all_att",
            result_text=result_text,
            target=target,
            color=discord.Color.green(),
        )

    @commands.command(name="add_stats_pt")
    async def add_stats_pt(
        self,
        ctx: commands.Context,
        amount: int,
        member: Optional[discord.Member] = None,
    ):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="add_stats_pt",
                result_text="ปฏิเสธการใช้งาน: ไม่มีสิทธิ์",
                target=member,
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        target = self.resolve_target(ctx, member)
        ensure_player(target.id, target.name)

        success, msg = add_player_stats_point(target.id, amount)

        if success:
            result_text = f"เพิ่ม Stats Point ให้ {target.display_name} +{amount}"
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Stats Point สำเร็จ",
                description=f"{target.mention}\nเพิ่ม Stats Point +{amount}",
                color=discord.Color.green()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_stats_pt",
                result_text=result_text,
                target=target,
                color=discord.Color.green(),
            )
        else:
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Stats Point ไม่สำเร็จ",
                description=msg,
                color=discord.Color.red()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_stats_pt",
                result_text=msg,
                target=target,
                color=discord.Color.red(),
            )

    @commands.command(name="add_skill_pt")
    async def add_skill_pt(
        self,
        ctx: commands.Context,
        amount: int,
        member: Optional[discord.Member] = None,
    ):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="add_skill_pt",
                result_text="ปฏิเสธการใช้งาน: ไม่มีสิทธิ์",
                target=member,
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        target = self.resolve_target(ctx, member)
        ensure_player(target.id, target.name)

        success, msg = add_player_skill_point(target.id, amount)

        if success:
            result_text = f"เพิ่ม Skill Point ให้ {target.display_name} +{amount}"
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Skill Point สำเร็จ",
                description=f"{target.mention}\nเพิ่ม Skill Point +{amount}",
                color=discord.Color.green()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_skill_pt",
                result_text=result_text,
                target=target,
                color=discord.Color.green(),
            )
        else:
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Skill Point ไม่สำเร็จ",
                description=msg,
                color=discord.Color.red()
            )
            await self.send_log_embed(
                ctx,
                action_name="add_skill_pt",
                result_text=msg,
                target=target,
                color=discord.Color.red(),
            )

async def setup(bot):
    await bot.add_cog(Admin(bot))