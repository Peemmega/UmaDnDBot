import discord

from utils.database import (
    update_player_stats,
)
from utils.icon_presets import STAT_EMOJIS, Status_Icon_Type
STATS_CAP = 8

def get_stat_emoji(value: int) -> str:
    value = max(1, min(value, 8))
    return STAT_EMOJIS[value]


def get_stat_icon(value: str) -> str:
    return Status_Icon_Type[value]


def build_stat_embed(user: discord.User | discord.Member, player: dict, title_text: str = "จัดการค่าสเตตัส") -> discord.Embed:
    embed = discord.Embed(
        title=f"{title_text}ของ {player['username']}",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(
        name="ค่าสเตตัส",
        value=(
            f"{get_stat_icon('SPD')} : {get_stat_emoji(player['speed'])} {player['speed']}\n"
            f"{get_stat_icon('STA')} : {get_stat_emoji(player['stamina'])} {player['stamina']}\n"
            f"{get_stat_icon('POW')} : {get_stat_emoji(player['power'])} {player['power']}\n"
            f"{get_stat_icon('GUT')} : {get_stat_emoji(player['gut'])} {player['gut']}\n"
            f"{get_stat_icon('WIT')} : {get_stat_emoji(player['wit'])} {player['wit']}"
        ),
        inline=False
    )

    embed.add_field(
        name="แต้มคงเหลือ",
        value=f"**Stats Point** : {player['stats_point']}",
        inline=False
    )

    embed.set_footer(text="ใช้ปุ่มด้านล่างเพื่อเพิ่มหรือลดค่าสเตตัส")
    return embed


class ProfileStatView(discord.ui.View):
    def __init__(self, user_id, player):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.player_cache = player.copy()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "มีแค่เจ้าของโปรไฟล์เท่านั้นที่ใช้ปุ่มนี้ได้",
                ephemeral=True
            )
            return False
        return True

    def refresh_button_state(self, player: dict):
        has_points = player["stats_point"] > 0

        for item in self.children:
            if not isinstance(item, discord.ui.Button):
                continue

            # ปุ่มเพิ่ม
            if item.custom_id and item.custom_id.startswith("add_"):
                item.disabled = not has_points

            # ปุ่มลด
            if item.custom_id == "remove_speed":
                item.disabled = player["speed"] <= 1
            elif item.custom_id == "remove_stamina":
                item.disabled = player["stamina"] <= 1
            elif item.custom_id == "remove_power":
                item.disabled = player["power"] <= 1
            elif item.custom_id == "remove_gut":
                item.disabled = player["gut"] <= 1
            elif item.custom_id == "remove_wit":
                item.disabled = player["wit"] <= 1


    async def update_message(self, interaction: discord.Interaction, player: dict, footer_text: str):
        self.refresh_button_state(player)
        embed = build_stat_embed(interaction.user, player)
        embed.set_footer(text=footer_text)
        await interaction.response.edit_message(embed=embed, view=self)

    async def add_stat(self, interaction, stat_name, short_name):
        player = self.player_cache

        if player["stats_point"] <= 0:
            await interaction.response.send_message("แต้มไม่พอ", ephemeral=True)
            return

        if player[stat_name] >= STATS_CAP:
            await interaction.response.send_message("ถึงขีดจำกัดแล้ว", ephemeral=True)
            return

        player[stat_name] += 1
        player["stats_point"] -= 1

        await self.update_message(interaction, player, f"เพิ่ม {short_name} +1")


    async def remove_stat(self, interaction, stat_name, short_name):
        player = self.player_cache

        if player[stat_name] <= 1:
            await interaction.response.send_message("ลดไม่ได้แล้ว", ephemeral=True)
            return

        player[stat_name] -= 1
        player["stats_point"] += 1

        await self.update_message(interaction, player, f"ลด {short_name} -1")

    # -------- แถวบน (เพิ่ม) --------
    @discord.ui.button(label="SPD +", style=discord.ButtonStyle.success, row=0, custom_id="add_speed")
    async def add_speed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.add_stat(interaction, "speed", 'SPD')

    @discord.ui.button(label="SPD -", style=discord.ButtonStyle.danger, row=1, custom_id="remove_speed")
    async def remove_speed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.remove_stat(interaction, "speed", 'SPD')

    @discord.ui.button(label="STA +", style=discord.ButtonStyle.success, row=0, custom_id="add_stamina")
    async def add_stamina_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.add_stat(interaction, "stamina", 'STA')

    @discord.ui.button(label="STA -", style=discord.ButtonStyle.danger, row=1, custom_id="remove_stamina")
    async def remove_stamina_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.remove_stat(interaction, "stamina", 'STA')

    @discord.ui.button(label="POW +", style=discord.ButtonStyle.success, row=0, custom_id="add_power")
    async def add_power_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.add_stat(interaction, "power", "POW")

    @discord.ui.button(label="POW -", style=discord.ButtonStyle.danger, row=1, custom_id="remove_power")
    async def remove_power_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.remove_stat(interaction, "power", "POW")

    @discord.ui.button(label="GUT +", style=discord.ButtonStyle.success, row=0, custom_id="add_gut")
    async def add_gut_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.add_stat(interaction, "gut", "GUT")

    @discord.ui.button(label="GUT -", style=discord.ButtonStyle.danger, row=1, custom_id="remove_gut")
    async def remove_gut_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.remove_stat(interaction, "gut", "GUT")

    @discord.ui.button(label="WIT +", style=discord.ButtonStyle.success, row=0, custom_id="add_wit")
    async def add_wit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.add_stat(interaction, "wit", "WIT")

    @discord.ui.button(label="WIT -", style=discord.ButtonStyle.danger, row=1, custom_id="remove_wit")
    async def remove_wit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.remove_stat(interaction, "wit", "WIT")

    @discord.ui.button(label="บันทึก", style=discord.ButtonStyle.primary, row=2)
    async def save_button(self, interaction, button):
        update_player_stats(
            self.user_id,
            speed=self.player_cache["speed"],
            stamina=self.player_cache["stamina"],
            power=self.player_cache["power"],
            gut=self.player_cache["gut"],
            wit=self.player_cache["wit"],
            stats_point=self.player_cache["stats_point"]
        )

        await interaction.response.send_message("บันทึกแล้ว", ephemeral=True)