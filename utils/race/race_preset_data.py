"""Central race preset catalogue and path-derived race metadata."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL
from utils.race.presets.chukyo import RACES as CHUKYO_RACES, TRACK_PATHS as CHUKYO_PATHS
from utils.race.presets.fukushima import RACES as FUKUSHIMA_RACES, TRACK_PATHS as FUKUSHIMA_PATHS
from utils.race.presets.funabashi import RACES as FUNABASHI_RACES, TRACK_PATHS as FUNABASHI_PATHS
from utils.race.presets.hakodate import RACES as HAKODATE_RACES, TRACK_PATHS as HAKODATE_PATHS
from utils.race.presets.hanshin import RACES as HANSHIN_RACES, TRACK_PATHS as HANSHIN_PATHS
from utils.race.presets.kawasaki import RACES as KAWASAKI_RACES, TRACK_PATHS as KAWASAKI_PATHS
from utils.race.presets.kokura import RACES as KOKURA_RACES, TRACK_PATHS as KOKURA_PATHS
from utils.race.presets.kyoto import RACES as KYOTO_RACES, TRACK_PATHS as KYOTO_PATHS
from utils.race.presets.morioka import RACES as MORIOKA_RACES, TRACK_PATHS as MORIOKA_PATHS
from utils.race.presets.nakayama import RACES as NAKAYAMA_RACES, TRACK_PATHS as NAKAYAMA_PATHS
from utils.race.presets.niigata import RACES as NIIGATA_RACES, TRACK_PATHS as NIIGATA_PATHS
from utils.race.presets.ooi import RACES as OOI_RACES, TRACK_PATHS as OOI_PATHS
from utils.race.presets.other import RACES as OTHER_RACES, TRACK_PATHS as OTHER_PATHS
from utils.race.presets.sapporo import RACES as SAPPORO_RACES, TRACK_PATHS as SAPPORO_PATHS
from utils.race.presets.special import RACES as SPECIAL_RACES, TRACK_PATHS as SPECIAL_PATHS
from utils.race.presets.tokyo import RACES as TOKYO_RACES, TRACK_PATHS as TOKYO_PATHS
from utils.race.presets.tokyo_steeplechase import RACES as TOKYO_STEEPLECHASE_RACES, TRACK_PATHS as TOKYO_STEEPLECHASE_PATHS

_VENUE_PRESETS = {
    "Hanshin": HANSHIN_RACES,
    "Tokyo": TOKYO_RACES,
    "Nakayama": NAKAYAMA_RACES,
    "Chukyo": CHUKYO_RACES,
    "Kyoto": KYOTO_RACES,
    "Ooi": OOI_RACES,
    "Kawasaki": KAWASAKI_RACES,
    "Funabashi": FUNABASHI_RACES,
    "Morioka": MORIOKA_RACES,
    "Hakodate": HAKODATE_RACES,
    "Niigata": NIIGATA_RACES,
    "Sapporo": SAPPORO_RACES,
    "Kokura": KOKURA_RACES,
    "Fukushima": FUKUSHIMA_RACES,
    "Tokyo (Steeplechase)": TOKYO_STEEPLECHASE_RACES,
    "Special": SPECIAL_RACES,
    "Other": OTHER_RACES,
}
_VENUE_PATHS = (
    CHUKYO_PATHS,
    FUKUSHIMA_PATHS,
    FUNABASHI_PATHS,
    HAKODATE_PATHS,
    HANSHIN_PATHS,
    KAWASAKI_PATHS,
    KOKURA_PATHS,
    KYOTO_PATHS,
    MORIOKA_PATHS,
    NAKAYAMA_PATHS,
    NIIGATA_PATHS,
    OOI_PATHS,
    OTHER_PATHS,
    SAPPORO_PATHS,
    SPECIAL_PATHS,
    TOKYO_PATHS,
    TOKYO_STEEPLECHASE_PATHS,
)
RACETRACKS = {
    path_key: path
    for venue_paths in _VENUE_PATHS
    for path_key, path in venue_paths.items()
}

RACE_VENUE_BY_ID = {
    venue: set(races)
    for venue, races in _VENUE_PRESETS.items()
}
RACE_PRESET = {
    race_id: race
    for races in _VENUE_PRESETS.values()
    for race_id, race in races.items()
}

# Consistent grade artwork for races without individual artwork.
for _race in RACE_PRESET.values():
    _name = str(_race.get("name", ""))
    if "(GII)" in _name:
        _race["thumnail"] = G2_RACE_THUMBNAIL
    elif "(GIII)" in _name:
        _race["thumnail"] = G3_RACE_THUMBNAIL


def get_race_venue(race_id: str) -> str:
    """Return the course grouping for a race preset."""
    for venue, race_ids in RACE_VENUE_BY_ID.items():
        if race_id in race_ids:
            return venue
    return "Other"


def get_race_turns(race: dict | None) -> int:
    """The number of turns is the number of segments in its path."""
    return len((race or {}).get("path") or [])


def get_race_distance_m(race: dict | None) -> int:
    """Get the distance encoded by the selected path layout/course key."""
    race = race or {}
    race_path = race.get("path")
    if race_path is not None:
        for path_key, path in RACETRACKS.items():
            if path is race_path:
                suffix = path_key.rsplit("_", 1)[-1]
                if suffix.isdigit():
                    return int(suffix)
    course = race.get("course") or {}
    if course.get("distance_m") is not None:
        return max(1, int(course["distance_m"]))
    # Fallback for custom entries that only provide a category.
    distance_type = str(race.get("distance_type") or "medium").lower()
    return {"sprint": 1400, "mile": 1600, "medium": 2000, "long": 3000}.get(distance_type, 2000)


def get_race_distance_type(race: dict | None) -> str:
    """Categorize distance from the course attached to the race path."""
    meters = get_race_distance_m(race)
    if meters <= 1400:
        return "sprint"
    if meters <= 1800:
        return "mile"
    if meters <= 2400:
        return "medium"
    return "long"
