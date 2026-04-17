from typing import Optional

from utils.skill_presets import SKILLS, ICON

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


def get_all_skills() -> dict:
    return SKILLS


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
        key: skill
        for key, skill in SKILLS.items()
        if skill.get("icon") == icon_type
    }


def get_skills_by_tag(tag: str) -> dict:
    tag_lower = tag.lower()
    return {
        key: skill
        for key, skill in SKILLS.items()
        if tag_lower in [t.lower() for t in skill.get("tags", [])]
    }


def get_skills_by_active_roll(active_roll: bool) -> dict:
    return {
        key: skill
        for key, skill in SKILLS.items()
        if skill.get("active_roll", False) == active_roll
    }


def describe_trigger(trigger: dict) -> str:
    parts = []

    if "path_type" in trigger:
        parts.append(f"เมื่ออยู่บน{PATH_TEXT.get(trigger['path_type'], 'สนามพิเศษ')}")

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

    if "target_distance_min" in trigger and "target_distance_max" in trigger:
        parts.append(
            f"เมื่อมีเป้าหมายอยู่ในระยะ {trigger['target_distance_min']} ถึง {trigger['target_distance_max']}"
        )

    return " • ".join(parts) if parts else "ไม่มีเงื่อนไขพิเศษ"


def describe_target(target: dict) -> str:
    scope = target.get("scope", "self")
    return TARGET_TEXT.get(scope, scope)


def describe_effect(effect: dict) -> str:
    effect_type = effect["type"]
    value = effect.get("value")
    duration = effect.get("duration")

    if effect_type == "modify_velocity":
        return f"เพิ่มผลรวมการวิ่ง +{value}" + (f" ({duration})" if duration else "")
    if effect_type == "modify_selected_die":
        return f"เพิ่มแต้มเต๋าที่ถูกเลือกทุกลูก +{value}" + (f" ({duration})" if duration else "")
    if effect_type == "modify_roll_floor":
        return f"เพิ่มแต้มขั้นต่ำของลูกเต๋า +{value}" + (f" ({duration})" if duration else "")
    if effect_type == "modify_roll_cap":
        sign = "+" if value >= 0 else ""
        return f"ปรับแต้มสูงสุดลูกเต๋า {sign}{value}" + (f" ({duration})" if duration else "")
    if effect_type == "add_dkh":
        return f"เพิ่มจำนวนลูกเต๋าและจำนวนลูกที่เลือก +{value}" + (f" ({duration})" if duration else "")
    if effect_type == "add_d":
        return f"เพิ่มจำนวนลูกเต๋า +{value}" + (f" ({duration})" if duration else "")
    if effect_type == "add_kh":
        return f"เพิ่มจำนวนลูกที่เลือก +{value}" + (f" ({duration})" if duration else "")
    if effect_type == "recover_stamina":
        return f"ฟื้นฟู Stamina +{value}"
    if effect_type == "reduce_stamina":
        return f"ลด Stamina เป้าหมาย -{value}"
    if effect_type == "flat_score_change":
        sign = "+" if value >= 0 else ""
        return f"ปรับคะแนนทันที {sign}{value}"
    if effect_type == "modify_gold_range":
        return f"เพิ่มระยะตรวจ Gold +{value}"
    if effect_type == "modify_enemy_gold_range":
        return f"ลดระยะตรวจ Gold ของศัตรู -{value}"
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

    return f"{effect_type}: {effect}"


def build_skill_description(skill_key: str) -> Optional[str]:
    skill = get_skill(skill_key)
    if skill is None:
        return None

    icon = ICON.get(skill["icon"], "")
    name = skill["name"]
    cooldown = skill.get("cooldown", 0)
    cost = skill.get("cost", 0)
    active_roll = "ใช้งานตอนทอยวิ่ง" if skill.get("active_roll") else "ทำงานอัตโนมัติ"

    trigger_text = describe_trigger(skill.get("trigger", {}))
    target_text = describe_target(skill.get("target", {}))
    effect_texts = [describe_effect(effect) for effect in skill.get("effects", [])]

    lines = [
        f"{icon} **{name}**",
        f"CD: {cooldown} เทิร์น | Cost: {cost}",
        f"ประเภท: {active_roll}",
        f"เป้าหมาย: {target_text}",
        f"เงื่อนไข: {trigger_text}",
        "ผลของสกิล:",
    ]

    for effect_text in effect_texts:
        lines.append(f"- {effect_text}")

    return "\n".join(lines)


def build_skill_list_text(skills: dict) -> str:
    if not skills:
        return "ไม่พบสกิล"

    lines = []
    for key, skill in skills.items():
        icon = ICON.get(skill.get("icon", ""), "")
        lines.append(f"{icon} `{key}` - {skill['name']}")

    return "\n".join(lines)