import discord

from utils.game_manager import add_mob_from_preset, create_game, get_game, set_game_rule
from utils.mob.mob_presets import MOB_PRESETS
from utils.race.legend_race_presets import LEGEND_RACE_PRESETS
from utils.race.race_presets import RACE_PRESET
from utils.race.race_weather import WEATHER_RULE
from views.create_game_view import build_lobby_message_payload
from views.join_view import LobbyView


def _preset_labels(preset_key: str, preset: dict) -> tuple[str, str]:
    legend = MOB_PRESETS.get(preset.get("legend_key"), {})
    stage = RACE_PRESET.get(preset.get("stage_key"), {})
    legend_name = legend.get("name", preset.get("legend_key", preset_key))
    stage_name = stage.get("name", preset.get("stage_key", "?"))
    mob_level = int((preset.get("mobs") or {}).get("level", 2))
    detail = (
        f"{stage_name} · Legend Lv.{int(preset.get('legend_level', 1))} · "
        f"Mob Lv.{mob_level} · {preset.get('record_type', 'official')}"
    )
    return legend_name, detail


def _valid_presets() -> dict[str, dict]:
    return {
        key: preset
        for key, preset in LEGEND_RACE_PRESETS.items()
        if preset.get("legend_key") in MOB_PRESETS and preset.get("stage_key") in RACE_PRESET
    }


def build_legend_preset_menu_embed() -> discord.Embed:
    presets = _valid_presets()
    lines = []
    for key, preset in presets.items():
        name, detail = _preset_labels(key, preset)
        lines.append(f"• **{name}** — {detail}")
    embed = discord.Embed(
        title="🏟️ Create Legend Race",
        description=(
            "เลือก Legend preset ที่ต้องการสร้าง\n\n" + ("\n".join(lines) if lines else "ยังไม่มี Legend preset")
        ),
        color=discord.Color.gold(),
    )
    embed.set_footer(text="สนาม, ระดับ Legend, Mob และสภาพอากาศจะตั้งตาม preset")
    return embed


def setup_legend_game(channel_id: int, owner_id: int, preset_key: str) -> tuple[bool, str]:
    preset = LEGEND_RACE_PRESETS.get(preset_key)
    if not preset:
        return False, "ไม่พบ Legend preset"
    if preset.get("legend_key") not in MOB_PRESETS or preset.get("stage_key") not in RACE_PRESET:
        return False, "Legend preset ไม่ถูกต้อง"
    if not create_game(channel_id, preset["stage_key"], owner_id, is_legend=True):
        return False, "สร้างไม่สำเร็จ (ห้องนี้อาจมีเกมอยู่แล้ว)"

    game = get_game(channel_id)
    game["legend_key"] = preset["legend_key"]
    game["legend_preset_key"] = preset_key
    game["record_type"] = preset.get("record_type", "official")
    set_game_rule(channel_id, WEATHER_RULE, preset.get("weather", "none"))

    for player_id, player in list(game["players"].items()):
        if player.get("is_mob"):
            del game["players"][player_id]

    add_mob_from_preset(channel_id, preset["legend_key"], int(preset.get("legend_level", 1)))
    mob_level = int((preset.get("mobs") or {}).get("level", 2))
    for mob_key in RACE_PRESET.get("Debut", {}).get("auto_mobs", []):
        if mob_key in MOB_PRESETS:
            add_mob_from_preset(channel_id, mob_key, mob_level)
    return True, ""


class LegendPresetSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for key, preset in list(_valid_presets().items())[:25]:
            name, detail = _preset_labels(key, preset)
            options.append(discord.SelectOption(label=name[:100], description=detail[:100], value=key))
        if not options:
            options.append(discord.SelectOption(label="ไม่มี Legend preset", value="__none__"))
        super().__init__(placeholder="เลือก Legend preset", options=options, disabled=options[0].value == "__none__")

    async def callback(self, interaction: discord.Interaction):
        view: "LegendPresetSelectView" = self.view
        if not interaction.guild or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("เฉพาะ Admin ผู้เปิดเมนูเท่านั้นที่สร้างเกมได้", ephemeral=True)
            return

        success, message = setup_legend_game(view.channel_id, interaction.user.id, self.values[0])
        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        embed, file = build_lobby_message_payload(view.channel_id)
        await interaction.response.defer()
        try:
            await interaction.delete_original_response()
        except (discord.NotFound, discord.HTTPException):
            pass

        if file:
            await interaction.channel.send(file=file, view=LobbyView(view.channel_id))
        else:
            await interaction.channel.send(embed=embed, view=LobbyView(view.channel_id))


class LegendPresetSelectView(discord.ui.View):
    def __init__(self, channel_id: int, owner_id: int):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.add_item(LegendPresetSelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("เมนู Legend Race นี้ใช้ได้เฉพาะผู้สร้างคำสั่ง", ephemeral=True)
            return False
        return True
