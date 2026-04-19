import discord
from utils.zone.zone_preset import DEFAULT_ZONE_IMAGE
from utils.zone.zone_manager import (
    get_player_zone,
    get_zone_points_used,
    get_zone_points_left,
    get_zone_effect_preview
)

ZONE_LABELS = {
    "flat": "Flat Total",
    "add_d": "Add Dice",
    "add_kh": "Keep High",
    "floor": "Floor",
    "selected_die": "Selected Die",
    "cap": "Cap",
}

ZONE_PREVIEW_LABELS = {
    "flat": "ผลรวม",
    "add_d": "ลูกเต๋า",
    "add_kh": "ลูกที่เลือก",
    "floor": "ขั้นต่ำ",
    "selected_die": "ลูกที่เลือก +",
    "cap": "สูงสุด",
}


def build_zone_manage_embed(user_id: int, display_name: str) -> discord.Embed:
    zone = get_player_zone(user_id)

    if zone is None:
        return discord.Embed(
            title="Zone Manager",
            description="ไม่พบข้อมูลผู้เล่น",
            color=discord.Color.red()
        )

    used = get_zone_points_used(zone)
    left = get_zone_points_left(zone)
    build = zone["build"]
    preview = get_zone_effect_preview(zone)

    lines = []
    for key, label in ZONE_LABELS.items():
        lines.append(f"**{label}**: {build.get(key, 0)}")

    preview_lines = []
    if preview["flat"]:
        preview_lines.append(f"เพิ่มผลรวม +{preview['flat']}")
    if preview["add_d"]:
        preview_lines.append(f"เพิ่มลูกเต๋า +{preview['add_d']}")
    if preview["add_kh"]:
        preview_lines.append(f"เพิ่มจำนวนลูกที่เลือก +{preview['add_kh']}")
    if preview["floor"]:
        preview_lines.append(f"เพิ่มแต้มขั้นต่ำ +{preview['floor']}")
    if preview["selected_die"]:
        preview_lines.append(f"เพิ่มแต้มลูกที่เลือก +{preview['selected_die']}")
    if preview["cap"]:
        preview_lines.append(f"เพิ่มแต้มสูงสุด +{preview['cap']}")

    if not preview_lines:
        preview_lines.append("ยังไม่มีการอัป Zone")

    embed = discord.Embed(
        title=f"🌌 Zone Manager : {display_name}",
        description=f"**Zone Name:** {zone['name']}",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Zone Points",
        value=(
            f"ทั้งหมด: {zone['points']}\n"
            f"ใช้ไป: {used}\n"
            f"คงเหลือ: {left}"
        ),
        inline=True
    )

    embed.add_field(
        name="Build",
        value="\n".join(lines),
        inline=True
    )

    embed.add_field(
        name="Preview เมื่อใช้ Zone",
        value="\n".join(preview_lines),
        inline=False
    )

    embed.add_field(
        name="วิธีใช้",
        value=(
            "เลือกหมวดจากเมนูด้านล่าง แล้วกด ➕ หรือ ➖\n"
            "ค่า Zone จะถูกบันทึกลง player data ทันที"
        ),
        inline=False
    )

    if zone.get("image_url"):
        embed.set_image(url=zone["image_url"])
    else:
        embed.set_image(url=DEFAULT_ZONE_IMAGE)

    return embed