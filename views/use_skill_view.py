import discord
from utils.game_manager import (
    get_game,
    is_skill_on_cooldown,
    set_player_skill_cd,
    apply_next_roll_effects_to_player
)
from utils.dice.race_presets import (
    get_current_path_type,
)
from utils.dice.race_dice import (
    get_phase_from_turn,
)
from utils.skill.skill_runtime import (
    apply_non_active_skill,
    check_skill_trigger,
    build_next_roll_buff_text
)

from utils.zone.zone_manager import apply_zone_in_game
from utils.zone.zone_embed import build_zone_used_preview_embed

from utils.skill.skill_presets import SKILLS, ICON
from utils.icon_presets import Status_Icon_Type

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
        if game is None:
            await interaction.response.send_message("ไม่พบเกม", ephemeral=True)
            return

        player = game["players"].get(interaction.user.id)
        if player is None:
            await interaction.response.send_message("ไม่พบผู้เล่น", ephemeral=True)
            return

        skills = player.get("skills")
        if not skills:
            await interaction.response.send_message(
                "ยังไม่มีข้อมูลสกิลในเกมนี้ กรุณาเริ่มเกมใหม่อีกครั้ง",
                ephemeral=True
            )
            return

        skill_id = skills.get(slot)
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

        cost = skill.get("cost", 0)
        if player.get("wit_mana", 0) < cost:
            await interaction.response.send_message(
                f"Wit ไม่พอ (ต้องใช้ {cost})",
                ephemeral=True
            )
            return

        instant_effects = []
        queued_effects = []

        for effect in skill.get("effects", []):
            effect_type = effect.get("type")
            duration = effect.get("duration")

            if effect_type in [
                "modify_velocity",
                "modify_selected_die",
                "modify_roll_floor",
                "modify_roll_cap",
                "add_d",
                "add_kh",
                "add_dkh",
            ] or duration == "this_roll":
                queued_effects.append(effect)
            else:
                instant_effects.append(effect)

        result_texts = []

        if instant_effects:
            temp_skill = skill.copy()
            temp_skill["effects"] = instant_effects

            success, result_text = apply_non_active_skill(
                self.channel_id,
                interaction.user.id,
                skill_id,
                temp_skill
            )
            if not success:
                await interaction.response.send_message(result_text, ephemeral=True)
                return

            result_texts.append(result_text)

        if queued_effects:
            apply_next_roll_effects_to_player(player, queued_effects)
            result_texts.append("บัฟถูกสะสมไว้สำหรับการวิ่งครั้งถัดไป")

        if not instant_effects and not queued_effects:
            await interaction.response.send_message(
                "สกิลนี้ยังไม่มีผลที่รองรับในระบบตอนนี้",
                ephemeral=True
            )
            return

        player["wit_mana"] -= cost
        set_player_skill_cd(
            self.channel_id,
            interaction.user.id,
            skill_id,
            skill.get("cooldown", 0)
        )

        emoji = ICON.get(skill.get("icon"), "❓")

        embed = discord.Embed(
            title=f"{emoji} {interaction.user.display_name} ใช้สกิล {skill['name']}",
            description="\n".join(result_texts),
            color=discord.Color.green()
        )

        embed.add_field(
            name=f"{Status_Icon_Type["WIT"]} คงเหลือ",
            value=str(player.get("wit_mana", 0)),
            inline=True
        )

        embed.add_field(
            name="⏳ Cooldown",
            value=f"{skill.get('cooldown', 0)} เทิร์น",
            inline=True
        )

        embed.add_field(
            name="✨ บัพรวมทั้งหมด",
            value=build_next_roll_buff_text(player),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def slot1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 1)

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def slot2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 2)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def slot3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.use_slot(interaction, 3)

    @discord.ui.button(label="Zone", style=discord.ButtonStyle.success, emoji="🌌")
    async def use_zone_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message("ไม่พบเกม", ephemeral=True)
            return

        player = game["players"].get(interaction.user.id)
        if player is None:
            await interaction.response.send_message("ไม่พบผู้เล่น", ephemeral=True)
            return

        if player.get("zone_left", 0) <= 0:
            await interaction.response.send_message("Zone ถูกใช้ไปแล้ว", ephemeral=True)
            return

        success, result_text = apply_zone_in_game(player)
        if not success:
            await interaction.response.send_message(result_text, ephemeral=True)
            return
    
        embed = build_zone_used_preview_embed(player)

        await interaction.response.send_message(embed=embed, ephemeral=False)