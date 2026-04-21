import copy
import discord

from utils.database import reset_zone_build
from utils.zone.zone_manager import (
    get_player_zone,
    get_zone_points_left,
    set_player_zone_build,
    ZONE_POINT_COST,
)
from utils.zone.zone_embed import build_zone_manage_embed_from_zone

ZONE_OPTIONS = [
    discord.SelectOption(label="เพิ่มคะแนน", value="flat", description="เพิ่มผลรวมโดยตรง | cost 1"),
    discord.SelectOption(label="เพิ่มลูกเต๋า", value="add_dkh", description="เพิ่มจำนวนลูกเต๋า | cost 3"),
    discord.SelectOption(label="เพิ่มพื้นลูกเต๋า", value="floor", description="เพิ่มแต้มขั้นต่ำ | cost 1"),
    discord.SelectOption(label="เพราะคะแนนลูกเต๋าที่เลือก", value="selected_die", description="เพิ่มแต้มลูกที่เลือก | cost 1"),
    discord.SelectOption(label="เพิ่มแต้มสูงสุดลูกเต๋า", value="cap", description="เพิ่มแต้มสูงสุด | cost 1"),
    discord.SelectOption(label="ฟื้นฟู Stamina", value="self_heal_stamina", description="ฟื้นฟู STA ตัวเอง | cost 1"),
]


class ZoneFieldSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="เลือกค่าสำหรับอัป Zone",
            min_values=1,
            max_values=1,
            options=ZONE_OPTIONS
        )

    async def callback(self, interaction: discord.Interaction):
        view: ZoneManageView = self.view
        view.selected_field = self.values[0]

        embed = build_zone_manage_embed_from_zone(
            view.temp_zone,
            interaction.user.display_name,
            selected_field=view.selected_field,
            note="เลือกหมวดสำหรับปรับค่าแล้ว"
        )
        await interaction.response.edit_message(embed=embed, view=view)


class ZoneManageView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.selected_field = "flat"

        zone = get_player_zone(user_id)
        if not zone:
            zone = {
                "name": "Default Zone",
                "build": {key: 0 for key in ZONE_POINT_COST.keys()},
                "image_url": ""
            }

        zone.setdefault("build", {})
        for key in ZONE_POINT_COST.keys():
            zone["build"].setdefault(key, 0)

        self.original_zone = copy.deepcopy(zone)
        self.temp_zone = copy.deepcopy(zone)

        self.add_item(ZoneFieldSelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("ปุ่มนี้ไม่ใช่ของคุณ", ephemeral=True)
            return False
        return True

    def _add_temp_stat(self, field: str, amount: int = 1) -> tuple[bool, str]:
        build = self.temp_zone["build"]
        cost = ZONE_POINT_COST[field] * amount
        left = get_zone_points_left(self.temp_zone)

        if left < cost:
            return False, f"Zone point ไม่พอ (ต้องใช้ {cost})"

        build[field] = int(build.get(field, 0)) + amount
        return True, f"เพิ่ม {field} +{amount} ชั่วคราว"

    def _remove_temp_stat(self, field: str, amount: int = 1) -> tuple[bool, str]:
        build = self.temp_zone["build"]
        current = int(build.get(field, 0))

        if current - amount < 0:
            return False, "ค่านี้ต่ำกว่า 0 ไม่ได้"

        build[field] = current - amount
        return True, f"ลด {field} -{amount} ชั่วคราว"

    @discord.ui.button(label="➕ เพิ่ม", style=discord.ButtonStyle.success)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, msg = self._add_temp_stat(self.selected_field, 1)
        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        embed = build_zone_manage_embed_from_zone(
            self.temp_zone,
            interaction.user.display_name,
            selected_field=self.selected_field,
            note=msg
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="➖ ลด", style=discord.ButtonStyle.danger)
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ok, msg = self._remove_temp_stat(self.selected_field, 1)
        if not ok:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        embed = build_zone_manage_embed_from_zone(
            self.temp_zone,
            interaction.user.display_name,
            selected_field=self.selected_field,
            note=msg
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="💾 บันทึก", style=discord.ButtonStyle.primary)
    async def save_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        set_player_zone_build(self.user_id, self.temp_zone["build"])
        self.original_zone = copy.deepcopy(self.temp_zone)

        embed = build_zone_manage_embed_from_zone(
            self.temp_zone,
            interaction.user.display_name,
            selected_field=self.selected_field,
            note="บันทึกค่า Zone เรียบร้อยแล้ว"
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="↺ รีเซ็ต", style=discord.ButtonStyle.secondary)
    async def reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        reset_zone_build(self.temp_zone)
        self.selected_field = "flat"

        embed = build_zone_manage_embed_from_zone(
            self.temp_zone,
            interaction.user.display_name,
            selected_field=self.selected_field,
            note="รีเซ็ตแต้ม Zone ชั่วคราวแล้ว กรุณากด 💾 บันทึก เพื่อยืนยัน"
        )
        await interaction.response.edit_message(embed=embed, view=self)