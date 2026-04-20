import discord
from utils.zone.zone_manager import (
    get_player_zone,
    get_zone_points_left,
    get_zone_effect_preview,
    get_zone_effect
)
from utils.zone.zone_preset import (
    DEFAULT_ZONE_IMAGE
)

from utils.icon_presets import ICONS, Status_Icon_Type

ZONE_LABELS = {
    "flat": "Flat Total",
    "add_d": "Add Dice",
    "add_kh": "Keep High",
    "floor": "Floor",
    "selected_die": "Selected Die",
    "cap": "Cap",
    "self_heal_stamina": "Self Heal STA",
}

def build_zone_manage_embed(user_id: int, display_name: str) -> discord.Embed:
    zone = get_player_zone(user_id)
    if zone is None:
        return discord.Embed(
            title="Zone Manager",
            description="ไม่พบข้อมูลผู้เล่น",
            color=discord.Color.red()
        )
    return build_zone_manage_embed_from_zone(zone, display_name)

def build_zone_manage_embed_from_zone(
    zone: dict,
    display_name: str,
    selected_field: str | None = None,
    note: str | None = None
) -> discord.Embed:
    left = get_zone_points_left(zone)
    build = zone["build"]
    preview = get_zone_effect_preview(zone)

    zone_title = zone.get("name", "Default Zone")
    image_url = zone.get("image_url", "")

    stat_lines = []
    zone_labels = {
        "flat": f"{ICONS["Aoharu"]} เพิ่มคะแนนรวม",
        "add_d": f"{ICONS["Aoharu"]} เพิ่มลูกเต๋า",
        "add_kh": f"{ICONS["Aoharu"]} เพิ่มจำนวนลูกที่เลือก",
        "floor": f"{ICONS["Aoharu"]} เพิ่มแต้มลูกเต๋าขั้นต่ำ",
        "selected_die": f"{ICONS["Aoharu"]} เพิ่มแต้มลูกที่เลือก",
        "cap": f"{ICONS["Aoharu"]} เพิ่มแต้มลูกเต๋าสูงสุด",
        "self_heal_stamina": f"{ICONS["Aoharu"]} ฟื้นฟู Stamina",
    }

    for key, label in zone_labels.items():
        # cost = ZONE_POINT_COST[key]
        value = build.get(key, 0)
        prefix = "➤ " if key == selected_field else ""
        stat_lines.append(f"{prefix}{label}: **{value}**") # `cost {cost}`

    preview_lines = []
    if preview["flat"]:
        preview_lines.append(f"✨ เพิ่มผลรวม **+{preview['flat']}**")
    if preview["add_d"]:
        preview_lines.append(f"🎲 เพิ่มลูกเต๋า **+{preview['add_d']}**")
    if preview["add_kh"]:
        preview_lines.append(f"🖐️ เพิ่มจำนวนลูกที่เลือก **+{preview['add_kh']}**")
    if preview["floor"]:
        preview_lines.append(f"🧱 เพิ่มแต้มขั้นต่ำ **+{preview['floor']}**")
    if preview["selected_die"]:
        preview_lines.append(f"🎯 เพิ่มแต้มลูกที่เลือก **+{preview['selected_die']}**")
    if preview["cap"]:
        preview_lines.append(f"📈 เพิ่มแต้มสูงสุด **+{preview['cap']}**")
    if preview["self_heal_stamina"]:
        preview_lines.append(f"{Status_Icon_Type["STA"]} ฟื้นฟู STA ตัวเอง +{preview['self_heal_stamina']}")
    if not preview_lines:
        preview_lines.append("ยังไม่มีการอัป Zone")

    embed = discord.Embed(
        title=f"🌌 Zone Manager : {display_name}",
        description=(
            f"**「 {zone_title} 」**\n"
            f"โหมดปรับแต่งพลัง Zone พร้อมใช้งาน"
        ),
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🧬 Current Build",
        value="\n".join(stat_lines),
        inline=True
    )

    embed.add_field(
        name="🔮 Zone pt",
        value=(
            # f"**ทั้งหมด**: {zone['points']}\n"
            # f"**ใช้ไป**: {used}\n"
            f"**คงเหลือ**: {left}"
        ),
        inline=True
    )

    embed.add_field(
        name="__⚡ ความสามารถทั้งหมด__",
        value="\n".join(preview_lines),
        inline=False
    )

    guide_text = (
        "เลือกหมวดจากเมนูด้านล่าง แล้วกด **เพิ่ม** หรือ **ลด**\n"
        "กด **💾 บันทึก** เมื่อพอใจกับค่าที่อัปแล้ว"
    )
    if note:
        guide_text += f"\n\n**ล่าสุด:** {note}"

    embed.add_field(
        name="__🛠️ วิธีใช้งาน__",
        value=guide_text,
        inline=False
    )

    if image_url:
        embed.set_image(url=image_url)

    embed.set_footer(text="Zone tuning panel • Customize your awakening")
    return embed

def build_zone_used_preview_embed(player: dict) -> discord.Embed:
    zone = player.get("zone")

    if not zone:
        return discord.Embed(
            title="❌ Zone Error",
            description="ไม่พบข้อมูล Zone",
            color=discord.Color.red()
        )

    zone_name = zone.get("name", "Default Zone")
    zone_img = zone.get("image_url", DEFAULT_ZONE_IMAGE)
    result_text = get_zone_effect(zone)

    embed = discord.Embed(
        title=f"🌌 {player.get('username', 'Unknown')} ใช้งาน Zone:\n【{zone_name}】",
        description=result_text,
        color=discord.Color.purple()
    )

    embed.set_image(url=zone_img)
    embed.set_footer(text="Zone Preview • ยังไม่ได้ใช้จริง")

    return embed