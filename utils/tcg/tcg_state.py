import random

from .tcg_decks import DECKS_BY_ID, create_carrot_card, create_deck_instance, create_trainer_card


ZONES = ['deck', 'hand', 'field', 'trainer', 'life', 'discard', 'carrot', 'expel']
PRIVATE_ZONES = {'hand', 'deck', 'life'}


def setup_player_state(player_slot: str, loadout: dict | str) -> dict:
    deck_id = loadout if isinstance(loadout, str) else loadout["deck_id"]
    trainer_id = DECKS_BY_ID[deck_id].get("trainer") if isinstance(loadout, str) else loadout["trainer_id"]
    deck_cards = create_deck_instance(deck_id, player_slot)
    hand = deck_cards[:5]
    life = deck_cards[5:10]
    remaining_deck = deck_cards[10:]
    return {
        'id': player_slot,
        'deckId': deck_id,
        'carrotCounter': 0,
        'zones': {
            'deck': remaining_deck,
            'hand': hand,
            'field': [],
            'trainer': [create_trainer_card(player_slot, trainer_id)],
            'life': life,
            'discard': [],
            'carrot': [],
            'expel': [],
        },
    }


def setup_game_state(player1_loadout: dict | str, player2_loadout: dict | str) -> dict:
    return {
        'turnPlayer': 'player1',
        'players': {
            'player1': setup_player_state('player1', player1_loadout),
            'player2': setup_player_state('player2', player2_loadout),
        },
    }


def draw_cards(game_state: dict, player_slot: str, count: int) -> None:
    player = game_state['players'][player_slot]
    drawn = player['zones']['deck'][:count]
    player['zones']['deck'] = player['zones']['deck'][count:]
    player['zones']['hand'].extend(drawn)


def shuffle_deck(game_state: dict, player_slot: str) -> None:
    random.shuffle(game_state['players'][player_slot]['zones']['deck'])


def add_carrot(game_state: dict, player_slot: str) -> None:
    player = game_state['players'][player_slot]
    player['carrotCounter'] += 1
    player['zones']['carrot'].append(create_carrot_card(player_slot, player['carrotCounter']))


def find_card(player: dict, card_id: str, zone: str) -> dict | None:
    return next((card for card in player['zones'][zone] if card['instanceId'] == card_id), None)


def find_card_location(game_state: dict, card_id: str) -> tuple[str, str, dict] | None:
    for player_slot, player in game_state['players'].items():
        for zone in ZONES:
            card = find_card(player, card_id, zone)
            if card:
                return player_slot, zone, card
    return None


def move_card(game_state: dict, player_slot: str, card_id: str, from_zone: str, to_zone: str, field_x=None, field_y=None) -> None:
    if from_zone not in ZONES or to_zone not in ZONES:
        raise ValueError('Invalid zone')
    location = find_card_location(game_state, card_id)
    if not location:
        raise ValueError('Card not found')
    owner_slot, actual_zone, card = location
    if owner_slot != player_slot:
        raise ValueError('Cannot move opponent cards')
    if actual_zone != from_zone:
        raise ValueError('Card is not in the requested source zone')

    player = game_state['players'][player_slot]
    player['zones'][from_zone] = [item for item in player['zones'][from_zone] if item['instanceId'] != card_id]
    moved = dict(card)
    if to_zone == 'field':
        moved['fieldX'] = field_x if field_x is not None else moved.get('fieldX', 18)
        moved['fieldY'] = field_y if field_y is not None else moved.get('fieldY', 18)
    else:
        moved.pop('fieldX', None)
        moved.pop('fieldY', None)
    if to_zone in {'deck', 'life'}:
        player['zones'][to_zone].insert(0, moved)
    else:
        player['zones'][to_zone].append(moved)


def tap_card(game_state: dict, player_slot: str, card_id: str) -> None:
    location = find_card_location(game_state, card_id)
    if not location:
        raise ValueError('Card not found')
    owner_slot, _zone, card = location
    if owner_slot != player_slot:
        raise ValueError('Cannot tap opponent cards')
    card['status'] = 'active' if card.get('status') == 'rest' else 'rest'


def untap_all(game_state: dict, player_slot: str) -> None:
    player = game_state['players'][player_slot]
    for zone in ['field', 'trainer', 'carrot']:
        for card in player['zones'][zone]:
            card['status'] = 'active'
