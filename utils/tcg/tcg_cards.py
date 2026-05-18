TODO_TEXT = "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"

KEYWORD_TAGS = {
    "Rush": "ลงมาแล้วสามารถโจมตีได้ทันที",
    "Quick Step": "สามารถลงการ์ดใบนี้แบบ Flash ได้",
    "Counter": "ถ้าไม่ถูกทำลายหลังโจมตี ทำลายการ์ดที่โจมตี",
    "Guard": "ป้องกันการถูกทำลาย {value} ครั้ง",
    "Duel": "สามารถโจมตีใส่การ์ด Trainee ที่ฟื้นสภาพอยู่ได้",
    "Impact": "ทำดาเมจใส่ Life Zone 2 หน่วยเมื่อโจมตี Trainer สำเร็จ",
    "Burning Soul": "พลังเพิ่ม 2 เท่าเมื่อโจมตี และทำลายการ์ดใบนี้หลังต่อสู้",
    "Fury": "ชนะแล้วฟื้นสภาพอีกครั้ง {value} ครั้ง",
    "Trick": "ทำงานเมื่อใช้ Event Card {value} ครั้ง",
    "Fan": "ทำงานเมื่อการ์ดใบนี้ได้รับ {value} Carrot",
    "Last Stand": "เมื่อการ์ดนี้กำลังถูกทำลาย สามารถสั่งโจมตีได้ 1 ครั้งก่อนถูกทำลาย และไม่สามารถใช้งาน Carrot ในการโจมตีนี้ได้",
}

CARD_DATABASE = {
    "UMT-001": {"id": "UMT-001", "name": "Spica Trainer", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_001.webp", "text": TODO_TEXT},
    "UMT-002": {"id": "UMT-002", "name": "Trainer Kitahara", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_002.webp", "text": TODO_TEXT},
    "UMT-003": {"id": "UMT-003", "name": "Trainer Riko", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_003.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMT-004": {"id": "UMT-004", "name": "Trainer Muteki", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_004.webp", "text": TODO_TEXT},
    "UMT-005": {"id": "UMT-005", "name": "Trainer Kuronuma", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_005.webp", "text": TODO_TEXT, "tags": ["Last Stand"]},
    "UMT-006": {"id": "UMT-006", "name": "Trainer Tsubaki", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_006.webp", "text": "TODO"},

    "UMC-01": {"id": "UMC-01", "name": "Carrot", "type": "Carrot", "cost": 0, "power": 0, "image": "/tcg/cards/carrots/UMC_01.webp", "text": TODO_TEXT},
    
    "UMTD01-01": {"id": "UMTD01-01", "name": "Oguri Cap", "type": "Trainee", "cost": 6, "power": 6000, "image": "/tcg/cards/trainees/UMTD01_01.webp", "text": TODO_TEXT, "tags": ["Rush"]},
    "UMTD01-02": {"id": "UMTD01-02", "name": "Tamamo Cross", "type": "Trainee", "cost": 5, "power": 5000, "image": "/tcg/cards/trainees/UMTD01_02.webp", "text": TODO_TEXT, "tags": ["Rush", "Quick Step"]},
    "UMTD01-03": {"id": "UMTD01-03", "name": "Fujimasa March", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMTD01_03.webp", "text": TODO_TEXT, "tags": ["Rush"]},
    "UMTD01-04": {"id": "UMTD01-04", "name": "Belno Light", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMTD01_04.webp", "text": TODO_TEXT},
    "UMTD01-05": {"id": "UMTD01-05", "name": "Super Creek", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMTD01_05.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMTD01-06": {"id": "UMTD01-06", "name": "Dicta Striker", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMTD01_06.webp", "text": TODO_TEXT, "tags": ["Block", "Quick Step"]},
    "UMTD01-07": {"id": "UMTD01-07", "name": "Party Time", "type": "Event", "cost": 0, "power": 0, "image": "/tcg/cards/trainees/UMTD01_07.webp", "text": TODO_TEXT},
    "UMTD01-08": {"id": "UMTD01-08", "name": "Special Meal", "type": "Event", "cost": 1, "power": 0, "image": "/tcg/cards/trainees/UMTD01_08.webp", "text": TODO_TEXT},
    "UMTD01-09": {"id": "UMTD01-09", "name": "Training", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD01_09.webp", "text": TODO_TEXT},
    "UMTD01-10": {"id": "UMTD01-10", "name": "Grey Monster", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD01_10.webp", "text": TODO_TEXT},
    "UMTD02-01": {"id": "UMTD02-01", "name": "T.M. Opera O", "type": "Trainee", "cost": 7, "power": 6000, "image": "/tcg/cards/trainees/UMTD02_01.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMTD02-02": {"id": "UMTD02-02", "name": "Biwa Hayahide", "type": "Trainee", "cost": 6, "power": 5000, "image": "/tcg/cards/trainees/UMTD02_02.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMTD02-03": {"id": "UMTD02-03", "name": "Meisho Doto", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMTD02_03.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMTD02-04": {"id": "UMTD02-04", "name": "Rice Shower", "type": "Trainee", "cost": 4, "power": 2000, "image": "/tcg/cards/trainees/UMTD02_04.webp", "text": TODO_TEXT, "tags": ["Counter"]},
    "UMTD02-05": {"id": "UMTD02-05", "name": "Mejiro McQueen", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMTD02_05.webp", "text": TODO_TEXT},
    "UMTD02-06": {"id": "UMTD02-06", "name": "Tokai Teio", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMTD02_06.webp", "text": TODO_TEXT},
    "UMTD02-07": {"id": "UMTD02-07", "name": "Uma Engine", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD02_07.webp", "text": TODO_TEXT},
    "UMTD02-08": {"id": "UMTD02-08", "name": "Training", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD02_08.webp", "text": TODO_TEXT},
    "UMTD02-09": {"id": "UMTD02-09", "name": "Centurial Overlord", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD02_09.webp", "text": TODO_TEXT},
    "UMTD02-10": {"id": "UMTD02-10", "name": "Hard Training", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD02_10.webp", "text": TODO_TEXT},
    "UMTD03-01": {"id": "UMTD03-01", "name": "Gentildonna", "type": "Trainee", "cost": 8, "power": 7000, "image": "/tcg/cards/trainees/UMTD03_01.webp", "text": TODO_TEXT, "tags": ["Duel"]},
    "UMTD03-02": {"id": "UMTD03-02", "name": "Yaeno Muteki", "type": "Trainee", "cost": 6, "power": 5000, "image": "/tcg/cards/trainees/UMTD03_02.webp", "text": TODO_TEXT, "tags": ["Duel"]},
    "UMTD03-03": {"id": "UMTD03-03", "name": "Tanino Gimlet", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMTD03_03.webp", "text": TODO_TEXT},
    "UMTD03-04": {"id": "UMTD03-04", "name": "Symboli Kris S", "type": "Trainee", "cost": 3, "power": 3000, "image": "/tcg/cards/trainees/UMTD03_04.webp", "text": TODO_TEXT},
    "UMTD03-05": {"id": "UMTD03-05", "name": "Narita Brian", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMTD03_05.webp", "text": TODO_TEXT, "tags": ["Duel"]},
    "UMTD03-06": {"id": "UMTD03-06", "name": "Mejiro Ryan", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMTD03_06.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMTD03-07": {"id": "UMTD03-07", "name": "Warrior Spirit", "type": "Event", "cost": 4, "power": 0, "image": "/tcg/cards/trainees/UMTD03_07.webp", "text": TODO_TEXT},
    "UMTD03-08": {"id": "UMTD03-08", "name": "Training", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD03_08.webp", "text": TODO_TEXT},
    "UMTD03-09": {"id": "UMTD03-09", "name": "Destruction", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD03_09.webp", "text": TODO_TEXT},
    "UMTD03-10": {"id": "UMTD03-10", "name": "Mission Complete", "type": "Event", "cost": 1, "power": 0, "image": "/tcg/cards/trainees/UMTD03_10.webp", "text": TODO_TEXT},
    "UMTD04-01": {"id": "UMTD04-01", "name": "Orfevre", "type": "Trainee", "cost": 7, "power": 6000, "image": "/tcg/cards/trainees/UMTD04_01.webp", "text": TODO_TEXT},
    "UMTD04-02": {"id": "UMTD04-02", "name": "Stay Gold", "type": "Trainee", "cost": 6, "power": 4000, "image": "/tcg/cards/trainees/UMTD04_02.webp", "text": TODO_TEXT, "tags": ["Burning Soul"]},
    "UMTD04-03": {"id": "UMTD04-03", "name": "Dream Journey", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMTD04_03.webp", "text": TODO_TEXT},
    "UMTD04-04": {"id": "UMTD04-04", "name": "Fenomeno", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMTD04_04.webp", "text": TODO_TEXT, "tags": ["Block"]},
    "UMTD04-05": {"id": "UMTD04-05", "name": "Gold Ship", "type": "Trainee", "cost": 3, "power": 3000, "image": "/tcg/cards/trainees/UMTD04_05.webp", "text": TODO_TEXT, "tags": ["Burning Soul"]},
    "UMTD04-06": {"id": "UMTD04-06", "name": "Nakayama Festa", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMTD04_06.webp", "text": TODO_TEXT},
    "UMTD04-07": {"id": "UMTD04-07", "name": "Golden Chaos", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD04_07.webp", "text": TODO_TEXT},
    "UMTD04-08": {"id": "UMTD04-08", "name": "Royal Award", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD04_08.webp", "text": TODO_TEXT},
    "UMTD04-09": {"id": "UMTD04-09", "name": "Golden Switch", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD04_09.webp", "text": TODO_TEXT},
    "UMTD04-10": {"id": "UMTD04-10", "name": "Power of Demon King", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD04_10.webp", "text": TODO_TEXT},
    "UMTD05-01": {"id": "UMTD05-01", "name": "Agnes Tachyon", "type": "Trainee", "cost": 6, "power": 6000, "image": "/tcg/cards/trainees/UMTD05_01.webp", "text": TODO_TEXT, "tags": [{"name": "Trick", "value": 2}]},
    "UMTD05-02": {"id": "UMTD05-02", "name": "Sweep Tosho", "type": "Trainee", "cost": 6, "power": 4000, "image": "/tcg/cards/trainees/UMTD05_02.webp", "text": TODO_TEXT, "tags": [{"name": "Trick", "value": 0}]},
    "UMTD05-03": {"id": "UMTD05-03", "name": "Manhattan Cafe", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMTD05_03.webp", "text": TODO_TEXT, "tags": [{"name": "Trick", "value": 1}]},
    "UMTD05-04": {"id": "UMTD05-04", "name": "Air Shakur", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMTD05_04.webp", "text": TODO_TEXT, "tags": [{"name": "Trick", "value": 1}, "Block"]},
    "UMTD05-05": {"id": "UMTD05-05", "name": "Matikanefukukitaru", "type": "Trainee", "cost": 3, "power": 200, "image": "/tcg/cards/trainees/UMTD05_05.webp", "text": TODO_TEXT, "tags": [{"name": "Trick", "value": 1}]},
    "UMTD05-06": {"id": "UMTD05-06", "name": "Uma Radio", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD05_06.webp", "text": TODO_TEXT},
    "UMTD05-07": {"id": "UMTD05-07", "name": "Weapon Spell", "type": "Event", "cost": 1, "power": 0, "image": "/tcg/cards/trainees/UMTD05_07.webp", "text": TODO_TEXT},
    "UMTD05-08": {"id": "UMTD05-08", "name": "Beyond The Light", "type": "Event", "cost": 10, "power": 0, "image": "/tcg/cards/trainees/UMTD05_08.webp", "text": TODO_TEXT},
    "UMTD05-09": {"id": "UMTD05-09", "name": "Call of Silent", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMTD05_09.webp", "text": TODO_TEXT},
    "UMTD05-10": {"id": "UMTD05-10", "name": "Neko Neko Lucky", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMTD05_10.webp", "text": TODO_TEXT, "tags": [{"name": "Trick", "value": 2}]},
   
    "UMBT01-01": {"id": "UMBT01-01", "name": "Sakura Laurel", "type": "Trainee", "cost": 6, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_01.webp", "text": "TODO", "tags": ["Burning Soul"]},
    "UMBT01-02": {"id": "UMBT01-02", "name": "Sakura Bakushin O", "type": "Trainee", "cost": 6, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_02.webp", "text": "TODO", "tags": ["Burning Soul"]},
    "UMBT01-03": {"id": "UMBT01-03", "name": "Sakura Chiyono O", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMBT01_03.webp", "text": "TODO"},
    "UMBT01-04": {"id": "UMBT01-04", "name": "Sakura Chitose O", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMBT01_04.webp", "text": "TODO", "tags": ["Block"]},
    "UMBT01-05": {"id": "UMBT01-05", "name": "Haru Urara", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMBT01_05.webp", "text": "TODO", "tags": ["Burning Soul"]},
    "UMBT01-06": {"id": "UMBT01-06", "name": "The Path to Spring", "type": "Event", "cost": 0, "power": 0, "image": "/tcg/cards/trainees/UMBT01_06.webp", "text": "TODO"},
    "UMBT01-07": {"id": "UMBT01-07", "name": "Fierce Battle Dodgeball", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMBT01_07.webp", "text": "TODO"},
    "UMBT01-08": {"id": "UMBT01-08", "name": "The Waltz of Spring", "type": "Event", "cost": 4, "power": 0, "image": "/tcg/cards/trainees/UMBT01_08.webp", "text": "TODO"},
    "UMBT01-09": {"id": "UMBT01-09", "name": "Almond Eye", "type": "Trainee", "cost": 7, "power": 5000, "image": "/tcg/cards/trainees/UMBT01_09.webp", "text": "TODO", "tags": ["Rush"]},
    "UMBT01-10": {"id": "UMBT01-10", "name": "Still in love", "type": "Trainee", "cost": 6, "power": 6000, "image": "/tcg/cards/trainees/UMBT01_10.webp", "text": "TODO", "tags": ["Rush", "Block"]},
    "UMBT01-11": {"id": "UMBT01-11", "name": "Daring Tact", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_11.webp", "text": "TODO", "tags": ["Rush"]},
    "UMBT01-12": {"id": "UMBT01-12", "name": "Catch my rhythm", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMBT01_12.webp", "text": "TODO"},
    "UMBT01-13": {"id": "UMBT01-13", "name": "Love me Love me Love me", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_13.webp", "text": "TODO"},
    "UMBT01-14": {"id": "UMBT01-14", "name": "Vixena", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_14.webp", "text": "TODO", "tags": ["Block"]},
    "UMBT01-15": {"id": "UMBT01-15", "name": "Cheval Grand", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_15.webp", "text": "TODO"},
    "UMBT01-16": {"id": "UMBT01-16", "name": "Vivlos", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMBT01_16.webp", "text": "TODO"},
    "UMBT01-17": {"id": "UMBT01-17", "name": "Uma Summer Time Yay~", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_17.webp", "text": "TODO"},
    "UMBT01-18": {"id": "UMBT01-18", "name": "Beyond the Horizon, We Meet", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_18.webp", "text": "TODO"},
    "UMBT01-19": {"id": "UMBT01-19", "name": "Admire Vega", "type": "Trainee", "cost": 6, "power": 5000, "image": "/tcg/cards/trainees/UMBT01_19.webp", "text": "TODO", "tags": ["Duel", "Block"]},
    "UMBT01-20": {"id": "UMBT01-20", "name": "Sister", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_20.webp", "text": "TODO", "tags": ["Duel"]},
    "UMBT01-21": {"id": "UMBT01-21", "name": "It is fun to running with those two, Is not it?", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_21.webp", "text": "TODO"},
    "UMBT01-22": {"id": "UMBT01-22", "name": "Togerther, with you", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMBT01_22.webp", "text": "TODO"},
    "UMBT01-23": {"id": "UMBT01-23", "name": "Curren Chan", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_23.webp", "text": "TODO", "tags": [{"name": "Trick", "value": 1}, {"name": "Fan", "value": 3}]},
    "UMBT01-24": {"id": "UMBT01-24", "name": "Smart Falcon", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_24.webp", "text": "TODO", "tags": [{"name": "Trick", "value": 1}, {"name": "Fan", "value": 3}]},
    "UMBT01-25": {"id": "UMBT01-25", "name": "Gold City", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_25.webp", "text": "TODO", "tags": [{"name": "Fan", "value": 2}]},
    "UMBT01-26": {"id": "UMBT01-26", "name": "Grand Live!", "type": "Event", "cost": 1, "power": 0, "image": "/tcg/cards/trainees/UMBT01_26.webp", "text": "TODO", "tags": [{"name": "Trick", "value": 2}]},
    "UMBT01-27": {"id": "UMBT01-27", "name": "Fire dance festival", "type": "Event", "cost": 8, "power": 0, "image": "/tcg/cards/trainees/UMBT01_27.webp", "text": "TODO", "tags": [{"name": "Trick", "value": 0}]},
}


def _add_card_if_missing(card_id: str, name: str, card_type: str, cost: int, power: int, image: str) -> None:
    CARD_DATABASE.setdefault(
        card_id,
        {
            "id": card_id,
            "name": name,
            "type": card_type,
            "cost": cost,
            "power": power,
            "image": image,
            "text": TODO_TEXT,
        },
    )


for deck_number in range(1, 6):
    for card_number in range(1, 11):
        card_id = f"UMTD{deck_number:02d}-{card_number:02d}"
        is_trainee = card_number <= 5
        _add_card_if_missing(
            card_id,
            card_id,
            "Trainee" if is_trainee else "Event",
            min(card_number, 8),
            3000 if is_trainee else 0,
            f"/tcg/cards/trainees/UMTD{deck_number:02d}_{card_number:02d}.webp",
        )

for trainer_number in range(1, 7):
    trainer_id = f"UMT-{trainer_number:03d}"
    _add_card_if_missing(
        trainer_id,
        f"Trainer {trainer_number:03d}",
        "Trainer",
        5,
        5000,
        f"/tcg/cards/trainers/UMT_{trainer_number:03d}.webp",
    )

_add_card_if_missing(
    "UMC-01",
    "Carrot",
    "Carrot",
    0,
    0,
    "/tcg/cards/carrots/UMC_01.webp",
)


def hydrate_card_tags(card: dict) -> dict:
    hydrated_card = dict(card)
    raw_tags = card.get("tags") or []
    hydrated_tags = []

    for tag in raw_tags:
        if isinstance(tag, str):
            name = tag
            value = None
        elif isinstance(tag, dict):
            name = tag.get("name")
            value = tag.get("value")
        else:
            continue

        if not name:
            continue

        label = f"{name} {value}" if value is not None else name
        description = KEYWORD_TAGS.get(name, "")
        if value is not None:
            description = description.replace("{value}", str(value))

        hydrated_tags.append(
            {
                "name": name,
                "value": value,
                "label": label,
                "description": description,
            }
        )

    hydrated_card["tags"] = hydrated_tags
    return hydrated_card

CARD_DATABASE_BY_TYPE = {
    card_type: {
        card_id: card
        for card_id, card in CARD_DATABASE.items()
        if card["type"] == card_type
    }
    for card_type in {"Trainee", "Event", "Carrot", "Trainer"}
}


def get_card(card_id: str) -> dict:
    try:
        return CARD_DATABASE[card_id]
    except KeyError as exc:
        raise ValueError(f"Unknown card id: {card_id}") from exc


def get_cards_by_type(card_type: str) -> dict:
    return {
        card_id: hydrate_card_tags(card)
        for card_id, card in CARD_DATABASE_BY_TYPE.get(card_type, {}).items()
    }
