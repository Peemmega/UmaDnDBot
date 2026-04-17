ICON = {
    "Concentration": "<:Concentration:1494389544127172728>",
    "Acceleration": "<:Acceleration:1494389491337527538>",
    "Velocity": "<:Velocity:1494389507666088100>",
    "Recovery": "<:Recovery:1494389472337330196>",
    "DecreaseVelocity": "<:DecreaseVelocity:1494389430721577070>",
    "ReduceSTA": "<:ReduceSTA:1494389406109270026>",
    "LookUp": "<:LookUp:1494389526359969873>",
    "Blind": "<:Blind:1494389451114151939>",
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
    "flat_score_change",        # เพิ่ม/ลด score ทันที
    "modify_gold_range",        # เพิ่มระยะนับ Gold
    "modify_enemy_gold_range",  # ลดระยะนับ Gold ของศัตรู
    "apply_debuff_next_turn",   # debuff เทิร์นหน้า
    "apply_buff_next_turn",     # buff เทิร์นหน้า
    "block_reroll",             # ห้าม reroll
    "force_path_bonus",         # เปลี่ยนผลของ path
    "modify_start_loss",        # ลดโอกาส/ผลเสียตอนออกตัว
}

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
                "value": 8,
                "duration": "this_roll"
            }
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
                "type": "add_d",
                "value": 2,
                "duration": "this_roll"
            }
        ],
        "active_roll": True,
        "tags": ["straight", "lastspurt", "acceleration"],
    },

    "s003": {
        "name": "Concentration",
        "icon": "Concentration",
        "cooldown": 20,
        "cost": 80,
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
                "type": "modify_start_loss",
                "value": -1,
                "duration": "this_turn"
            },
            {
                "type": "modify_roll_floor",
                "value": 3,
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
                "value": 1
            }
        ],
        "active_roll": False,
        "tags": ["downhill", "recovery"],
    },

    "s006": {
        "name": "Keen Eye",
        "icon": "DecreaseVelocity",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "style": "Pace",
            "phase_min": 2,
            "phase_max": 3,
            "target_distance_min": 1,
            "target_distance_max": 20,
        },
        "target": {
            "scope": "nearest_front",
            "limit": 1,
        },
        "effects": [
            {
                "type": "recover_stamina",
                "value": 1
            },
            {
                "type": "apply_debuff_next_turn",
                "stat": "flat_total",
                "value": -5
            }
        ],
        "active_roll": False,
        "tags": ["recovery", "debuff", "front_target"],
    },
    "s007": {
        "name": "Technician",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Pace",
            "path_type": 2,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_selected_die", "value": 2, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["corner", "pace", "velocity"],
    },

    "s008": {
        "name": "Lightning Step",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "position_group": "back",
            "phase_min": 2,
            "phase_max": 3,
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_gold_range", "value": 5, "duration": "this_turn"},
            {"type": "modify_velocity", "mode": "flat_total", "value": 4, "duration": "this_roll"},
        ],
        "active_roll": True,
        "tags": ["medium", "positioning", "back"],
    },

    "s009": {
        "name": "Vanguard Spirit",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Front",
            "phase_min": 2,
            "phase_max": 3,
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_velocity", "mode": "flat_total", "value": 6, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["front", "long", "lead"],
    },

    "s010": {
        "name": "The Coast Is Clear!",
        "icon": "LookUp",
        "cooldown": 10,
        "cost": 50,
        "trigger": {
            "style": "End",
            "being_overtaken": False,
            "phase_min": 2,
            "phase_max": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_gold_range", "value": 8, "duration": "this_turn"}
        ],
        "active_roll": False,
        "tags": ["vision", "end", "positioning"],
    },

    "s011": {
        "name": "Killer Tunes",
        "icon": "Velocity",
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
            {"type": "modify_velocity", "mode": "flat_total", "value": 5, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["medium", "front", "velocity"],
    },

    "s012": {
        "name": "Speed Star",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 80,
        "trigger": {
            "style": "Pace",
            "path_type": 2,
            "lastspurt": True,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "add_kh", "value": 1, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["pace", "final_corner", "acceleration"],
    },

    "s013": {
        "name": "Determined Descent",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Pace",
            "path_type": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "add_d", "value": 1, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["pace", "downhill", "acceleration"],
    },

    "s014": {
        "name": "On Your Left!",
        "icon": "Acceleration",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "style": "Late",
            "phase_min": 3,
            "phase_max": 4,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "add_d", "value": 1, "duration": "this_roll"},
            {"type": "add_kh", "value": 1, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["late", "acceleration", "late_race"],
    },

    "s015": {
        "name": "Beeline Burst",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 1,
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_velocity", "mode": "flat_total", "value": 6, "duration": "this_roll"}
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
            {"type": "add_d", "value": 1, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["sprint", "straight", "acceleration"],
    },

    "s017": {
        "name": "Flash Forward",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 1,
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_velocity", "mode": "flat_total", "value": 6, "duration": "this_roll"}
        ],
        "active_roll": True,
        "tags": ["medium", "straight", "velocity"],
    },

    "s018": {
        "name": "Blast Forward",
        "icon": "Velocity",
        "cooldown": 8,
        "cost": 50,
        "trigger": {
            "path_type": 1,
            "distance_type": "Long",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_velocity", "mode": "flat_total", "value": 6, "duration": "this_roll"}
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
            "target_distance_max": 20,
        },
        "target": {"scope": "all_front", "limit": 2},
        "effects": [
            {"type": "apply_debuff_next_turn", "stat": "selected_die", "value": -2}
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
            "target_distance_max": 20,
        },
        "target": {"scope": "nearest_front", "limit": 1},
        "effects": [
            {"type": "reduce_stamina", "value": 1}
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
            {"type": "recover_stamina", "value": 1}
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
            {"type": "recover_stamina", "value": 1}
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
            {"type": "recover_stamina", "value": 1}
        ],
        "active_roll": False,
        "tags": ["medium", "front", "recovery"],
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
            {"type": "recover_stamina", "value": 1}
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
            {"type": "recover_stamina", "value": 1}
        ],
        "active_roll": False,
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
            "target_distance_max": 20,
        },
        "target": {"scope": "all_front", "limit": 3},
        "effects": [
            {"type": "apply_debuff_next_turn", "stat": "flat_total", "value": -5}
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
            "target_distance_min": -20,
            "target_distance_max": -1,
        },
        "target": {"scope": "all_back", "limit": 3},
        "effects": [
            {"type": "modify_enemy_gold_range", "value": -5, "duration": "next_turn"}
        ],
        "active_roll": False,
        "tags": ["blind", "pace", "debuff"],
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
            "target_distance_max": 20,
        },
        "target": {"scope": "all_front", "limit": 3},
        "effects": [
            {"type": "modify_enemy_gold_range", "value": -6, "duration": "next_turn"}
        ],
        "active_roll": False,
        "tags": ["blind", "long", "debuff"],
    },
}