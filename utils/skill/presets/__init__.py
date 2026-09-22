"""Skill catalogs grouped by gameplay type."""

from .acceleration import ACCELERATION_SKILLS
from .velocity import VELOCITY_SKILLS
from .passive import PASSIVE_SKILLS
from .recovery import RECOVERY_SKILLS
from .unique import UNIQUE_SKILLS
from .utility import UTILITY_SKILLS
from .debuff import DEBUFF_SKILLS


# Tags are normalized when catalogs are assembled.  Preset authors can keep a
# short hand-written tag list, while the public catalog always reflects the
# gameplay condition that is actually evaluated.
_TAG_ORDER = (
    "turf", "dirt", "sprint", "mile", "medium", "long",
    "front", "pace", "late", "end",
    "passive", "unique", "acceleration", "velocity", "recovery", "debuff",
    "blind", "concentration", "vision", "positioning",
    "early_race", "mid_race", "late_race", "lastspurt",
    "straight", "corner", "final_corner", "uphill", "downhill",
    "front_position", "middle_position", "back_position",
    "front_blocked", "target_ahead", "target_behind",
    "target_all_front", "target_all_back", "nearby_uma", "followed",
    "stability", "cap_boost", "burst", "sustain", "power", "stamina", "mindgame",
)
_TAG_ORDER_INDEX = {tag: index for index, tag in enumerate(_TAG_ORDER)}
_TAG_ALIASES = {
    "start": "early_race",
    "last_spurt": "lastspurt",
    "straightaway": "straight",
    "lead": "front_position",
    "back": "back_position",
    "middle": "middle_position",
    "blocked": "front_blocked",
    "all_front": "target_all_front",
    "all_back": "target_all_back",
    "front_target": "target_ahead",
    "stamina_cost": "stamina",
}
_DERIVED_TAGS = {
    "turf", "dirt", "sprint", "mile", "medium", "long",
    "front", "pace", "late", "end",
    "early_race", "mid_race", "late_race", "lastspurt",
    "mid_late",
    "straight", "corner", "final_corner", "uphill", "downhill",
    "front_position", "middle_position", "back_position", "front_blocked",
}
_ICON_TAGS = {
    "Acceleration": {"acceleration"}, "Acceleration_rare": {"acceleration"},
    "acceleration": {"acceleration"}, "UniqueAcceleration": {"unique", "acceleration"},
    "Velocity": {"velocity"}, "Velocity_rare": {"velocity"}, "velocity": {"velocity"},
    "UniqueVelocity": {"unique", "velocity"},
    "Recovery": {"recovery"}, "Recovery_rare": {"recovery"}, "stamina": {"recovery"},
    "Passive": {"passive"}, "Passive_rare": {"passive"},
    "Concentration": {"concentration"}, "Concentration_rare": {"concentration"},
    "LookUp": {"vision", "positioning"}, "LookUp_rare": {"vision", "positioning"},
    "Navigation": {"positioning"}, "Navigation_rare": {"positioning"},
    "DecreaseVelocity": {"debuff"}, "DecreaseVelocity_rare": {"debuff"},
    "ReduceSTA": {"debuff", "stamina"}, "ReduceSTA_rare": {"debuff", "stamina"},
    "Blind": {"debuff", "blind"}, "Blind_rare": {"debuff", "blind"},
}
_EFFECT_TAGS = {
    "modify_velocity": {"velocity"},
    "modify_current_speed": {"acceleration"},
    "recover_stamina": {"recovery", "stamina"},
    "self_heal_stamina": {"recovery", "stamina"},
    "reduce_stamina": {"debuff", "stamina"},
    "apply_debuff_next_turn": {"debuff"},
    "modify_enemy_gold_range": {"debuff", "blind"},
    "modify_enemy_gold_lane_range": {"debuff", "blind"},
    "resolve_pending_lane_now": {"positioning"},
    "force_path_bonus": {"positioning"},
    "block_reroll": {"mindgame"},
    "force_rush": {"debuff", "mindgame"},
}


def _phase_tags(trigger: dict) -> set[str]:
    tags = set()
    phase_min = trigger.get("phase_min")
    phase_max = trigger.get("phase_max")
    if phase_min is not None and phase_max is not None:
        phase_min, phase_max = int(phase_min), int(phase_max)
        if phase_min <= 1 <= phase_max:
            tags.add("early_race")
        if phase_min <= 2 <= phase_max:
            tags.add("mid_race")
        if phase_min <= 3 <= phase_max or phase_min <= 4 <= phase_max:
            tags.add("late_race")
    elif trigger.get("turn_min") == 1:
        tags.add("early_race")
    if trigger.get("lastspurt"):
        tags.add("lastspurt")
    return tags


def _canonical_skill_tags(skill: dict) -> list[str]:
    trigger = skill.get("trigger", {})
    target = skill.get("target", {})
    tags = set()

    # Preserve only semantic hand-written tags; conditions below become the
    # single source of truth instead of aliases that can disagree with triggers.
    for raw_tag in skill.get("tags", []):
        tag = _TAG_ALIASES.get(str(raw_tag).lower(), str(raw_tag).lower())
        if tag not in _DERIVED_TAGS and tag != "rare":
            tags.add(tag)

    track = str(trigger.get("track", "")).lower()
    if track in {"turf", "dirt"}:
        tags.add(track)
    distance = str(trigger.get("distance_type", "")).lower()
    if distance in {"sprint", "mile", "medium", "long"}:
        tags.add(distance)
    style = str(trigger.get("style", "")).lower()
    if style in {"front", "pace", "late", "end"}:
        tags.add(style)

    tags.update(_phase_tags(trigger))
    path_tag = {1: "straight", 2: "corner", 3: "uphill", 4: "downhill"}.get(trigger.get("path_type"))
    if path_tag:
        tags.add(path_tag)
    if trigger.get("last_corner"):
        tags.update({"corner", "final_corner"})
    position_tag = {
        "front": "front_position",
        "middle": "middle_position",
        "back": "back_position",
    }.get(trigger.get("position_group"))
    if position_tag:
        tags.add(position_tag)
    if trigger.get("front_blocked"):
        tags.add("front_blocked")
    if trigger.get("nearby_uma_count"):
        tags.add("nearby_uma")
    if trigger.get("target_distance_min") is not None:
        if trigger["target_distance_min"] > 0:
            tags.add("target_ahead")
        elif trigger.get("target_distance_max", 0) < 0:
            tags.add("target_behind")

    scope = target.get("scope")
    if scope == "all_front":
        tags.add("target_all_front")
    elif scope == "all_back":
        tags.add("target_all_back")
    tags.update(_ICON_TAGS.get(skill.get("icon"), set()))
    if skill.get("activation") == "passive":
        tags.add("passive")
    for effect in skill.get("effects", []):
        tags.update(_EFFECT_TAGS.get(effect.get("type"), set()))
        condition = effect.get("condition") or {}
        condition_track = str(condition.get("track", "")).lower()
        if condition_track in {"turf", "dirt"}:
            tags.add(condition_track)
        condition_distance = str(condition.get("distance_type", "")).lower()
        if condition_distance in {"sprint", "mile", "medium", "long"}:
            tags.add(condition_distance)
        condition_style = str(condition.get("style", "")).lower()
        if condition_style in {"front", "pace", "late", "end"}:
            tags.add(condition_style)

    return sorted(tags, key=lambda tag: (_TAG_ORDER_INDEX.get(tag, len(_TAG_ORDER)), tag))


def _merge_catalogs(*catalogs: dict) -> dict:
    merged = {}
    for catalog in catalogs:
        duplicate_ids = merged.keys() & catalog.keys()
        if duplicate_ids:
            raise ValueError(f"Duplicate skill IDs: {sorted(duplicate_ids)}")
        merged.update({
            skill_id: {**skill, "tags": _canonical_skill_tags(skill)}
            for skill_id, skill in catalog.items()
        })
    return merged


SKILLS = _merge_catalogs(
    ACCELERATION_SKILLS,
    VELOCITY_SKILLS,
    PASSIVE_SKILLS,
    RECOVERY_SKILLS,
    UNIQUE_SKILLS,
    UTILITY_SKILLS,
    DEBUFF_SKILLS,
)
