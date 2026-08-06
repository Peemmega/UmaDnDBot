from pathlib import Path
from io import BytesIO
import os
import math
from PIL import Image, ImageDraw, ImageFont
from utils.race.wit import build_single_wit_regen_text
from utils.race.runtime_stamina import format_runtime_stamina
from utils.race.result_display import format_bonus_display, format_stamina_line
import aiohttp
import re
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

BG_PATH = ASSETS_DIR / "race_dice_preview_bg.png"
FONT_PATH = ASSETS_DIR / "fonts" / "Prompt-Bold.ttf"

ICON_MAP = {
    "Speed": ASSETS_DIR / "stats_icon/utx_ico_obtain_00.png",
    "Stamina": ASSETS_DIR / "stats_icon/utx_ico_obtain_01.png",
    "Power": ASSETS_DIR / "stats_icon/utx_ico_obtain_02.png",
    "Gut": ASSETS_DIR / "stats_icon/utx_ico_obtain_03.png",
    "Velocity": ASSETS_DIR / "skill_icons/Velocity.png",
    "Navigation": ASSETS_DIR / "skill_icons/Navigation.png",
    "Block": ASSETS_DIR / "icons" / "block_icon.png",
}

DEFAULT_IMAGE = BASE_DIR / "assets" / "characters" / "mob_01.png"
_REMOTE_IMAGE_CACHE: dict[str, Image.Image] = {}


@lru_cache(maxsize=64)
def _load_local_rgba(path: str, modified_at_ns: int = 0) -> Image.Image:
    return Image.open(path).convert("RGBA")


@lru_cache(maxsize=8)
def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except OSError:
        return ImageFont.load_default()

async def load_image_url(path_or_url):
    try:
        if not path_or_url:
            raise ValueError("empty image path")

        path_or_url = str(path_or_url)
        cached = _REMOTE_IMAGE_CACHE.get(path_or_url)
        if cached is not None:
            return cached.copy()

        # Local profile uploads keep a stable filename and are overwritten on
        # update.  Include the file modification time in the cache key so a
        # newly uploaded profile is rendered immediately without restarting.
        local_path = Path(path_or_url)
        if local_path.exists():
            stat = local_path.stat()
            cache_key = f"{local_path.resolve()}:{stat.st_mtime_ns}"
            cached = _REMOTE_IMAGE_CACHE.get(cache_key)
            if cached is not None:
                return cached.copy()

            image = _load_local_rgba(str(local_path.resolve()), stat.st_mtime_ns)
            _REMOTE_IMAGE_CACHE[cache_key] = image
            return image.copy()

        # URL
        if path_or_url.startswith(("http://", "https://")):
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(path_or_url) as resp:
                    if resp.status != 200:
                        raise ValueError(f"HTTP {resp.status}")

                    data = await resp.read()
                    image = Image.open(BytesIO(data)).convert("RGBA")
                    _REMOTE_IMAGE_CACHE[path_or_url] = image
                    return image.copy()

        raise ValueError(f"invalid image path: {path_or_url}")

    except Exception as e:
        if DEFAULT_IMAGE.exists():
            return _load_local_rgba(str(DEFAULT_IMAGE.resolve())).copy()

        # fallback สุดท้าย: สร้างรูปโปร่งใส กัน crash
        return Image.new("RGBA", (512, 512), (0, 0, 0, 0))

def draw_text_with_underline(draw, xy, text, font, fill, underline_offset=5, thickness=3):
    x, y = xy

    # วาดข้อความ
    draw.text((x, y), text, font=font, fill=fill)

    # วัดขนาดข้อความ
    bbox = draw.textbbox((x, y), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # วาดเส้นใต้
    underline_y = y + text_height + underline_offset

    draw.line(
        (x, underline_y, x + text_width, underline_y),
        fill=fill,
        width=thickness
    )

def crop_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    img = img.convert("RGBA")
    tw, th = size
    sw, sh = img.size

    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)

    img = img.resize((nw, nh), Image.LANCZOS)

    left = (nw - tw) // 2
    top = (nh - th) // 2

    return img.crop((left, top, left + tw, top + th))


def draw_text_outline(draw, xy, text, font, fill, outline=(255, 255, 255), width=3, anchor="la"):
    x, y = xy
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def paste_icon(card: Image.Image, path: Path, pos, size):
    icon = _load_local_rgba(str(path.resolve())).resize(size, Image.LANCZOS)
    card.paste(icon, pos, icon)

def draw_debug_grid(draw):
    for x in range(0, 1500, 50):
        draw.line((x, 0, x, 800), fill=(255, 0, 0, 90), width=1)
        draw.text((x + 2, 2), str(x), fill=(255, 0, 0))

    for y in range(0, 800, 50):
        draw.line((0, y, 1500, y), fill=(0, 0, 255, 90), width=1)
        draw.text((2, y + 2), str(y), fill=(0, 0, 255))



def parse_display_text(text: str):
    tokens = []

    # split ด้วย __ __ และ emoji
    pattern = r"(__.*?__|<:.*?:\d+>|Speed|Power|Gut|Velocity|Navigation|Stamina|Block)"
    parts = re.split(pattern, text)

    for part in parts:
        if not part:
            continue

        # underline
        if part.startswith("__") and part.endswith("__"):
            tokens.append(("underline", part[2:-2]))

        # discord emoji
        elif part.startswith("<:"):
            name = part.split(":")[1]
            tokens.append(("icon", name))

        elif part in ICON_MAP:
            tokens.append(("icon", part))

        else:
            tokens.append(("text", part))

    return tokens

def draw_rich_text(card, draw, base_pos, tokens, font, color):
    x, y = base_pos

    for t_type, value in tokens:
        if t_type == "text":
            draw.text((x, y), value, font=font, fill=color)
            bbox = draw.textbbox((x, y), value, font=font)
            x += bbox[2] - bbox[0]

        elif t_type == "underline":
            draw.text((x, y), value, font=font, fill=color)

            bbox = draw.textbbox((x, y), value, font=font)
            w = bbox[2] - bbox[0]

            draw.line(
                (x, y + 50, x + w, y + 50),
                fill=color,
                width=4
            )
            x += w

        elif t_type == "icon":
            icon_path = ICON_MAP.get(value)

            if icon_path and icon_path.exists():
                icon = Image.open(icon_path).convert("RGBA").resize((42, 42), Image.LANCZOS)
                card.paste(icon, (x + 4, y + 6), icon)
                x += 52
            else:
                fallback = value
                draw.text((x, y), fallback, font=font, fill=color)
                bbox = draw.textbbox((x, y), fallback, font=font)
                x += bbox[2] - bbox[0]

async def create_race_dice_preview(
    *,
    game_player: dict,
    result: dict,
    payload: dict,
    path_label: str,
    character_image_url: str,
):
    card = _load_local_rgba(str(BG_PATH.resolve())).copy()
    draw = ImageDraw.Draw(card)

    font_big = _font(58)
    font_mid = _font(42)
    font_small = _font(30)
    font_score = _font(92)

    brown = (112, 70, 35)
    green = (105, 178, 45)
    white = (255, 255, 255)

    # ===== left character image =====
    LEFT_POS = (0, 0)
    LEFT_SIZE = (480, 500)

    char_img = await load_image_url(character_image_url)
    char_img = crop_cover(char_img, LEFT_SIZE)
    card.paste(char_img, LEFT_POS, char_img)

    # ===== left text =====
    phase = result.get("phase", "?")
    turn = result.get("turn", "?")
    distance_color = "อยู่ในกลุ่ม" if result.get("distance_color", "White") == "Gold" else "อยู่นอกกลุ่ม"
    style = game_player.get("style", "-")

    draw_text_outline(
        draw,
        (90, 20),
        f"{phase}",
        font_score,
        fill=(255, 205, 80),
        outline=(80, 45, 20),
        width=4,
        anchor="ra",
    )

    draw_text_outline(
        draw,
        (100, 85),
        f"/{turn}",
        font_mid,
        fill=white,
        outline=(80, 45, 20),
        width=4,
    )

    draw_text_outline(
        draw,
        (30, 400),
        style,
        font_big,
        fill=white,
        outline=(80, 45, 20),
        width=4,
    )

    draw_text_outline(
        draw,
        (345, 370),
        "คะแนน",
        font_small,
        fill=white,
        outline=(80, 45, 20),
        width=3,
    )

    newscore = payload["new_score"]
    draw_text_outline(
        draw,
        (435, 405),
        str(newscore),
        font_big,
        fill=white,
        outline=(80, 45, 20),
        width=4,
        anchor="ra",
    )

    # ===== right content =====
    current_speed = math.floor(game_player.get("current_max_speed", 0))

    draw.text(
        (520, 30),
        f"ความเร็วปัจจุบัน {current_speed}",
        font=font_big,
        fill=green,
    )

    total = result.get("total", 0)
    draw.text(
        (1325, 18),
        str(total),
        font=font_score,
        fill=brown,
        anchor="ra",
    )

    current_lane = int(game_player.get("current_lane", game_player.get("entry_number", 1)) or 1)
    draw.text(
        (520, 100),
        f"{path_label} / {distance_color} / lane {current_lane}",
        font=font_mid,
        fill=brown,
    )

    # dice breakdown
    display = result.get("display", "")
    bonus = format_bonus_display(result.get("bonus_display", ""), block_label="Block")


    draw_rich_text(
        card,
        draw,
        (520, 160),
        parse_display_text(display),
        font_mid,
        brown
    )

    draw_rich_text(
        card,
        draw,
        (520, 225),
        parse_display_text(bonus),
        font_mid,
        brown
    )

    # stamina
    current_stamina = int(game_player.get("stamina_left", 0) or 0)
    stamina_drain = int(game_player.get("last_stamina_drain", 0) or 0)
    sta_text = f"{current_stamina} (-{stamina_drain})" if stamina_drain > 0 else str(current_stamina)
    sta_text = format_stamina_line(
        sta_text,
        drafting_active=bool(result.get("drafting_active", game_player.get("drafting_active", False))),
    )
    draw.text((595, 340), sta_text, font=font_mid, fill=brown)

    # wit mana
    wit_text = build_single_wit_regen_text(game_player)

    draw.text((595, 415), f"{wit_text} pt.", font=font_mid, fill=brown)

    # reroll
    draw.text((1130, 400), str(game_player.get("reroll_left", 0)), font=font_mid, fill=brown)
    draw.text((1245, 400), str(game_player.get("wit_reroll_left", 0)), font=font_mid, fill=brown)

    # draw_debug_grid(draw)

    return card
