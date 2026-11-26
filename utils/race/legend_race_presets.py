"""Editable default configurations for scheduled Legend Race rooms.

Add one entry per scheduled Legend challenge. ``legend_key`` must exist in
``MOB_PRESETS`` and ``stage_key`` must exist in ``RACE_PRESET``. The ``mobs``
field sets the level for the eight standard Debut opponents.
"""

LEGEND_RACE_PRESETS = {
    "tamamo_cross": {
        "legend_key": "tamamo_cross",
        "stage_key": "TennoShoAutumn",
        "legend_level": 2,
        "mobs": {"level": 1},
        "weather": "random",
        "record_type": "practice",
    },
    "tokai_teio": {
        "legend_key": "tokai_teio",
        "stage_key": "JapanCup",
        "legend_level": 2,
        "mobs": {"level": 3},
        "weather": "random",
        "record_type": "practice",
    },
    "silent_suzuka": {
        "legend_key": "silent_suzuka",
        "stage_key": "TakarazukaKinen",
        "legend_level": 3,
        "mobs": {"level": 4},
        "weather": "random",
        "record_type": "practice",
    },
    "StillInLove": {
        "legend_key": "StillInLove",
        "stage_key": "ShukaSho",
        "legend_level": 3,
        "mobs": {"level": 4},
        "weather": "random",
        "record_type": "practice",
    },
    "narita_top_road": {
        "legend_key": "narita_top_road",
        "stage_key": "KikukaSho",
        "legend_level": 3,
        "mobs": {"level": 4},
        "weather": "random",
        "record_type": "practice",
    },
    "almond_eye": {
        "legend_key": "almond_eye",
        "stage_key": "TennoShoAutumn",
        "legend_level": 3,
        "mobs": {"level": 4},
        "weather": "random",
        "record_type": "practice",
    },
}
