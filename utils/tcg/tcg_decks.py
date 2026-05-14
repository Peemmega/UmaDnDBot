import random
from copy import deepcopy

from .tcg_cards import CARD_DATABASE, get_card


MAX_COPIES_PER_CARD = 4
MAIN_DECK_SIZE = 40

STYLES = ["Speed", "Stamina", "Power", "Guts", "Wit"]
STYLE_TAGS = {
    "Speed": ["Starter", "Tempo", "Low cost"],
    "Stamina": ["Starter", "Steady", "Board tests"],
    "Power": ["Starter", "High power", "Field tests"],
    "Guts": ["Starter", "Rest state", "Pressure"],
    "Wit": ["Starter", "Utility", "Control tests"],
}


PREDEFINED_DECKS = [
    {
        "id": "starter-speed",
        "name": "Starter Speed Deck",
        "description": "Basic 40-card starter deck using UMTD01 trainee cards.",
        "style": "Speed",
        "highlight": "Simple trainee spread for online board testing.",
        "tags": STYLE_TAGS["Speed"],
        "trainer": "UMT-001",
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
            "UMTD01-10": 4,
        },
    },
    {
        "id": "starter-basic",
        "name": "Starter Basic Deck",
        "description": "Basic 40-card starter deck using UMBT01 trainee cards.",
        "style": "Stamina",
        "highlight": "Uses the newer UMBT01 image set for card database checks.",
        "tags": STYLE_TAGS["Stamina"],
        "trainer": "UMT-002",
        "mainDeck": {
            "UMBT01-01": 4,
            "UMBT01-02": 4,
            "UMBT01-03": 4,
            "UMBT01-04": 4,
            "UMBT01-05": 4,
            "UMBT01-06": 4,
            "UMBT01-07": 4,
            "UMBT01-08": 4,
            "UMBT01-09": 4,
            "UMBT01-10": 4,
        },
    },
]


def expand_deck_list(main_deck: dict[str, int]) -> list[dict]:
    cards = []
    for card_id, quantity in main_deck.items():
        card = get_card(card_id)
        cards.extend(deepcopy(card) for _ in range(quantity))
    return cards


def validate_deck(deck: dict) -> list[str]:
    errors = []
    main_deck = deck.get("mainDeck") or {}
    total_cards = sum(main_deck.values())
    if total_cards != MAIN_DECK_SIZE:
        errors.append(f"Main Deck must contain {MAIN_DECK_SIZE} cards, got {total_cards}")

    for card_id, quantity in main_deck.items():
        if card_id not in CARD_DATABASE:
            errors.append(f"Unknown card id in Main Deck: {card_id}")
            continue
        if quantity < 1:
            errors.append(f"{card_id} quantity must be at least 1")
        if quantity > MAX_COPIES_PER_CARD:
            errors.append(f"{card_id} exceeds {MAX_COPIES_PER_CARD} copies")
        if CARD_DATABASE[card_id]["type"] == "Trainer":
            errors.append(f"Trainer card cannot be in Main Deck: {card_id}")

    trainer_id = deck.get("trainer")
    trainer = CARD_DATABASE.get(trainer_id)
    if not trainer:
        errors.append(f"Unknown trainer id: {trainer_id}")
    elif trainer["type"] != "Trainer":
        errors.append(f"Trainer slot must be a Trainer card: {trainer_id}")

    return errors


def get_deck_validation(deck: dict) -> dict:
    errors = validate_deck(deck)
    return {"valid": not errors, "errors": errors}


def hydrate_deck(deck: dict) -> dict:
    main_deck = deck["mainDeck"]
    cards = expand_deck_list(main_deck)
    key_cards = [CARD_DATABASE[card_id]["name"] for card_id in list(main_deck)[:3]]
    validation = get_deck_validation(deck)
    return {
        **deck,
        "mainDeckCount": sum(main_deck.values()),
        "trainerCard": CARD_DATABASE.get(deck["trainer"]),
        "cards": cards,
        "keyCards": key_cards,
        "validation": validation,
    }


PREDEFINED_DECKS = [hydrate_deck(deck) for deck in PREDEFINED_DECKS]
DECKS_BY_ID = {deck["id"]: deck for deck in PREDEFINED_DECKS}

for deck in PREDEFINED_DECKS:
    validation = deck["validation"]
    if not validation["valid"]:
        raise ValueError(f"Invalid predefined deck {deck['id']}: {validation['errors']}")


def create_deck_instance(deck_id: str, player_slot: str) -> list[dict]:
    deck = DECKS_BY_ID[deck_id]
    cards = []
    for index, card in enumerate(expand_deck_list(deck["mainDeck"])):
        instance = deepcopy(card)
        instance["instanceId"] = f"{player_slot}-{deck_id}-{index + 1}"
        instance["status"] = "active"
        cards.append(instance)
    random.shuffle(cards)
    return cards


def create_trainer_card(player_slot: str, deck_id: str) -> dict:
    deck = DECKS_BY_ID[deck_id]
    trainer = deepcopy(get_card(deck["trainer"]))
    trainer["instanceId"] = f"{player_slot}-{deck_id}-trainer"
    trainer["status"] = "active"
    trainer["fieldX"] = 18
    trainer["fieldY"] = 18
    return trainer


def create_carrot_card(player_slot: str, index: int) -> dict:
    carrot = deepcopy(get_card("UMC-01"))
    carrot["instanceId"] = f"{player_slot}-carrot-{index}"
    carrot["status"] = "active"
    return carrot
