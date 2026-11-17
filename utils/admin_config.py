"""Discord user IDs with bot-wide admin rights (shared by cogs and the web API)."""

ADMIN_IDS = {
    464058883556769793,
}


def is_bot_admin(user_id) -> bool:
    try:
        return int(user_id) in ADMIN_IDS
    except (TypeError, ValueError):
        return False
