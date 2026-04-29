ICON = {
    "Concentration": "<:Concentration:1494389544127172728>",
    "Acceleration": "<:Acceleration:1494389491337527538>",
    "Velocity": "<:Velocity:1494389507666088100>",
    "Recovery": "<:Recovery:1494389472337330196>",
    "DecreaseVelocity": "<:DecreaseVelocity:1494389430721577070>",
    "ReduceSTA": "<:ReduceSTA:1494389406109270026>",
    "LookUp": "<:LookUp:1494389526359969873>",
    "Blind": "<:Blind:1494389451114151939>",
    "UniqueVelocity": "<:UniqueSkillVelocity:1499064862888824923>",
    "UniqueAcceleration": "<:UniqueSkillVelocity:1499064862888824923>",
}

EFFECT_TYPES = {
    "modify_velocity",          # เพิ่มผลรวมตอนวิ่งครั้งนี้
    "modify_selected_die",      # เพิ่มแต้มทุกลูกที่ถูกเลือก
    "modify_roll_floor",        # เพิ่มแต้มต่ำสุดลูกเต๋า
    "modify_roll_cap",          # เพิ่ม/ลดแต้มสูงสุดลูกเต๋า
    "add_dkh",                  # เพิ่ม d และ kh พร้อมกัน
    "add_d",                    # เพิ่มจำนวนลูกเต๋า
    "add_kh",                   # เพิ่มจำนวนลูกที่เลือก
    "recover_stamina",          # เพิ่ม STA
    "reduce_stamina",           # ลด STA เป้าหมาย
    "flat_total",        # เพิ่ม/ลด score ทันที
    "modify_gold_range",        # เพิ่มระยะนับ Gold
    "modify_enemy_gold_range",  # ลดระยะนับ Gold ของศัตรู
    "apply_debuff_next_turn",   # debuff เทิร์นหน้า
    "apply_buff_next_turn",     # buff เทิร์นหน้า
    "block_reroll",             # ห้าม reroll
    "force_path_bonus",         # เปลี่ยนผลของ path
    "modify_start_loss",        # ลดโอกาส/ผลเสียตอนออกตัว
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
]

TRIGGER_SCHEMA = {
    "path_type": None,
    "style": None,
    "turn_min": None,
    "turn_max": None,
    "phase_min": None,
    "phase_max": None,
    "lastspurt": None,
    "distance_color": None,
    "overtaking": None,
    "being_overtaken": None,
    "position_group": None,
    "distance_type": None,
    "surface": None,
    "target_distance_min": None,
    "target_distance_max": None,
    "front_blocked": None, 
}

TARGET_SCHEMA = {
    "scope": "self",   # self / nearest_front / nearest_back / all_front / all_back / random_enemy
    "limit": 1
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
                "duration": "this_roll"
            },
            {"type": "modify_roll_cap", "value": 10, "duration": "this_roll"},
        ],
        "active_roll": True,
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
            {
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
        "tags": ["straight", "lastspurt", "end", "acceleration"],
    },

    "s003": {
        "name": "Concentration",
        "icon": "Concentration",
        "cooldown": 20,
        "cost": 50,
        "trigger": {
            "turn_min": 1,
            "turn_max": 1,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_roll_floor",
                "value": 15,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
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
        "effects": [
            {
                "type": "recover_stamina",
                "value": 2
            }
        ],
        "active_roll": False,
        "tags": ["corner", "recovery"],
    },

    "s005": {
        "name": "Go-Home Specialist",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 4,
            "style": "End",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "recover_stamina",
                "value": 2
            }
        ],
        "active_roll": False,
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
            "target_distance_max": 120,
        },
        "target": {
            "scope": "nearest_front",
            "limit": 3,
        },
        "effects": [
            {"type": "recover_stamina","value": 1},
            {"type": "modify_roll_cap", "value": -7, "duration": "this_roll"},
        ],
        "active_roll": False,
        "tags": ["recovery", "debuff", "front_target"],
    },

    "s007": {
        "name": "Technician",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Pace",
            "path_type": 2,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {
                "type": "modify_roll_floor",
                "value": 5,
                "duration": "this_roll"
            },
            {
                "type": "modify_roll_cap",
                "value": 14,
                "duration": "this_roll"
            }
        ],
        "active_roll": False,
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
            {"type": "modify_gold_range", "value": 60, "duration": "this_turn"},
            {"type": "modify_roll_cap", "value": 10, "duration": "this_roll"},
        ],
        "active_roll": True,
        "tags": ["medium", "positioning", "back"],
    },

    "s009": {
        "name": "Vanguard Spirit",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 90,
        "trigger": {
            "style": "Front",
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "front",
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_roll_cap", "value": 7, "duration": "this_roll"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 40, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["front", "long", "lead"],
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
            {"type": "modify_gold_range", "value": 100, "duration": "this_turn"},
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
        ],
        "active_roll": False,
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
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 40, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["medium", "lead", "velocity"],
    },

    "s012": {
        "name": "Speed Star",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Pace",
            "phase_min": 4,
            "phase_max": 4,
            "path_type": 2,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 40, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["pace", "final_corner", "velocity"],
    },

    "s013": {
        "name": "Determined Descent",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 70,
        "trigger": {
            "style": "Pace",
            "path_type": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "add_dkh", "value": 2, "duration": "this_roll"}
        ],
        "active_roll": True,
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
            {"type": "add_dkh", "value": 2, "duration": "this_roll"},
        ],
        "active_roll": True,
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
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 40, "duration": "this_roll"}
        ],
        "active_roll": True,
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
            {"type": "add_dkh", "value": 2, "duration": "this_roll"},
        ],
        "active_roll": True,
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
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 40, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["medium", "straight", "velocity"],
    },

    "s018": {
        "name": "Blast Forward",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 90,
        "trigger": {
            "path_type": 1,
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_roll_cap", "value": 7, "duration": "this_roll"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 40, "duration": "this_roll"}
        ],
        "active_roll": True,
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
            "target_distance_max": 100,
        },
        "target": {"scope": "all_front", "limit": 3},
        "effects": [
            {"type": "modify_roll_cap", "value": -12, "duration": "this_roll"},
        ],
        "active_roll": False,
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
            "target_distance_max": 120,
        },
        "target": {"scope": "nearest_front", "limit": 4},
        "effects": [
            {"type": "reduce_stamina", "value": 1},  # ศัตรู
            {"type": "self_heal_stamina", "value": 1}     # ตัวเอง
        ],
        "active_roll": False,
        "tags": ["debuff", "long", "stamina"],
    },

    # ---------- RECOVERY ----------
    "s021": {
        "name": "Calm and Collected",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Pace",
            "phase_min": 2,
            "phase_max": 2,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "recover_stamina", "value": 2}
        ],
        "active_roll": False,
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
        "effects": [
            {"type": "recover_stamina", "value": 2}
        ],
        "active_roll": False,
        "tags": ["straight", "recovery"],
    },

    "s023": {
        "name": "Cooldown",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 1,
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "recover_stamina", "value": 2}
        ],
        "active_roll": False,
        "tags": ["long", "straight", "recovery"],
    },

    "s024": {
        "name": "Trackblazer",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
            "position_group": "front",
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "recover_stamina", "value": 2}
        ],
        "active_roll": False,
        "tags": ["medium", "lead", "recovery"],
    },

    "s025": {
        "name": "Restless",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Front",
            "path_type": 3,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "recover_stamina", "value": 2}
        ],
        "active_roll": False,
        "tags": ["front", "uphill", "recovery"],
    },

    "s026": {
        "name": "Relax",
        "icon": "Recovery",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Late",
            "phase_min": 4,
            "phase_max": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "recover_stamina", "value": 2}
        ],
        "active_roll": False,
        "tags": ["late", "recovery", "late_race"],
    },

    # ---------- DEBUFF ----------
    "s027": {
        "name": "Dominator",
        "icon": "DecreaseVelocity",
        "cooldown": 10,
        "cost": 100,
        "trigger": {
            "phase_min": 4,
            "phase_max": 4,
            "position_group": "back",
            "distance_type": "Medium",
            "target_distance_min": 1,
            "target_distance_max": 120,
        },
        "target": {"scope": "all_front", "limit": 4},
        "effects": [
            {"type": "modify_roll_cap", "value": -7, "duration": "this_roll"},
            {"type": "apply_debuff_next_turn", "stat": "flat_total", "value": -35}
        ],
        "active_roll": False,
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
            "target_distance_min": -100,
            "target_distance_max": 100,
        },
        "target": {"scope": "all_back", "limit": 5},
        "effects": [
            {"type": "modify_enemy_gold_range", "value": -15, "duration": "next_turn"}
        ],
        "active_roll": False,
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
            "target_distance_max": 200,
        },
        "target": {"scope": "all_front", "limit": 4},
        "effects": [
            {"type": "modify_enemy_gold_range", "value": -7, "duration": "next_turn"}
        ],
        "active_roll": False,
        "tags": ["blind", "long", "debuff"],
    },

    "s030": {
        "name": "Groundwork",
        "icon": "Acceleration",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "phase_min": 1,
            "phase_max": 1,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {
                "type": "add_dkh",
                "value": 1,
                "duration": "this_roll"
            },
            {
                "type": "modify_roll_cap",
                "value": 5,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
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
            {"type": "add_dkh", "value": 2, "duration": "this_roll"},
            {"type": "modify_roll_cap", "value": 7, "duration": "this_roll"},
        ],
        "active_roll": True,
        "tags": ["lastspurt", "blocked", "acceleration"],
    },

    # "s032": {
    #     "name": "March Licker",
    #     "icon": "Blind",
    #     "cooldown": 5,
    #     "cost": 0,
    #     "trigger": {
    #         "phase_min": 1,
    #         "phase_max": 4,
    #     },
    #     "target": {"scope": "all_front", "limit": 6},
    #     "effects": [
    #         {"type": "apply_debuff_next_turn", "stat": "flat_total", "value": -50}
    #     ],
    #     "active_roll": False,
    #     "tags": ["blind", "long", "debuff"],
    # },
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
            {
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
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
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            },
            {
                "type": "reduce_stamina", 
                "value": 1
            }
        ],
        "active_roll": True,
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
        "effects": [
            {
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            }
        ],
        "active_roll": False,
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
                "type": "modify_velocity",
                "value": 50,
                "duration": "this_roll"
            },
            {
                "type": "modify_roll_cap",
                "value": 7,
                "duration": "this_roll"
            },
            {
                "type": "add_dkh",
                "value": 1,
                "duration": "this_roll"
            },
            {
                "type": "recover_stamina",
                "value": 1
            }
        ],
        "active_roll": False,
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
            {
                "type": "modify_velocity",
                "value": 40,
                "duration": "this_roll"
            },
            {"type": "modify_roll_cap", "value": 5, "duration": "this_roll"},
        ],
        "active_roll": False,
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
            {
                "type": "modify_velocity",
                 "value": 35,
                "duration": "this_roll"
            },
            {
            "type": "modify_roll_cap",
            "value": 7,
            "duration": "this_roll"
        }
    ],
        "active_roll": False,
        "tags": ["last_spurt", "velocity", "stability"],
    },


    "s038": {
        "name": "All-Seeing Eyes",
        "icon": "ReduceSTA",
        "cooldown": 10,
        "cost": 80,
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
        "effects": [
            {
                "type": "reduce_stamina",
                "value": 1
            }
        ],
        "active_roll": False,
        "tags": ["late", "debuff", "stamina", "all_front"],
    },

    "s039": {
        "name": "Rising Dragon",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 80,
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
            {
                "type": "modify_roll_cap",
                "value": 21,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
        "tags": ["late", "corner", "burst", "stability"],
    },

    "s040": {
        "name": "Tail Nine",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 60,
        "trigger": {
            "phase_min": 2,
            "phase_max": 3,
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "modify_roll_cap",
                "value": 12,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
        "tags": ["mid_race", "velocity", "cap_boost"],
    },

    "s041": {
        "name": "Tantalizing Trick",
        "icon": "ReduceSTA",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "target_distance_min": -11,
            "target_distance_max": -30,
        },
        "target": {
            "scope": "all_back",
            "limit": 1,
        },
        "effects": [
            {"type": "reduce_stamina", "value": 1},
            {"type": "force_rush", "value": 1}
        ],
        "active_roll": False,
        "tags": ["debuff", "mindgame"],
    },

    "s042": {
        "name": "Let's Pump Some Iron",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "phase_min": 3,
            "phase_max": 4,
            "path_type": 2,
            "position_group": "back",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {"type": "add_dkh","value": 3,"duration": "this_roll"}
        ],
        "active_roll": False,
        "tags": ["corner", "late_race", "acceleration"],
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
            {
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            },
            {
                "type": "modify_roll_cap",
                "value": 14,
                "duration": "this_roll"
            },
        ],
        "active_roll": True,
        "tags": ["corner", "late_race", "lead", "acceleration"],
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
            {"type": "modify_roll_cap","value": 21,"duration": "this_roll"},
            {"type": "modify_roll_floor","value": 10,"duration": "this_roll"},
        ],
        "active_roll": True,
        "tags": ["late_race", "lead", "velocity", "positioning"],
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
            {
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            },
            {
                "type": "modify_roll_cap",
                "value": 14,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
        "tags": ["mid_race", "late_race", "acceleration"],
    },

    "s046": {
        "name": "Angling and Scheming",
        "icon": "UniqueAcceleration",
        "cooldown": 8,
        "cost": 120,
        "trigger": {
            "phase_min": 3,
            "phase_max": 4,
            "path_type": 2,
            "position_group": "front",
        },
        "target": {
            "scope": "self",
            "limit": 1,
        },
        "effects": [
            {
                "type": "add_dkh",
                "value": 2,
                "duration": "this_roll"
            },
            {"type": "modify_roll_floor","value": 10,"duration": "this_roll"},

        ],
        "active_roll": True,
        "tags": ["corner", "late_race", "lead", "acceleration"],
    },


    # "s099": {
    #     "name": "March Licking",
    #     "icon": "LookUp",
    #     "cooldown": 10,
    #     "cost": 60,
    #     "trigger": {
    #         "style": "End",
    #         "phase_min": 1,
    #         "phase_max": 4,
    #     },
    #     "target": {"scope": "self", "limit": 1},
    #     "effects": [
    #         {"type": "modify_gold_range", "value": 100, "duration": "this_turn"},
    #         {"type": "modify_roll_cap", "value": 99, "duration": "this_roll"},
    #     ],
    #     "active_roll": False,
    #     "tags": ["vision", "end", "positioning"],
    # },
}