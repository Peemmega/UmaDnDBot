import discord
import os

from utils.game_manager import get_game, get_game_rule, set_game_rule, add_mob_from_preset
from utils.mob.mob_presets import MOB_PRESETS


ROOKIE_PRESET_KEYS = (
    "rookie_front",
    "rookie_pace",
    "rookie_late",
    "rookie_end",
    "rookie_alt_front",
    "rookie_alt_pace",
    "rookie_alt_late",
    "rookie_alt_end",
)
UMA_PRESETS = [(key, data) for key, data in MOB_PRESETS.items() if key not in ROOKIE_PRESET_KEYS]
UMA_PAGE_SIZE = 25
RULE_LABELS = {
    "AllowSkill": "AllowSkill · Skill / Zone",
    "DreamMode": "DreamMode · ค่าสเตตัสเริ่มต้น 8",
    "NoDebuff": "NoDebuff · ปิด Debuff",
    "Weather": "Weather · สภาพอากาศ",
    "FastMode": "Fast Mode · รูปแบบผลทอยบอท",
}
WEATHER_LABELS = {
    "none": "ไม่กำหนด",
    "random": "สุ่ม",
    "warm": "อบอุ่น",
    "rainy": "ฝนตก",
    "sunny": "แดดจัด",
}


def _room_open(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return None, "ไม่พบเกมในห้องนี้"
    if game.get("started"):
        return None, "เริ่มแข่งแล้ว จึงเปลี่ยนการตั้งค่าหรือเพิ่ม Bot ไม่ได้"
    return game, None


class SettingsView(discord.ui.View):
    def __init__(self, channel_id: int, owner_id: int, selected_rule: str = "AllowSkill"):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.selected_rule = selected_rule
        self.refresh_components()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("เปิดดูและแก้ Settings ได้เฉพาะผู้สร้างห้อง", ephemeral=True)
            return False
        game = get_game(self.channel_id)
        if game is None or game.get("started"):
            await interaction.response.send_message("ห้องนี้ไม่มีอยู่แล้วหรือเริ่มแข่งไปแล้ว", ephemeral=True)
            return False
        return True

    def refresh_components(self):
        self.clear_items()
        self.add_item(RuleSelect(self))
        self.add_item(RuleValueSelect(self))
        self.add_item(CloseSettingsButton())

    def build_embed(self) -> discord.Embed:
        game = get_game(self.channel_id)
        if game is None:
            return discord.Embed(title="ไม่พบเกม", color=discord.Color.red())
        rules = game.get("game_rules", {})
        weather = str(rules.get("Weather", "none")).lower()
        fast_mode = str(game.get("mob_render_mode", os.getenv("MOB_RENDER_MODE", "detailed"))).lower() == "compact"
        embed = discord.Embed(
            title="Race Settings",
            description="เมนูนี้มองเห็นและใช้งานได้เฉพาะผู้สร้างห้อง เลือกกฎและค่าที่ต้องการจาก dropdown",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="AllowSkill", value="เปิด" if get_game_rule(game, "AllowSkill") else "ปิด", inline=True)
        embed.add_field(name="DreamMode", value="เปิด" if get_game_rule(game, "DreamMode") else "ปิด", inline=True)
        embed.add_field(name="NoDebuff", value="เปิด" if get_game_rule(game, "NoDebuff") else "ปิด", inline=True)
        embed.add_field(name="Weather", value=WEATHER_LABELS.get(weather, weather), inline=True)
        embed.add_field(name="Fast Mode", value="เปิด · แสดงผลแบบข้อความ" if fast_mode else "ปิด · แสดงภาพผลทอย", inline=True)
        embed.set_footer(text=f"กำลังแก้: {RULE_LABELS.get(self.selected_rule, self.selected_rule)}")
        return embed


class RuleSelect(discord.ui.Select):
    def __init__(self, parent_view: SettingsView):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=label, value=key, default=key == parent_view.selected_rule)
            for key, label in RULE_LABELS.items()
        ]
        super().__init__(placeholder="เลือก Setting ที่ต้องการแก้", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.selected_rule = self.values[0]
        self.parent_view.refresh_components()
        await interaction.response.edit_message(embed=self.parent_view.build_embed(), view=self.parent_view)


class RuleValueSelect(discord.ui.Select):
    def __init__(self, parent_view: SettingsView):
        self.parent_view = parent_view
        game = get_game(parent_view.channel_id) or {}
        rule = parent_view.selected_rule
        if rule == "Weather":
            options = [discord.SelectOption(label=label, value=value) for value, label in WEATHER_LABELS.items()]
        elif rule == "FastMode":
            options = [
                discord.SelectOption(label="ปิด · แสดงภาพผลทอย", value="detailed"),
                discord.SelectOption(label="เปิด · แสดงผลแบบข้อความ", value="compact"),
            ]
        else:
            options = [discord.SelectOption(label="ปิด", value="false"), discord.SelectOption(label="เปิด", value="true")]
        super().__init__(placeholder="เลือกค่า", options=options, row=1)

    async def callback(self, interaction: discord.Interaction):
        game, error = _room_open(self.parent_view.channel_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        rule = self.parent_view.selected_rule
        value = self.values[0]
        if rule == "FastMode":
            game["mob_render_mode"] = value
        else:
            success, result = set_game_rule(
                self.parent_view.channel_id,
                rule,
                value if rule == "Weather" else value == "true",
            )
            if not success:
                await interaction.response.send_message(str(result), ephemeral=True)
                return
        await interaction.response.edit_message(embed=self.parent_view.build_embed(), view=self.parent_view)


class CloseSettingsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ปิด Settings", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ปิด Settings แล้ว", embed=None, view=None)


class AddBotView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=180)
        self.channel_id = channel_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        _, error = _room_open(self.channel_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Add Rookie", style=discord.ButtonStyle.primary, emoji="🤖")
    async def add_rookie(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="เลือกเลเวลของ Rookie ทั้ง 8 ตัว:",
            embed=None,
            view=RookieLevelView(self.channel_id),
        )

    @discord.ui.button(label="Add Uma", style=discord.ButtonStyle.success, emoji="🏇")
    async def add_uma(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="เลือกหน้าและตัวละคร Uma ที่ต้องการเพิ่ม:",
            embed=None,
            view=UmaPageView(self.channel_id),
        )

    @discord.ui.button(label="ยกเลิก", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="ปิดเมนู Add bot แล้ว", embed=None, view=None)


def level_options():
    return [discord.SelectOption(label=f"Level {level}", value=str(level)) for level in range(1, 9)]


class RookieLevelView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=180)
        self.channel_id = channel_id
        self.add_item(RookieLevelSelect(channel_id))


class RookieLevelSelect(discord.ui.Select):
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        super().__init__(placeholder="เลือกระดับ Rookie 1–8", options=level_options())

    async def callback(self, interaction: discord.Interaction):
        _, error = _room_open(self.channel_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        level = int(self.values[0])
        added = []
        for preset_key in ROOKIE_PRESET_KEYS:
            success, message = add_mob_from_preset(self.channel_id, preset_key, level)
            if not success:
                await interaction.response.send_message(message, ephemeral=True)
                return
            added.append(message)
        await interaction.response.edit_message(
            content=f"เพิ่ม Rookie ทั้ง 8 ตัวที่ Level {level} แล้ว\n" + "\n".join(added),
            embed=None,
            view=None,
        )


class UmaPageView(discord.ui.View):
    def __init__(self, channel_id: int, page: int = 0):
        super().__init__(timeout=180)
        self.channel_id = channel_id
        self.page = page
        start = page * UMA_PAGE_SIZE
        entries = UMA_PRESETS[start:start + UMA_PAGE_SIZE]
        self.add_item(UmaPresetSelect(channel_id, entries))
        self.add_item(UmaPageButton(channel_id, page, -1, disabled=page == 0))
        self.add_item(UmaPageButton(channel_id, page, 1, disabled=start + UMA_PAGE_SIZE >= len(UMA_PRESETS)))
        self.add_item(CancelAddBotButton())


class UmaPresetSelect(discord.ui.Select):
    def __init__(self, channel_id: int, entries):
        self.channel_id = channel_id
        options = [discord.SelectOption(label=data["name"][:100], value=key) for key, data in entries]
        super().__init__(placeholder="เลือกตัวละคร Uma", options=options or [discord.SelectOption(label="ไม่มีตัวละคร", value="__none__")], disabled=not options)

    async def callback(self, interaction: discord.Interaction):
        _, error = _room_open(self.channel_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        preset_key = self.values[0]
        if preset_key == "__none__":
            await interaction.response.send_message("ไม่พบตัวละครในหน้านี้", ephemeral=True)
            return
        preset = MOB_PRESETS[preset_key]
        await interaction.response.edit_message(
            content=f"เลือก **{preset['name']}** แล้ว เลือกระดับ 1–8:",
            embed=None,
            view=UmaLevelView(self.channel_id, preset_key, self.view.page),
        )


class UmaPageButton(discord.ui.Button):
    def __init__(self, channel_id: int, page: int, delta: int, *, disabled: bool = False):
        self.channel_id = channel_id
        self.page = page
        self.delta = delta
        label = "ก่อนหน้า" if delta < 0 else "หน้าถัดไป"
        super().__init__(label=label, style=discord.ButtonStyle.secondary, disabled=disabled, row=1)

    async def callback(self, interaction: discord.Interaction):
        _, error = _room_open(self.channel_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        page_count = max(1, (len(UMA_PRESETS) + UMA_PAGE_SIZE - 1) // UMA_PAGE_SIZE)
        next_page = min(page_count - 1, max(0, self.page + self.delta))
        await interaction.response.edit_message(
            content=f"เลือกหน้า {next_page + 1}/{page_count} และตัวละคร Uma ที่ต้องการเพิ่ม:",
            view=UmaPageView(self.channel_id, next_page),
        )


class UmaLevelView(discord.ui.View):
    def __init__(self, channel_id: int, preset_key: str, page: int = 0):
        super().__init__(timeout=180)
        self.channel_id = channel_id
        self.preset_key = preset_key
        self.add_item(UmaLevelSelect(channel_id, preset_key))
        self.add_item(ReturnToUmaPageButton(channel_id, page))


class UmaLevelSelect(discord.ui.Select):
    def __init__(self, channel_id: int, preset_key: str):
        self.channel_id = channel_id
        self.preset_key = preset_key
        super().__init__(placeholder="เลือกระดับ 1–8", options=level_options())

    async def callback(self, interaction: discord.Interaction):
        _, error = _room_open(self.channel_id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        success, message = add_mob_from_preset(self.channel_id, self.preset_key, int(self.values[0]))
        await interaction.response.edit_message(content=message if success else f"เพิ่มไม่สำเร็จ: {message}", embed=None, view=None if success else self.view)


class ReturnToUmaPageButton(discord.ui.Button):
    def __init__(self, channel_id: int, page: int):
        self.channel_id = channel_id
        self.page = page
        super().__init__(label="กลับไปเลือกตัวละคร", style=discord.ButtonStyle.secondary, row=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=f"เลือกหน้า {self.page + 1} และตัวละคร Uma ที่ต้องการเพิ่ม:",
            view=UmaPageView(self.channel_id, self.page),
        )


class CancelAddBotButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ยกเลิก", style=discord.ButtonStyle.danger, row=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="ปิดเมนู Add bot แล้ว", embed=None, view=None)
