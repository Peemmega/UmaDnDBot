import discord
from utils.game_manager import (
    get_game,
    is_skill_on_cooldown,
    set_player_skill_cd
)
from utils.dice.race_presets import (
    get_current_path_type,
)
from utils.dice.race_dice import (
    get_phase_from_turn,
)
from utils.skill.skill_runtime import (
    apply_non_active_skill,
    check_skill_trigger 
)
from utils.skill.skill_presets import SKILLS, ICON

class UseSkillView(discord.ui.View):
    def __init__(self, cog, owner_id: int, channel_id: int):
        super().__init__(timeout=60)
        self.cog = cog
        self.owner_id = owner_id
        self.channel_id = channel_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "เมนูนี้เป็นของคุณคนเดียว",
                ephemeral=True
            )
            return False
        return True

    async def use_slot(self, interaction: discord.Interaction, slot: int):
        game = get_game(self.channel_id)
        player = game["players"].get(interaction.user.id)

        if game is None or player is None:
            await interaction.response.send_message("ไม่พบเกมหรือผู้เล่น", ephemeral=True)
            return

        skill_id = player["skills"].get(slot)
        if not skill_id:
            await interaction.response.send_message(f"Slot {slot} ว่าง", ephemeral=True)
            return

        skill = SKILLS.get(skill_id)
        if not skill:
            await interaction.response.send_message(
                f"ไม่พบข้อมูลสกิล `{skill_id}`",
                ephemeral=True
            )
            return

        on_cd, cd_left = is_skill_on_cooldown(self.channel_id, interaction.user.id, skill_id)
        if on_cd:
            await interaction.response.send_message(
                f"สกิลนี้ยังติดคูลดาวน์อีก {cd_left} เทิร์น",
                ephemeral=True
            )
            return
        
        path_type = get_current_path_type(game)
        phase = get_phase_from_turn(game["turn"], game["max_turn"])

        ok, reason = check_skill_trigger(
            self.channel_id,
            interaction.user.id,
            skill,
            path_type=path_type,
            phase=phase
        )
        if not ok:
            await interaction.response.send_message(reason, ephemeral=True)
            return

        # active_roll = ใช้โควต้าทอยเดียวกับ /run
        if skill.get("active_roll", False):
            can_roll, message = self.cog.can_use_roll_skill(
                interaction.channel_id,
                interaction.user.id
            )
            if not can_roll:
                await interaction.response.send_message(message, ephemeral=True)
                return

            success, payload = await self.cog.execute_skill_roll(
                interaction=interaction,
                skill_id=skill_id,
                skill=skill,
            )
            if not success:
                await interaction.response.send_message(payload, ephemeral=True)
                return

            await interaction.response.send_message(
                content=f"✨ <@{interaction.user.id}> ใช้สกิล {ICON.get(skill.get('icon'), '❓')} **{skill['name']}**!",
                embed=payload["embed"]
            )

            set_player_skill_cd(self.channel_id, interaction.user.id, skill_id, skill.get("cooldown", 0))
            game = get_game(self.channel_id)
            await self.cog.handle_after_roll(interaction, game)

            self.stop()
            return

        # non-active skill
        success, result_text = apply_non_active_skill(
            self.channel_id,
            interaction.user.id,
            skill_id,
            skill
        )

        if not success:
            await interaction.response.send_message(result_text, ephemeral=True)
            return

        set_player_skill_cd(
            self.channel_id,
            interaction.user.id,
            skill_id,
            skill.get("cooldown", 0)
        )

        set_player_skill_cd(self.channel_id, interaction.user.id, skill_id, skill.get("cooldown", 0))
        embed = discord.Embed(
            title=f"{ICON.get(skill.get('icon'), '❓')} ใช้สกิล {skill['name']}",
            description=result_text,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        self.stop()

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def slot1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def slot2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def slot3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 3)

    @discord.ui.button(label="ปิด", style=discord.ButtonStyle.secondary)
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="ปิดเมนูสกิลแล้ว", embed=None, view=None)
        self.stop()