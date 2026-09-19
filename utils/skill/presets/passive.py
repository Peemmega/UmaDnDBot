"""Passive Skills catalog."""

PASSIVE_SKILLS = {
    "pas_001": {
        "name": "Impulse",
        "icon": "Passive_rare",
        "activation": "passive",
        "cooldown": 99,
        "cost": 120,
        "trigger": {"style": "Late", "track": "turf", "turn_min": 1, "turn_max": 1},
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "modify_race_stats", "stats": "all", "value": 1}],
        "tags": ["late", "turf", "passive"],
    },
    "pas_002": {
        "name": "Track Demon",
        "icon": "Passive_rare",
        "activation": "passive",
        "cooldown": 99,
        "cost": 80,
        "trigger": {"turn_min": 1, "turn_max": 1},
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "modify_race_stats", "stats": {"power": 2, "speed": 1}}],
        "tags": ["start", "power", "velocity"],
    },
    "pas_003": {
        "name": "Singularity",
        "icon": "Passive_rare",
        "activation": "passive",
        "cooldown": 99,
        "cost": 80,
        "trigger": {
            "turn_min": 1,
            "turn_max": 1,
            "style": "Pace",
            "distance_type": "Medium",
        },
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_race_stats", "stat": "speed", "value": 3},
            {
                "type": "modify_race_stats",
                "stat": "speed",
                "value": 1,
                "condition": {"base_stats_min": {"wit": 4}},
            },
        ],
        "tags": ["start", "pace", "medium", "velocity"],
    },
}
