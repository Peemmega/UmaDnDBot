import random
from copy import deepcopy


STYLES = ["Speed", "Stamina", "Power", "Guts", "Wit"]
STYLE_TAGS = {
    "Speed": ["Fast open", "Tempo", "Low cost"],
    "Stamina": ["Defense", "Life pressure", "Late game"],
    "Power": ["High power", "Breakthrough", "Board push"],
    "Guts": ["Rest synergy", "Comeback", "Pressure"],
    "Wit": ["Draw", "Tricks", "Control"],
}
CARD_NAMES = {
    "Speed": ["Silent Sprint", "Corner Dash", "Front Runner", "Blue Gear"],
    "Stamina": ["Long Climb", "Deep Breath", "Iron Pace", "Green Endurance"],
    "Power": ["Final Push", "Heavy Drive", "Gold Stride", "Hill Breaker"],
    "Guts": ["Last Spurt", "Fighting Pose", "Pink Resolve", "Never Fold"],
    "Wit": ["Race Read", "Clean Line", "Violet Plan", "Smart Timing"],
}
TYPES = ["Trainee", "Trainer", "Event"]


def card_image(style: str, index: int) -> str:
    style_index = STYLES.index(style) + 1
    return f"/assets/tcg/cards/trainees/UMTD{style_index:02d}_{(index % 10) + 1:02d}.webp"


def make_card(style: str, index: int) -> dict:
    card_type = TYPES[index % len(TYPES)]
    cost = (index % 4) + 1
    return {
        "id": f"{style.lower()}-{index + 1}",
        "name": CARD_NAMES[style][index % len(CARD_NAMES[style])],
        "type": card_type,
        "cost": cost,
        "power": 2000 + cost * 1000 + (index % 3) * 500 if card_type == "Trainee" else 0,
        "style": style,
        "image": card_image(style, index),
        "text": f"{style} {card_type} for online playtest sandbox.",
    }


def build_deck(style: str, description: str, highlight: str) -> dict:
    cards = [make_card(style, index) for index in range(20)]
    return {
        "id": f"{style.lower()}-deck",
        "name": f"{style} Deck",
        "description": description,
        "style": style,
        "highlight": highlight,
        "tags": STYLE_TAGS[style],
        "keyCards": [card["name"] for card in cards[:3]],
        "cards": cards,
    }


PREDEFINED_DECKS = [
    build_deck("Speed", "Low-cost tempo deck for quick online tests.", "Early cards and pressure."),
    build_deck("Stamina", "Defensive deck with slower setup turns.", "Long game and Life Zone tests."),
    build_deck("Power", "Board-focused deck with higher power mock trainees.", "Field layout and rested cards."),
    build_deck("Guts", "Comeback deck around active/rest sandbox states.", "Repeated tap and movement tests."),
    build_deck("Wit", "Utility deck for future rule hooks.", "Draw, keyword, and control tests."),
]
DECKS_BY_ID = {deck["id"]: deck for deck in PREDEFINED_DECKS}


def create_deck_instance(deck_id: str, player_slot: str) -> list[dict]:
    deck = DECKS_BY_ID[deck_id]
    cards = []
    for index, card in enumerate(deck["cards"]):
        instance = deepcopy(card)
        instance["instanceId"] = f"{player_slot}-{deck_id}-{index + 1}"
        instance["status"] = "active"
        cards.append(instance)
    random.shuffle(cards)
    return cards


def create_trainer_card(player_slot: str) -> dict:
    return {
        "id": f"trainer-{player_slot}",
        "instanceId": f"{player_slot}-trainer-card",
        "name": "Trainer",
        "type": "Trainer",
        "cost": 0,
        "power": 0,
        "style": "Wit",
        "status": "active",
        "image": "/assets/tcg/cards/trainers/UMT_001.webp",
        "text": "Starting trainer card for online sandbox.",
        "fieldX": 18,
        "fieldY": 18,
    }


def create_carrot_card(player_slot: str, index: int) -> dict:
    return {
        "id": "carrot-token",
        "instanceId": f"{player_slot}-carrot-{index}",
        "name": "Carrot",
        "type": "Carrot",
        "cost": 0,
        "power": 0,
        "style": "Stamina",
        "status": "active",
        "image": "/assets/tcg/cards/carrots/UMC_01.webp",
        "text": "Resource card for future carrot costs.",
    }
