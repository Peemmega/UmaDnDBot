from __future__ import annotations


# UI countdown. Keep the backend bot delay derived from these values so bots and
# players begin moving after the same countdown.
WEB_TIMING_COUNTDOWN_STEPS = ("3", "2", "1", "GO!")
WEB_TIMING_COUNTDOWN_STEP_MS = 780
WEB_TIMING_GO_HOLD_MS = 520
WEB_TIMING_START_DELAY_MS = 500

# Gauge timing and request limits.
DEFAULT_GAUGE_HALF_CYCLE_MS = 1450
WEB_TIMING_GAUGE_HALF_CYCLE_MS = DEFAULT_GAUGE_HALF_CYCLE_MS / 1.5
WEB_TIMING_MIN_HALF_CYCLE_MS = 520
TIMING_MIN_INTERVAL_SECONDS = 0.2
BOT_TIMING_POLL_INTERVAL_SECONDS = 0.05

# Race balance.
WEB_TIMING_TEMPO_TABLE = {
    "Front": {1: "H", 2: "N", 3: "N", 4: "M"},
    "Pace": {1: "M", 2: "M", 3: "M", 4: "M"},
    "Late": {1: "N", 2: "N", 3: "H", 4: "M"},
    "End": {1: "N", 2: "N", 3: "M", 4: "H"},
}

WEB_TIMING_TEMPO_CONFIG = {
    "N": {
        "label": "Normal",
        "speed_multiplier": 1.00,
        "acceleration_multiplier": 1.00,
        "gauge_speed_multiplier": 1.00,
    },
    "M": {
        "label": "Medium",
        "speed_multiplier": 1.00,
        "acceleration_multiplier": 1.10,
        "gauge_speed_multiplier": 1.10,
    },
    "H": {
        "label": "High",
        "speed_multiplier": 1.00,
        "acceleration_multiplier": 1.30,
        "gauge_speed_multiplier": 1.30,
    },
}

WEB_TIMING_ZONE_EFFECT = {
    "duration_seconds": 8.0,
    "speed_bonus": 1.20,
    "acceleration_multiplier": 1.20,
    "gauge_speed_bonus": 1.15,
}

TIMING_RESULT_MULTIPLIERS = {
    "Perfect": 1.20,
    "Great": 1.00,
    "Good": 0.80,
    "Bad": 0.65,
    "Miss": 0.35,
}

MAX_WEB_TIMING_SPEED = 40.0
MAX_WEB_TIMING_ACCELERATION = 4.0
MIN_WEB_TIMING_ACCELERATION = 0.30
MAX_ACCELERATION_ELAPSED_SECONDS = 3.0
WEB_TIMING_BASE_ACCELERATION = 0.30
WEB_TIMING_POWER_ACCELERATION_MULTIPLIER_PER_POINT = 0.10


def get_web_timing_start_delay_seconds() -> float:
    countdown_ms = (
        (len(WEB_TIMING_COUNTDOWN_STEPS) - 1) * WEB_TIMING_COUNTDOWN_STEP_MS
        + WEB_TIMING_GO_HOLD_MS
        + WEB_TIMING_START_DELAY_MS
    )
    return countdown_ms / 1000.0


def get_web_timing_ui_config() -> dict:
    return {
        "countdown_steps": list(WEB_TIMING_COUNTDOWN_STEPS),
        "countdown_step_ms": WEB_TIMING_COUNTDOWN_STEP_MS,
        "go_hold_ms": WEB_TIMING_GO_HOLD_MS,
        "start_delay_ms": WEB_TIMING_START_DELAY_MS,
        "min_half_cycle_ms": WEB_TIMING_MIN_HALF_CYCLE_MS,
        "default_half_cycle_ms": DEFAULT_GAUGE_HALF_CYCLE_MS,
    }
