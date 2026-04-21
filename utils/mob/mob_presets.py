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
                "add_dkh": 1,
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
                "add_dkh": 1,
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
            "speed": 7,
            "stamina": 4,
            "power": 6,
            "gut": 1,
            "wit": 1,

            "turf": 7,
            "dirt": 6,
            "sprint": 3,
            "mile": 7,
            "medium": 7,
            "long": 6,
            "front": 2,
            "pace": 7,
            "late": 7,
            "end_style": 4,
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
                "add_dkh": 3,
                "floor": 3,
                "selected_die": 0,
                "cap": 3,
                "self_heal_stamina": 0,
            }
        },
    },

    "sprinter_end": {
        "name": "Obey Your Master",
        "style": "End",
        "race_profile": {
            "speed": 4,
            "stamina": 4,
            "power": 7,
            "gut": 0,
            "wit": 1,

            "turf": 7,
            "dirt": 1,
            "sprint": 2,
            "mile": 6,
            "medium": 7,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 6,
            "end_style": 7,
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
                "add_dkh": 2,
                "floor": 3,
                "selected_die": 0,   # 🔥 boost ลูกที่เลือก
                "cap": 2,            # 🔥 สำคัญมากกับ 10d
                "self_heal_stamina": 0,
            }
        },
    },

    "boss_champion": {
        "name": "Beyond The Light",
        "style": "Pace",
        "race_profile": {
            "speed": 8,
            "stamina": 4,
            "power": 5,
            "gut": 1,
            "wit": 1,
            
            "turf": 7,
            "dirt": 1,
            "sprint": 1,
            "mile": 7,
            "medium": 7,
            "long": 6,
            "front": 1,
            "pace": 7,
            "late": 6,
            "end_style": 1,
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
                "add_dkh": 2,
                
                "floor": 3,
                "selected_die": 0,
                "cap": 3,
                "self_heal_stamina": 0,
            }
        },
    },

    "almond_eye": {
        "name": "Almond Eye",
        "style": "Pace",
        "race_profile": {
            "speed": 8,
            "stamina": 4,
            "power": 6,
            "gut": 2,
            "wit": 1,

            "turf": 7,
            "dirt": 1,
            "sprint": 2,
            "mile": 7,
            "medium": 7,
            "long": 3,
            "front": 1,
            "pace": 7,
            "late": 5,
            "end_style": 2,
        },
        "skills": {
            1: "s014",   # On Your Left!
            2: "s039",   # Rising Dragon
            3: "s042",   # Tail Nine
        },
        "zone": {
            "name": "Peerless Heroine",
            "image_url": "https://media.discordapp.net/attachments/1494733536656097340/1496040180648378428/-almond-eye.gif?ex=69e86f7e&is=69e71dfe&hm=3201c1caf77c93aebaa9050246a12b44920d492936be5df9ba20d7426a00f1a0&=&width=561&height=317",
            "points": 6,
            "build": {
                "flat": 0,
                "add_dkh": 3,
                "floor": 3,
                "selected_die": 0,
                "cap": 3,
                "self_heal_stamina": 0,
            }
        },
    },

    "equinox": {
        "name": "Equinox",
        "style": "Pace",
        "race_profile": {
            "speed": 8,
            "stamina": 8,
            "power": 8,
            "gut": 8,
            "wit": 8,

            "turf": 8,
            "dirt": 8,
            "sprint": 8,
            "mile": 8,
            "medium": 8,
            "long": 8,
            "front": 8,
            "pace": 8,
            "late": 8,
            "end_style": 8,
        },
        "skills": {
            1: "s012",   # Speed Star
            2: "s035",   # Radiant Star
            3: "s041",   # Rising Dragon / หรือสกิลท้ายแรงตัวอื่น
        },
        "zone": {
            "name": "I SHOW SPEED",
            "image_url": "https://media.discordapp.net/attachments/1494733536656097340/1496040976911831142/ishowspeed-speed.gif?ex=69e8703b&is=69e71ebb&hm=2b52dfe8463eb477dc7709da57887a7e790f51f4d57f59cd84d04368f0ec2765&=&width=561&height=374",
            "points": 6,
            "build": {
                "flat": 3,
                "add_dkh": 3,
                "floor": 3,
                "selected_die": 3,
                "cap": 3,
                "self_heal_stamina": 3,
            }
        },
    },
}