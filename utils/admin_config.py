"""Bot-wide admin rights, shared by cogs, views and the web API.

A user is an admin when their Discord user ID is in ADMIN_IDS, or when they
hold one of the Discord admin roles in ADMIN_ROLE_IDS (the same roles the
admin-data page accepts, plus ADMIN_ROLE_ID from the environment).
Admins override every room / booking rule.
"""

import os
import time

ADMIN_IDS = {
    464058883556769793,
}

ADMIN_ROLE_IDS = {
    1526245809459298417,
    1494752623683834038,
}
_env_role = os.getenv("ADMIN_ROLE_ID", "").strip()
if _env_role.isdigit():
    ADMIN_ROLE_IDS.add(int(_env_role))

# user_id -> (has_admin_role, checked_at). Filled whenever we see a member's
# roles (Discord interactions or an explicit fetch from the web API).
_ROLE_CACHE: dict[int, tuple[bool, float]] = {}
ROLE_CACHE_TTL = 300


def remember_admin_role(user_id, has_role: bool) -> None:
    try:
        _ROLE_CACHE[int(user_id)] = (bool(has_role), time.monotonic())
    except (TypeError, ValueError):
        pass


def cached_admin_role(user_id) -> bool | None:
    """True/False if we checked this user's roles recently, None if unknown."""
    try:
        entry = _ROLE_CACHE.get(int(user_id))
    except (TypeError, ValueError):
        return None
    if entry is None or time.monotonic() - entry[1] > ROLE_CACHE_TTL:
        return None
    return entry[0]


def has_admin_role(member) -> bool:
    """Check a discord.Member's roles directly (and refresh the cache)."""
    roles = getattr(member, "roles", None)
    if roles is None:
        return False
    result = any(getattr(role, "id", None) in ADMIN_ROLE_IDS for role in roles)
    remember_admin_role(getattr(member, "id", None), result)
    return result


def is_bot_admin(user_id) -> bool:
    """Admin by user ID, or by an admin role seen recently for this user."""
    try:
        if int(user_id) in ADMIN_IDS:
            return True
    except (TypeError, ValueError):
        return False
    return bool(cached_admin_role(user_id))


def is_admin_member(member) -> bool:
    """Admin check for a Discord member/user object from an interaction or ctx."""
    if member is None:
        return False
    return is_bot_admin(getattr(member, "id", None)) or has_admin_role(member)
