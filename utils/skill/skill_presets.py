from utils.icon_presets import SKILL_ICONS

# Selected at startup using BOT_EMOJI_SET (main or test).  Existing presets use
# the rare variants; the lowercase keys are reserved for common skill presets.
RARE_ICON_KEYS = {
    "Concentration": "Concentration_rare",
    "Acceleration": "Acceleration_rare",
    "Velocity": "Velocity_rare",
    "Passive": "Passive_rare",
    "Navigation": "Navigation_rare",
    "Recovery": "Recovery_rare",
    "DecreaseVelocity": "DecreaseVelocity_rare",
    "ReduceSTA": "ReduceSTA_rare",
    "LookUp": "LookUp_rare",
    "Blind": "Blind_rare",
}

COMMON_ICON_KEYS = {
    "acceleration": "Acceleration",
    "velocity": "Velocity",
    "stamina": "Recovery",
    "navigation": "Navigation",
    "passive": "Passive",
}

ICON = {
    **SKILL_ICONS,
    **{
        rare_key: SKILL_ICONS[icon_key]
        for icon_key, rare_key in RARE_ICON_KEYS.items()
    },
    **{
        common_key: SKILL_ICONS[icon_key]
        for common_key, icon_key in COMMON_ICON_KEYS.items()
    },
}

ICON_URL = {
    "Concentration_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292466570100956/Concentration.png?ex=6a567e21&is=6a552ca1&hm=ba72a3078b0e0cd3cc9ba5128a8280d78bfb14de88c696fe40855a455a597a97&=&format=webp&quality=lossless&width=240&height=240",
    "Acceleration_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292465185722469/Acceleration.png?ex=6a567e20&is=6a552ca0&hm=5887f9dfc6348323c2e75c277470052d38bf9d8f15d50b9e84182107fdf32f67&=&format=webp&quality=lossless&width=240&height=240",
    "Velocity_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292464552640652/Velocity.png?ex=6a567e20&is=6a552ca0&hm=cdec2ebfd23657a87bdcecbfd11d1c8dfd528917561d628b792825a64d017add&=&format=webp&quality=lossless&width=240&height=240",
    "Passive_rare": "https://cdn.discordapp.com/attachments/697810514448744448/1543574020023128115/Passive.png?ex=6a955cd4&is=6a940b54&hm=b50e5dd13c0a5e306d9faa48953d051cdf73d6bb89838d87b3b4baca5ce73766",
    "passive": "https://cdn.discordapp.com/attachments/697810514448744448/1543574020023128115/Passive.png?ex=6a955cd4&is=6a940b54&hm=b50e5dd13c0a5e306d9faa48953d051cdf73d6bb89838d87b3b4baca5ce73766",
    "Navigation_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292468520321267/Navigation.png?ex=6a567e21&is=6a552ca1&hm=bd100dd98982668b999927406c724fdc5cc8d68c2e366286ee9446d03a85b545&=&format=webp&quality=lossless&width=240&height=240",
    "Recovery_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292463436693565/Recovery.png?ex=6a567e20&is=6a552ca0&hm=a8f676d62e27898fcfe21a282a019de5585a298635afa011ec96b472c97f56e1&=&format=webp&quality=lossless&width=240&height=240",
    "DecreaseVelocity_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292466993467513/DecreaseVelocity.png?ex=6a567e21&is=6a552ca1&hm=a12f7f4f7803e42dded5b924be383355dc1bd0861067e8018cd67822bce2f9d7&=&format=webp&quality=lossless&width=240&height=240",
    "ReduceSTA_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292463990472745/ReduceSTA.png?ex=6a567e20&is=6a552ca0&hm=4440cdf2afbcada9225a656eb455334b54e5a8c4fe7bd2377b9c945279ef27ee&=&format=webp&quality=lossless&width=240&height=240",
    "LookUp_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292467794837644/LookUp.png?ex=6a567e21&is=6a552ca1&hm=3b9ea7d0b5969d7c01acbc51b002861014736acf8e78404dfd1402fa01b6b369&=&format=webp&quality=lossless&width=240&height=240",
    "Blind_rare": "https://media.discordapp.net/attachments/697810514448744448/1526292465932566711/Blind.png?ex=6a567e21&is=6a552ca1&hm=5600daab0bbce3ea5864c631eebd5c9e4ea47eae2ebae7b97fc421579841e383&=&format=webp&quality=lossless&width=240&height=240",
    "UniqueVelocity": "https://media.discordapp.net/attachments/697810514448744448/1526293634964787290/UniqueSkillVelocity.png?ex=6a567f37&is=6a552db7&hm=5e684019a190cc2ac0ac7af155d6b3e6407e5393132151b037b8c0d85ff0804d&=&format=webp&quality=lossless&width=240&height=240",
    "UniqueAcceleration": "https://media.discordapp.net/attachments/697810514448744448/1526293634671050953/UniqueSkillAcceleration.png?ex=6a567f37&is=6a552db7&hm=1b6f28a0127dea9deb384c6de4deacb21fca958325aff0cc6c663b44b5fdf5af&=&format=webp&quality=lossless&width=240&height=240",
    "velocity": "https://media.discordapp.net/attachments/697810514448744448/1550789849022464060/velocity_common.png?ex=6aaf9d18&is=6aae4b98&hm=a9f19f91c2533a2c162d872312d4659b7e9bc777533afb4c4019d806ea04dca9&=&format=webp&quality=lossless",
    "acceleration": "https://media.discordapp.net/attachments/697810514448744448/1550789849685172274/acceleration_common.png?ex=6aaf9d18&is=6aae4b98&hm=f37c89fa4aa1a9a20c58b298a88af12bfcd8d82ff151789db567ee9f0e75f27f&=&format=webp&quality=lossless",
    "stamina": "https://media.discordapp.net/attachments/697810514448744448/1550789850221776916/stamina_common.png?ex=6aaf9d18&is=6aae4b98&hm=074c4f6b4e8abc3bbe07487c908cd6239e197e42a49b1a814d503536be81630f&=&format=webp&quality=lossless",
    "navigation": "https://media.discordapp.net/attachments/697810514448744448/1550789850792326144/navigation_common.png?ex=6aaf9d18&is=6aae4b98&hm=3b9ea7d0b5969d7c01acbc51b002861014736acf8e78404dfd1402fa01b6b369&=&format=webp&quality=lossless",
}

EFFECT_TYPES = {
    "cap_floor",
    "modify_roll_cap_floor",
    "modify_velocity",  # เพิ่มผลรวมตอนวิ่งครั้งนี้
    "modify_roll_floor",  # เพิ่มแต้มต่ำสุดลูกเต๋า
    "modify_roll_cap",  # เพิ่ม/ลดแต้มสูงสุดลูกเต๋า
    "add_dkh",  # เพิ่ม d และ kh พร้อมกัน
    "add_d",  # เพิ่มจำนวนลูกเต๋า
    "add_kh",  # เพิ่มจำนวนลูกที่เลือก
    "recover_stamina",  # เพิ่ม STA
    "reduce_stamina",  # ลด STA เป้าหมาย
    "flat_total",  # เพิ่ม/ลด score ทันที
    "modify_gold_range",  # เพิ่มระยะนับ Gold
    "modify_enemy_gold_range",  # ลดระยะนับ Gold ของศัตรู
    "apply_debuff_next_turn",  # debuff เทิร์นหน้า
    "apply_buff_next_turn",  # buff เทิร์นหน้า
    "block_reroll",  # ห้าม reroll
    "force_path_bonus",  # เปลี่ยนผลของ path
    "modify_current_speed",  # เพิ่ม current speed โดยตรง
    "modify_race_stats",  # ปรับ stat เฉพาะการแข่งขันนี้
    "resolve_pending_lane_now",
    "activate_random_equipped_skills",
}

SKILL_TAG_OPTIONS = [
    ("all", "ทั้งหมด"),
    ("corner", "สกิลทางโค้ง"),
    ("straight", "สกิลทางตรง"),
    ("uphill", "สกินขึ้นเนิน"),
    ("downhill", "สกิลลงเนิน"),
    ("velocity", "เพิ่มความเร็ว"),
    ("acceleration", "เพิ่มความเร่ง"),
    ("recovery", "ฟื้นฟู Stamina"),
    ("debuff", "สกิลแดง ดีบัฟ"),
    ("vision", "สกิลมองทาง"),
    ("front", "แผนวิ่ง Front"),
    ("pace", "แผนวิ่ง Pace"),
    ("late", "แผนวิ่ง Late"),
    ("end", "แผนวิ่ง End"),
    ("start", "ช่วง Early Race"),
    ("mid_race", "ช่วง Mid Race"),
    ("late_race", "ช่วง Late Race"),
    ("unique", "Unique Skill"),
]

# Skill browsing has two independent taxonomies. Aptitude describes where a
# skill can be used; detail describes its effect or activation characteristic.
# The game still evaluates the original trigger/tags fields.
SKILL_APTITUDE_OPTIONS = [
    ("all", "All aptitudes"),
    ("turf", "Turf"), ("dirt", "Dirt"),
    ("sprint", "Sprint"), ("mile", "Mile"), ("medium", "Medium"), ("long", "Long"),
    ("front", "Front"), ("pace", "Pace"), ("late", "Late"), ("end", "End"),
]

SKILL_DETAIL_OPTIONS = [
    ("all", "All details"),
    ("acceleration", "Acceleration"), ("velocity", "Velocity"),
    ("recovery", "Recovery"), ("debuff", "Debuff"), ("passive", "Passive"),
    ("blind", "Blind"), ("unique", "Unique"), ("concentration", "Concentration"),
    ("vision", "Vision"), ("positioning", "Positioning"),
    ("corner", "Corner"), ("straight", "Straight"),
    ("final_corner", "Final corner"), ("uphill", "Uphill"), ("downhill", "Downhill"),
    ("early_race", "Early race"), ("mid_race", "Mid race"),
    ("late_race", "Late race"), ("lastspurt", "Last spurt"),
    ("front_position", "Front position"), ("middle_position", "Middle position"),
    ("back_position", "Back position"), ("front_blocked", "Front blocked"),
    ("target_ahead", "Target ahead"), ("target_behind", "Target behind"),
    ("nearby_uma", "Nearby Uma"), ("followed", "Being followed"),
    ("stability", "Stability"), ("cap_boost", "Cap boost"),
    ("blocked", "Blocked"), ("burst", "Burst"), ("sustain", "Sustain"),
    ("power", "Power"), ("stamina", "Stamina"), ("mindgame", "Mind game"),
]

_DETAIL_KEYS = {key for key, _ in SKILL_DETAIL_OPTIONS if key != "all"}
_STYLE_TO_APTITUDE = {"Front": "front", "Pace": "pace", "Late": "late", "End": "end"}
_ICON_TO_DETAIL = {
    "Acceleration": "acceleration", "Acceleration_rare": "acceleration",
    "acceleration": "acceleration", "UniqueAcceleration": "acceleration",
    "Velocity": "velocity", "Velocity_rare": "velocity", "velocity": "velocity",
    "UniqueVelocity": "velocity", "Recovery": "recovery", "Recovery_rare": "recovery",
    "stamina": "recovery", "Passive": "passive", "Passive_rare": "passive",
    "Concentration": "concentration", "Concentration_rare": "concentration",
    "LookUp": "vision", "LookUp_rare": "vision",
    "DecreaseVelocity": "debuff", "DecreaseVelocity_rare": "debuff",
    "ReduceSTA": "debuff", "ReduceSTA_rare": "debuff",
    "Blind": "debuff", "Blind_rare": "debuff",
}


def get_skill_category_groups(skill: dict) -> dict[str, list[str]]:
    """Return stable aptitude/detail categories for a skill preset."""
    trigger = skill.get("trigger", {})
    tags = {str(tag).lower() for tag in skill.get("tags", [])}
    aptitude = set()
    detail = set()

    track = str(trigger.get("track", "")).lower()
    if track in {"turf", "dirt"}:
        aptitude.add(track)
    distance = str(trigger.get("distance_type", "")).lower()
    if distance in {"sprint", "mile", "medium", "long"}:
        aptitude.add(distance)
    style = _STYLE_TO_APTITUDE.get(trigger.get("style"))
    if style:
        aptitude.add(style)

    for effect in skill.get("effects", []):
        condition = effect.get("condition") or {}
        condition_track = str(condition.get("track", "")).lower()
        if condition_track in {"turf", "dirt"}:
            aptitude.add(condition_track)
        condition_distance = str(condition.get("distance_type", "")).lower()
        if condition_distance in {"sprint", "mile", "medium", "long"}:
            aptitude.add(condition_distance)
        condition_style = _STYLE_TO_APTITUDE.get(condition.get("style"))
        if condition_style:
            aptitude.add(condition_style)
    detail_aliases = {
        "start": "early_race",
        "last_spurt": "lastspurt",
        "straightaway": "straight",
        "mid_late": "late_race",
    }
    for tag in tags:
        normalized = detail_aliases.get(tag, tag)
        if normalized in _DETAIL_KEYS:
            detail.add(normalized)
    path_detail = {1: "straight", 2: "corner", 3: "uphill", 4: "downhill"}.get(trigger.get("path_type"))
    if path_detail:
        detail.add(path_detail)
    if trigger.get("lastspurt"):
        detail.add("lastspurt")
    icon_detail = _ICON_TO_DETAIL.get(skill.get("icon"))
    if icon_detail:
        detail.add(icon_detail)

    return {
        "aptitude": [key for key, _ in SKILL_APTITUDE_OPTIONS if key in aptitude],
        "detail": [key for key, _ in SKILL_DETAIL_OPTIONS if key in detail],
    }

TRIGGER_SCHEMA = {
    "path_type": None,
    "style": None,
    "turn_min": None,
    "turn_max": None,
    "phase_min": None,
    "phase_max": None,
    "lastspurt": None,
    "last_corner": None,
    "distance_color": None,
    "position_group": None,
    "distance_type": None,
    "track": None,
    "target_distance_min": None,
    "target_distance_max": None,
    "front_blocked": None,
    "nearby_uma_count": None,
    "skill_use_count_min": None,
    "base_stats_min": None,
}

TARGET_SCHEMA = {
    "scope": "self",  # self / nearest_front / nearest_back / all_front / all_back / random_enemy
    "limit": 1,
    "same_lane_only": None,
}

from utils.skill.presets import SKILLS
