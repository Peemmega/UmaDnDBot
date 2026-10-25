"""Resolve Discord profile-card identity from the account's active role."""

from utils.storage.database import get_account_role, get_player, get_profile_preset


def get_profile_identity(user_id: int | str, fallback_name: str = "") -> dict:
    role = get_account_role(str(user_id)) or "trainee"

    if role in {"trainer", "npc"}:
        profile = get_profile_preset(str(user_id), role)
        if profile:
            return {
                "profile_type": role,
                "username": profile["name"],
                "profile_image_url": profile["image_url"],
            }
        return {
            "profile_type": role,
            "username": fallback_name or role.title(),
            "profile_image_url": "",
        }

    player = get_player(user_id)
    if player:
        return {
            "profile_type": "trainee",
            "username": player.get("username") or fallback_name or "Trainee",
            "profile_image_url": player.get("profile_image_url") or "",
        }

    return {
        "profile_type": "trainee",
        "username": fallback_name or "Trainee",
        "profile_image_url": "",
    }
