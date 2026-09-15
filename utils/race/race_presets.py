"""Backward-compatible exports for race presets.

Race track data lives in :mod:`utils.race.race_tracks` to keep this module
as the stable import path for existing callers.
"""

from utils.race.race_tracks import (
    PATH_TYPE,
    PATH_TYPE_ICON,
    PATH_TYPE_TEXT,
    RACE_PRESET,
    RACE_SCHEDULE,
    WEB_RACE_FINISH_DISTANCE_BY_TYPE,
    build_current_track_text,
    build_path_effect_text,
    build_track_progress_text,
    get_current_path_type,
    get_path_effect,
    get_web_race_finish_distance,
    render_path,
)

__all__ = [
    "PATH_TYPE",
    "PATH_TYPE_ICON",
    "PATH_TYPE_TEXT",
    "RACE_PRESET",
    "RACE_SCHEDULE",
    "WEB_RACE_FINISH_DISTANCE_BY_TYPE",
    "build_current_track_text",
    "build_path_effect_text",
    "build_track_progress_text",
    "get_current_path_type",
    "get_path_effect",
    "get_web_race_finish_distance",
    "render_path",
]
