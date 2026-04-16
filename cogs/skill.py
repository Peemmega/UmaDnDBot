import discord
from discord.ext import commands
from discord import app_commands

from utils.skill_manager import (
    get_all_skills,
    get_skills_by_icon,
    get_skills_by_active_roll,
    build_skill_description,
    build_skill_list_text,
    find_skill_by_name,
)

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
    @app_commands.choices(stage=[
        app_commands.Choice(name="Concentration", value="Concentration"),
        app_commands.Choice(name="Acceleration", value="Acceleration"),
        app_commands.Choice(name="Velocity", value="Velocity"),
        app_commands.Choice(name="Recovery", value="Recovery"),
        app_commands.Choice(name="DecreaseVelocity", value="DecreaseVelocity"),
        app_commands.Choice(name="ReduceSTA", value="ReduceSTA"),
        app_commands.Choice(name="LookUp", value="LookUp"),
        app_commands.Choice(name="Blind", value="Blind"),
    ])
    @app_commands.describe(tag="ชื่อ tag")
    async def skill_tag(self, interaction: discord.Interaction, tag: str):
        from utils.skill_manager import get_skills_by_tag
        skills = get_skills_by_tag(tag)

        embed = discord.Embed(
            title=f"🏷️ สกิล tag: {tag}",
            description=build_skill_list_text(skills),
            color=discord.Color.teal()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SkillCog(bot))