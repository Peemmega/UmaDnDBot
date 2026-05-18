import random
from copy import deepcopy

from .tcg_cards import CARD_DATABASE, hydrate_card_tags

def get_card(card_id: str) -> dict | None:
    card = CARD_DATABASE.get(card_id)
    return hydrate_card_tags(card) if card else None


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

    return {'valid': not errors, 'errors': errors}


def build_deck(deck: dict) -> dict:
    cards = expand_deck_list(deck.get('mainDeck') or {})
    main_deck_keys = list((deck.get('mainDeck') or {}).keys())
    cover_card = get_card(main_deck_keys[0]) if main_deck_keys else None
    key_cards = []
    for card_id in main_deck_keys[:3]:
        card = get_card(card_id)
        if card:
            key_cards.append(card['name'])
    return {
        **deck,
        'cards': cards,
        'mainDeckCount': len(cards),
        'coverCard': cover_card,
        'coverImage': cover_card.get('image') if cover_card else '',
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
