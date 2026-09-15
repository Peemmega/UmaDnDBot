"""Race track definitions and shared track-path helpers."""

from utils.icon_presets import Status_Icon_Type

PATH_TYPE = {1: "STRAIGHT", 2: "CURVE", 3: "UPHILL", 4: "DOWNHILL"}

PATH_TYPE_TEXT = {
    1: "ทางตรง",
    2: "ทางโค้ง",
    3: "เนินขึ้น",
    4: "เนินลง",
}

PATH_TYPE_ICON = {
    1: "➡️",  # ทางตรง
    2: "⤵️",  # ทางโค้ง
    3: "↗️",  # เนินขึ้น
    4: "↘️",  # เนินลง
}

WEB_RACE_FINISH_DISTANCE_BY_TYPE = {
    "sprint": 1400,
    "mile": 1600,
    "medium": 2000,
    "long": 3000,
}


def get_web_race_finish_distance(stage: dict | None) -> int:
    stage = stage or {}
    custom_distance = stage.get("finish_distance")
    if custom_distance is not None:
        return max(1, int(custom_distance))

    distance_type = (
        stage.get("category") or stage.get("distance_type") or stage.get("distance")
    )
    return WEB_RACE_FINISH_DISTANCE_BY_TYPE.get(str(distance_type or "").lower(), 2000)


def get_current_path_type(game: dict) -> int:
    turn = game["turn"]
    path = game["path"]

    if not path:
        return 1

    index = max(0, min(turn - 1, len(path) - 1))
    return path[index]


def build_path_effect_text(path_type: int) -> str:
    if path_type == 1:
        return f"หัก 1 {Status_Icon_Type['STA']}"
    if path_type == 2:
        return f"หัก 1 {Status_Icon_Type['STA']} • แต้มสูงสุดลูกเต๋าลดลง 5"
    if path_type == 3:
        return f"หัก 2 {Status_Icon_Type['STA']} • {Status_Icon_Type['SPD']} เหลือครึ่งหนึ่ง • {Status_Icon_Type['POW']} โบนัสรวม x3"
    if path_type == 4:
        return f"ไม่เสีย {Status_Icon_Type['STA']} • เพิ่มแต้มสูงสุดลูกเต๋าตามค่า {Status_Icon_Type['WIT']}"
    return "-"


def build_track_progress_text(path: list[int], current_turn: int) -> str:
    parts = []

    for i, path_type in enumerate(path, start=1):
        icon = PATH_TYPE_ICON.get(path_type, "➡️")

        if i == current_turn:
            parts.append(f"【{icon}】")
        else:
            parts.append(icon)

    return " ".join(parts)


def build_current_track_text(path: list[int], current_turn: int) -> str:
    if not path:
        return "ไม่พบข้อมูลสนาม"

    current_turn = max(1, min(current_turn, len(path)))
    path_type = path[current_turn - 1]
    path_label = PATH_TYPE_TEXT.get(path_type, "ทางตรง")

    return f"ตอนนี้อยู่ช่วงที่ {current_turn}/{len(path)} : {path_label}"


def get_path_effect(path_type: int, game_player: dict, player_stat: dict) -> dict:
    effect = {
        "stamina_cost": 0,
        "stamina_multiplier": 1.0,
        "stamina_gain": 0,
        "reduce_dice_value": 0,
        "spd_multiplier": 1.0,
        "power_total_multiplier": 1.0,
        "extra_max_from_wit": 0,
        "extra_floor_from_wit": 0,
        "label": PATH_TYPE_TEXT.get(path_type, "ทางตรง"),
    }

    if path_type == 1:  # ทางตรง
        effect["stamina_cost"] = 0

    elif path_type == 2:  # ทางโค้ง
        effect["stamina_cost"] = 0
        effect["reduce_dice_value"] = 5
        effect["extra_max_from_wit"] = player_stat.get("wit", 0)
        effect["extra_floor_from_wit"] = player_stat.get("wit", 0)

    elif path_type == 3:  # เนินขึ้น
        effect["stamina_multiplier"] = 2.0
        effect["power_total_multiplier"] = 3.0
        if not game_player.get("debuffPower"):
            game_player["debuffPower"] = True
            game_player["current_max_speed"] *= 0.95

    elif path_type == 4:  # เนินลง
        effect["stamina_cost"] = 0
        effect["stamina_multiplier"] = 0.0
        downhill_wit_bonus = int(float(player_stat.get("wit", 0) or 0) * 1.5)
        effect["extra_max_from_wit"] = downhill_wit_bonus
        effect["extra_floor_from_wit"] = downhill_wit_bonus

    return effect


def render_path(path: list[int]) -> str:
    return "".join(PATH_TYPE_ICON.get(x, "⬜") for x in path)


# 2026 JRA race dates, sourced from https://www.jra.go.jp/keiba/calendar/
# Times are the app's scheduled start time (ICT); JRA's calendar supplies dates.
RACE_SCHEDULE = [
    # February — Tokyo
    {"race_id": "DiamondStakes", "date": "2026-02-21", "time": "20:00"},
    {"race_id": "FebruaryStakes", "date": "2026-02-22", "time": "20:00"},

    # March — Chukyo
    {"race_id": "TakamatsunomiyaKinen", "date": "2026-03-29", "time": "20:00"},

    # April — Hanshin / Nakayama
    {"race_id": "OsakaHai", "date": "2026-04-05", "time": "20:00"},
    {"race_id": "OkaSho", "date": "2026-04-12", "time": "20:00"},
    {"race_id": "SatsukiSho", "date": "2026-04-19", "time": "20:00"},

    # May — Tokyo / Kyoto
    {"race_id": "NHK", "date": "2026-05-10", "time": "20:00"},
    {"race_id": "VictoriaMileTokyo", "date": "2026-05-17", "time": "20:00"},
    {"race_id": "JapaneseOaks", "date": "2026-05-24", "time": "20:00"},
    {"race_id": "Aoi Stakes", "date": "2026-05-30", "time": "20:00"},
    {"race_id": "JapaneseDerby", "date": "2026-05-31", "time": "20:00"},

    # June — Tokyo / Hanshin
    {"race_id": "YasudaKinen", "date": "2026-06-07", "time": "20:00"},
    {"race_id": "TakarazukaKinen", "date": "2026-06-14", "time": "20:00"},

    # July–August — Hakodate / Niigata
    {"race_id": "HakodateJuniorStakes", "date": "2026-07-19", "time": "20:00"},
    {"race_id": "NiigataJuniorStakes", "date": "2026-08-23", "time": "20:00"},

    # September — Nakayama
    {"race_id": "SprintersStakes", "date": "2026-09-27", "time": "20:00"},

    # October — Tokyo / Kyoto
    {"race_id": "SaudiArabiaRoyalCup", "date": "2026-10-10", "time": "20:00"},
    {"race_id": "ShukaSho", "date": "2026-10-18", "time": "20:00"},
    {"race_id": "KikukaSho", "date": "2026-10-25", "time": "20:00"},

    # November — Tokyo / Kyoto
    {"race_id": "TennoShoAutumn", "date": "2026-11-01", "time": "20:00"},
    {"race_id": "QueenElizabethIICup", "date": "2026-11-15", "time": "20:00"},
    {"race_id": "MileChampionship", "date": "2026-11-22", "time": "20:00"},
    {"race_id": "KyotoJuniorStakes", "date": "2026-11-28", "time": "20:00"},
    {"race_id": "JapanCup", "date": "2026-11-29", "time": "20:00"},

    # December — Chukyo / Hanshin / Nakayama
    {"race_id": "ChunichiShimbunHai", "date": "2026-12-12", "time": "20:00"},
    {"race_id": "HanshinJuvenileFillies", "date": "2026-12-13", "time": "20:00"},
    {"race_id": "AsahiHaiFuturityStakes", "date": "2026-12-20", "time": "20:00"},
    {"race_id": "HopefulStakes", "date": "2026-12-26", "time": "20:00"},
    {"race_id": "ArimaKinen", "date": "2026-12-27", "time": "20:00"},

    # JRA also holds 2026 meetings at Sapporo, Fukushima, and Kokura.  Do not
    # add their events until matching RACE_PRESET/RACETRACKS path data exists.
]

# Add community events here when they should appear in the News & Schedule desk.
# ``image_url`` is optional; the desk uses an event icon when it is omitted.
# Example:
# {"id": "autumn-fan-meeting", "kind": "event", "name": "Autumn Fan Meeting",
#  "description": "พบปะและแข่งกระชับมิตร", "date": "2026-10-03", "time": "19:00",
#  "image_url": "https://example.com/event-banner.webp"},
EVENT_SCHEDULE: list[dict] = []

# Race definitions are intentionally stored separately from path behaviour.
from utils.race.race_preset_data import RACE_PRESET
