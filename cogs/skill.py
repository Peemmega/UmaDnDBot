import discord
from discord.ext import commands
from discord import app_commands

from utils.skill.skill_manager import (
    get_all_skills,
    get_skills_by_icon,
    get_skills_by_active_roll,
    build_skill_description,
    build_skill_list_text,
    find_skill_by_name,
    get_skill_display,
    build_skill_card_text,
    get_skill_short
)

from utils.database import ensure_player, set_player_skill_slot, clear_player_skill_slot, get_player_skill_slots
from utils.skill.skill_presets import SKILLS

class SkillCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    skill_group = app_commands.Group(name="skill", description="จัดการข้อมูลสกิล")

    @skill_group.command(name="list", description="ดูรายชื่อสกิลทั้งหมด")
    async def skill_list(self, interaction: discord.Interaction):
        skills = get_all_skills()

        embed = discord.Embed(
            title="📘 รายชื่อสกิลทั้งหมด",
            description=build_skill_list_text(skills),
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

    @skill_group.command(name="type", description="ดูสกิลตามประเภทไอคอน")
    @app_commands.describe(icon_type="ประเภทสกิล")
    @app_commands.choices(icon_type=[
        app_commands.Choice(name="Concentration", value="Concentration"),
        app_commands.Choice(name="Acceleration", value="Acceleration"),
        app_commands.Choice(name="Velocity", value="Velocity"),
        app_commands.Choice(name="Recovery", value="Recovery"),
        app_commands.Choice(name="DecreaseVelocity", value="DecreaseVelocity"),
        app_commands.Choice(name="ReduceSTA", value="ReduceSTA"),
        app_commands.Choice(name="LookUp", value="LookUp"),
        app_commands.Choice(name="Blind", value="Blind"),
    ])
    async def skill_type(self, interaction: discord.Interaction, icon_type: app_commands.Choice[str]):
        skills = get_skills_by_icon(icon_type.value)

        embed = discord.Embed(
            title=f"📂 สกิลประเภท {icon_type.value}",
            description=build_skill_list_text(skills),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @skill_group.command(name="active", description="ดูสกิลที่กดใช้ตอนทอย")
    async def skill_active(self, interaction: discord.Interaction):
        skills = get_skills_by_active_roll(True)

        embed = discord.Embed(
            title="🎲 สกิลที่ใช้งานตอนทอยวิ่ง",
            description=build_skill_list_text(skills),
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)

    @skill_group.command(name="passive", description="ดูสกิลที่ทำงานอัตโนมัติ")
    async def skill_passive(self, interaction: discord.Interaction):
        skills = get_skills_by_active_roll(False)

        embed = discord.Embed(
            title="⚙️ สกิลที่ทำงานอัตโนมัติ",
            description=build_skill_list_text(skills),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    @skill_group.command(name="info", description="ดูข้อมูลสกิล")
    @app_commands.describe(skill_name="ชื่อหรือ key ของสกิล")
    async def skill_info(self, interaction: discord.Interaction, skill_name: str):
        result = find_skill_by_name(skill_name)
        if result is None:
            await interaction.response.send_message("ไม่พบสกิลนี้", ephemeral=True)
            return

        skill_key, skill = result
        description = build_skill_description(skill_key)

        embed = discord.Embed(
            title=f"🔎 Skill Info: {skill['name']}",
            description=description,
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)


    @skill_group.command(name="tag", description="ดูสกิลตาม tag")
    @app_commands.choices(tag=[
        app_commands.Choice(name="corner", value="corner"),
        app_commands.Choice(name="straight", value="straight"),
        app_commands.Choice(name="velocity", value="velocity"),
        app_commands.Choice(name="acceleration", value="acceleration"),
        app_commands.Choice(name="recovery", value="recovery"),
        app_commands.Choice(name="debuff", value="debuff"),
        app_commands.Choice(name="front", value="front"),
        app_commands.Choice(name="pace", value="pace"),
        app_commands.Choice(name="late", value="late"),
        app_commands.Choice(name="end", value="end"),
    ])
    @app_commands.describe(tag="ชื่อ tag")
    async def skill_tag(self, interaction: discord.Interaction, tag: str):
        from utils.skill.skill_manager import get_skills_by_tag
        skills = get_skills_by_tag(tag)

        embed = discord.Embed(
            title=f"🏷️ สกิล tag: {tag}",
            description=build_skill_list_text(skills),
            color=discord.Color.teal()
        )
        await interaction.response.send_message(embed=embed)

    @skill_group.command(name="equip", description="ติดตั้งสกิลลงช่อง")
    @app_commands.describe(slot="ช่องสกิล", skill_id="รหัสสกิล เช่น s001")
    @app_commands.choices(slot=[
        app_commands.Choice(name="Slot 1", value=1),
        app_commands.Choice(name="Slot 2", value=2),
        app_commands.Choice(name="Slot 3", value=3),
    ])
    async def skill_equip(
        self,
        interaction: discord.Interaction,
        slot: app_commands.Choice[int],
        skill_id: str
    ):
        ensure_player(interaction.user.id, interaction.user.name)

        skill_id = skill_id.strip().lower()

        if skill_id not in SKILLS:
            await interaction.response.send_message(
                f"ไม่พบสกิล `{skill_id}`",
                ephemeral=True
            )
            return

        slots = get_player_skill_slots(interaction.user.id)
        if skill_id in slots.values():
            await interaction.response.send_message(
                "คุณติดตั้งสกิลนี้ไว้แล้ว",
                ephemeral=True
            )
            return

        success, message = set_player_skill_slot(
            interaction.user.id,
            slot.value,
            skill_id
        )

        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        skill_text = get_skill_display(skill_id)

        embed = discord.Embed(
            title="ติดตั้งสกิลสำเร็จ",
            color=discord.Color.green(),
            description=(
                f"ช่อง: **{slot.value}**\n"
                f"{skill_text}"
            )
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @skill_group.command(name="unequip", description="ถอดสกิลออกจากช่อง")
    @app_commands.describe(slot="ช่องสกิล")
    @app_commands.choices(slot=[
        app_commands.Choice(name="Slot 1", value=1),
        app_commands.Choice(name="Slot 2", value=2),
        app_commands.Choice(name="Slot 3", value=3),
    ])
    async def skill_unequip(
        self,
        interaction: discord.Interaction,
        slot: app_commands.Choice[int]
    ):
        ensure_player(interaction.user.id, interaction.user.name)

        slots = get_player_skill_slots(interaction.user.id)
        slot_key = f"slot_{slot.value}"
        old_skill_id = slots[slot_key] if slots else None

        success, message = clear_player_skill_slot(interaction.user.id, slot.value)

        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        if old_skill_id:
            skill_text = get_skill_display(old_skill_id)
            text = f"ถอด {skill_text} ออกจากช่อง {slot.value} เรียบร้อย"
        else:
            text = f"ช่อง {slot.value} ว่างอยู่แล้ว"

        await interaction.response.send_message(text, ephemeral=True)

    @skill_group.command(name="my", description="ดูสกิลที่ติดตั้ง")
    async def my_skills(self, interaction: discord.Interaction):
        ensure_player(interaction.user.id, interaction.user.name)

        slots = get_player_skill_slots(interaction.user.id)
        if slots is None:
            await interaction.response.send_message("ไม่พบข้อมูลผู้เล่น", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📘 Skill presets: {interaction.user.display_name}",
            color=discord.Color.red()
        )

        embed.add_field(
            name="🎯 Skill Slot 1",
            value=build_skill_card_text(slots["slot_1"]),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 2",
            value=build_skill_card_text(slots["slot_2"]),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 3",
            value=build_skill_card_text(slots["slot_3"]),
            inline=False
        )

        embed.set_footer(text="ใช้ /skill info <id> เพื่อดูรายละเอียดเพิ่มเติม")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(SkillCog(bot))