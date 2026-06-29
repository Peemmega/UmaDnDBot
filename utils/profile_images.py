from __future__ import annotations

import os
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PUBLIC_BASE_URL = "https://umadndbot-production.up.railway.app"
ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}
MAX_PROFILE_IMAGE_BYTES = 2 * 1024 * 1024
PROFILE_IMAGE_SIZE = (256, 256)
USER_ID_PATTERN = re.compile(r"^\d+$")


def get_public_base_url() -> str:
    explicit_base_url = (os.getenv("PUBLIC_BASE_URL") or "").strip()
    if explicit_base_url:
        return explicit_base_url.rstrip("/")

    railway_public_domain = (os.getenv("RAILWAY_PUBLIC_DOMAIN") or "").strip()
    if railway_public_domain:
        return f"https://{railway_public_domain}".rstrip("/")

    railway_static_url = (os.getenv("RAILWAY_STATIC_URL") or "").strip()
    if railway_static_url:
        return railway_static_url.rstrip("/")

    return DEFAULT_PUBLIC_BASE_URL.rstrip("/")


def get_upload_root_dir() -> Path:
    upload_dir = (os.getenv("UPLOAD_DIR") or "").strip()
    if upload_dir:
        return Path(upload_dir)

    player_db_path = (os.getenv("PLAYER_DB_PATH") or "").strip()
    if player_db_path:
        return Path(player_db_path).parent / "uploads"

    return BASE_DIR / "static" / "uploads"


def get_profile_uploads_dir() -> Path:
    return get_upload_root_dir() / "profiles"


def ensure_upload_dirs() -> None:
    get_profile_uploads_dir().mkdir(parents=True, exist_ok=True)


def sanitize_numeric_user_id(user_id: str | int) -> str:
    safe_user_id = str(user_id).strip()
    if not USER_ID_PATTERN.fullmatch(safe_user_id):
        raise ValueError("Invalid user_id")
    return safe_user_id


def build_profile_image_relative_url(user_id: str | int, updated_at: int | str | None) -> str:
    safe_user_id = sanitize_numeric_user_id(user_id)
    url = f"/uploads/profiles/{safe_user_id}.webp"
    if updated_at is None or str(updated_at).strip() == "":
        return url
    return f"{url}?v={updated_at}"


def is_absolute_url(value: str | None) -> bool:
    text = str(value or "").strip().lower()
    return text.startswith("http://") or text.startswith("https://")


def resolve_public_url(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if is_absolute_url(text):
        return text
    if text.startswith("/"):
        return f"{get_public_base_url()}{text}"
    return f"{get_public_base_url()}/{text.lstrip('/')}"


def is_local_filesystem_path(value: str | None) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    return bool(
        re.match(r"^[A-Za-z]:[\\/]", text)
        or text.startswith("\\\\")
        or text.startswith("file://")
    )


def resolve_player_avatar_url(player: dict | None, fallback: str = "") -> str:
    player = player or {}
    profile_image_url = resolve_public_url(player.get("profile_image_url"))
    if profile_image_url:
        return profile_image_url

    raw_avatar = player.get("avatar")
    avatar = "" if is_local_filesystem_path(raw_avatar) else resolve_public_url(raw_avatar)
    if avatar:
        return avatar

    thumbnail = resolve_public_url(player.get("thumnail") or player.get("thumbnail"))
    if thumbnail:
        return thumbnail

    return resolve_public_url(fallback)


def resolve_player_render_image(player: dict | None, fallback: str = "") -> str:
    player = player or {}

    profile_image_url = resolve_public_url(player.get("profile_image_url"))
    if profile_image_url:
        return profile_image_url

    raw_avatar = player.get("avatar")
    if is_local_filesystem_path(raw_avatar):
        return str(raw_avatar).strip()

    avatar = resolve_public_url(raw_avatar)
    if avatar:
        return avatar

    thumbnail = resolve_public_url(player.get("thumnail") or player.get("thumbnail"))
    if thumbnail:
        return thumbnail

    if is_local_filesystem_path(fallback):
        return str(fallback).strip()

    return resolve_public_url(fallback)

