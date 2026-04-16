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
    "ProfessorOfCurvature": {
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

    "EncroachingShadow": {
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

    "Concentration": {
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

    "SwingingMaestro": {
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

    "GoHomeSpecialist": {
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

    "KeenEye": {
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
}