from utils.icon_presets import SKILL_ICONS

# Selected at startup using BOT_EMOJI_SET (main or test).
ICON = dict(SKILL_ICONS)

ICON_URL = {
    "Concentration": "https://media.discordapp.net/attachments/697810514448744448/1526292466570100956/Concentration.png?ex=6a567e21&is=6a552ca1&hm=ba72a3078b0e0cd3cc9ba5128a8280d78bfb14de88c696fe40855a455a597a97&=&format=webp&quality=lossless&width=240&height=240",
    "Acceleration": "https://media.discordapp.net/attachments/697810514448744448/1526292465185722469/Acceleration.png?ex=6a567e20&is=6a552ca0&hm=5887f9dfc6348323c2e75c277470052d38bf9d8f15d50b9e84182107fdf32f67&=&format=webp&quality=lossless&width=240&height=240",
    "Velocity": "https://media.discordapp.net/attachments/697810514448744448/1526292464552640652/Velocity.png?ex=6a567e20&is=6a552ca0&hm=cdec2ebfd23657a87bdcecbfd11d1c8dfd528917561d628b792825a64d017add&=&format=webp&quality=lossless&width=240&height=240",
    "Navigation": "https://media.discordapp.net/attachments/697810514448744448/1526292468520321267/Navigation.png?ex=6a567e21&is=6a552ca1&hm=bd100dd98982668b999927406c724fdc5cc8d68c2e366286ee9446d03a85b545&=&format=webp&quality=lossless&width=240&height=240",
    "Recovery": "https://media.discordapp.net/attachments/697810514448744448/1526292463436693565/Recovery.png?ex=6a567e20&is=6a552ca0&hm=a8f676d62e27898fcfe21a282a019de5585a298635afa011ec96b472c97f56e1&=&format=webp&quality=lossless&width=240&height=240",
    "DecreaseVelocity": "https://media.discordapp.net/attachments/697810514448744448/1526292466993467513/DecreaseVelocity.png?ex=6a567e21&is=6a552ca1&hm=a12f7f4f7803e42dded5b924be383355dc1bd0861067e8018cd67822bce2f9d7&=&format=webp&quality=lossless&width=240&height=240",
    "ReduceSTA": "https://media.discordapp.net/attachments/697810514448744448/1526292463990472745/ReduceSTA.png?ex=6a567e20&is=6a552ca0&hm=4440cdf2afbcada9225a656eb455334b54e5a8c4fe7bd2377b9c945279ef27ee&=&format=webp&quality=lossless&width=240&height=240",
    "LookUp": "https://media.discordapp.net/attachments/697810514448744448/1526292467794837644/LookUp.png?ex=6a567e21&is=6a552ca1&hm=3b9ea7d0b5969d7c01acbc51b002861014736acf8e78404dfd1402fa01b6b369&=&format=webp&quality=lossless&width=240&height=240",
    "Blind": "https://media.discordapp.net/attachments/697810514448744448/1526292465932566711/Blind.png?ex=6a567e21&is=6a552ca1&hm=5600daab0bbce3ea5864c631eebd5c9e4ea47eae2ebae7b97fc421579841e383&=&format=webp&quality=lossless&width=240&height=240",
    "UniqueVelocity": "https://media.discordapp.net/attachments/697810514448744448/1526293634964787290/UniqueSkillVelocity.png?ex=6a567f37&is=6a552db7&hm=5e684019a190cc2ac0ac7af155d6b3e6407e5393132151b037b8c0d85ff0804d&=&format=webp&quality=lossless&width=240&height=240",
    "UniqueAcceleration": "https://media.discordapp.net/attachments/697810514448744448/1526293634671050953/UniqueSkillAcceleration.png?ex=6a567f37&is=6a552db7&hm=1b6f28a0127dea9deb384c6de4deacb21fca958325aff0cc6c663b44b5fdf5af&=&format=webp&quality=lossless&width=240&height=240",
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
    "resolve_pending_lane_now",
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
    "surface": None,
    "target_distance_min": None,
    "target_distance_max": None,
    "front_blocked": None,
    "nearby_uma_count": None,
}

TARGET_SCHEMA = {
    "scope": "self",  # self / nearest_front / nearest_back / all_front / all_back / random_enemy
    "limit": 1,
}

SKILLS = {
    "s001": {
        "name": "Professor of Curvature",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "path_type": 2,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 30,
                "duration": "this_roll",
            },
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
        ],
        "tags": ["corner", "velocity"],
    },
    "s002": {
        "name": "Encroaching Shadow",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "End",
            "lastspurt": True,
            "path_type": 1,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_current_speed", "value": 2},
            {"type": "add_dkh", "value": 1, "duration": "this_roll"},
        ],
        "tags": ["straight", "lastspurt", "end", "acceleration"],
    },
    "s003": {
        "name": "Concentration",
        "icon": "Concentration",
        "cooldown": 20,
        "cost": 40,
        "trigger": {
            "turn_min": 1,
            "turn_max": 1,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_roll_floor", "value": 15, "duration": "this_roll"},
        ],
        "tags": ["start", "concentration"],
    },
    "s004": {
        "name": "Swinging Maestro",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 2,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["corner", "recovery"],
    },
    "s005": {
        "name": "Go-Home Specialist",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "path_type": 4,
            "style": "End",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["downhill", "recovery", "end"],
    },
    "s006": {
        "name": "Keen Eye",
        "icon": "DecreaseVelocity",
        "cooldown": 10,
        "cost": 60,
        "trigger": {
            "style": "Pace",
            "phase_min": 2,
            "phase_max": 3,
            "target_distance_min": 1,
            "target_distance_max": 150,
        },
        "target": {
            "scope": "nearest_front",
            "limit": 3,
        },
        "effects": [
            {"type": "recover_stamina", "value": 1},
            {"type": "modify_roll_cap", "value": -10, "duration": "this_roll"},
        ],
        "tags": ["recovery", "debuff", "front_target"],
    },
    "s007": {
        "name": "Technician",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 70,
        "trigger": {
            "style": "Pace",
            "path_type": 2,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 10, "duration": "this_roll"},
        ],
        "tags": ["corner", "pace", "stability"],
    },
    "s008": {
        "name": "Lightning Step",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 60,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "back",
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_gold_range", "value": 50, "duration": "this_turn"},
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
        ],
        "tags": ["medium", "positioning", "back"],
    },
    "s009": {
        "name": "Vanguard Spirit",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "front",
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["velocity", "long", "lead"],
    },
    "s010": {
        "name": "The Coast Is Clear!",
        "icon": "LookUp",
        "cooldown": 10,
        "cost": 60,
        "trigger": {
            "style": "End",
            "phase_min": 2,
            "phase_max": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_gold_range", "value": 50, "duration": "this_turn"},
            {"type": "modify_gold_lane_range", "value": 1, "duration": "this_turn"},
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
        ],
        "tags": ["vision", "end", "positioning"],
    },
    "s011": {
        "name": "Killer Tunes",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "distance_type": "Medium",
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "front",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["medium", "lead", "velocity"],
    },
    "s012": {
        "name": "Speed Star",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {"style": "Pace", "last_corner": True},
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["pace", "final_corner", "velocity"],
    },
    "s013": {
        "name": "Determined Descent",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Pace",
            "path_type": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_current_speed", "value": 1.5},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["pace", "downhill", "acceleration"],
    },
    "s014": {
        "name": "On Your Left!",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Late",
            "phase_min": 3,
            "phase_max": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_current_speed", "value": 2},
            {"type": "add_dkh", "value": 1, "duration": "this_roll"},
        ],
        "tags": ["late", "acceleration", "late_race"],
    },
    "s015": {
        "name": "Beeline Burst",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "path_type": 1,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 3, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["straight", "velocity"],
    },
    "s016": {
        "name": "Turbo Sprint",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 1,
            "distance_type": "Sprint",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "add_dkh", "value": 3, "duration": "this_roll"},
        ],
        "tags": ["sprint", "straight", "acceleration"],
    },
    "s017": {
        "name": "Flash Forward",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "path_type": 1,
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["medium", "straight", "velocity"],
    },
    "s018": {
        "name": "Blast Forward",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "path_type": 1,
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
        ],
        "tags": ["long", "straight", "velocity"],
    },
    "s019": {
        "name": "Battle Formation",
        "icon": "DecreaseVelocity",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "phase_min": 1,
            "phase_max": 2,
            "distance_type": "Mile",
            "position_group": "back",
            "target_distance_min": 1,
            "target_distance_max": 200,
        },
        "target": {"scope": "all_front", "limit": 8},
        "effects": [
            {"type": "modify_roll_cap", "value": -10, "duration": "this_roll"},
        ],
        "tags": ["debuff", "mile", "early_race"],
    },
    "s020": {
        "name": "Stamina Siphon",
        "icon": "ReduceSTA",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "back",
            "distance_type": "Long",
            "target_distance_min": 1,
            "target_distance_max": 150,
        },
        "target": {"scope": "nearest_front", "limit": 4},
        "effects": [
            {"type": "reduce_stamina", "value": 1},  # ศัตรู
            {"type": "self_heal_stamina", "value": 1},  # ตัวเอง
        ],
        "tags": ["debuff", "long", "stamina"],
    },
    # ---------- RECOVERY ----------
    "s021": {
        "name": "Calm and Collected",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "style": "Pace",
            "phase_min": 2,
            "phase_max": 2,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["pace", "recovery", "mid_race"],
    },
    "s022": {
        "name": "Breath of Fresh Air",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 1,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["straight", "recovery"],
    },
    "s023": {
        "name": "Cooldown",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "path_type": 1,
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["long", "straight", "recovery"],
    },
    "s024": {
        "name": "Trackblazer",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "front",
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["medium", "lead", "recovery"],
    },
    "s025": {
        "name": "Restless",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "style": "Front",
            "path_type": 3,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["front", "uphill", "recovery"],
    },
    "s026": {
        "name": "Relax",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "style": "Late",
            "phase_min": 4,
            "phase_max": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "recover_stamina", "value": 2}],
        "tags": ["late", "recovery", "late_race"],
    },
    # ---------- DEBUFF ----------
    "s027": {
        "name": "Dominator",
        "icon": "DecreaseVelocity",
        "cooldown": 10,
        "cost": 80,
        "trigger": {
            "phase_min": 4,
            "phase_max": 4,
            "position_group": "back",
            "distance_type": "Medium",
            "target_distance_min": 1,
            "target_distance_max": 200,
        },
        "target": {"scope": "all_front", "limit": 4},
        "effects": [
            {"type": "modify_roll_cap", "value": -12, "duration": "this_roll"},
        ],
        "tags": ["debuff", "medium", "late_race"],
    },
    "s028": {
        "name": "Dazzling Disorientation",
        "icon": "Blind",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "style": "Pace",
            "phase_min": 4,
            "phase_max": 4,
            "position_group": "front",
            "target_distance_min": -150,
            "target_distance_max": 150,
        },
        "target": {"scope": "all_back", "limit": 3},
        "effects": [
            {"type": "modify_enemy_gold_range", "value": -15, "duration": "next_turn"},
            {
                "type": "modify_enemy_gold_lane_range",
                "value": -1,
                "duration": "next_turn",
            },
        ],
        "tags": ["blind", "pace", "debuff", "lead"],
    },
    "s029": {
        "name": "Illusionist",
        "icon": "Blind",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "phase_min": 4,
            "phase_max": 4,
            "distance_type": "Long",
            "target_distance_min": 1,
            "target_distance_max": 300,
        },
        "target": {"scope": "all_front", "limit": 5},
        "effects": [
            {"type": "modify_enemy_gold_range", "value": -12, "duration": "next_turn"},
            {
                "type": "modify_enemy_gold_lane_range",
                "value": -1,
                "duration": "next_turn",
            },
        ],
        "tags": ["blind", "long", "debuff"],
    },
    "s030": {
        "name": "Groundwork",
        "icon": "Acceleration",
        "cooldown": 10,
        "cost": 40,
        "trigger": {
            "phase_min": 1,
            "phase_max": 1,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_current_speed", "value": 1},
        ],
        "tags": ["start", "acceleration"],
    },
    "s031": {
        "name": "No Stopping Me!",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "lastspurt": True,
            "front_blocked": True,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_current_speed", "value": 2},
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
        ],
        "tags": ["lastspurt", "blocked", "acceleration"],
    },
    "s032": {
        "name": "Neck and Neck",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Pace",
            "phase_min": 3,
            "phase_max": 4,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_current_speed", "value": 1},
            {"type": "add_dkh", "value": 2},
        ],
        "tags": ["pace", "late_race", "acceleration", "burst"],
    },
    "s033": {
        "name": "Runaway",
        "icon": "Acceleration",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "style": "Front",
            "turn_min": 1,
            "turn_max": 1,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_current_speed",
                "value": 2,
            },
            {"type": "reduce_stamina", "value": 1},
        ],
        "tags": ["front", "start", "acceleration", "stamina_cost"],
    },
    "s034": {
        "name": "Unrestrained",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Front",
            "phase_min": 4,
            "phase_max": 4,
            "path_type": 2,  # ทางโค้ง
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [{"type": "add_dkh", "value": 3, "duration": "this_roll"}],
        "tags": ["front", "final_corner", "acceleration", "burst"],
    },
    "s035": {
        "name": "Radiant Star",
        "icon": "Acceleration",
        "cooldown": 6,
        "cost": 120,
        "trigger": {
            "phase_min": 3,
            "phase_max": 4,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_current_speed",
                "value": 1,
            },
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
            {"type": "add_dkh", "value": 2, "duration": "this_roll"},
            {"type": "recover_stamina", "value": 1},
        ],
        "tags": ["mid_late", "acceleration", "sustain"],
    },
    "s036": {
        "name": "Sturm und Drang",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "phase_min": 3,
            "phase_max": 4,
            "position_group": "back",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_velocity", "value": 40, "duration": "this_roll"},
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
        ],
        "tags": ["late_race", "back", "velocity"],
    },
    "s037": {
        "name": "In Body and Mind",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "lastspurt": True,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_velocity", "value": 40, "duration": "this_roll"},
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
        ],
        "tags": ["last_spurt", "velocity", "stability"],
    },
    "s038": {
        "name": "All-Seeing Eyes",
        "icon": "ReduceSTA",
        "cooldown": 10,
        "cost": 60,
        "trigger": {
            "style": "Late",
            "phase_min": 3,
            "phase_max": 4,
            "target_distance_min": 1,
            "target_distance_max": 999,
        },
        "target": {
            "scope": "all_front",
            "limit": 10,
        },
        "effects": [{"type": "reduce_stamina", "value": 0.6}],
        "tags": ["late", "debuff", "stamina", "all_front"],
    },
    "s039": {
        "name": "Rising Dragon",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 70,
        "trigger": {
            "style": "Late",
            "phase_min": 3,
            "phase_max": 4,
            "path_type": 2,  # ทางโค้ง
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 30,
                "duration": "this_roll",
            },
        ],
        "tags": ["late", "corner", "burst", "stability"],
    },
    "s040": {
        "name": "Tail Nine",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [{"type": "modify_roll_cap", "value": 10, "duration": "this_roll"}],
        "tags": ["mid_race", "velocity", "cap_boost"],
    },
    "s041": {
        "name": "Tantalizing Trick",
        "icon": "ReduceSTA",
        "cooldown": 8,
        "cost": 40,
        "trigger": {
            "target_distance_min": 0,
            "target_distance_max": -30,
        },
        "target": {
            "scope": "all_back",
            "limit": 1,
        },
        "effects": [
            {"type": "reduce_stamina", "value": 1},
            {"type": "force_rush", "value": 1},
        ],
        "tags": ["debuff", "mindgame"],
    },
    "s042": {
        "name": "Let's Pump Some Iron",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "last_corner": True,
            "position_group": "back",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_current_speed", "value": 2},
            {"type": "cap_floor", "value": 9, "duration": "this_roll"},
        ],
        "tags": ["corner", "late_race", "acceleration", "unique"],
    },
    "s043": {
        "name": "Red Shift/LP1211-M",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "phase_min": 4,
            "phase_max": 4,
            "position_group": "front",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "add_dkh", "value": 2, "duration": "this_roll"},
            {"type": "cap_floor", "value": 9, "duration": "this_roll"},
        ],
        "tags": ["corner", "late_race", "lead", "acceleration", "unique"],
    },
    "s044": {
        "name": "Triumphant Pulse",
        "icon": "UniqueVelocity",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "phase_min": 4,
            "phase_max": 4,
            "position_group": "front",
            "target_distance_min": 0,
            "target_distance_max": 200,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "cap_floor", "value": 15, "duration": "this_roll"},
        ],
        "tags": ["late_race", "lead", "velocity", "positioning", "unique"],
    },
    "s045": {
        "name": "Moving Past, and Beyond",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "phase_min": 3,
            "phase_max": 4,
            "position_group": "middle",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "add_dkh", "value": 3, "duration": "this_roll"},
            {"type": "modify_current_speed", "value": 2},
        ],
        "tags": ["mid_race", "late_race", "acceleration", "unique"],
    },
    "s046": {
        "name": "Angling and Scheming",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "last_corner": True,
            "position_group": "front",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "add_dkh", "value": 3, "duration": "this_roll"},
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
        ],
        "tags": ["corner", "late_race", "lead", "acceleration", "unique"],
    },
    "s047": {
        "name": "Ramp Up",
        "icon": "Velocity",
        "cooldown": 20,
        "cost": 50,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "target_distance_min": -30,
            "target_distance_max": -1,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            }
        ],
        "tags": ["mid_race", "velocity", "positioning"],
    },
    "s048": {
        "name": "Uma Stan",
        "icon": "Velocity",
        "cooldown": 20,
        "cost": 50,
        "trigger": {
            "nearby_uma_count": 2,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_roll_cap", "value": 10, "duration": "this_roll"},
        ],
        "tags": ["velocity"],
    },
    "s049": {
        "name": "Homestretch Haste",
        "icon": "Velocity",
        "cooldown": 20,
        "cost": 50,
        "trigger": {
            "last_corner": True,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_roll_cap", "value": 10, "duration": "this_roll"},
        ],
        "tags": ["velocity"],
    },
    "s050": {
        "name": "Daring Strike",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 60,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "back",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "modify_roll_cap", "value": 7, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 60,
                "duration": "this_roll",
            },
        ],
        "tags": ["velocity", "mid_race", "back"],
    },
    "s051": {
        "name": "Escape Artist",
        "icon": "Velocity",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "style": "Front",
            "phase_min": 2,
            "phase_max": 3,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
            {"type": "reduce_stamina", "value": 1},
        ],
        "tags": [
            "front",
            "mid_race",
            "velocity",
        ],
    },
    "s052": {
        "name": "15,000,000 CC",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Late",
            "path_type": 4,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "cap_floor", "value": 9, "duration": "this_roll"},
        ],
        "tags": [
            "late",
            "downhill",
            "velocity",
            "stability",
        ],
    },
    "s053": {
        "name": "Go with the Flow",
        "icon": "Navigation",
        "cooldown": 8,
        "cost": 40,
        "trigger": {},
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "resolve_pending_lane_now"}],
        "tags": ["positioning"],
    },
    "s054": {
        "name": "Cacao Operation Cacao",
        "icon": "UniqueVelocity",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "front",
            "path_type": 2,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 40,
                "duration": "this_roll",
            },
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
            {"type": "recover_stamina", "value": 1},
        ],
        "tags": ["corner", "mid_race", "lead", "velocity", "recovery", "unique"],
    },
    "s055": {
        "name": "U=ma2",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 100,
        "trigger": {
            "phase_min": 3,
            "phase_max": 4,
            "position_group": "middle",
            "path_type": 2,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
            {"type": "recover_stamina", "value": 3},
        ],
        "tags": ["corner", "late_race", "middle", "acceleration", "recovery", "unique"],
    },
    "s056": {
        "name": "Budding Blossom",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "last_corner": True,
            "phase_min": 3,
            "phase_max": 4,
            "position_group": "middle",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "cap_floor", "value": 12, "duration": "this_roll"},
            {"type": "modify_current_speed", "value": 1},
        ],
        "tags": ["corner", "late_race", "middle", "acceleration", "recovery", "unique"],
    },
}
