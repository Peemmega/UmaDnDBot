"""Skill catalogs grouped by gameplay type."""

from .acceleration import ACCELERATION_SKILLS
from .velocity import VELOCITY_SKILLS
from .passive import PASSIVE_SKILLS
from .recovery import RECOVERY_SKILLS
from .unique import UNIQUE_SKILLS
from .utility import UTILITY_SKILLS
from .debuff import DEBUFF_SKILLS


def _merge_catalogs(*catalogs: dict) -> dict:
    merged = {}
    for catalog in catalogs:
        duplicate_ids = merged.keys() & catalog.keys()
        if duplicate_ids:
            raise ValueError(f"Duplicate skill IDs: {sorted(duplicate_ids)}")
        merged.update(catalog)
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
