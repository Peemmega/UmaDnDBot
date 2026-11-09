"""Editable default configurations for scheduled Legend Race rooms.

Add one entry per scheduled Legend challenge. ``legend_key`` must exist in
``MOB_PRESETS`` and ``stage_key`` must exist in ``RACE_PRESET``. Mob entries
use the same preset keys and levels as the regular race room controls.
"""

LEGEND_RACE_PRESETS = {
    "tamamo_cross": {
        "legend_key": "tamamo_cross",
        "stage_key": "TennoShoAutumn",
        "legend_level": 2,
        "mobs": [
            {"key": "rookie_pace", "level": 1},
        ],
        "weather": "random",
        "record_type": "practice",
    },
}
