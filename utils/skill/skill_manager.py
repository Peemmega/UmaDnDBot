from typing import Optional
import discord
from utils.skill.skill_presets import SKILLS, ICON
from utils.icon_presets import Status_Icon_Type
from utils.database import ensure_player, set_player_skill_slot, get_player_skill_slots

PATH_TEXT = {
    1: "ทางตรง",
    2: "ทางโค้ง",
    3: "เนินขึ้น",
    4: "เนินลง",
}

STYLE_TEXT = {
    "Front": "Front",
    "Pace": "Pace",
    "Late": "Late",
    "End": "End",
}

TARGET_TEXT = {
    "self": "ตัวเอง",
    "nearest_front": "เป้าหมายด้านหน้าที่ใกล้ที่สุด",
    "nearest_back": "เป้าหมายด้านหลังที่ใกล้ที่สุด",
    "all_front": "ผู้เล่นด้านหน้าทั้งหมด",
    "all_back": "ผู้เล่นด้านหลังทั้งหมด",
    "random_enemy": "ศัตรูแบบสุ่ม",
}

from utils.skill.skill_presets import SKILLS, ICON


def get_skill_display(skill_id: str) -> str:
    skill = SKILLS.get(skill_id)
    if not skill:
        return f"❓ `{skill_id}`"

    icon_key = skill.get("icon")
    emoji = ICON.get(icon_key, "❓")

    return f"{emoji} `{skill_id}` - **{skill['name']}**"


def get_skill_short(skill_id: str) -> str:
    skill = SKILLS.get(skill_id)
    if not skill:
        return "❓"

    emoji = ICON.get(skill.get("icon"), "❓")
    return f"{emoji} **{skill['name']}**"


def get_all_skills() -> dict:
    return SKILLS


def normalize_duration(duration: str | None) -> str:
    if duration == "this_roll":
        return "รอบนี้"
    if duration == "this_turn":
        return "เทิร์นนี้"
    if duration == "next_turn":
        return "เทิร์นหน้า"
    return ""


def get_skill(skill_key: str) -> Optional[dict]:
    return SKILLS.get(skill_key)


def find_skill_by_name(name: str) -> Optional[tuple[str, dict]]:
    name_lower = name.strip().lower()

    for key, skill in SKILLS.items():
        if key.lower() == name_lower or skill["name"].lower() == name_lower:
            return key, skill

    return None


def get_skills_by_icon(icon_type: str) -> dict:
    return {
        key: skill for key, skill in SKILLS.items() if skill.get("icon") == icon_type
    }


def get_skills_by_tag(tag: str) -> dict:
    tag_lower = tag.lower()
    return {
        key: skill
        for key, skill in SKILLS.items()
        if tag_lower in [t.lower() for t in skill.get("tags", [])]
    }


def get_skill_emoji(skill_id: str) -> str:
    skill = SKILLS.get(skill_id)
    if not skill:
        return "❓"
    return ICON.get(skill.get("icon"), "❓")


def build_skill_list_embed(
    skills: dict, title: str = "📘 รายชื่อสกิลทั้งหมด"
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=build_skill_list_text(skills),
        color=discord.Color.blurple(),
    )
    return embed


def build_skill_tag_embed(tag_value: str):
    skills = get_skills_by_tag(tag_value)

    embed = discord.Embed(title=f"🏷️ สกิล tag: {tag_value}", color=discord.Color.teal())

    if not skills:
        embed.description = "ไม่พบสกิล"
        return embed

    count = 0
    for skill_id in skills.keys():
        desc = build_skill_description(skill_id)
        if len(desc) > 1024:
            desc = desc[:1000] + "..."

        embed.add_field(name="", value=desc, inline=False)

        count += 1
        if count >= 25:
            embed.set_footer(text="แสดงสูงสุด 25 สกิล")
            break

    return embed


def build_skill_card_text(skill_id: str | None) -> str:
    if not skill_id:
        return "➖ **ว่าง**"

    skill = SKILLS.get(skill_id)
    if not skill:
        return f"❓ `{skill_id}` ไม่พบข้อมูล"

    emoji = ICON.get(skill.get("icon"), "❓")
    name = skill["name"]
    cooldown = skill.get("cooldown", 0)
    cost = skill.get("cost", 0)
    activation_text = "🟣 Passive: ทำงานอัตโนมัติ\n" if skill.get("activation") == "passive" else ""

    trigger_text = describe_trigger(skill.get("trigger", {}))
    target_text = describe_target(skill.get("target", {}))
    effect_texts = [describe_effect(effect) for effect in skill.get("effects", [])]
    effect_text = "\n".join(f"• {text}" for text in effect_texts)

    return (
        f"{emoji} `{skill_id}` **{name}**\n"
        f"{activation_text}"
        f"⏱️ {cooldown} | {Status_Icon_Type['WIT']} {cost}\n"
        f"**เป้าหมาย:** {target_text}\n"
        f"**เงื่อนไข:** {trigger_text}\n"
        f"ผล: {effect_text}\n"
        f"--------------------------------------"
    )


POSITION_GROUP_TEXT = {
    "front": "กลุ่มหน้า",
    "middle": "กลุ่มกลาง",
    "back": "กลุ่มท้าย",
}


def describe_trigger(trigger: dict) -> str:
    parts = []

    if "path_type" in trigger:
        parts.append(f"เมื่ออยู่บน{PATH_TEXT.get(trigger['path_type'], 'สนามพิเศษ')}")

    if "distance_type" in trigger:
        parts.append(f"เมื่ออยู่ในสนามระยะ {trigger['distance_type']}")

    if "track" in trigger:
        parts.append(f"เมื่ออยู่บนสนาม {str(trigger['track']).title()}")

    if "style" in trigger:
        parts.append(f"สำหรับสาย {STYLE_TEXT.get(trigger['style'], trigger['style'])}")

    if "turn_min" in trigger and "turn_max" in trigger:
        if trigger["turn_min"] == trigger["turn_max"]:
            parts.append(f"ในเทิร์น {trigger['turn_min']}")
        else:
            parts.append(f"ในช่วงเทิร์น {trigger['turn_min']}-{trigger['turn_max']}")

    if "phase_min" in trigger and "phase_max" in trigger:
        if trigger["phase_min"] == trigger["phase_max"]:
            parts.append(f"ใน Phase {trigger['phase_min']}")
        else:
            parts.append(f"ในช่วง Phase {trigger['phase_min']}-{trigger['phase_max']}")

    if trigger.get("lastspurt") is True:
        parts.append("ในช่วง Last Spurt")

    if trigger.get("last_corner") is True:
        parts.append("ในโค้งสุดท้าย")

    if trigger.get("front_blocked") is True:
        parts.append("มีคู่แข่งในระยะ 20 ช่องด้านหน้า")

    if trigger.get("nearby_uma_count") is not None:
        parts.append(f"มีคู่แข่ง {trigger['nearby_uma_count']} คนหรือมากกว่าในกลุ่ม")

    if trigger.get("skill_use_count_min") is not None:
        parts.append(
            f"ใช้สกิลแล้วอย่างน้อย {trigger['skill_use_count_min']} ครั้งในการแข่งขันนี้"
        )

    if trigger.get("base_stats_min"):
        stat_text = ", ".join(
            f"{stat.title()} ≥ {value}"
            for stat, value in trigger["base_stats_min"].items()
        )
        parts.append(f"Stats พื้นฐาน: {stat_text}")

    if "target_distance_min" in trigger and "target_distance_max" in trigger:
        parts.append(
            f"เมื่อมีเป้าหมายอยู่ในระยะ {trigger['target_distance_min']} ถึง {trigger['target_distance_max']}"
        )

    if "position_group" in trigger:
        parts.append(
            f"เมื่ออยู่ใน{POSITION_GROUP_TEXT.get(trigger['position_group'], trigger['position_group'])}"
        )

    return " • ".join(parts) if parts else "ไม่มีเงื่อนไขพิเศษ"


def describe_target(target: dict) -> str:
    return TARGET_TEXT.get(target.get("scope", "self"), target.get("scope", "self"))


def describe_effect(effect: dict) -> str:
    effect_type = effect["type"]
    value = effect.get("value")
    duration = effect.get("duration")
    condition = effect.get("condition")
    condition_text = (
        f" (เฉพาะเมื่อ {describe_trigger(condition)})" if condition else ""
    )

    dur = normalize_duration(duration)

    if effect_type == "modify_velocity":
        return f"เพิ่มผลรวมการวิ่ง +{value}" + (f" ({dur})" if dur else "") + condition_text
    if effect_type == "modify_race_stats":
        stats = effect.get("stats", effect.get("stat", "all"))
        if stats == "all":
            return f"เพิ่มทุก Stats +{value} เฉพาะการแข่งขันนี้" + condition_text
        if isinstance(stats, dict):
            stat_text = ", ".join(f"{stat.title()} {delta:+}" for stat, delta in stats.items())
            return f"ปรับ Stats ({stat_text}) เฉพาะการแข่งขันนี้" + condition_text
        return f"เพิ่ม {str(stats).title()} +{value} เฉพาะการแข่งขันนี้" + condition_text
    if effect_type == "modify_roll_floor":
        return f"เพิ่มแต้มขั้นต่ำของลูกเต๋า +{value}" + (f" ({dur})" if dur else "")
    if effect_type == "modify_roll_cap":
        sign = "+" if value >= 0 else ""
        return f"ปรับแต้มสูงสุดลูกเต๋า {sign}{value}" + (f" ({dur})" if dur else "")
    if effect_type in {"modify_roll_cap_floor", "cap_floor"}:
        cap = effect.get("cap", value)
        floor = effect.get("floor", value)
        return f"ปรับแต้มสูงสุดลูกเต๋า {cap}, เพิ่มแต้มขั้นต่ำของลูกเต๋า {floor}" + (
            f" ({dur})" if dur else ""
        ) + condition_text
    if effect_type == "add_dkh":
        return f"เพิ่มจำนวนลูกเต๋าและจำนวนลูกที่เลือก +{value}" + (
            f" ({dur})" if dur else ""
        )
    if effect_type == "add_d":
        return f"เพิ่มจำนวนลูกเต๋า +{value}" + (f" ({dur})" if dur else "")
    if effect_type == "add_kh":
        return f"เพิ่มจำนวนลูกที่เลือก +{value}" + (f" ({dur})" if dur else "")

    if effect_type in ["recover_stamina"]:
        return f"ฟื้นฟู {Status_Icon_Type['STA']} +{value}{condition_text}"

    if effect_type in ["modify_current_speed"]:
        return f"เร่งความเร็วปัจจุบัน {value} ระดับ"

    if effect_type == "resolve_pending_lane_now":
        return "ย้ายไป Lane ที่ตั้งรอไว้ทันที"
    if effect_type == "activate_random_equipped_skills":
        return (
            f"สุ่มใช้สกิลติดตั้ง {effect.get('count', 2)} สกิลทันที "
            f"(Cost ไม่เกิน {effect.get('max_cost', 80)}, ไม่หัก Wit, "
            "ข้ามและไม่ทำให้ติด CD, ข้ามเงื่อนไข และไม่รวมสกิลนี้เอง)"
        )
    if effect_type == "self_heal_stamina":
        return f"ฟื้นฟู {Status_Icon_Type['STA']} ให้ตัวเอง +{value}"
    if effect_type == "reduce_stamina":
        return f"ลด {Status_Icon_Type['STA']} เป้าหมาย -{value}"
    if effect_type == "force_rush":
        return f"บังคับเป้าหมายใช้ Rush"
    if effect_type == "flat_total":
        sign = "+" if value >= 0 else ""
        return f"ปรับคะแนนทันที {sign}{value}"
    if effect_type == "modify_gold_range":
        return f"เพิ่มระยะตรวจ Gold +{value}"
    if effect_type == "modify_enemy_gold_range":
        return f"ลดระยะตรวจ Gold ของศัตรู {value}"
    if effect_type == "modify_gold_lane_range":
        sign = "+" if value >= 0 else ""
        return f"ปรับช่วง Gold Lane ของตัวเอง {sign}{value}" + (
            f" ({dur})" if dur else ""
        )
    if effect_type == "modify_enemy_gold_lane_range":
        return f"ลดช่วง Gold Lane ของศัตรู {abs(value)}" + (f" ({dur})" if dur else "")
    if effect_type == "apply_debuff_next_turn":
        stat = effect.get("stat", "unknown")
        return f"ทำให้เป้าหมายได้รับดีบัฟเทิร์นหน้า {stat} {value}"
    if effect_type == "apply_buff_next_turn":
        stat = effect.get("stat", "unknown")
        return f"ได้รับบัฟเทิร์นหน้า {stat} +{value}"
    if effect_type == "block_reroll":
        return "ทำให้ไม่สามารถใช้ Reroll ได้"
    if effect_type == "force_path_bonus":
        return f"เปลี่ยนผลของเส้นทาง +{value}"
    if effect_type == "modify_start_loss":
        return f"ลดผลเสียช่วงออกตัว {value}"

    return str(effect)


def build_skill_description(skill_id: str) -> str:
    skill = SKILLS.get(skill_id)
    if not skill:
        return f"❓ `{skill_id}`"

    emoji = get_skill_emoji(skill_id)
    activation_text = "🟣 Passive: ทำงานอัตโนมัติ\n" if skill.get("activation") == "passive" else ""
    trigger_text = describe_trigger(skill.get("trigger", {}))
    target_text = describe_target(skill.get("target", {}))
    effects = "\n".join(
        f"• {describe_effect(effect)}" for effect in skill.get("effects", [])
    )

    return (
        f"{emoji} `{skill_id}` **{skill['name']}**\n"
        f"{activation_text}"
        f"⏱️: {skill.get('cooldown', 0)} | {Status_Icon_Type['WIT']}: {skill.get('cost', 0)}\n"
        f"เป้าหมาย: {target_text}\n"
        f"เงื่อนไข: {trigger_text}\n"
        f"ผล:\n{effects}"
    )


def build_skill_embed_from_dict(skills: dict, title: str):
    return discord.Embed(
        title=title,
        description=build_skill_list_text(skills) or "ไม่พบสกิล",
        color=discord.Color.blurple(),
    )


def filter_skills(skills: dict, *, style=None, distance=None) -> dict:
    result = {}

    for key, skill in skills.items():
        trigger = skill.get("trigger", {})

        # เช็ค style
        if style:
            s = trigger.get("style")
            if isinstance(s, list):
                if style not in s:
                    continue
            elif s != style:
                continue

        # เช็ค distance
        if distance:
            d = trigger.get("distance_type")
            if isinstance(d, list):
                if distance not in d:
                    continue
            elif d != distance:
                continue

        result[key] = skill

    return result


def build_skill_list_text(skills: dict) -> str:
    if not skills:
        return "ไม่พบสกิล"

    lines = []
    for key, skill in skills.items():
        icon = ICON.get(skill.get("icon", ""), "")
        lines.append(f"{icon} `{key}` - {skill['name']}")

    return "\n".join(lines)


def build_skill_detail_embed(skills: dict, title: str) -> discord.Embed:
    embed = discord.Embed(title=title, color=discord.Color.gold())

    if not skills:
        embed.description = "ไม่พบสกิล"
        return embed

    count = 0
    for skill_id in skills.keys():
        desc = build_skill_description(skill_id)

        if len(desc) > 1024:
            desc = desc[:1000] + "..."

        embed.add_field(name="", value=desc, inline=False)

        count += 1
        if count >= 25:
            embed.set_footer(text="แสดงสูงสุด 25 สกิล")
            break

    return embed
