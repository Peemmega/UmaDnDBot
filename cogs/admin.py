import discord
from typing import Optional
from discord.ext import commands
from utils.database import (
    ensure_player,
    reset_all_zone_data,
    add_player_aptitude,
    set_all_aptitude,
    add_player_stats_point,
    add_player_skill_point,
    clear_race_records,
    clear_race_rankings,
    clear_legacy_profile_data,
    reset_all_data,
    clear_player_mailbox,
    clear_player_skills,
    get_admin_player_overview,
    remove_player_from_team,
    reset_player_data_section,
    set_admin_player_value,
)
from utils.race.race_presets import RACE_PRESET
from utils.channel_config import COMMAND_LOG_CHANNEL_ID

ADMIN_IDS = {
    464058883556769793,
}

VALID_APTITUDE_FIELDS = {
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

    async def require_admin(
        self,
        ctx: commands.Context,
        action_name: str,
        target: discord.Member | None = None,
    ) -> bool:
        if self.is_admin_user(ctx.author.id):
            return True
        await self.silent_delete(ctx.message)
        await self.send_log_embed(
            ctx,
            action_name=action_name,
            result_text="Permission denied",
            target=target,
            color=discord.Color.red(),
        )
        return False

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
        channel = self.bot.get_channel(COMMAND_LOG_CHANNEL_ID)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(COMMAND_LOG_CHANNEL_ID)
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

    @commands.command(name="help")
    async def admin_help(self, ctx: commands.Context):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="help",
                result_text="Permission denied",
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)
        embed = discord.Embed(
            title="คำสั่งผู้ดูแลระบบ",
            description="ใช้ได้เฉพาะผู้ดูแลที่กำหนดไว้ในบอต",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="ตรวจสอบและแก้ไขข้อมูลรายคน",
            value=(
                "`!admin_profile @member` — ดูข้อมูลและสถานะระบบของผู้เล่น\n"
                "`!set_stat <speed|stamina|power|gut|wit> <1-8> [@member]` — ตั้งค่าสเตตัส\n"
                "`!set_point <stats|skill|fans|zone> <จำนวน> [@member]` — ตั้งค่าแต้ม/แฟน\n"
                "`!remove_skill <1-4|all> @member CONFIRM` — ล้างสกิลที่ติดตั้ง\n"
                "`!reset_player <stats|skills|zone> @member CONFIRM` — รีเซ็ตข้อมูลเป็นหมวด\n"
                "`!team_remove @trainee CONFIRM` — นำผู้เล่นออกจากทีมและยกเลิกคำเชิญค้าง\n"
                "`!mail_clear @member CONFIRM` — ลบจดหมายทั้งหมดของผู้เล่น"
            ),
            inline=False,
        )
        embed.add_field(
            name="เพิ่มหรือปรับค่าผู้เล่น",
            value=(
                "`!add_att <aptitude> [@member]` — เพิ่ม aptitude 1 ระดับ\n"
                "`!set_all_att <1-8> [@member]` — ตั้ง aptitude ทุกค่า\n"
                "`!add_stats_pt <amount> [@member]` — เพิ่ม/ลด Stats Point\n"
                "`!add_skill_pt <amount> [@member]` — เพิ่ม/ลด Event Point"
            ),
            inline=False,
        )
        embed.add_field(
            name="จัดการข้อมูลทั้งระบบ",
            value=(
                "`!clear_race_ranking [stage_key|all]` — ลบอันดับสนามที่เลือก\n"
                "`!clear_race_records <all|official|practice> CONFIRM` — ลบประวัติการแข่งขันตามประเภท\n"
                "`!resetzoneall` — รีเซ็ต Zone Build และ Zone Point ของทุกคน\n"
                "`!clear_legacy_profile @member CONFIRM` — ล้าง role/profile เก่าของผู้เล่น\n"
                "`!resetall CONFIRM` — ลบข้อมูลผู้เล่นและการเล่นทั้งหมดอย่างถาวร"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(name="admin_profile", aliases=["adminprofile", "ap"])
    async def admin_profile(self, ctx: commands.Context, member: discord.Member):
        """Show an operational summary of one player's stored data."""
        if not await self.require_admin(ctx, "admin_profile", member):
            return
        await self.silent_delete(ctx.message)

        player = get_admin_player_overview(member.id)
        if player is None:
            result_text = f"ไม่พบข้อมูลผู้เล่นของ {member.display_name}"
            await self.send_result_embed(
                ctx, title="ไม่พบข้อมูลผู้เล่น", description=result_text, color=discord.Color.orange()
            )
            await self.send_log_embed(ctx, action_name="admin_profile", result_text=result_text, target=member)
            return

        skills = [player.get(f"skill_slot_{slot}") for slot in range(1, 5)]
        skill_text = " • ".join(
            f"{index}: {skill or '-'}" for index, skill in enumerate(skills, start=1)
        )
        zone = player["zone"]
        admin = player["admin"]
        team_text = (
            f"Trainer: `{admin['trainer_user_id']}`"
            if admin["trainer_user_id"]
            else "ไม่มี Trainer"
        )
        if admin["trainee_count"]:
            team_text += f"\nดูแล Trainee: `{admin['trainee_count']}` คน"

        embed = discord.Embed(
            title=f"ข้อมูลผู้เล่น: {player['username']}",
            description=f"{member.mention}\nUser ID: `{player['user_id']}`",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="ค่าสเตตัส",
            value=(
                f"SPD `{player['speed']}` | STA `{player['stamina']}` | POW `{player['power']}`\n"
                f"GUT `{player['gut']}` | WIT `{player['wit']}` | Stats Point `{player['stats_point']}`"
            ),
            inline=False,
        )
        embed.add_field(
            name="Aptitude",
            value=(
                f"Turf/Dirt: `{player['turf']}` / `{player['dirt']}`\n"
                f"Sprint/Mile/Medium/Long: `{player['sprint']}` / `{player['mile']}` / `{player['medium']}` / `{player['long']}`\n"
                f"Front/Pace/Late/End: `{player['front']}` / `{player['pace']}` / `{player['late']}` / `{player['end_style']}`"
            ),
            inline=False,
        )
        embed.add_field(
            name="แต้มและสกิล",
            value=f"Fans `{player['fans']}` | Event Point `{player['skill_point']}`\n{skill_text}",
            inline=False,
        )
        embed.add_field(
            name="Zone",
            value=f"{zone['name']} | Point `{zone['points']}`",
            inline=True,
        )
        embed.add_field(
            name="ข้อมูลระบบ",
            value=(
                f"Role: `{admin['role'] or '-'}`\n{team_text}\n"
                f"Mailbox: `{admin['mailbox_count']}` | Skill presets: `{admin['skill_preset_count']}`"
            ),
            inline=True,
        )
        await ctx.send(embed=embed)
        await self.send_log_embed(ctx, action_name="admin_profile", result_text="Viewed player overview", target=member)

    @commands.command(name="set_stat")
    async def set_stat(
        self,
        ctx: commands.Context,
        stat_name: str,
        value: int,
        member: Optional[discord.Member] = None,
    ):
        if not await self.require_admin(ctx, "set_stat", member):
            return
        await self.silent_delete(ctx.message)
        target = self.resolve_target(ctx, member)
        ensure_player(target.id, target.name)

        stat_name = stat_name.lower().strip()
        if stat_name not in {"speed", "stamina", "power", "gut", "wit"}:
            result_text = "เลือกได้เฉพาะ `speed`, `stamina`, `power`, `gut`, หรือ `wit`"
            await self.send_result_embed(ctx, title="ตั้งค่าสเตตัสไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="set_stat", result_text=result_text, target=target, color=discord.Color.red())
            return
        try:
            set_admin_player_value(target.id, stat_name, value)
        except ValueError as error:
            result_text = str(error)
            await self.send_result_embed(ctx, title="ตั้งค่าสเตตัสไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="set_stat", result_text=result_text, target=target, color=discord.Color.red())
            return

        result_text = f"ตั้งค่า `{stat_name}` เป็น `{value}` ให้ {target.display_name}"
        await self.send_result_embed(ctx, title="ตั้งค่าสเตตัสสำเร็จ", description=f"{target.mention}\n{result_text}", color=discord.Color.green())
        await self.send_log_embed(ctx, action_name="set_stat", result_text=result_text, target=target, color=discord.Color.green())

    @commands.command(name="set_point")
    async def set_point(
        self,
        ctx: commands.Context,
        point_type: str,
        value: int,
        member: Optional[discord.Member] = None,
    ):
        if not await self.require_admin(ctx, "set_point", member):
            return
        await self.silent_delete(ctx.message)
        target = self.resolve_target(ctx, member)
        ensure_player(target.id, target.name)

        field_by_type = {"stats": "stats_point", "skill": "skill_point", "fans": "fans", "zone": "zone_points"}
        point_type = point_type.lower().strip()
        field = field_by_type.get(point_type)
        if field is None:
            result_text = "เลือกได้เฉพาะ `stats`, `skill`, `fans`, หรือ `zone`"
            await self.send_result_embed(ctx, title="ตั้งค่าแต้มไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="set_point", result_text=result_text, target=target, color=discord.Color.red())
            return
        try:
            set_admin_player_value(target.id, field, value)
        except ValueError as error:
            result_text = str(error)
            await self.send_result_embed(ctx, title="ตั้งค่าแต้มไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="set_point", result_text=result_text, target=target, color=discord.Color.red())
            return

        result_text = f"ตั้งค่า `{point_type}` เป็น `{value}` ให้ {target.display_name}"
        await self.send_result_embed(ctx, title="ตั้งค่าแต้มสำเร็จ", description=f"{target.mention}\n{result_text}", color=discord.Color.green())
        await self.send_log_embed(ctx, action_name="set_point", result_text=result_text, target=target, color=discord.Color.green())

    @commands.command(name="remove_skill", aliases=["clearskill"])
    async def remove_skill(
        self,
        ctx: commands.Context,
        slot: str,
        member: discord.Member,
        confirmation: str = "",
    ):
        if not await self.require_admin(ctx, "remove_skill", member):
            return
        await self.silent_delete(ctx.message)
        if confirmation != "CONFIRM":
            result_text = "คำสั่งนี้ล้างสกิลที่ติดตั้งอยู่ ใช้ `!remove_skill <1-4|all> @member CONFIRM` เพื่อยืนยัน"
            await self.send_result_embed(ctx, title="ยกเลิกการล้างสกิล", description=result_text, color=discord.Color.orange())
            await self.send_log_embed(ctx, action_name="remove_skill", result_text="Cancelled: no confirmation", target=member, color=discord.Color.orange())
            return

        normalized_slot = slot.strip().lower()
        try:
            parsed_slot = None if normalized_slot == "all" else int(normalized_slot)
            clear_player_skills(member.id, parsed_slot)
        except (ValueError, LookupError) as error:
            result_text = str(error)
            await self.send_result_embed(ctx, title="ล้างสกิลไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="remove_skill", result_text=result_text, target=member, color=discord.Color.red())
            return

        label = "ทุกช่อง" if parsed_slot is None else f"ช่อง {parsed_slot}"
        result_text = f"ล้างสกิล{label}ของ {member.display_name} แล้ว"
        await self.send_result_embed(ctx, title="ล้างสกิลสำเร็จ", description=f"{member.mention}\n{result_text}", color=discord.Color.green())
        await self.send_log_embed(ctx, action_name="remove_skill", result_text=result_text, target=member, color=discord.Color.green())

    @commands.command(name="reset_player")
    async def reset_player(
        self,
        ctx: commands.Context,
        section: str,
        member: discord.Member,
        confirmation: str = "",
    ):
        if not await self.require_admin(ctx, "reset_player", member):
            return
        await self.silent_delete(ctx.message)
        normalized_section = section.strip().lower()
        if normalized_section not in {"stats", "skills", "zone"}:
            result_text = "เลือกหมวดได้เฉพาะ `stats`, `skills`, หรือ `zone`"
            await self.send_result_embed(ctx, title="รีเซ็ตข้อมูลไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="reset_player", result_text=result_text, target=member, color=discord.Color.red())
            return
        if confirmation != "CONFIRM":
            result_text = "คำสั่งนี้รีเซ็ตข้อมูลผู้เล่น ใช้ `!reset_player <stats|skills|zone> @member CONFIRM` เพื่อยืนยัน"
            await self.send_result_embed(ctx, title="ยกเลิกการรีเซ็ต", description=result_text, color=discord.Color.orange())
            await self.send_log_embed(ctx, action_name="reset_player", result_text="Cancelled: no confirmation", target=member, color=discord.Color.orange())
            return
        try:
            counts = reset_player_data_section(member.id, normalized_section)
        except (ValueError, LookupError) as error:
            result_text = str(error)
            await self.send_result_embed(ctx, title="รีเซ็ตข้อมูลไม่สำเร็จ", description=result_text, color=discord.Color.red())
            await self.send_log_embed(ctx, action_name="reset_player", result_text=result_text, target=member, color=discord.Color.red())
            return

        result_text = f"รีเซ็ตหมวด `{normalized_section}` ของ {member.display_name} แล้ว ({sum(counts.values())} รายการ)"
        await self.send_result_embed(ctx, title="รีเซ็ตข้อมูลสำเร็จ", description=f"{member.mention}\n{result_text}", color=discord.Color.green())
        await self.send_log_embed(ctx, action_name="reset_player", result_text=result_text, target=member, color=discord.Color.green())

    @commands.command(name="team_remove", aliases=["removeteam"])
    async def team_remove(self, ctx: commands.Context, member: discord.Member, confirmation: str = ""):
        if not await self.require_admin(ctx, "team_remove", member):
            return
        await self.silent_delete(ctx.message)
        if confirmation != "CONFIRM":
            result_text = "ใช้ `!team_remove @trainee CONFIRM` เพื่อยืนยันการนำออกจากทีม"
            await self.send_result_embed(ctx, title="ยกเลิกการนำออกจากทีม", description=result_text, color=discord.Color.orange())
            await self.send_log_embed(ctx, action_name="team_remove", result_text="Cancelled: no confirmation", target=member, color=discord.Color.orange())
            return
        counts = remove_player_from_team(member.id)
        total = sum(counts.values())
        result_text = f"นำ {member.display_name} ออกจากทีมแล้ว ({total} รายการ)"
        await self.send_result_embed(ctx, title="จัดการทีมสำเร็จ", description=f"{member.mention}\n{result_text}", color=discord.Color.green())
        await self.send_log_embed(ctx, action_name="team_remove", result_text=result_text, target=member, color=discord.Color.green())

    @commands.command(name="mail_clear", aliases=["clearmail"])
    async def mail_clear(self, ctx: commands.Context, member: discord.Member, confirmation: str = ""):
        if not await self.require_admin(ctx, "mail_clear", member):
            return
        await self.silent_delete(ctx.message)
        if confirmation != "CONFIRM":
            result_text = "ใช้ `!mail_clear @member CONFIRM` เพื่อยืนยันการลบจดหมายทั้งหมด"
            await self.send_result_embed(ctx, title="ยกเลิกการลบจดหมาย", description=result_text, color=discord.Color.orange())
            await self.send_log_embed(ctx, action_name="mail_clear", result_text="Cancelled: no confirmation", target=member, color=discord.Color.orange())
            return
        deleted_count = clear_player_mailbox(member.id)
        result_text = f"ลบจดหมายของ {member.display_name} แล้ว {deleted_count} ฉบับ"
        await self.send_result_embed(ctx, title="ลบจดหมายสำเร็จ", description=f"{member.mention}\n{result_text}", color=discord.Color.green())
        await self.send_log_embed(ctx, action_name="mail_clear", result_text=result_text, target=member, color=discord.Color.green())

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

    @commands.command(name="clear_race_ranking", aliases=["clearranking", "clear_rank"])
    async def clear_race_ranking(self, ctx: commands.Context, stage_key: str = "all"):
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="clear_race_ranking",
                result_text="Permission denied",
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        normalized_key = stage_key.strip()
        delete_all = normalized_key.lower() in {"all", "*"}

        if not delete_all and normalized_key not in RACE_PRESET:
            examples = ", ".join(list(RACE_PRESET.keys())[:10])
            error_text = (
                f"Unknown stage_key: `{normalized_key}`\n"
                f"Use `all` to clear every ranking, or use a stage key such as: {examples}"
            )
            await self.send_result_embed(
                ctx,
                title="Clear Race Ranking Failed",
                description=error_text,
                color=discord.Color.red(),
            )
            await self.send_log_embed(
                ctx,
                action_name="clear_race_ranking",
                result_text=error_text,
                color=discord.Color.red(),
            )
            return

        deleted_count = clear_race_rankings(None if delete_all else normalized_key)
        target_text = "all stages" if delete_all else normalized_key
        result_text = f"Deleted {deleted_count} ranking row(s) from {target_text}."

        await self.send_result_embed(
            ctx,
            title="Race Ranking Cleared",
            description=result_text,
            color=discord.Color.green(),
        )
        await self.send_log_embed(
            ctx,
            action_name="clear_race_ranking",
            result_text=result_text,
            color=discord.Color.green(),
        )

    @commands.command(name="clear_race_records", aliases=["clearracerecords", "clear_race_history"])
    async def clear_race_records_command(
        self,
        ctx: commands.Context,
        record_type: str = "",
        confirmation: str = "",
    ):
        """Permanently delete completed race records by type."""
        if not await self.require_admin(ctx, "clear_race_records"):
            return
        await self.silent_delete(ctx.message)

        normalized_type = record_type.strip().lower()
        if normalized_type not in {"all", "official", "practice"}:
            result_text = "เลือกประเภทได้เฉพาะ `all`, `official`, หรือ `practice`"
            await self.send_result_embed(
                ctx,
                title="ลบประวัติการแข่งขันไม่สำเร็จ",
                description=result_text,
                color=discord.Color.red(),
            )
            await self.send_log_embed(
                ctx,
                action_name="clear_race_records",
                result_text=result_text,
                color=discord.Color.red(),
            )
            return

        if confirmation != "CONFIRM":
            result_text = (
                "คำสั่งนี้ลบประวัติการแข่งขันและข้อมูลผู้เข้าร่วม/เทิร์น/แอ็กชันที่เกี่ยวข้องอย่างถาวร\n"
                "ใช้ `!clear_race_records <all|official|practice> CONFIRM` เพื่อยืนยัน"
            )
            await self.send_result_embed(
                ctx,
                title="ยกเลิกการลบประวัติการแข่งขัน",
                description=result_text,
                color=discord.Color.orange(),
            )
            await self.send_log_embed(
                ctx,
                action_name="clear_race_records",
                result_text="Cancelled: no confirmation",
                color=discord.Color.orange(),
            )
            return

        deleted_counts = clear_race_records(normalized_type)
        deleted_total = sum(deleted_counts.values())
        type_label = {"all": "ทั้งหมด", "official": "Official", "practice": "Practice"}[normalized_type]
        result_text = (
            f"ลบ race record ประเภท `{type_label}` แล้ว {deleted_counts['race_history']} รายการ "
            f"(รวมข้อมูลที่เกี่ยวข้อง {deleted_total} แถว)"
        )
        await self.send_result_embed(
            ctx,
            title="ลบประวัติการแข่งขันสำเร็จ",
            description=result_text,
            color=discord.Color.green(),
        )
        await self.send_log_embed(
            ctx,
            action_name="clear_race_records",
            result_text=result_text,
            color=discord.Color.green(),
        )

    @commands.command(name="resetall")
    async def reset_all(self, ctx: commands.Context, confirmation: str = ""):
        """Permanently clear all persisted player and gameplay data."""
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="resetall",
                result_text="Permission denied",
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        if confirmation != "CONFIRM":
            result_text = "This permanently deletes all player data. Run `!resetall CONFIRM` to continue."
            await self.send_result_embed(
                ctx,
                title="Reset All Cancelled",
                description=result_text,
                color=discord.Color.orange(),
            )
            await self.send_log_embed(
                ctx,
                action_name="resetall",
                result_text="Cancelled: confirmation text was not supplied.",
                color=discord.Color.orange(),
            )
            return

        deleted_counts = reset_all_data()
        deleted_total = sum(deleted_counts.values())
        result_text = f"Permanently deleted {deleted_total} record(s) from all player and gameplay data."

        await self.send_result_embed(
            ctx,
            title="Reset All Complete",
            description=result_text,
            color=discord.Color.red(),
        )
        await self.send_log_embed(
            ctx,
            action_name="resetall",
            result_text=result_text,
            color=discord.Color.red(),
        )

    @commands.command(name="clear_legacy_profile", aliases=["clearprofile", "resetprofile"])
    async def clear_legacy_profile(
        self,
        ctx: commands.Context,
        member: discord.Member,
        confirmation: str = "",
    ):
        """Remove old role/profile records for one member without deleting gameplay data."""
        if not self.is_admin_user(ctx.author.id):
            await self.silent_delete(ctx.message)
            await self.send_log_embed(
                ctx,
                action_name="clear_legacy_profile",
                result_text="Permission denied",
                target=member,
                color=discord.Color.red(),
            )
            return

        await self.silent_delete(ctx.message)

        if confirmation != "CONFIRM":
            result_text = (
                "This removes the member's old role/profile records but keeps player and gameplay data. "
                "Run `!clear_legacy_profile @member CONFIRM` to continue."
            )
            await self.send_result_embed(
                ctx,
                title="Clear Legacy Profile Cancelled",
                description=result_text,
                color=discord.Color.orange(),
            )
            await self.send_log_embed(
                ctx,
                action_name="clear_legacy_profile",
                result_text="Cancelled: confirmation text was not supplied.",
                target=member,
                color=discord.Color.orange(),
            )
            return

        deleted_counts = clear_legacy_profile_data(member.id)
        deleted_total = sum(deleted_counts.values())
        result_text = (
            f"Removed {deleted_total} old role/profile record(s) for {member.display_name}. "
            "Their player and gameplay data were kept."
        )
        await self.send_result_embed(
            ctx,
            title="Legacy Profile Cleared",
            description=f"{member.mention}\n{result_text}",
            color=discord.Color.green(),
        )
        await self.send_log_embed(
            ctx,
            action_name="clear_legacy_profile",
            result_text=result_text,
            target=member,
            color=discord.Color.green(),
        )

    @commands.command(name="add_att")
    async def add_att(
        self,
        ctx: commands.Context,
        aptitude_name: str,
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

        aptitude_name = aptitude_name.lower().strip()
        if aptitude_name not in VALID_APTITUDE_FIELDS:
            error_text = (
                f"ไม่พบ aptitude: `{aptitude_name}`\n"
                f"ใช้ได้: {', '.join(sorted(VALID_APTITUDE_FIELDS))}"
            )
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Aptitude ไม่สำเร็จ",
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

        success, msg = add_player_aptitude(target.id, aptitude_name, 1)

        if success:
            result_text = f"เพิ่ม `{aptitude_name}` +1 ให้ {target.display_name}"
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Aptitude สำเร็จ",
                description=f"{target.mention}\nเพิ่ม `{aptitude_name}` +1 แล้ว",
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
                title="เพิ่ม Aptitude ไม่สำเร็จ",
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
                title="ตั้งค่า Aptitude ไม่สำเร็จ",
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

        set_all_aptitude(target.id, value)

        result_text = f"ตั้งค่า Aptitude ทั้งหมดของ {target.display_name} เป็น {value}"
        await self.send_result_embed(
            ctx,
            title="ตั้งค่า Aptitude สำเร็จ",
            description=f"{target.mention}\nตั้งค่า Aptitude ทั้งหมดเป็น `{value}` แล้ว",
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
            result_text = f"เพิ่ม Event Point ให้ {target.display_name} +{amount}"
            await self.send_result_embed(
                ctx,
                title="เพิ่ม Event Point สำเร็จ",
                description=f"{target.mention}\nเพิ่ม Event Point +{amount}",
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
                title="เพิ่ม Event Point ไม่สำเร็จ",
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
