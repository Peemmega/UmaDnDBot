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
# Times are the app's scheduled start time (GMT+7); JRA's calendar supplies dates.
def _jra_race(race_id: str, name: str, venue: str, date: str) -> dict:
    return {
        "race_id": race_id,
        "name": name,
        "venue": venue,
        "date": date,
        "time": "20:00",
    }


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
    {
        "race_id": "FukushimaHimbaStakes",
        "name": "Fukushima Himba Stakes (GIII)",
        "venue": "Fukushima",
        "track": "turf",
        "distance": "medium",
        "date": "2026-04-19",
        "time": "20:00",
    },
    # May — Tokyo / Kyoto
    {"race_id": "NHK", "date": "2026-05-10", "time": "20:00"},
    {"race_id": "VictoriaMileTokyo", "date": "2026-05-17", "time": "20:00"},
    {"race_id": "JapaneseOaks", "date": "2026-05-24", "time": "20:00"},
    {"race_id": "Aoi Stakes", "date": "2026-05-30", "time": "20:00"},
    {"race_id": "JapaneseDerby", "date": "2026-05-31", "time": "20:00"},
    # June — Tokyo / Hanshin
    {"race_id": "YasudaKinen", "date": "2026-06-07", "time": "20:00"},
    {"race_id": "TakarazukaKinen", "date": "2026-06-14", "time": "20:00"},
    # July–August — Hakodate / Kokura / Niigata / Sapporo
    {"race_id": "HakodateJuniorStakes", "date": "2026-07-19", "time": "20:00"},
    {
        "race_id": "KokuraKinen",
        "name": "Kokura Kinen (GIII)",
        "venue": "Kokura",
        "track": "turf",
        "distance": "medium",
        "date": "2026-07-19",
        "time": "20:00",
    },
    {
        "race_id": "SapporoKinen",
        "name": "Sapporo Kinen (GII)",
        "venue": "Sapporo",
        "track": "turf",
        "distance": "medium",
        "date": "2026-08-16",
        "time": "20:00",
    },
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
    # Schedule-only races have no RACE_PRESET yet; they remain visible in News.
    *(
        _jra_race(*race)
        for race in [
            # January
            (
                "NakayamaKimpai",
                "Nikkan Sports Sho Nakayama Kimpai (GIII)",
                "Nakayama",
                "2026-01-04",
            ),
            (
                "KyotoKimpai",
                "Sports Nippon Sho Kyoto Kimpai (GIII)",
                "Kyoto",
                "2026-01-04",
            ),
            ("FairyStakes", "Fairy Stakes (GIII)", "Nakayama", "2026-01-11"),
            (
                "ShinzanKinen",
                "Nikkan Sports Sho Shinzan Kinen (GIII)",
                "Kyoto",
                "2026-01-12",
            ),
            ("KeiseiHai", "Keisei Hai (GIII)", "Nakayama", "2026-01-18"),
            ("NikkeiShinshunHai", "Nikkei Shinshun Hai (GII)", "Kyoto", "2026-01-18"),
            ("KokuraHimbaStakes", "Kokura Himba Stakes (GIII)", "Kokura", "2026-01-24"),
            (
                "AmericanJockeyClubCup",
                "American Jockey Club Cup (GII)",
                "Nakayama",
                "2026-01-25",
            ),
            ("ProcyonStakes", "Procyon Stakes (GII)", "Kyoto", "2026-01-25"),
            # February
            ("NegishiStakes", "Negishi Stakes (GIII)", "Tokyo", "2026-02-01"),
            ("SilkRoadStakes", "Silk Road Stakes (GIII)", "Kyoto", "2026-02-01"),
            ("KisaragiSho", "Kisaragi Sho (GIII)", "Kyoto", "2026-02-10"),
            ("TokyoShimbunHai", "Tokyo Shimbun Hai (GIII)", "Tokyo", "2026-02-10"),
            ("DailyHaiQueenCup", "Daily Hai Queen Cup (GIII)", "Tokyo", "2026-02-14"),
            (
                "KyodoNewsHai",
                "Kyodo News Hai (Tokinominoru Kinen) (GIII)",
                "Tokyo",
                "2026-02-15",
            ),
            ("KyotoKinen", "Kyoto Kinen (GII)", "Kyoto", "2026-02-15"),
            ("HankyuHai", "Hankyu Hai (GIII)", "Hanshin", "2026-02-21"),
            ("KokuraDaishoten", "Kokura Daishoten (GIII)", "Kokura", "2026-02-22"),
            ("OceanStakes", "Ocean Stakes (GIII)", "Nakayama", "2026-02-28"),
            # March
            ("NakayamaKinen", "Nakayama Kinen (GII)", "Nakayama", "2026-03-01"),
            (
                "TulipSho",
                "Tulip Sho (Japanese 1000 Guineas Trial) (GII)",
                "Hanshin",
                "2026-03-01",
            ),
            (
                "NakayamaHimbaStakes",
                "Laurel R.C. Sho Nakayama Himba Stakes (GIII)",
                "Nakayama",
                "2026-03-07",
            ),
            (
                "FilliesRevue",
                "Hochi Hai Fillies' Revue (Japanese 1000 Guineas Trial) (GII)",
                "Hanshin",
                "2026-03-07",
            ),
            (
                "YayoiSho",
                "Hochi Hai Yayoi Sho Deep Impact Kinen (GII)",
                "Nakayama",
                "2026-03-08",
            ),
            (
                "SpringStakes",
                "Fuji TV Sho Spring Stakes (GII)",
                "Nakayama",
                "2026-03-15",
            ),
            ("KinkoSho", "Tokai TV Hai Kinko Sho (GII)", "Chukyo", "2026-03-15"),
            ("FlowerCup", "Flower Cup (GIII)", "Nakayama", "2026-03-21"),
            (
                "FalconStakes",
                "Chunichi Sports Sho Falcon Stakes (GIII)",
                "Chukyo",
                "2026-03-21",
            ),
            ("HanshinDaishoten", "Hanshin Daishoten (GII)", "Hanshin", "2026-03-22"),
            ("AichiHai", "Aichi Hai (GIII)", "Chukyo", "2026-03-22"),
            ("NikkeiSho", "Nikkei Sho (GII)", "Nakayama", "2026-03-28"),
            ("MainichiHai", "Mainichi Hai (GIII)", "Hanshin", "2026-03-28"),
            ("MarchStakes", "March Stakes (GIII)", "Nakayama", "2026-03-29"),
            # April
            (
                "LordDerbyChallengeTrophy",
                "Lord Derby Challenge Trophy (GIII)",
                "Nakayama",
                "2026-04-04",
            ),
            (
                "ChurchillDownsCup",
                "Churchill Downs Cup (GIII)",
                "Hanshin",
                "2026-04-04",
            ),
            ("NewZealandTrophy", "New Zealand Trophy (GII)", "Nakayama", "2026-04-11"),
            (
                "HanshinHimbaStakes",
                "Sankei Sports Hai Hanshin Himba Stakes (GII)",
                "Hanshin",
                "2026-04-11",
            ),
            ("AntaresStakes", "Antares Stakes (GIII)", "Hanshin", "2026-04-18"),
            ("AobaSho", "TV Tokyo Hai Aoba Sho (GII)", "Tokyo", "2026-04-25"),
            (
                "FloraStakes",
                "Sankei Sports Sho Flora Stakes (GII)",
                "Tokyo",
                "2026-04-26",
            ),
            ("MilersCup", "Yomiuri Milers Cup (GII)", "Kyoto", "2026-04-26"),
            # May
            ("KeioHaiSpringCup", "Keio Hai Spring Cup (GII)", "Tokyo", "2026-05-02"),
            ("UnicornStakes", "Unicorn Stakes (GIII)", "Kyoto", "2026-05-02"),
            ("TennoShoSpring", "Tenno Sho (Spring) (GI)", "Kyoto", "2026-05-03"),
            ("EpsomCup", "Epsom Cup (GIII)", "Tokyo", "2026-05-09"),
            ("KyotoShimbunHai", "Kyoto Shimbun Hai (GII)", "Kyoto", "2026-05-09"),
            ("NiigataDaishoten", "Niigata Daishoten (GIII)", "Niigata", "2026-05-16"),
            ("HeianStakes", "Heian Stakes (GIII)", "Kyoto", "2026-05-23"),
            ("MeguroKinen", "Meguro Kinen (GII)", "Tokyo", "2026-05-31"),
            # June
            (
                "HakodateSprintStakes",
                "Hakodate Sprint Stakes (GIII)",
                "Hakodate",
                "2026-06-13",
            ),
            ("FuchuHimbaStakes", "Fuchu Himba Stakes (GIII)", "Tokyo", "2026-06-21"),
            ("ShirasagiStakes", "Shirasagi Stakes (GIII)", "Hanshin", "2026-06-21"),
            ("RadioNikkeiSho", "Radio Nikkei Sho (GIII)", "Fukushima", "2026-06-28"),
            ("HakodateKinen", "Hakodate Kinen (GIII)", "Hakodate", "2026-06-28"),
            # July and August
            (
                "KitakyushuKinen",
                "TV Nishinippon Corp. Sho Kitakyushu Kinen (GIII)",
                "Kokura",
                "2026-07-05",
            ),
            ("TanabataSho", "Tanabata Sho (GIII)", "Fukushima", "2026-07-12"),
            ("SekiyaKinen", "Sekiya Kinen (GIII)", "Niigata", "2026-07-26"),
            ("TokaiStakes", "Tokai Stakes (GIII)", "Chukyo", "2026-07-26"),
            ("IbisSummerDash", "Ibis Summer Dash (GIII)", "Niigata", "2026-08-02"),
            (
                "QueenStakes",
                "Hokkaido Shimbun Hai Queen Stakes (GIII)",
                "Sapporo",
                "2026-08-02",
            ),
            ("ElmStakes", "Elm Stakes (GIII)", "Sapporo", "2026-08-08"),
            ("LeopardStakes", "Leopard Stakes (GIII)", "Niigata", "2026-08-09"),
            ("CBCSho", "CBC Sho (GIII)", "Chukyo", "2026-08-09"),
            ("ChukyoKinen", "Chukyo Kinen (GIII)", "Chukyo", "2026-08-16"),
            ("KeenelandCup", "Keeneland Cup (GIII)", "Sapporo", "2026-08-23"),
            ("NiigataKinen", "Niigata Kinen (GIII)", "Niigata", "2026-08-30"),
            ("ChukyoNisaiStakes", "Chukyo Nisai Stakes (GIII)", "Chukyo", "2026-08-30"),
            # September
            (
                "KeiseiHaiAutumnHandicap",
                "Keisei Hai Autumn Handicap (GIII)",
                "Nakayama",
                "2026-09-05",
            ),
            (
                "SapporoNisaiStakes",
                "Sapporo Nisai Stakes (GIII)",
                "Sapporo",
                "2026-09-05",
            ),
            ("ShionStakes", "Shion Stakes (GII)", "Nakayama", "2026-09-06"),
            (
                "CentaurStakes",
                "Sankei Sho Centaur Stakes (GII)",
                "Chukyo",
                "2026-09-06",
            ),
            ("ChallengeCup", "Challenge Cup (GIII)", "Hanshin", "2026-09-12"),
            ("StLiteKinen", "Asahi Hai St. Lite Kinen (GII)", "Nakayama", "2026-09-20"),
            (
                "RoseStakes",
                "Kansai Telecasting Corp. Sho Rose Stakes (GII)",
                "Chukyo",
                "2026-09-20",
            ),
            ("KobeShimbunHai", "Kobe Shimbun Hai (GII)", "Chukyo", "2026-09-21"),
            ("SiriusStakes", "Sirius Stakes (GIII)", "Hanshin", "2026-09-26"),
            # October
            ("MainichiOkan", "Mainichi Okan (GII)", "Tokyo", "2026-10-04"),
            ("KyotoDaishoten", "Kyoto Daishoten (GII)", "Kyoto", "2026-10-04"),
            ("IrelandTrophy", "Ireland Trophy (GII)", "Tokyo", "2026-10-11"),
            ("SwanStakes", "MBS Sho Swan Stakes (GII)", "Kyoto", "2026-10-12"),
            ("FujiStakes", "Fuji Stakes (GIII)", "Tokyo", "2026-10-17"),
            ("ArtemisStakes", "Artemis Stakes (GIII)", "Tokyo", "2026-10-24"),
            (
                "FantasyStakes",
                "KBS Kyoto Sho Fantasy Stakes (GIII)",
                "Kyoto",
                "2026-10-31",
            ),
            # November
            (
                "KeioHaiNisaiStakes",
                "Keio Hai Nisai Stakes (GII)",
                "Tokyo",
                "2026-11-07",
            ),
            (
                "CopaRepublicaArgentina",
                "Copa Republica Argentina (GII)",
                "Tokyo",
                "2026-11-08",
            ),
            ("MiyakoStakes", "Miyako Stakes (GIII)", "Kyoto", "2026-11-08"),
            ("MusashinoStakes", "Musashino Stakes (GIII)", "Tokyo", "2026-11-14"),
            (
                "DailyHaiNisaiStakes",
                "Daily Hai Nisai Stakes (GII)",
                "Kyoto",
                "2026-11-14",
            ),
            ("FukushimaKinen", "Fukushima Kinen (GIII)", "Fukushima", "2026-11-21"),
            (
                "TokyoSportsHaiNisaiStakes",
                "Tokyo Sports Hai Nisai Stakes (GII)",
                "Tokyo",
                "2026-11-23",
            ),
            ("KeihanHai", "Keihan Hai (GIII)", "Kyoto", "2026-11-29"),
            # December
            (
                "StayersStakes",
                "Sports Nippon Sho Stayers Stakes (GII)",
                "Nakayama",
                "2026-12-05",
            ),
            ("NaruoKinen", "Naruo Kinen (GIII)", "Hanshin", "2026-12-05"),
            ("ChampionsCup", "Champions Cup (GI)", "Chukyo", "2026-12-06"),
            ("CapellaStakes", "Capella Stakes (GIII)", "Nakayama", "2026-12-13"),
            ("TurquoiseStakes", "Turquoise Stakes (GIII)", "Nakayama", "2026-12-19"),
            ("HanshinCup", "Hanshin Cup (GII)", "Hanshin", "2026-12-26"),
        ]
    ),
    # JRA also lists these graded jump races in the 2026 fixture calendar.
    _jra_race(
        "KokuraJumpStakes", "Kokura Jump Stakes (J-GIII)", "Kokura", "2026-02-14"
    ),
    _jra_race(
        "HanshinSpringJump", "Hanshin Spring Jump (J-GII)", "Hanshin", "2026-03-14"
    ),
    _jra_race(
        "NakayamaGrandJump", "Nakayama Grand Jump (J-GI)", "Nakayama", "2026-04-18"
    ),
    _jra_race("KyotoHighJump", "Kyoto High-Jump (J-GII)", "Kyoto", "2026-05-16"),
    _jra_race("TokyoJumpStakes", "Tokyo Jump Stakes (J-GIII)", "Tokyo", "2026-06-13"),
    _jra_race(
        "NiigataJumpStakes", "Niigata Jump Stakes (J-GIII)", "Niigata", "2026-08-15"
    ),
    _jra_race(
        "HanshinJumpStakes", "Hanshin Jump Stakes (J-GIII)", "Hanshin", "2026-09-19"
    ),
    _jra_race("TokyoHighJump", "Tokyo High-Jump (J-GII)", "Tokyo", "2026-10-18"),
    _jra_race("KyotoJumpStakes", "Kyoto Jump Stakes (J-GIII)", "Kyoto", "2026-11-07"),
    _jra_race(
        "NakayamaDaishogai", "Nakayama Daishogai (J-GI)", "Nakayama", "2026-12-26"
    ),
]

# Race definitions are intentionally stored separately from path behaviour.
from utils.race.race_preset_data import RACE_PRESET
