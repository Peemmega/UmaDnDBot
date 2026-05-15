import os
from pathlib import Path
from typing import Any
import math

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

BG_PATH = ASSETS_DIR / "raceroom_temp.png"
RACE_THUMBNAIL_DIR = ASSETS_DIR / "race_thumnail"
FONT_BOLD_PATH = ASSETS_DIR / "fonts" / "Prompt-Bold.ttf"
FONT_REGULAR_PATH = ASSETS_DIR / "fonts" / "Prompt-Regular.ttf"
EMOJI_FONT_PATHS = [
    Path(os.environ["RACE_ROOM_EMOJI_FONT"]) if os.environ.get("RACE_ROOM_EMOJI_FONT") else None,
    Path("C:/Windows/Fonts/seguiemj.ttf"),
    Path("C:/Windows/Fonts/seguisym.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
]

W, H = 1240, 827

ICON_MAP = {
    "Speed": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_00.png",
    "Stamina": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_01.png",
    "Power": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_02.png",
    "Gut": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_03.png",
    "Wit": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_04.png",
}

PATH_TYPE_LABELS = {
    1: "straight",
    2: "curve",
    3: "uphill",
    4: "downhill",
}

PATH_TYPE_EMOJI = {
    1: "\u27a1",
    2: "\u2935",
    3: "\u2197",
    4: "\u2198",
}


def _font(size: int, *, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def _emoji_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in EMOJI_FONT_PATHS:
        if path and path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return _font(size)


def _resolve_path(value: str | Path | None, fallback: Path | None = None) -> Path | None:
    if not value:
        return fallback

    path = Path(value)
    if path.exists():
        return path

    asset_path = ASSETS_DIR / path
    if asset_path.exists():
        return asset_path

    base_path = BASE_DIR / path
    if base_path.exists():
        return base_path

    return fallback


def _resolve_race_thumbnail(stage: dict[str, Any]) -> Path | None:
    explicit = _resolve_path(stage.get("thumbnail"))
    if explicit:
        return explicit

    key = stage.get("thumbnail_key") or stage.get("race_key")
    if key:
        key_path = RACE_THUMBNAIL_DIR / str(key)
        if key_path.suffix:
            if key_path.exists():
                return key_path
        else:
            webp_path = key_path.with_suffix(".webp")
            if webp_path.exists():
                return webp_path

    name_key = "".join(ch for ch in str(stage.get("name", "")) if ch.isalnum())
    for thumbnail in RACE_THUMBNAIL_DIR.glob("*.webp"):
        stem_key = "".join(ch for ch in thumbnail.stem if ch.isalnum())
        if stem_key and stem_key in name_key:
            return thumbnail

    return None


def _load_image(
    value: str | Path | None,
    *,
    fallback: Path | None = None,
    size: tuple[int, int] | None = None,
    fill: tuple[int, int, int, int] = (255, 255, 255, 0),
) -> Image.Image:
    path = _resolve_path(value, fallback)
    if path and path.exists():
        img = Image.open(path).convert("RGBA")
    else:
        img = Image.new("RGBA", size or (320, 180), fill)

    if size:
        img = img.resize(size, Image.LANCZOS)
    return img


def draw_debug_grid(draw: ImageDraw.ImageDraw):
    for x in range(0, W + 1, 50):
        draw.line((x, 0, x, H), fill=(255, 0, 0, 90), width=1)
        draw.text((x + 2, 2), str(x), fill=(255, 0, 0), font=_font(12))

    for y in range(0, H + 1, 50):
        draw.line((0, y, W, y), fill=(0, 0, 255, 90), width=1)
        draw.text((2, y + 2), str(y), fill=(0, 0, 255), font=_font(12))


def _normalize_path_type(value: Any) -> int:
    try:
        path_type = int(value)
        if path_type in PATH_TYPE_LABELS:
            return path_type
    except (TypeError, ValueError):
        pass

    text = str(value).strip().lower()
    try:
        text = text.encode("cp1252").decode("utf-8").strip().lower()
    except UnicodeError:
        pass

    if text in {"1", "straight", "right", "arrow", "->", "→", "➡", "➡️"}:
        return 1
    if text in {"2", "curve", "corner", "turn", "↩", "⤵", "⤵️"}:
        return 2
    if text in {"3", "uphill", "up", "↗", "↗️"}:
        return 3
    if text in {"4", "downhill", "down", "↘", "↘️"}:
        return 4

    return 1


def _draw_arrow_head(
    draw: ImageDraw.ImageDraw,
    tip: tuple[int, int],
    angle_degrees: float,
    *,
    size: int = 9,
    fill: tuple[int, int, int] = (255, 255, 255),
):
    angle = math.radians(angle_degrees)
    left = angle + math.radians(150)
    right = angle - math.radians(150)
    points = [
        tip,
        (int(tip[0] + math.cos(left) * size), int(tip[1] + math.sin(left) * size)),
        (int(tip[0] + math.cos(right) * size), int(tip[1] + math.sin(right) * size)),
    ]
    draw.polygon(points, fill=fill)


def _draw_path_symbol(draw: ImageDraw.ImageDraw, path_type: int, box: tuple[int, int, int, int]):
    left, top, right, bottom = box
    cx = (left + right) // 2
    cy = (top + bottom) // 2
    color = (255, 255, 255)
    width = 5

    if path_type == 2:
        mid_y = top + 12
        end = (right - 10, bottom - 9)
        draw.line((left + 10, mid_y, right - 14, mid_y), fill=color, width=width)
        draw.line((right - 14, mid_y, right - 14, bottom - 14), fill=color, width=width)
        _draw_arrow_head(draw, end, 90, size=8, fill=color)
        return

    if path_type == 3:
        start = (left + 9, bottom - 9)
        end = (right - 9, top + 9)
        angle = -45
    elif path_type == 4:
        start = (left + 9, top + 9)
        end = (right - 9, bottom - 9)
        angle = 45
    else:
        start = (left + 8, cy)
        end = (right - 8, cy)
        angle = 0

    draw.line((start, end), fill=color, width=width)
    _draw_arrow_head(draw, end, angle, size=8, fill=color)


def _draw_path_icons(draw: ImageDraw.ImageDraw, icons: list[Any], start: tuple[int, int]):
    x, y = start
    start_x = x
    max_x = 1110
    row_gap = 42

    for icon in icons:
        size = 36
        if x + size > max_x:
            x = start_x
            y += row_gap

        box = (x, y, x + size, y + size)
        draw.rounded_rectangle(box, radius=5, fill=(79, 155, 190, 235))
        _draw_path_symbol(draw, _normalize_path_type(icon), box)
        x += 42


def _title_value(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text[:1].upper() + text[1:] if text else fallback


def _build_aptitude_bonus(stage: dict[str, Any]) -> list[dict[str, str]]:
    bonuses = stage.get("aptitude_bonus")
    if bonuses:
        return list(bonuses)

    return [
        {
            "label": _title_value(stage.get("track"), "Track"),
            "value": "+1",
            "icon": "Power",
        },
        {
            "label": _title_value(stage.get("distance"), "Distance"),
            "value": "+1",
            "icon": "Speed",
        },
        {
            "label": "Your Style",
            "value": "+1",
            "icon": "Wit",
        },
    ]


def _draw_bonus_rows(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    bonuses: list[dict[str, Any]],
    start_y: int,
):
    font = _font(26)
    y = start_y

    for bonus in bonuses:
        label = str(bonus.get("label", ""))
        value = str(bonus.get("value", ""))
        icon_name = str(bonus.get("icon", ""))

        draw.text((150, y), f"{label} {value}".strip(), font=font, fill=(45, 45, 45))

        icon_path = ICON_MAP.get(icon_name)
        if icon_path and icon_path.exists():
            icon_img = Image.open(icon_path).convert("RGBA").resize((34, 34), Image.LANCZOS)
            canvas.alpha_composite(icon_img, (345, y + 1))

        y += 38

def create_racing_room_image(stage: dict[str, Any], *, debug: bool = False) -> Image.Image:
    bg = _load_image(stage.get("background"), fallback=BG_PATH, size=(W, H), fill=(235, 246, 230, 255))
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    canvas.alpha_composite(bg)
    draw = ImageDraw.Draw(canvas)

    path_icons = list(stage.get("path") or stage.get("path_icons", []))

    draw.text(
        (133, 200),
        str(stage.get("name", "Unknown Race")),
        font=_font(32),
        fill=(150, 55, 5),
    )

    thumb = _load_image(_resolve_race_thumbnail(stage), fallback=stage.get("background") or BG_PATH, size=(170, 86))
    canvas.alpha_composite(thumb, (938, 143))

    draw.text((395, 266), str(stage.get("turns", "-")), font=_font(28), fill=(40, 40, 40), anchor="ra")

    _draw_path_icons(draw, path_icons, (150, 330))
    _draw_bonus_rows(canvas, draw, _build_aptitude_bonus(stage), 450)

    track_path = _resolve_path(stage.get("track_image"))
    if track_path:
        track = Image.open(track_path).convert("RGBA")
        track.thumbnail((540, 360), Image.LANCZOS)
        canvas.alpha_composite(track, (620, 350))
   
    if debug:
        draw_debug_grid(draw)

    return canvas.convert("RGB")
