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
                "add_d": 1,
                "add_kh": 1,         # 🔥 สำคัญ
                "floor": 0,
                "selected_die": 1,
                "cap": 2,
                "self_heal_stamina": 0,
            },
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
                "flat": 0,
                "add_d": 1,
                "add_kh": 1,         # 🔥 สำคัญ
                "floor": 0,
                "selected_die": 1,
                "cap": 2,
                "self_heal_stamina": 0,
            },
        },
    },

    "chaser_late": {
        "name": "Oguri Cap",
        "style": "Late",
        "race_profile": {
            "speed": 5,
            "stamina": 4,
            "power": 4,
            "gut": 1,
            "wit": 3,

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
            "name": "Grey Phantom",
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1495910813691809813/umamusume-cinderella-gray.gif?ex=69e7f702&is=69e6a582&hm=79435ae723a1e2952da81083223166a29644bfccc6e26dc43f7d952fbe424707&=&width=561&height=317",
            "points": 4,
            "build": {
                "flat": 0,
                "add_d": 2,
                "add_kh": 2,         # 🔥 สาย late ต้อง kh เยอะ
                "floor": 0,
                "selected_die": 1,
                "cap": 2,
                "self_heal_stamina": 0,
            }
        },
    },

    "sprinter_end": {
        "name": "Obey Your Master",
        "style": "End",
        "race_profile": {
            "speed": 6,
            "stamina": 4,
            "power": 3,
            "gut": 0,
            "wit": 3,

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
            "name": "Wild Joker",
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1495910826534637709/obey-your-master-umamusume.gif?ex=69e7f705&is=69e6a585&hm=dbb241a5960cf39bc83a4fffba9b24dcbf2888d7fc6b46257c1e0a9e004462a0&=&width=561&height=317",
            "points": 4,
            "build": {
                "flat": 0,
                "add_d": 0,
                "add_kh": 0,
                "floor": 0,
                "selected_die": 2,   # 🔥 boost ลูกที่เลือก
                "cap": 4,            # 🔥 สำคัญมากกับ 10d
                "self_heal_stamina": 0,
            }
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
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1495910874370543746/agnes-tachyon-watch-me-run.gif?ex=69e7f711&is=69e6a591&hm=2cf187ac55166488c0e95a9e598dc6cfda93ec3a3a6df21e393cfb3ec8631179&=&width=561&height=317",
            "points": 6,
            "build": {
                "flat": 0,
                "add_d": 2,
                "add_kh": 1,
                "floor": 0,
                "selected_die": 1,
                "cap": 5,
                "self_heal_stamina": 0,
            }
        },
    },
}