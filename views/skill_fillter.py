import discord
from utils.skill.skill_manager import (
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