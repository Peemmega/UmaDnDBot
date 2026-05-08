from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHARACTER_DIR = BASE_DIR / "assets" / "characters"

thumnails = {
    "Rookie1": "https://media.discordapp.net/attachments/697810514448744448/1499637818228604978/2026-05-01_115945.png?ex=69f6d78d&is=69f5860d&hm=5b1d9d621d0d05111445415dc3dbfc7bd622432e9d2e21bc2ec2342506484685&=&format=webp&quality=lossless&width=554&height=497",
    "Rookie2": "https://media.discordapp.net/attachments/697810514448744448/1499637819352813669/2026-05-01_120449.png?ex=69f6d78e&is=69f5860e&hm=400d694636b583a161e87d6fd55c3dc01cfab83dca40db7b4fe88952c576e723&=&format=webp&quality=lossless&width=477&height=479",
    "Rookie3": "https://media.discordapp.net/attachments/697810514448744448/1499637820585672714/2026-05-01_120327.png?ex=69f6d78e&is=69f5860e&hm=62cb74c9d9c39e68cda4dece69b4e374ea392627662e5721f4675f7d99ea83d5&=&format=webp&quality=lossless&width=429&height=446",
    "Rookie4": "https://media.discordapp.net/attachments/697810514448744448/1499637821181530152/2026-05-01_120159.png?ex=69f6d78e&is=69f5860e&hm=6f5dd0a4417abe109486594b70cc920803bc573608b09b2ed6c999cac43722e1&=&format=webp&quality=lossless&width=1211&height=1202",
    
    "FujimasaMarch": "https://media.discordapp.net/attachments/697810514448744448/1499644108015272017/2026-05-01_121038.png",
    "OguriCap": "https://media.discordapp.net/attachments/697810514448744448/1499644107721674862/oguri-cap-icons-v0-u9uln20fic7g1.png",
    "ObeyYourMaster": "https://media.discordapp.net/attachments/697810514448744448/1499644108841549965/3a7b0a372020f36c86bd9ee53eb64184.jpg?ex=69f6dd69&is=69f58be9&hm=ccb67c0aee388e56cb5ef039578a2b915e5581b57208ceb15547c8744b045999&=&format=webp&width=354&height=354",
    "BeyondTheLight": "https://media.discordapp.net/attachments/697810514448744448/1499644108577312839/4c0fa686a849947746b5c1a06720c9ab.jpg?ex=69f6dd69&is=69f58be9&hm=4789496a55fa43f4baa21ac13806fda80d06672872a10a9804e61b70b59f7125&=&format=webp&width=1104&height=1104",
    "AlmondEye": "https://media.discordapp.net/attachments/697810514448744448/1499644108292231208/2026-05-01_122211.png",
    "Equinox": "https://media.discordapp.net/attachments/697810514448744448/1499644107398844577/image.png",

    "Orfevre": "https://media.discordapp.net/attachments/697810514448744448/1501877411736846346/orfevre.png?ex=69fdabd6&is=69fc5a56&hm=b113ec0a768cdfc0a0ada79d9012dcc1746e93e0a542031c16209321671e3dca&=&format=webp&quality=lossless&width=617&height=603",
    "Gentildonna": "https://media.discordapp.net/attachments/697810514448744448/1501877412097687592/gentildonna.png?ex=69fdabd6&is=69fc5a56&hm=316cea94428f39b9b75a5389683b48b06fff378618f0765b257ffc1f0ebddca1&=&format=webp&quality=lossless&width=1040&height=1080",
    "Verxina": "https://media.discordapp.net/attachments/697810514448744448/1501877410662977638/verxina.png?ex=69fdabd6&is=69fc5a56&hm=fb13acd113f2a020aac967c8b83d7297188e70552c2943c8ae2f326716bed5c3&=&format=webp&quality=lossless&width=695&height=699",
    "StillInLove": "https://media.discordapp.net/attachments/697810514448744448/1501877410348400740/still_in_love.png?ex=69fdabd6&is=69fc5a56&hm=1e0ee128672b833bbfb0b743917d19d22063850714ad15b122862ec9b41641a5&=&format=webp&quality=lossless&width=1289&height=1265",
    "SpecialWeek": "https://media.discordapp.net/attachments/697810514448744448/1501877410948186222/special_week_2.png?ex=69fdabd6&is=69fc5a56&hm=80e639767f44a85c7855d9a6fa30dd7954b17198dd986e7f111803e5f8c3a163&=&format=webp&quality=lossless&width=560&height=545",
    "SilecneSusuka": "https://media.discordapp.net/attachments/697810514448744448/1501877411267219559/silent_susuka.png?ex=69fdabd6&is=69fc5a56&hm=ea687d3b478824505cf91f4ed30b6ef8cabbcfc702766f355f6986843fb54555&=&format=webp&quality=lossless&width=734&height=749",
    
    "aaa": "",
}

MOB_PRESETS = {
    "rookie_front": {
        "name": "Rookie Runner",
        "avatar": CHARACTER_DIR / "mob_01.png",
        "thumnail": thumnails["Rookie1"],
        "style": "Front",
        "race_profile": {
            "speed": 5,
            "stamina": 4,
            "power": 6,
            "gut": 1,
            "wit": 1,

            "turf": 1,"dirt": 1,
            "sprint": 1,"mile": 1,"medium": 1,"long": 1,
            "front": 1,"pace": 1,"late": 1,"end_style": 1,
        },
        "skills": {
            # 1: "s033",
            # 2: "s035",
            # 4: "s030",
            # 3: "s034",
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
            "speed": 4,
            "stamina": 4,
            "power": 5,
            "gut": 2,
            "wit": 2,

            "turf": 1,"dirt": 1,
            "sprint": 1,"mile": 1,"medium": 1,"long": 1,
            "front": 1,"pace": 1,"late": 1,"end_style": 1,
        },
        "skills": {
            # 1: "s013",
            # 2: "s015",
            # 3: "s032",
            # 4: "s047",
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
            "power": 5,
            "gut": 2,
            "wit": 2,

            "turf": 1,"dirt": 1,
            "sprint": 1,"mile": 1,"medium": 1,"long": 1,
            "front": 1,"pace": 1,"late": 1,"end_style": 1,
        },
        "skills": {
            # 1: "s014",
            # 2: "s015",
            # 3: "s037",
            # 4: "s049",
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
            "power": 6,
            "gut": 2,
            "wit": 1,

            "turf": 1,"dirt": 1,
            "sprint": 1,"mile": 1,"medium": 1,"long": 1,
            "front": 1,"pace": 1,"late": 1,"end_style": 1,
        },
        "skills": {
            # 1: "s010",
            # 2: "s031",
            # 3: "s036",
            # 4: "s002",
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

            "turf": 1,"dirt": 1,
            "sprint": 1,"mile": 1,"medium": 1,"long": 1,
            "front": 1,"pace": 1,"late": 1,"end_style": 1,
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
        "avatar": CHARACTER_DIR / "obey_your_master.jpg",
        "thumnail": thumnails["ObeyYourMaster"],
        "style": "End",
        "race_profile": {
            "speed": 4,
            "stamina": 4,
            "power": 7,
            "gut": 0,
            "wit": 1,

            "turf": 7,"dirt": 1,
            "sprint": 2,"mile": 6,"medium": 7,"long": 1,
            "front": 1,"pace": 1,"late": 6,"end_style": 7,
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
        "avatar": CHARACTER_DIR / "beyond_the_light.jpg",
        "thumnail": thumnails["BeyondTheLight"],
        "style": "Pace",
        "race_profile": {
            "speed": 8,
            "stamina": 4,
            "power": 5,
            "gut": 1,
            "wit": 1,
            
            "turf": 7,"dirt": 1,
            "sprint": 1,"mile": 7,"medium": 7,"long": 6,
            "front": 1,"pace": 7,"late": 6,"end_style": 1,
        },
        "skills": {
            1: "s012",   # Speed Star
            2: "s035",   # Radiant Star
            3: "s040",   # Tail Nine
        },
        "zone": {
            "name": "Champion Zone",
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1495910874370543746/agnes-tachyon-watch-me-run.gif?ex=69e7f711&is=69e6a591&hm=2cf187ac55166488c0e95a9e598dc6cfda93ec3a3a6df21e393cfb3ec8631179&=&width=561&height=317",
            
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

            "turf": 7,"dirt": 1,
            "sprint": 2, "mile": 7, "medium": 7, "long": 3,
            "front": 1, "pace": 7, "late": 5, "end_style": 2,
        },
        "skills": {
            1: "s014",   # On Your Left!
            2: "s039",   # Rising Dragon
            3: "s042",   # Tail Nine
        },
        "zone": {
            "name": "Peerless Heroine",
            "image_url": "https://media.discordapp.net/attachments/1494733536656097340/1496040180648378428/-almond-eye.gif?ex=69e86f7e&is=69e71dfe&hm=3201c1caf77c93aebaa9050246a12b44920d492936be5df9ba20d7426a00f1a0&=&width=561&height=317",
            
            "build": {
                "flat": 0,
                "add_dkh": 1,
                "floor": 5,
                "selected_die": 0,
                "cap": 7,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },

    "orfevre": {
        "name": "Orfevre",
        "avatar": CHARACTER_DIR / "orfevre.png",
        "thumnail": thumnails["Orfevre"],
        "style": "End",
        "race_profile": {
            "speed": 4,
            "stamina": 5,
            "power": 6,
            "gut": 3,
            "wit": 2,

            "turf": 7,"dirt": 1,
            "sprint": 1, "mile": 5, "medium": 7, "long": 7,
            "front": 1, "pace": 2, "late": 7, "end_style": 7,
        },
        "skills": {
            1: "s002",  # Encroaching Shadow
            2: "s031",  # No Stopping Me!
            3: "s037",  # In Body and Mind
            4: "s010",  # The Coast Is Clear!
        },
        "zone": {
            "name": "None Shall Object My Rule",
            "image_url": "https://cdn.discordapp.com/attachments/697810514448744448/1501860045405818880/orfevre-umamusume.gif",
            
            "build": {
                "flat": 0,
                "add_dkh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 0,
                "self_heal_stamina": 0,
                "modify_current_speed": 5,
            }
        },
    },
    "gentildonna": {
        "name": "Gentildonna",
        "avatar": CHARACTER_DIR / "gentildonna.png",
        "thumnail": thumnails["Gentildonna"],
        "style": "Pace",
        "race_profile": {
            "speed": 5,
            "stamina": 4,
            "power": 5,
            "gut": 2,
            "wit": 4,

            "turf": 7,"dirt": 1,
            "sprint": 1, "mile": 7, "medium": 7, "long": 7,
            "front": 3, "pace": 7, "late": 7, "end_style": 4,
        },
        "skills": {
            1: "s032",  # Neck and Neck
            2: "s035",  # Radiant Star
            3: "s045",  # Moving Past, and Beyond
            4: "s012",  # Speed Star
        },
        "zone": {
            "name": "Rose Conquest",
            "image_url": "https://cdn.discordapp.com/attachments/697810514448744448/1501860043153215488/gentildonna-uma.gif",
            
            "build": {
                "flat": 0,
                "add_dkh": 1,
                "floor": 0,
                "selected_die": 0,
                "cap": 2,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },
    "verxina": {
        "name": "Verxina",
        "avatar": CHARACTER_DIR / "verxina.png",
        "thumnail": thumnails["Verxina"],
        "style": "Front",
        "race_profile": {
            "speed": 6,
            "stamina": 5,
            "power": 5,
            "gut": 1,
            "wit": 3,

            "turf": 7,"dirt": 1,
            "sprint": 4, "mile": 7, "medium": 7, "long": 1,
            "front": 7, "pace": 7, "late": 3, "end_style": 1,
        },
        "skills": {
            1: "s033",  # Runaway
            2: "s034",  # Unrestrained
            3: "s043",  # Red Shift/LP1211-M
            4: "s046",  # Angling and Scheming
        },
        "zone": {
            "name": "Queen's Rebirth",
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1501860043618910380/star-rail-seele.gif?ex=69fd9ba9&is=69fc4a29&hm=6340d35338211b603505e6cace56ac47a5ef6a32616f59fb232eea2de0605a43&=&width=747&height=420",
            
            "build": {
                "flat": 0,
                "add_dkh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 0,
                "self_heal_stamina": 0,
                "modify_current_speed": 5,
            }
        },
    },
    "still_in_love": {
        "name": "Still In Love",
        "avatar": CHARACTER_DIR / "still_in_love.png",
        "thumnail": thumnails["StillInLove"],
        "style": "Late",
        "race_profile": {
            "speed": 4,
            "stamina": 4,
            "power": 5,
            "gut": 3,
            "wit": 4,

            "turf": 7,"dirt": 1,
            "sprint": 5, "mile": 7, "medium": 7, "long": 1,
            "front": 1, "pace": 7, "late": 7, "end_style": 2,
        },
        "skills": {
            1: "s014",  # On Your Left!
            2: "s038",  # All-Seeing Eyes
            3: "s039",  # Rising Dragon
            4: "s042",  # Let's Pump Some Iron
        },
        "zone": {
            "name": "Scarlet Lily's Elation",
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1501860044105322657/still-in-love-umamusume.gif?ex=69fd9ba9&is=69fc4a29&hm=55cc976721949bfe47c4c5caa70a4100a65148fd4ccc034d0fc949573268140e&=&width=747&height=422",
            
            "build": {
                "flat": 0,
                "add_dkh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 2,
                "self_heal_stamina": 0,
                "modify_current_speed": 3,
            }
        },
    },
    "special_week": {
        "name": "Special Week",
        "avatar": CHARACTER_DIR / "special_week.png",
        "thumnail": thumnails["SpecialWeek"],
        "style": "Pace",
        "race_profile": {
            "speed": 5,
            "stamina": 5,
            "power": 4,
            "gut": 3,
            "wit": 3,

            "turf": 7,"dirt": 1,
            "sprint": 2, "mile": 5, "medium": 7, "long": 7,
            "front": 1, "pace": 7, "late": 7, "end_style": 5,
        },
        "skills": {
            1: "s033",  # Runaway
            2: "s034",  # Unrestrained
            3: "s043",  # Red Shift/LP1211-M
            4: "s046",  # Angling and Scheming
        },
        "zone": {
            "name": "Shooting Star",
            "image_url": "https://media.discordapp.net/attachments/697810514448744448/1501860044654903357/special-week-uma-musume.gif?ex=69fd9ba9&is=69fc4a29&hm=cd45451695cd05f8381609c0ef8d8ae5daa05e883a90b0d060c6d1a8247e4f8a&=&width=747&height=422",
            
            "build": {
                "flat": 0,
                "add_dkh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 7,
                "self_heal_stamina": 0,
                "modify_current_speed": 0,
            }
        },
    },
    "silecne_susuka": {
        "name": "Silecnt Susuka",
        "avatar": CHARACTER_DIR / "silecne_susuka.png",
        "thumnail": thumnails["SilecneSusuka"],
        "style": "Front",
        "race_profile": {
            "speed": 7,
            "stamina": 4,
            "power": 3,
            "gut": 1,
            "wit": 5,

            "turf": 7,"dirt": 1,
            "sprint": 4, "mile": 7, "medium": 7, "long": 3,
            "front": 7, "pace": 5, "late": 3, "end_style": 1,
        },
        "skills": {
            1: "s032",  # Neck and Neck
            2: "s035",  # Radiant Star
            3: "s045",  # Moving Past, and Beyond
            4: "s012",  # Speed Star
        },
        "zone": {
            "name": "I'm Not Giving up the Lead!",
            "image_url": "https://cdn.discordapp.com/attachments/697810514448744448/1501860045019680828/umamusume-.gif?ex=69fd9ba9&is=69fc4a29&hm=95851edc8c16f46af7011011ccc5e5b2094f800284a9f0ca0c01937cb175409a&",
            
            "build": {
                "flat": 0,
                "add_dkh": 0,
                "floor": 0,
                "selected_die": 0,
                "cap": 0,
                "self_heal_stamina": 0,
                "modify_current_speed": 5,
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

            "turf": 8, "dirt": 8,
            "sprint": 8, "mile": 8, "medium": 8, "long": 8,
            "front": 8, "pace": 8, "late": 8, "end_style": 8,
        },
        "skills": {
            1: "s012",   # Speed Star
            2: "s035",   # Radiant Star
            3: "s041",   # Rising Dragon / หรือสกิลท้ายแรงตัวอื่น
        },
        "zone": {
            "name": "I SHOW SPEED",
            "image_url": "https://media.discordapp.net/attachments/1494733536656097340/1496040976911831142/ishowspeed-speed.gif?ex=69e8703b&is=69e71ebb&hm=2b52dfe8463eb477dc7709da57887a7e790f51f4d57f59cd84d04368f0ec2765&=&width=561&height=374",
            
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