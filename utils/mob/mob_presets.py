from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHARACTER_DIR = BASE_DIR / "assets" / "characters"

thumnails = {
    "Rookie1": "https://media.discordapp.net/attachments/697810514448744448/1499637818228604978/2026-05-01_115945.png?ex=69f6d78d&is=69f5860d&hm=5b1d9d621d0d05111445415dc3dbfc7bd622432e9d2e21bc2ec2342506484685&=&format=webp&quality=lossless&width=554&height=497",
    "Rookie2": "https://media.discordapp.net/attachments/697810514448744448/1499637819352813669/2026-05-01_120449.png?ex=69f6d78e&is=69f5860e&hm=400d694636b583a161e87d6fd55c3dc01cfab83dca40db7b4fe88952c576e723&=&format=webp&quality=lossless&width=477&height=479",
    "Rookie3": "https://media.discordapp.net/attachments/697810514448744448/1499637820585672714/2026-05-01_120327.png?ex=69f6d78e&is=69f5860e&hm=62cb74c9d9c39e68cda4dece69b4e374ea392627662e5721f4675f7d99ea83d5&=&format=webp&quality=lossless&width=429&height=446",
    "Rookie4": "https://media.discordapp.net/attachments/697810514448744448/1499637821181530152/2026-05-01_120159.png?ex=69f6d78e&is=69f5860e&hm=6f5dd0a4417abe109486594b70cc920803bc573608b09b2ed6c999cac43722e1&=&format=webp&quality=lossless&width=1211&height=1202",
    
    "FujimasaMarch": "https://media.discordapp.net/attachments/697810514448744448/1499644108015272017/2026-05-01_121038.png?ex=69f6dd69&is=69f58be9&hm=d9b57dc56a1125aa67a0d29f9609caa63a90fb997c607fdf846651587bf28659&=&format=webp&quality=lossless&width=609&height=617",
    "OguriCap": "https://media.discordapp.net/attachments/697810514448744448/1499644107721674862/oguri-cap-icons-v0-u9uln20fic7g1.png?ex=69f6dd69&is=69f58be9&hm=8252a4885b7f65582e561addfb770b0bea7b9ad35bcae8a35ba6deaf7094f094&=&format=webp&quality=lossless&width=1080&height=1080",
    "ObeyYourMaster": "https://media.discordapp.net/attachments/697810514448744448/1499644108841549965/3a7b0a372020f36c86bd9ee53eb64184.jpg?ex=69f6dd69&is=69f58be9&hm=ccb67c0aee388e56cb5ef039578a2b915e5581b57208ceb15547c8744b045999&=&format=webp&width=354&height=354",
    "BeyondTheLight": "https://media.discordapp.net/attachments/697810514448744448/1499644108577312839/4c0fa686a849947746b5c1a06720c9ab.jpg?ex=69f6dd69&is=69f58be9&hm=4789496a55fa43f4baa21ac13806fda80d06672872a10a9804e61b70b59f7125&=&format=webp&width=1104&height=1104",
    "AlmondEye": "https://media.discordapp.net/attachments/697810514448744448/1499644108292231208/2026-05-01_122211.png?ex=69f6dd69&is=69f58be9&hm=d4a5b420ac0ec8f5ec50790f6cb0826ca80291209110b683dfb6e64e433b064c&=&format=webp&quality=lossless&width=528&height=533",
    "Equinox": "https://media.discordapp.net/attachments/697810514448744448/1499644107398844577/image.png?ex=69f6dd69&is=69f58be9&hm=9ffefbc037f34ffe3dbfdddec12b5a6114befa93cc95700214f2f15411468bd4&=&format=webp&quality=lossless&width=1059&height=1013",

    "aaa": "",
}

MOB_PRESETS = {
    "rookie_front": {
        "name": "Rookie Runner",
        "avatar": CHARACTER_DIR / "mob_01.png",
        "thumnail": thumnails["Rookie1"],
        "style": "Front",
        "race_profile": {
            "speed": 6,
            "stamina": 4,
            "power": 5,
            "gut": 1,
            "wit": 3,

            "turf": 1,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 1,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: "s033",
            2: "s025",
            3: "s034",
        },
        "zone": {
            "name": "Default Zone",
            "image_url": "",
            "points": 0,
            "build": {
                "flat": 0,
                "add_dkh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 0,
                "self_heal_stamina": 0,
                "modify_current_speed": 5,
            },
        },
    },

    "rookie_pace": {
        "name": "Rookie Pace",
        "avatar": CHARACTER_DIR / "mob_02.png",
        "thumnail": thumnails["Rookie2"],
        "style": "Pace",
        "race_profile": {
            "speed": 5,
            "stamina": 4,
            "power": 5,
            "gut": 2,
            "wit": 3,

            "turf": 1,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 1,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: "s007",
            2: "s021",
            3: "s032",
        },
        "zone": {
            "name": "Default Zone",
            "image_url": "",
            "points": 0,
            "build": {
                "flat": 0,
                "add_dkh": 1,
                "floor": 0,
                "selected_die": 0,
                "cap": 2,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            },
        },
    },

    "rookie_late": {
        "name": "Rookie Late",
        "avatar": CHARACTER_DIR / "mob_03.png",
        "thumnail": thumnails["Rookie3"],
        "style": "Late",
        "race_profile": {
            "speed": 4,
            "stamina": 4,
            "power": 6,
            "gut": 2,
            "wit": 3,

            "turf": 1,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 1,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: "s014",
            2: "s026",
            3: "s039",
        },
        "zone": {
            "name": "Default Zone",
            "image_url": "",
            "points": 0,
            "build": {
                "flat": 0,
                "add_dkh": 1,
                "floor": 0,
                "selected_die": 0,
                "cap": 2,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            },
        },
    },

    "rookie_end": {
        "name": "Rookie End",
        "avatar": CHARACTER_DIR / "mob_04.png",
        "thumnail": thumnails["Rookie4"],
        "style": "End",
        "race_profile": {
            "speed": 4,
            "stamina": 4,
            "power": 7,
            "gut": 1,
            "wit": 3,

            "turf": 1,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 1,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: "s010",
            2: "s031",
            3: "s005",
        },
        "zone": {
            "name": "Default Zone",
            "image_url": "",
            "points": 0,
            "build": {
                "flat": 0,
                "add_dkh": 1,
                "floor": 0,
                "selected_die": 0,
                "cap": 2,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            },
        },
    },

    "fujimasa_march": {
        "name": "Fujimasa March",
        "avatar": CHARACTER_DIR / "fujimasa_march.png",
        "thumnail": thumnails["FujimasaMarch"],
        "style": "Pace",
        "race_profile": {
            "speed": 6,
            "stamina": 4,
            "power": 5,
            "gut": 4,
            "wit": 1,

            "turf": 1,
            "dirt": 1,
            "sprint": 1,
            "mile": 1,
            "medium": 1,
            "long": 1,
            "front": 1,
            "pace": 1,
            "late": 1,
            "end_style": 1,
        },
        "skills": {
            1: "s007",
            2: "s032",
            3: "s015",
        },
        "zone": {
            "name": "Abyssal Lament",
            "image_url": "https://media.discordapp.net/attachments/1494733536656097340/1496112663816573059/fujimasa-march-cinderella-gray.gif?ex=69e8b2ff&is=69e7617f&hm=4b9847c6807ca04264aa0ea40a6bfac752465cd8ef4c96ec8ac962045b2cdb68&=&width=561&height=317",
            "points": 0,
            "build": {
                "flat": 0,
                "add_dkh": 2,
                "floor": 2,
                "selected_die": 0,
                "cap": 3,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            },
        },
    },

    "oguri_cap": {
        "name": "Oguri Cap",
        "avatar": CHARACTER_DIR / "oguri_cap.png",
        "thumnail": thumnails["OguriCap"],
        "style": "Late",
        "race_profile": {
            "speed": 7,
            "stamina": 6,
            "power": 8,
            "gut": 6,
            "wit": 1,

            "turf": 7,"dirt": 6,
            "sprint": 3,"mile": 7,"medium": 7,"long": 6,
            "front": 2,"pace": 7,"late": 7,"end_style": 4,
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
                "cap": 7,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },

    "obey_your_master": {
        "name": "Obey Your Master",
        "avatar": CHARACTER_DIR / "obey_your_master.png",
        "thumnail": thumnails["ObeyYourMaster"],
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
                "selected_die": 0,   
                "cap": 2,            
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },

    "beyond_the_light": {
        "name": "Beyond The Light",
        "avatar": CHARACTER_DIR / "beyond_the_light.png",
        "thumnail": thumnails["BeyondTheLight"],
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
                "add_dkh": 3,
                
                "floor": 3,
                "selected_die": 0,
                "cap": 3,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },

    "almond_eye": {
        "name": "Almond Eye",
        "avatar": CHARACTER_DIR / "almond_eye.png",
        "thumnail": thumnails["AlmondEye"],
        "style": "Pace",
        "race_profile": {
            "speed": 8,
            "stamina": 8,
            "power": 8,
            "gut": 8,
            "wit": 8,

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
                "add_dkh": 4,
                "floor": 5,
                "selected_die": 0,
                "cap": 7,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },

    "equinox": {
        "name": "Equinox",
        "avatar": CHARACTER_DIR / "equinox.png",
        "thumnail": thumnails["Equinox"],
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
                "cap": 7,
                "self_heal_stamina": 3,
                "modify_current_speed": 3,
            }
        },
    },
}