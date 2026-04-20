MOB_PRESETS = {
    "rookie_front": {
        "name": "Rookie Runner",
        "style": "Front",
        "race_profile": {
            "speed": 2,
            "stamina": 2,
            "power": 2,
            "gut": 1,
            "wit": 1,

            "turf": 1,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 1,
            "long": 1,
            "front": 2,
            "pace": 1,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: None,
            2: None,
            3: None,
        },
        "zone": {
            "name": "Default Zone",
            "image_url": "",
            "points": 0,
            "build": {
                "flat": 0,
                "add_d": 0,
                "add_kh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 0,
                "self_heal_stamina": 0,
            },
            "left": 0,
        },
    },

    "runner_pace": {
        "name": "Field Pace",
        "style": "Pace",
        "race_profile": {
            "speed": 3,
            "stamina": 3,
            "power": 2,
            "gut": 2,
            "wit": 2,

            "turf": 2,
            "dirt": 1,
            "sprint": 1,
            "mile": 2,
            "medium": 2,
            "long": 1,
            "front": 1,
            "pace": 3,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: "s007",   # Technician
            2: None,
            3: None,
        },
        "zone": {
            "name": "Pace Zone",
            "image_url": "",
            "points": 3,
            "build": {
                "flat": 1,
                "add_d": 0,
                "add_kh": 0,
                "floor": 1,
                "selected_die": 0,
                "cap": 1,
                "self_heal_stamina": 0,
            },
        },
    },

    "chaser_late": {
        "name": "Shadow Chaser",
        "style": "Late",
        "race_profile": {
            "speed": 3,
            "stamina": 2,
            "power": 3,
            "gut": 2,
            "wit": 2,

            "turf": 2,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 2,
            "long": 2,
            "front": 1,
            "pace": 1,
            "late": 3,
            "end_style": 2,
        },
        "skills": {
            1: "s014",   # On Your Left!
            2: "s039",   # Rising Dragon
            3: None,
        },
        "zone": {
            "name": "Shadow Zone",
            "image_url": "",
            "points": 4,
            "build": {
                "flat": 0,
                "add_d": 1,
                "add_kh": 0,
                "floor": 1,
                "selected_die": 0,
                "cap": 1,
                "self_heal_stamina": 0,
            },
        },
    },

    "sprinter_end": {
        "name": "Sprint Phantom",
        "style": "End",
        "race_profile": {
            "speed": 4,
            "stamina": 1,
            "power": 2,
            "gut": 2,
            "wit": 2,

            "turf": 2,
            "dirt": 1,
            "sprint": 3,
            "mile": 2,
            "medium": 1,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 2,
            "end_style": 3,
        },
        "skills": {
            1: "s002",   # Encroaching Shadow
            2: "s016",   # Turbo Sprint
            3: None,
        },
        "zone": {
            "name": "Phantom Burst",
            "image_url": "",
            "points": 4,
            "build": {
                "flat": 0,
                "add_d": 1,
                "add_kh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 1,
                "self_heal_stamina": 0,
            },
        },
    },

    "boss_champion": {
        "name": "Champion Alpha",
        "style": "Pace",
        "race_profile": {
            "speed": 5,
            "stamina": 5,
            "power": 5,
            "gut": 4,
            "wit": 4,
            
            "turf": 3,
            "dirt": 2,
            "sprint": 2,
            "mile": 3,
            "medium": 3,
            "long": 3,
            "front": 2,
            "pace": 4,
            "late": 3,
            "end_style": 2,
        },
        "skills": {
            1: "s012",   # Speed Star
            2: "s035",   # Radiant Star
            3: "s040",   # Tail Nine
        },
        "zone": {
            "name": "Champion Zone",
            "image_url": "",
            "points": 6,
            "build": {
                "flat": 2,
                "add_d": 1,
                "add_kh": 0,
                "floor": 1,
                "selected_die": 0,
                "cap": 1,
                "self_heal_stamina": 1,
            },
        },
    },
}