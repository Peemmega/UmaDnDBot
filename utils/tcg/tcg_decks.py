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
PREDEFINED_DECKS = [build_deck(deck) for deck in STARTER_DECKS]
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
