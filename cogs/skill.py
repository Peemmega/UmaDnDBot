import discord
from discord.ext import commands
from discord import app_commands

from utils.skill.skill_manager import (
    get_all_skills,
    get_skills_by_icon,
    build_skill_description,
    build_skill_list_text,
    find_skill_by_name,
    get_skill_display,
    build_skill_card_text,
    build_skill_tag_embed,
    build_skill_list_embed
)
from views.skill_fillter import SkillListView
from views.skill_equip_view import SkillEquipView

from utils.database import ensure_player, set_player_skill_slot, clear_player_skill_slot, get_player_skill_slots
from utils.skill.skill_presets import SKILLS


class SkillCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    skill_group = app_commands.Group(name="skill", description="จัดการข้อมูลสกิล")

    async def handle_skill_equip(
        self,
        interaction: discord.Interaction,
        *,
        slot: int,
        skill_id: str,
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
            slot,
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
                f"ช่อง: **{slot}**\n"
                f"{skill_text}"
            )
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        

    @skill_group.command(name="check", description="ตรวจสอบข้อมูลสกิล")
    @app_commands.describe(
        mode="โหมดที่ต้องการดู",
        type="ประเภทสกิล",
        tag="แท็กของสกิล",
        info="รหัสหรือชื่อสกิล"
    )
    @app_commands.choices(mode=[
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="info", value="info"),
    ])
    async def skill_check(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str],
        type: app_commands.Choice[str] | None = None,
        tag: app_commands.Choice[str] | None = None,
        info: str | None = None,
    ):
        mode_value = mode.value

        if mode_value == "list":
            skills = get_all_skills()
            embed = build_skill_list_embed(skills, "📘 รายชื่อสกิลทั้งหมด")
            view = SkillListView()

            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=False
            )
            return

        if mode_value == "type":
            if type is None:
                await interaction.response.send_message(
                    "กรุณาเลือก type",
                    ephemeral=True
                )
                return

            skills = get_skills_by_icon(type.value)
            embed = discord.Embed(
                title=f"📂 สกิลประเภท {type.value}",
                description=build_skill_list_text(skills),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            return

        if mode_value == "info":
            if not info:
                await interaction.response.send_message(
                    "กรุณาใส่รหัสหรือชื่อสกิล เช่น s001",
                    ephemeral=True
                )
                return

            result = find_skill_by_name(info)
            if result is None:
                await interaction.response.send_message(
                    "ไม่พบสกิลนี้",
                    ephemeral=True
                )
                return

            skill_key, skill = result
            description = build_skill_description(skill_key)

            embed = discord.Embed(
                title=f"🔎 Skill Info: {skill['name']}",
                description=description,
                color=discord.Color.gold()
            )

            view = SkillEquipView(
                skill_id=skill_key,
                equip_callback=self.handle_skill_equip
            )

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return

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
        await self.handle_skill_equip(
            interaction,
            slot=slot.value,
            skill_id=skill_id
        )

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