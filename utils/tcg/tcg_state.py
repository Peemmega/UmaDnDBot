import random

from .tcg_decks import create_carrot_card, create_deck_instance, create_trainer_card


ZONES = ["deck", "hand", "field", "life", "discard", "carrot", "expel"]
PRIVATE_ZONES = {"hand", "deck", "life"}


def setup_player_state(player_slot: str, deck_id: str) -> dict:
    deck = create_deck_instance(deck_id, player_slot)
    hand = deck[:5]
    life = deck[5:10]
    remaining_deck = deck[10:]
    return {
        "id": player_slot,
        "deckId": deck_id,
        "carrotCounter": 0,
        "zones": {
            "deck": remaining_deck,
            "hand": hand,
            "field": [create_trainer_card(player_slot)],
            "life": life,
            "discard": [],
            "carrot": [],
            "expel": [],
        },
    }


def setup_game_state(player1_deck_id: str, player2_deck_id: str) -> dict:
    return {
        "turnPlayer": "player1",
        "players": {
            "player1": setup_player_state("player1", player1_deck_id),
            "player2": setup_player_state("player2", player2_deck_id),
        },
    }


def draw_cards(game_state: dict, player_slot: str, count: int) -> None:
    player = game_state["players"][player_slot]
    drawn = player["zones"]["deck"][:count]
    player["zones"]["deck"] = player["zones"]["deck"][count:]
    player["zones"]["hand"].extend(drawn)


def shuffle_deck(game_state: dict, player_slot: str) -> None:
    random.shuffle(game_state["players"][player_slot]["zones"]["deck"])


def add_carrot(game_state: dict, player_slot: str) -> None:
    player = game_state["players"][player_slot]
    player["carrotCounter"] += 1
    player["zones"]["carrot"].append(create_carrot_card(player_slot, player["carrotCounter"]))


def find_card(player: dict, card_id: str, zone: str) -> dict | None:
    return next((card for card in player["zones"][zone] if card["instanceId"] == card_id), None)


def move_card(game_state: dict, player_slot: str, card_id: str, from_zone: str, to_zone: str, field_x=None, field_y=None) -> None:
    if from_zone not in ZONES or to_zone not in ZONES:
        raise ValueError("Invalid zone")
    player = game_state["players"][player_slot]
    card = find_card(player, card_id, from_zone)
    if not card:
        raise ValueError("Card not found")
    player["zones"][from_zone] = [item for item in player["zones"][from_zone] if item["instanceId"] != card_id]
    moved = dict(card)
    if to_zone == "field":
        moved["fieldX"] = field_x if field_x is not None else moved.get("fieldX", 18)
        moved["fieldY"] = field_y if field_y is not None else moved.get("fieldY", 18)
    else:
        moved.pop("fieldX", None)
        moved.pop("fieldY", None)
    if to_zone in {"deck", "life"}:
        player["zones"][to_zone].insert(0, moved)
    else:
        player["zones"][to_zone].append(moved)


def tap_card(game_state: dict, player_slot: str, card_id: str) -> None:
    player = game_state["players"][player_slot]
    for zone in ZONES:
        for card in player["zones"][zone]:
            if card["instanceId"] == card_id:
                card["status"] = "active" if card.get("status") == "rest" else "rest"
                return
    raise ValueError("Card not found")


def untap_all(game_state: dict, player_slot: str) -> None:
    player = game_state["players"][player_slot]
    for zone in ["field", "carrot"]:
        for card in player["zones"][zone]:
            card["status"] = "active"
