from .tcg_state import PRIVATE_ZONES, ZONES


def sanitize_card_back(zone: str, index: int) -> dict:
    return {
        "instanceId": f"hidden-{zone}-{index}",
        "id": "hidden-card",
        "name": "Hidden Card",
        "type": "Hidden",
        "style": "Speed",
        "cost": 0,
        "power": 0,
        "status": "active",
        "hidden": True,
    }


def sanitize_game_state(room: dict, viewer_user_id: str | None) -> dict:
    viewer_slot = room["player_slots"].get(str(viewer_user_id)) if viewer_user_id else None
    game_state = room.get("game_state")
    if not game_state:
        return None

    players = {}
    for slot, state in game_state["players"].items():
        visible_zones = {}
        is_self = slot == viewer_slot
        for zone in ZONES:
            cards = state["zones"][zone]
            if is_self or zone not in PRIVATE_ZONES:
                visible_zones[zone] = cards
            else:
                visible_zones[zone] = [sanitize_card_back(zone, index) for index, _card in enumerate(cards)]
        players[slot] = {
            **state,
            "zones": visible_zones,
            "zoneCounts": {zone: len(state["zones"][zone]) for zone in ZONES},
        }

    return {
        **game_state,
        "players": players,
    }


def sanitize_room(room: dict, viewer_user_id: str | None = None) -> dict:
    return {
        "room_id": room["room_id"],
        "room_code": room["room_code"],
        "host_id": room["host_id"],
        "phase": room["phase"],
        "players": room["players"],
        "player_slots": room["player_slots"],
        "deck_confirmed": room["deck_confirmed"],
        "created_at": room["created_at"],
        "updated_at": room["updated_at"],
        "game_state": sanitize_game_state(room, viewer_user_id),
        "my_player_id": room["player_slots"].get(str(viewer_user_id)) if viewer_user_id else None,
    }