import discord
from utils.skill.skill_manager import (
    build_skill_embed_from_dict,
    filter_skills,
    build_skill_detail_embed,
    build_skill_list_embed,
    get_all_skills,
    get_skills_by_tag
)

from utils.skill.skill_presets import (
    SKILL_TAG_OPTIONS
)

class SkillListTagSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in SKILL_TAG_OPTIONS
        ]

        super().__init__(
            placeholder="เลือก tag เพื่อกรองสกิล",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]

        if selected_tag == "all":
            skills = get_all_skills()
            embed = build_skill_list_embed(skills, "📘 รายชื่อสกิลทั้งหมด")
        else:
            skills = get_skills_by_tag(selected_tag)
            embed = build_skill_detail_embed(
                skills,
                f"🏷️ สกิล tag: {selected_tag}"
            )

        await interaction.response.edit_message(embed=embed, view=self.view)


class SkillListView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SkillListTagSelect())

class SkillFilterView(discord.ui.View):
    def __init__(self, skills: dict):
        super().__init__(timeout=120)
        self.skills = skills

    # ===== Style =====
    @discord.ui.button(label="Front", style=discord.ButtonStyle.primary)
    async def front(self, interaction: discord.Interaction, button):
        await self.update(interaction, style="Front")

    @discord.ui.button(label="Pace", style=discord.ButtonStyle.primary)
    async def pace(self, interaction: discord.Interaction, button):
        await self.update(interaction, style="Pace")

    @discord.ui.button(label="Late", style=discord.ButtonStyle.primary)
    async def late(self, interaction: discord.Interaction, button):
        await self.update(interaction, style="Late")

    @discord.ui.button(label="End", style=discord.ButtonStyle.primary)
    async def end(self, interaction: discord.Interaction, button):
        await self.update(interaction, style="End")

    # ===== Distance =====
    @discord.ui.button(label="Short", style=discord.ButtonStyle.secondary)
    async def short(self, interaction: discord.Interaction, button):
        await self.update(interaction, distance="Sprint")

    @discord.ui.button(label="Mile", style=discord.ButtonStyle.secondary)
    async def mile(self, interaction: discord.Interaction, button):
        await self.update(interaction, distance="Mile")

    @discord.ui.button(label="Medium", style=discord.ButtonStyle.secondary)
    async def medium(self, interaction: discord.Interaction, button):
        await self.update(interaction, distance="Medium")

    @discord.ui.button(label="Long", style=discord.ButtonStyle.secondary)
    async def long(self, interaction: discord.Interaction, button):
        await self.update(interaction, distance="Long")

    # ===== Reset =====
    @discord.ui.button(label="ทั้งหมด", style=discord.ButtonStyle.success)
    async def all(self, interaction: discord.Interaction, button):
        embed = build_skill_embed_from_dict(self.skills, "📘 สกิลทั้งหมด")
        await interaction.response.edit_message(embed=embed, view=self)

    # ===== Core update =====
    async def update(self, interaction, style=None, distance=None):
        filtered = filter_skills(
            self.skills,
            style=style,
            distance=distance
        )

        title = "📘 Skill Filter"
        if style:
            title += f" | {style}"
        if distance:
            title += f" | {distance}"

        embed = build_skill_detail_embed(filtered, title)

        await interaction.response.edit_message(embed=embed, view=self)