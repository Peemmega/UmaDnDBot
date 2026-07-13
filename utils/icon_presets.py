import os


def _resolve_emoji_set() -> str:
    """Use an explicit setting, with the known production domain as fallback."""
    configured = os.getenv("BOT_EMOJI_SET", "").strip().lower()
    if configured in {"main", "test"}:
        return configured

    runtime_hosts = (
        os.getenv("PUBLIC_BASE_URL", ""),
        os.getenv("RAILWAY_PUBLIC_DOMAIN", ""),
        os.getenv("RAILWAY_STATIC_URL", ""),
    )
    if any("umadndbot-production.up.railway.app" in host for host in runtime_hosts):
        return "main"
    return "test"


EMOJI_SET = _resolve_emoji_set()
USING_MAIN_EMOJIS = EMOJI_SET == "main"


STAT_EMOJIS = {
    1: "<:G_Rank:1493694904323412142>",
    2: "<:F_Rank:1493695005188161618>",
    3: "<:E_Rank:1493694944936726710>",
    4: "<:D_Rank:1493695027933610094>",
    5: "<:C_Rank:1493694926029062234>",
    6: "<:B_Rank:1493694964188581899>",
    7: "<:A_Rank:1493695074356166816>",
    8: "<:S_Rank:1493694983574655168>"
}

TEST_STATUS_ICONS = {
    "SPD": "<:Speed:1493706249714270248>",
    "STA": "<:Stamina:1493706286490189824>",
    "POW": "<:Power:1493706270488789082>",
    "GUT": "<:Gut:1493706305104379944>",
    "WIT": "<:Wit:1493706329406308352>",
}

MAIN_STATUS_ICONS = {
    "SPD": "<:Speed:1526294214114148513>",
    "STA": "<:Stamina:1526294249610674358>",
    "POW": "<:Power:1526294283336814784>",
    "GUT": "<:Gut:1526294332024422523>",
    "WIT": "<:Wit:1526294374340628510>",
}

TEST_SKILL_ICONS = {
    "Concentration": "<:Concentration:1494389544127172728>",
    "Acceleration": "<:Acceleration:1494389491337527538>",
    "Velocity": "<:Velocity:1494389507666088100>",
    "Navigation": "<:Navigation:1526295662881407108>",
    "Recovery": "<:Recovery:1494389472337330196>",
    "DecreaseVelocity": "<:DecreaseVelocity:1494389430721577070>",
    "ReduceSTA": "<:ReduceSTA:1494389406109270026>",
    "LookUp": "<:LookUp:1494389526359969873>",
    "Blind": "<:Blind:1494389451114151939>",
    "UniqueVelocity": "<:UniqueSkillVelocity:1499064862888824923>",
    "UniqueAcceleration": "<:UniqueSkillVelocity:1499064862888824923>",
}

MAIN_SKILL_ICONS = {
    "Acceleration": "<:Acceleration:1526293975512907926>",
    "Blind": "<:Blind:1526293997264441384>",
    "Concentration": "<:Concentration:1526294014330933518>",
    "DecreaseVelocity": "<:DecreaseVelocity:1526294031288504531>",
    "LookUp": "<:LookUp:1526294046530867320>",
    "Navigation": "<:Navigation:1526294065124216832>",
    "Recovery": "<:Recovery:1526294082597552228>",
    "ReduceSTA": "<:ReduceSTA:1526294099249074216>",
    "UniqueAcceleration": "<:UniqueSkillAcceleration:1526294117968117871>",
    "UniqueVelocity": "<:UniqueSkillVelocity:1526294132996308992>",
    "Velocity": "<:Velocity:1526294150130172045>",
}

TEST_ICONS = {
    "Aoharu": "<:Aoharu:1495417469328949258>",
    "AlarmClock": "<:AlarmClock:1499708925711487116>",
}

MAIN_ICONS = {
    "Aoharu": "<:Aoharu:1526296049365418156>",
    "AlarmClock": "<:AlarmClock:1526296859369279498>",
}

Status_Icon_Type = MAIN_STATUS_ICONS if USING_MAIN_EMOJIS else TEST_STATUS_ICONS
SKILL_ICONS = MAIN_SKILL_ICONS if USING_MAIN_EMOJIS else TEST_SKILL_ICONS
ICONS = MAIN_ICONS if USING_MAIN_EMOJIS else TEST_ICONS

GRADE_TEXT = {
    1: "G",
    2: "F",
    3: "E",
    4: "D",
    5: "C",
    6: "B",
    7: "A",
    8: "S",
}

GRADE_IMAGE_MAP = {
    1: "G.png",
    2: "F.png",
    3: "E.png",
    4: "D.png",
    5: "C.png",
    6: "B.png",
    7: "A.png",
    8: "S.png",
}
