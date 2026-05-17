import random
from copy import deepcopy

CARD_DATABASE = {
  "UMC-01": {
    "id": "UMC-01",
    "name": "Carrot",
    "type": "Carrot",
    "cost": 0,
    "power": 0,
    "image": "/tcg/cards/carrots/UMC_01.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMT-001": {
    "id": "UMT-001",
    "name": "Trainer Spica",
    "type": "Trainer",
    "cost": 5,
    "power": 5000,
    "image": "/tcg/cards/trainers/UMT_001.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMT-002": {
    "id": "UMT-002",
    "name": "Trainer Kitahara",
    "type": "Trainer",
    "cost": 5,
    "power": 5000,
    "image": "/tcg/cards/trainers/UMT_002.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMT-003": {
    "id": "UMT-003",
    "name": "Trainer Riko",
    "type": "Trainer",
    "cost": 5,
    "power": 5000,
    "image": "/tcg/cards/trainers/UMT_003.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMT-004": {
    "id": "UMT-004",
    "name": "Trainer Muteki",
    "type": "Trainer",
    "cost": 5,
    "power": 5000,
    "image": "/tcg/cards/trainers/UMT_004.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMT-005": {
    "id": "UMT-005",
    "name": "Trainer Kuronuma",
    "type": "Trainer",
    "cost": 5,
    "power": 5000,
    "image": "/tcg/cards/trainers/UMT_005.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-01": {
    "id": "UMTD01-01",
    "name": "Oguri Cap",
    "type": "Trainee",
    "cost": 6,
    "power": 5000,
    "image": "/tcg/cards/trainees/UMTD01_01.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-02": {
    "id": "UMTD01-02",
    "name": "Tamamo Cross",
    "type": "Trainee",
    "cost": 5,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD01_02.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-03": {
    "id": "UMTD01-03",
    "name": "Fujimasa March",
    "type": "Trainee",
    "cost": 3,
    "power": 2000,
    "image": "/tcg/cards/trainees/UMTD01_03.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-04": {
    "id": "UMTD01-04",
    "name": "Belno Light",
    "type": "Trainee",
    "cost": 3,
    "power": 2000,
    "image": "/tcg/cards/trainees/UMTD01_04.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-05": {
    "id": "UMTD01-05",
    "name": "Super Creek",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD01_05.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-06": {
    "id": "UMTD01-06",
    "name": "Dicta Striker",
    "type": "Trainee",
    "cost": 4,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD01_06.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-07": {
    "id": "UMTD01-07",
    "name": "Party Time",
    "type": "Event",
    "cost": 0,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD01_07.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-08": {
    "id": "UMTD01-08",
    "name": "Special Meal",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD01_08.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-09": {
    "id": "UMTD01-09",
    "name": "Training",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD01_09.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD01-10": {
    "id": "UMTD01-10",
    "name": "Grey Monster",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD01_10.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-01": {
    "id": "UMTD02-01",
    "name": "T.M. Opera O",
    "type": "Trainee",
    "cost": 7,
    "power": 6000,
    "image": "/tcg/cards/trainees/UMTD02_01.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-02": {
    "id": "UMTD02-02",
    "name": "Biwa Hayahide",
    "type": "Trainee",
    "cost": 6,
    "power": 5000,
    "image": "/tcg/cards/trainees/UMTD02_02.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-03": {
    "id": "UMTD02-03",
    "name": "Meisho Doto",
    "type": "Trainee",
    "cost": 3,
    "power": 2000,
    "image": "/tcg/cards/trainees/UMTD02_03.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-04": {
    "id": "UMTD02-04",
    "name": "Rice Shower",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD02_04.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-05": {
    "id": "UMTD02-05",
    "name": "Mejiro McQueen",
    "type": "Trainee",
    "cost": 5,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD02_05.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-06": {
    "id": "UMTD02-06",
    "name": "Tokai Teio",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD02_06.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-07": {
    "id": "UMTD02-07",
    "name": "Uma Engine",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD02_07.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-08": {
    "id": "UMTD02-08",
    "name": "Training",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD02_08.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-09": {
    "id": "UMTD02-09",
    "name": "Centurial Overlord",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD02_09.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD02-10": {
    "id": "UMTD02-10",
    "name": "Hard Training",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD02_10.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-01": {
    "id": "UMTD03-01",
    "name": "Gentildonna",
    "type": "Trainee",
    "cost": 8,
    "power": 7000,
    "image": "/tcg/cards/trainees/UMTD03_01.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-02": {
    "id": "UMTD03-02",
    "name": "Yaeno Muteki",
    "type": "Trainee",
    "cost": 6,
    "power": 5000,
    "image": "/tcg/cards/trainees/UMTD03_02.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-03": {
    "id": "UMTD03-03",
    "name": "Tanino Gimlet",
    "type": "Trainee",
    "cost": 3,
    "power": 1000,
    "image": "/tcg/cards/trainees/UMTD03_03.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-04": {
    "id": "UMTD03-04",
    "name": "Symboli Kris S",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD03_04.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-05": {
    "id": "UMTD03-05",
    "name": "Narita Brian",
    "type": "Trainee",
    "cost": 5,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD03_05.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-06": {
    "id": "UMTD03-06",
    "name": "Mejiro Ryan",
    "type": "Trainee",
    "cost": 4,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD03_06.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-07": {
    "id": "UMTD03-07",
    "name": "Warrior Spirit",
    "type": "Event",
    "cost": 4,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD03_07.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-08": {
    "id": "UMTD03-08",
    "name": "Training",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD03_08.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-09": {
    "id": "UMTD03-09",
    "name": "Destruction",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD03_09.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD03-10": {
    "id": "UMTD03-10",
    "name": "Mission Complete",
    "type": "Event",
    "cost": 1,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD03_10.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-01": {
    "id": "UMTD04-01",
    "name": "Orfevre",
    "type": "Trainee",
    "cost": 6,
    "power": 5000,
    "image": "/tcg/cards/trainees/UMTD04_01.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-02": {
    "id": "UMTD04-02",
    "name": "Stay Gold",
    "type": "Trainee",
    "cost": 6,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD04_02.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-03": {
    "id": "UMTD04-03",
    "name": "Dream Journey",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD04_03.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-04": {
    "id": "UMTD04-04",
    "name": "Fenomeno",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD04_04.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-05": {
    "id": "UMTD04-05",
    "name": "Gold Ship",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD04_05.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-06": {
    "id": "UMTD04-06",
    "name": "Nakayama Festa",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD04_06.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-07": {
    "id": "UMTD04-07",
    "name": "Golden Chaos",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD04_07.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-08": {
    "id": "UMTD04-08",
    "name": "Royal Award",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD04_08.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-09": {
    "id": "UMTD04-09",
    "name": "Confused",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD04_09.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD04-10": {
    "id": "UMTD04-10",
    "name": "Power of Demon King",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD04_10.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-01": {
    "id": "UMTD05-01",
    "name": "Agnes Tachyon",
    "type": "Trainee",
    "cost": 6,
    "power": 5000,
    "image": "/tcg/cards/trainees/UMTD05_01.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-02": {
    "id": "UMTD05-02",
    "name": "Sweep Tosho",
    "type": "Trainee",
    "cost": 6,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD05_02.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-03": {
    "id": "UMTD05-03",
    "name": "Manhattan Cafe",
    "type": "Trainee",
    "cost": 5,
    "power": 4000,
    "image": "/tcg/cards/trainees/UMTD05_03.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-04": {
    "id": "UMTD05-04",
    "name": "Air Shakur",
    "type": "Trainee",
    "cost": 4,
    "power": 3000,
    "image": "/tcg/cards/trainees/UMTD05_04.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-05": {
    "id": "UMTD05-05",
    "name": "Matikanefukukitaru",
    "type": "Trainee",
    "cost": 3,
    "power": 2000,
    "image": "/tcg/cards/trainees/UMTD05_05.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-06": {
    "id": "UMTD05-06",
    "name": "Uma Radio",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD05_06.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-07": {
    "id": "UMTD05-07",
    "name": "Weapon Spell",
    "type": "Event",
    "cost": 1,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD05_07.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-08": {
    "id": "UMTD05-08",
    "name": "Beyond The Light",
    "type": "Event",
    "cost": 7,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD05_08.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-09": {
    "id": "UMTD05-09",
    "name": "Call of Silent",
    "type": "Event",
    "cost": 3,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD05_09.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  },
  "UMTD05-10": {
    "id": "UMTD05-10",
    "name": "Neko Neko Lucky",
    "type": "Event",
    "cost": 2,
    "power": 0,
    "image": "/tcg/cards/trainees/UMTD05_10.webp",
    "text": "TODO: ใส่ความสามารถจากการ์ดจริงภายหลัง"
  }
}

CARD_DATABASE.update({
  "UMBT01-01": {"id": "UMBT01-01", "name": "Sakura Laurel", "type": "Trainee", "cost": 6, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_01.webp", "text": "TODO"},
  "UMBT01-02": {"id": "UMBT01-02", "name": "Sakura Bakushin O", "type": "Trainee", "cost": 6, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_02.webp", "text": "TODO"},
  "UMBT01-03": {"id": "UMBT01-03", "name": "Sakura Chiyono O", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMBT01_03.webp", "text": "TODO"},
  "UMBT01-04": {"id": "UMBT01-04", "name": "Sakura Chitose O", "type": "Trainee", "cost": 4, "power": 3000, "image": "/tcg/cards/trainees/UMBT01_04.webp", "text": "TODO"},
  "UMBT01-05": {"id": "UMBT01-05", "name": "Haru Urara", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMBT01_05.webp", "text": "TODO"},
  "UMBT01-06": {"id": "UMBT01-06", "name": "The Path to Spring", "type": "Event", "cost": 0, "power": 0, "image": "/tcg/cards/trainees/UMBT01_06.webp", "text": "TODO"},
  "UMBT01-07": {"id": "UMBT01-07", "name": "Fierce Battle Dodgeball", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMBT01_07.webp", "text": "TODO"},
  "UMBT01-08": {"id": "UMBT01-08", "name": "The Waltz of Spring", "type": "Event", "cost": 4, "power": 0, "image": "/tcg/cards/trainees/UMBT01_08.webp", "text": "TODO"},
  "UMBT01-09": {"id": "UMBT01-09", "name": "Almond Eye", "type": "Trainee", "cost": 7, "power": 5000, "image": "/tcg/cards/trainees/UMBT01_09.webp", "text": "TODO"},
  "UMBT01-10": {"id": "UMBT01-10", "name": "Still in love", "type": "Trainee", "cost": 6, "power": 6000, "image": "/tcg/cards/trainees/UMBT01_10.webp", "text": "TODO"},
  "UMBT01-11": {"id": "UMBT01-11", "name": "Daring Tact", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_11.webp", "text": "TODO"},
  "UMBT01-12": {"id": "UMBT01-12", "name": "Catch my rhythm", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMBT01_12.webp", "text": "TODO"},
  "UMBT01-13": {"id": "UMBT01-13", "name": "Love me Love me Love me", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_13.webp", "text": "TODO"},
  "UMBT01-14": {"id": "UMBT01-14", "name": "Vixena", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_14.webp", "text": "TODO"},
  "UMBT01-15": {"id": "UMBT01-15", "name": "Cheval Grand", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_15.webp", "text": "TODO"},
  "UMBT01-16": {"id": "UMBT01-16", "name": "Vivlos", "type": "Trainee", "cost": 3, "power": 2000, "image": "/tcg/cards/trainees/UMBT01_16.webp", "text": "TODO"},
  "UMBT01-17": {"id": "UMBT01-17", "name": "Uma Summer Time Yay~", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_17.webp", "text": "TODO"},
  "UMBT01-18": {"id": "UMBT01-18", "name": "Beyond the Horizon, We Meet", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_18.webp", "text": "TODO"},
  "UMBT01-19": {"id": "UMBT01-19", "name": "Admire Vega", "type": "Trainee", "cost": 6, "power": 5000, "image": "/tcg/cards/trainees/UMBT01_19.webp", "text": "TODO"},
  "UMBT01-20": {"id": "UMBT01-20", "name": "Sister", "type": "Trainee", "cost": 4, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_20.webp", "text": "TODO"},
  "UMBT01-21": {"id": "UMBT01-21", "name": "It is fun to running with those two, Is not it?", "type": "Event", "cost": 3, "power": 0, "image": "/tcg/cards/trainees/UMBT01_21.webp", "text": "TODO"},
  "UMBT01-22": {"id": "UMBT01-22", "name": "Togerther, with you", "type": "Event", "cost": 2, "power": 0, "image": "/tcg/cards/trainees/UMBT01_22.webp", "text": "TODO"},
  "UMBT01-23": {"id": "UMBT01-23", "name": "Curren Chan", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_23.webp", "text": "TODO"},
  "UMBT01-24": {"id": "UMBT01-24", "name": "Smart Falcon", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_24.webp", "text": "TODO"},
  "UMBT01-25": {"id": "UMBT01-25", "name": "Gold City", "type": "Trainee", "cost": 5, "power": 4000, "image": "/tcg/cards/trainees/UMBT01_25.webp", "text": "TODO"},
  "UMBT01-26": {"id": "UMBT01-26", "name": "Grand Live!", "type": "Event", "cost": 1, "power": 0, "image": "/tcg/cards/trainees/UMBT01_26.webp", "text": "TODO"},
  "UMBT01-27": {"id": "UMBT01-27", "name": "Fire dance festival", "type": "Event", "cost": 8, "power": 0, "image": "/tcg/cards/trainees/UMBT01_27.webp", "text": "TODO"},
  "UMT-006": {"id": "UMT-006", "name": "Trainer Tsubaki", "type": "Trainer", "cost": 5, "power": 5000, "image": "/tcg/cards/trainers/UMT_006.webp", "text": "TODO"},
})


def get_card(card_id: str) -> dict | None:
    return CARD_DATABASE.get(card_id)


MAX_COPIES_PER_CARD = 4
MAIN_DECK_SIZE = 40


def expand_deck_list(main_deck: dict) -> list[dict]:
    cards = []
    for card_id, quantity in (main_deck or {}).items():
        card = get_card(card_id)
        if not card:
            continue
        cards.extend(deepcopy(card) for _ in range(quantity))
    return cards


def validate_deck(deck: dict) -> dict:
    errors = []
    main_deck = deck.get('mainDeck') or {}
    total = sum(main_deck.values())

    if total != MAIN_DECK_SIZE:
        errors.append(f'Main Deck must contain {MAIN_DECK_SIZE} cards, got {total}')

    for card_id, quantity in main_deck.items():
        card = CARD_DATABASE.get(card_id)
        if not card:
            errors.append(f'Unknown card id in Main Deck: {card_id}')
            continue
        if quantity < 1:
            errors.append(f'{card_id} quantity must be at least 1')
        if quantity > MAX_COPIES_PER_CARD:
            errors.append(f'{card_id} exceeds {MAX_COPIES_PER_CARD} copies')
        if card.get('type') == 'Trainer':
            errors.append(f'Trainer card cannot be in Main Deck: {card_id}')

    trainer_id = deck.get('trainer')
    trainer = CARD_DATABASE.get(trainer_id)
    if not trainer:
        errors.append(f'Unknown trainer id: {trainer_id}')
    elif trainer.get('type') != 'Trainer':
        errors.append(f'Trainer slot must be a Trainer card: {trainer_id}')

    return {'valid': not errors, 'errors': errors}


def build_deck(deck: dict) -> dict:
    cards = expand_deck_list(deck.get('mainDeck') or {})
    trainer_card = get_card(deck.get('trainer'))
    main_deck_keys = list((deck.get('mainDeck') or {}).keys())
    key_cards = []
    for card_id in main_deck_keys[:3]:
        card = get_card(card_id)
        if card:
            key_cards.append(card['name'])
    return {
        **deck,
        'cards': cards,
        'mainDeckCount': len(cards),
        'trainerCard': trainer_card,
        'keyCards': key_cards,
        'validation': validate_deck(deck),
    }


STARTER_DECKS = [
  {
    "id": "starter-speed",
    "name": "Starter Speed Deck",
    "description": "Basic 40-card starter deck built for early tempo tests.",
    "style": "Speed",
    "highlight": "Fast open and simple board transitions.",
    "tags": [
      "Starter",
      "Tempo",
      "Low cost"
    ],
    "trainer": "UMT-002",
    "mainDeck": {
      "UMTD01-01": 4,
      "UMTD01-02": 4,
      "UMTD01-03": 4,
      "UMTD01-04": 4,
      "UMTD01-05": 4,
      "UMTD01-06": 4,
      "UMTD01-07": 4,
      "UMTD01-08": 4,
      "UMTD01-09": 4,
      "UMTD01-10": 4
    }
  },
  {
    "id": "starter-stamina",
    "name": "Starter Stamina Deck",
    "description": "Basic 40-card starter deck built for slower setup tests.",
    "style": "Stamina",
    "highlight": "Life zone and longer game flow checks.",
    "tags": [
      "Starter",
      "Steady",
      "Board tests"
    ],
    "trainer": "UMT-003",
    "mainDeck": {
      "UMTD02-01": 4,
      "UMTD02-02": 4,
      "UMTD02-03": 4,
      "UMTD02-04": 4,
      "UMTD02-05": 4,
      "UMTD02-06": 4,
      "UMTD02-07": 4,
      "UMTD02-08": 4,
      "UMTD02-09": 4,
      "UMTD02-10": 4
    }
  },
  {
    "id": "starter-power",
    "name": "Starter Power Deck",
    "description": "Basic 40-card starter deck built for field pressure tests.",
    "style": "Power",
    "highlight": "High power trainees and layout checks.",
    "tags": [
      "Starter",
      "Power",
      "Board push"
    ],
    "trainer": "UMT-004",
    "mainDeck": {
      "UMTD03-01": 4,
      "UMTD03-02": 4,
      "UMTD03-03": 4,
      "UMTD03-04": 4,
      "UMTD03-05": 4,
      "UMTD03-06": 4,
      "UMTD03-07": 4,
      "UMTD03-08": 4,
      "UMTD03-09": 4,
      "UMTD03-10": 4
    }
  },
  {
    "id": "starter-gut",
    "name": "Starter Gut Deck",
    "description": "Basic 40-card starter deck built for tap/rest tests.",
    "style": "Guts",
    "highlight": "Repeated tap and move interactions.",
    "tags": [
      "Starter",
      "Rest synergy",
      "Pressure"
    ],
    "trainer": "UMT-005",
    "mainDeck": {
      "UMTD04-01": 4,
      "UMTD04-02": 4,
      "UMTD04-03": 4,
      "UMTD04-04": 4,
      "UMTD04-05": 4,
      "UMTD04-06": 4,
      "UMTD04-07": 4,
      "UMTD04-08": 4,
      "UMTD04-09": 4,
      "UMTD04-10": 4
    }
  },
  {
    "id": "starter-wit",
    "name": "Starter Wit Deck",
    "description": "Basic 40-card starter deck built for draw and control tests.",
    "style": "Wit",
    "highlight": "Tricks, draw flow, and future keyword hooks.",
    "tags": [
      "Starter",
      "Draw",
      "Control"
    ],
    "trainer": "UMT-001",
    "mainDeck": {
      "UMTD05-01": 4,
      "UMTD05-02": 4,
      "UMTD05-03": 4,
      "UMTD05-04": 4,
      "UMTD05-05": 4,
      "UMTD05-06": 4,
      "UMTD05-07": 4,
      "UMTD05-08": 4,
      "UMTD05-09": 4,
      "UMTD05-10": 4
    }
  },
  {
    "id": "sakura-deck",
    "name": "Sakura Laurel",
    "description": "Basic 40-card starter deck built for draw and control tests.",
    "style": "Wit",
    "highlight": "Tricks, draw flow, and future keyword hooks.",
    "tags": [
      "Starter",
      "Draw",
      "Control"
    ],
    "trainer": "UMT-006",
    "mainDeck": {
      "UMTD05-01": 4,
      "UMTD05-02": 4,
      "UMTD05-03": 4,
      "UMTD05-04": 4,
      "UMTD05-05": 4,
      "UMTD05-06": 4,
      "UMTD05-07": 4,
      "UMTD05-08": 4,
      "UMTD05-09": 4,
      "UMTD05-10": 4
    }
  },
]

CUSTOM_DECKS = [
  {
    "id": "sakura-laurel",
    "name": "Sakura Laurel Deck",
    "description": "Sakura lineup built around Laurel and UMTD04 support.",
    "style": "Speed",
    "highlight": "Sakura Laurel leads the tempo package.",
    "tags": ["Custom", "Sakura", "Tempo"],
    "trainer": "UMT-006",
    "mainDeck": {
      "UMBT01-01": 4,
      "UMBT01-03": 4,
      "UMBT01-02": 2,
      "UMTD04-02": 4,
      "UMTD04-05": 4,
      "UMBT01-04": 4,
      "UMBT01-06": 3,
      "UMTD04-08": 4,
      "UMTD04-07": 4,
      "UMBT01-08": 4,
      "UMTD04-10": 3,
    },
  },
  {
    "id": "v-family",
    "name": "V Family Deck",
    "description": "V family core backed by Opera O and Meisho Doto.",
    "style": "Stamina",
    "highlight": "Vixena, Cheval Grand, and Vivlos anchor the deck.",
    "tags": ["Custom", "V Family", "Stamina"],
    "trainer": "UMT-003",
    "mainDeck": {
      "UMBT01-14": 4,
      "UMBT01-15": 4,
      "UMBT01-16": 4,
      "UMBT01-17": 4,
      "UMBT01-18": 4,
      "UMTD02-01": 4,
      "UMTD02-03": 4,
      "UMTD02-07": 2,
      "UMTD02-08": 4,
      "UMTD02-09": 2,
      "UMTD02-10": 4,
    },
  },
  {
    "id": "tiara",
    "name": "Tiara Deck",
    "description": "Almond Eye package mixed with the UMTD01 Tiara suite.",
    "style": "Speed",
    "highlight": "Almond Eye and Oguri Cap share the top end.",
    "tags": ["Custom", "Tiara", "Hybrid"],
    "trainer": "UMT-002",
    "mainDeck": {
      "UMBT01-09": 4,
      "UMTD01-02": 2,
      "UMBT01-11": 4,
      "UMTD01-03": 4,
      "UMTD01-04": 4,
      "UMTD01-01": 2,
      "UMTD01-05": 2,
      "UMBT01-12": 2,
      "UMTD01-08": 2,
      "UMBT01-13": 2,
      "UMTD01-07": 4,
      "UMTD01-09": 4,
      "UMTD01-10": 4,
    },
  },
  {
    "id": "admire-vega",
    "name": "Admire Vega Deck",
    "description": "Admire Vega booster cards with UMTD03 power support.",
    "style": "Power",
    "highlight": "Admire Vega drives a compact 40-card pressure plan.",
    "tags": ["Custom", "Admire Vega", "Power"],
    "trainer": "UMT-004",
    "mainDeck": {
      "UMBT01-19": 4,
      "UMTD03-02": 4,
      "UMBT01-20": 4,
      "UMBT01-21": 4,
      "UMBT01-22": 4,
      "UMTD03-04": 4,
      "UMTD03-05": 4,
      "UMTD03-08": 4,
      "UMTD03-09": 4,
      "UMTD03-10": 4,
    },
  },
  {
    "id": "still-in-love",
    "name": "Still in love Deck",
    "description": "Still in love list with Daring Tact and UMTD01 events.",
    "style": "Guts",
    "highlight": "Still in love leads a lean event-heavy shell.",
    "tags": ["Custom", "Still in love", "Events"],
    "trainer": "UMT-002",
    "mainDeck": {
      "UMBT01-10": 4,
      "UMTD01-02": 2,
      "UMBT01-11": 4,
      "UMTD01-03": 4,
      "UMTD01-04": 4,
      "UMBT01-12": 3,
      "UMTD01-08": 4,
      "UMBT01-13": 3,
      "UMTD01-07": 4,
      "UMTD01-09": 4,
      "UMTD01-10": 4,
    },
  },
]

PREDEFINED_DECKS = [build_deck(deck) for deck in [*STARTER_DECKS, *CUSTOM_DECKS]]
DECKS_BY_ID = {deck['id']: deck for deck in PREDEFINED_DECKS}


def create_deck_instance(deck_id: str, player_slot: str) -> list[dict]:
    deck = DECKS_BY_ID[deck_id]
    cards = []
    for index, card in enumerate(deck['cards']):
        instance = deepcopy(card)
        instance['instanceId'] = f"{player_slot}-{card['id']}-{index + 1}"
        instance['status'] = 'active'
        cards.append(instance)
    random.shuffle(cards)
    return cards


def create_trainer_card(player_slot: str, trainer_id: str = 'UMT-001') -> dict:
    trainer = deepcopy(get_card(trainer_id) or get_card('UMT-001'))
    trainer['instanceId'] = f'{player_slot}-trainer-card'
    trainer['status'] = 'active'
    trainer['fieldX'] = 18
    trainer['fieldY'] = 18
    return trainer


def create_carrot_card(player_slot: str, index: int) -> dict:
    carrot = deepcopy(get_card('UMC-01'))
    carrot['instanceId'] = f'{player_slot}-carrot-{index}'
    carrot['status'] = 'active'
    return carrot
