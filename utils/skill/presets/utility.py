"""Utility Skills catalog."""

UTILITY_SKILLS = {
    "utl_001": {
        "name": "Concentration",
        "icon": "Concentration_rare",
        "cooldown": 20,
        "cost": 40,
        "trigger": {"turn_min": 1, "turn_max": 1},
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_roll_floor", "value": 6, "duration": "this_roll"},
            {
                "type": "modify_velocity",
                "mode": "flat_total",
                "value": 20,
                "duration": "this_roll",
            },
        ],
        "tags": ["start", "concentration"],
    },
    "utl_002": {
        "name": "The Coast Is Clear!",
        "icon": "LookUp_rare",
        "cooldown": 10,
        "cost": 60,
        "trigger": {"style": "End", "phase_min": 2, "phase_max": 4},
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "modify_gold_range", "value": 50, "duration": "this_turn"},
            {"type": "modify_gold_lane_range", "value": 1, "duration": "this_turn"},
            {"type": "cap_floor", "value": 6, "duration": "this_roll"},
        ],
        "tags": ["vision", "end", "positioning"],
    },
    "utl_003": {
        "name": "Go with the Flow",
        "icon": "Navigation_rare",
        "cooldown": 8,
        "cost": 40,
        "trigger": {"phase_min": 4, "phase_max": 4},
        "target": {"scope": "self", "limit": 1},
        "effects": [{"type": "resolve_pending_lane_now"}],
        "tags": ["positioning"],
    },
    "utl_004": {
        "name": "Lane Legerdemain",
        "icon": "Navigation_rare",
        "cooldown": 8,
        "cost": 80,
        "trigger": {"phase_min": 4, "phase_max": 4},
        "target": {"scope": "self", "limit": 1},
        "effects": [
            {"type": "resolve_pending_lane_now"},
            {"type": "cap_floor", "value": 5, "duration": "this_roll"},
        ],
        "tags": ["late_race", "positioning"],
    },
}
