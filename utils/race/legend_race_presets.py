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
}
