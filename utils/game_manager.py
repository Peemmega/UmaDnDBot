from utils.race_presets import RACE_PRESET
from utils.database import get_player

VALID_STYLES = {"Front", "Pace", "Late", "End"}
games = {}

def create_game(channel_id: int, stage_key: str, owner_id: int):
    if channel_id in games:
        return False

    if stage_key not in RACE_PRESET:
        return False

    stage = RACE_PRESET[stage_key]

    games[channel_id] = {
        "stage_key": stage_key,
        "stage_name": stage["name"],
        "max_turn": stage["turn"],
        "path": stage["path"],
        "owner_id": owner_id,
        "turn": 0,
        "started": False,
        "players": {},
        "turn_snapshot_scores": {},

        "turn_confirmations": set(),
        "awaiting_turn_confirm": False,
    }
    return True

def have_all_players_rolled(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    players = game["players"]
    if not players:
        return False

    current_turn = game["turn"]
    return all(player["last_roll_turn"] == current_turn for player in players.values())

def reset_turn_confirmations(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    game["turn_confirmations"] = set()
    game["awaiting_turn_confirm"] = False
    return True


def start_turn_confirmation(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    game["turn_confirmations"] = set()
    game["awaiting_turn_confirm"] = True
    return True


def confirm_turn(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if not game["awaiting_turn_confirm"]:
        return False, "ตอนนี้ยังไม่อยู่ในช่วงยืนยันจบเทิร์น"

    if user_id not in game["players"]:
        return False, "คุณไม่ได้อยู่ในเกมนี้"

    game["turn_confirmations"].add(user_id)

    confirmed_count = len(game["turn_confirmations"])
    total_players = len(game["players"])

    all_confirmed = confirmed_count >= total_players

    return True, {
        "confirmed_count": confirmed_count,
        "total_players": total_players,
        "all_confirmed": all_confirmed,
    }

def refresh_turn_snapshot(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }
    return True

def get_game(channel_id: int):
    return games.get(channel_id)


def delete_game(channel_id: int) -> bool:
    if channel_id not in games:
        return False

    del games[channel_id]
    return True

def end_game(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    game["ended"] = True
    game["started"] = False
    game["phase"] = "ended"
    return True, "จบเกมแล้ว"

def is_owner(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False
    return game["owner_id"] == user_id


def is_game_started(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False
    return game["started"]

def have_all_players_rolled(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False

    players = game["players"]
    if not players:
        return False

    current_turn = game["turn"]
    return all(player["last_roll_turn"] == current_turn for player in players.values())

def start_game(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มไปแล้ว"

    if len(game["players"]) == 0:
        return False, "ยังไม่มีผู้เล่นในเกม"

    game["started"] = True
    game["phase"] = "running"
    game["turn"] = 1

    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }

    for user_id, player in game["players"].items():
        db_player = get_player(user_id)

        player["reroll_left"] = 2
        player["stamina_left"] = db_player["stamina"] if db_player is not None else 0

    return True, "เริ่มเกมเรียบร้อยแล้ว"

def use_player_stamina(channel_id: int, user_id: int, amount: int = 1):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"

    if player["stamina_left"] < amount:
        return False, player["stamina_left"]

    player["stamina_left"] -= amount
    return True, player["stamina_left"]

def apply_stamina_cost(channel_id: int, user_id: int, turn: int):
    game = get_game(channel_id)
    if game is None:
        return {"used": False, "penalty": 0, "stamina_left": None}

    player = game["players"].get(user_id)
    if player is None:
        return {"used": False, "penalty": 0, "stamina_left": None}

    if turn <= 8:
        return {
            "used": False,
            "penalty": 0,
            "stamina_left": player["stamina_left"]
        }

    if player["stamina_left"] > 0:
        player["stamina_left"] -= 1
        return {
            "used": True,
            "penalty": 0,
            "stamina_left": player["stamina_left"]
        }

    return {
        "used": False,
        "penalty": 30,
        "stamina_left": player["stamina_left"]
    }

def get_player_stamina_left(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return None

    player = game["players"].get(user_id)
    if player is None:
        return None

    return player["stamina_left"]

def use_reroll(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ไม่พบผู้เล่นในเกม"

    if player["reroll_left"] <= 0:
        return False, "คุณไม่มี reroll เหลือแล้ว"

    player["reroll_left"] -= 1
    return True, player["reroll_left"]

def next_turn(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return None

    game["turn"] += 1
    game["turn_snapshot_scores"] = {
        user_id: info["score"]
        for user_id, info in game["players"].items()
    }
    return game["turn"]

def get_ranked_players(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return []

    return sorted(
        game["players"].items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )

def add_player(channel_id: int, user_id: int, style: str):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if game["started"]:
        return False, "เกมเริ่มแล้ว ไม่สามารถเข้าร่วมเพิ่มได้"

    if style not in VALID_STYLES:
        return False, "รูปแบบการวิ่งไม่ถูกต้อง"

    if user_id in game["players"]:
        return False, "คุณเข้าร่วมเกมนี้แล้ว"

    game["players"][user_id] = {
        "style": style,
        "score": 0,
        "last_roll_turn": -1,
        "reroll_left": 0,
        "stamina_left": 0,
    }
    return True, "เข้าร่วมเกมสำเร็จ"

def grant_start_rerolls(channel_id: int, amount: int = 2):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    for user_id, player in game["players"].items():
        player["reroll_left"] = 2

    return True, f"แจก reroll คนละ {amount} ครั้งแล้ว"

def get_player_in_game(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return None
    return game["players"].get(user_id)


def get_players(channel_id: int):
    game = get_game(channel_id)
    if game is None:
        return None
    return game["players"]


def update_player_score(channel_id: int, user_id: int, amount: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "ผู้เล่นนี้ไม่ได้อยู่ในเกม"

    player["score"] += amount
    return True, player["score"]


def can_player_roll(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    if not game["started"]:
        return False, "เกมยังไม่เริ่ม"

    player = game["players"].get(user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    if player["last_roll_turn"] == game["turn"]:
        return False, "คุณทอยไปแล้วในเทิร์นนี้"

    return True, "สามารถทอยได้"


def mark_player_rolled(channel_id: int, user_id: int):
    game = get_game(channel_id)
    if game is None:
        return False, "ยังไม่มีเกมในห้องนี้"

    player = game["players"].get(user_id)
    if player is None:
        return False, "คุณยังไม่ได้เข้าร่วมเกมนี้"

    player["last_roll_turn"] = game["turn"]
    return True, "บันทึกการทอยแล้ว"