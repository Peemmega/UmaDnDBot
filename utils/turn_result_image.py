from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path
import re
from typing import Any

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

from utils.profile_images import is_local_filesystem_path, resolve_player_render_image
from utils.race.race_presets import PATH_TYPE_TEXT, build_path_effect_text, get_current_path_type
from utils.race.rank_display import is_in_gold_range


BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATE_PATH = ASSETS_DIR / "turn_result_temp.png"
FONT_BOLD_PATH = ASSETS_DIR / "fonts" / "Prompt-Bold.ttf"
FONT_REGULAR_PATH = ASSETS_DIR / "fonts" / "Prompt-Regular.ttf"
ICON_MAP = {
    "SPD": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_00.png",
    "STA": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_01.png",
    "POW": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_02.png",
    "GUT": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_03.png",
    "WIT": ASSETS_DIR / "stats_icon" / "utx_ico_obtain_04.png",
}

LANE_Y = {
    1: 244,
    2: 356,
    3: 468,
    4: 580,
    5: 692,
    6: 804,
}

TRACK_LEFT = 142
TRACK_RIGHT = 954
AVATAR_SIZE = 72
AVATAR_RADIUS = AVATAR_SIZE // 2
AVATAR_BORDER = 4
RIGHT_PANEL_X = 1120
RIGHT_PANEL_Y = 148
RIGHT_PANEL_WIDTH = 585
RIGHT_PANEL_BOTTOM = 860
NAME_MAX_WIDTH = 410
EFFECT_BOX_TOP = 690
EFFECT_BOX_BOTTOM = 875
YELLOW = (255, 210, 34, 255)
WHITE = (255, 255, 255, 255)
BLACK = (28, 28, 28, 255)
GREEN = (91, 183, 0, 255)
CUSTOM_EMOJI_RE = re.compile(r"<a?:([A-Za-z0-9_]+):\d+>")
EFFECT_TOKEN_RE = re.compile(r"(STA|SPD|POW|GUT|WIT)")
DEFAULT_AVATAR = ASSETS_DIR / "characters" / "mob_01.png"


def _font(size: int, *, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONT_BOLD_PATH if bold else FONT_REGULAR_PATH
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


async def _load_avatar_image(source: str, size: tuple[int, int]) -> Image.Image:
    image = None

    try:
        source_text = str(source or "").strip()
        local_path = Path(source_text.replace("file://", "")) if source_text else None

        if local_path and local_path.exists():
            image = Image.open(local_path).convert("RGBA")
        elif is_local_filesystem_path(source_text):
            image = None
        elif source_text:
            async with aiohttp.ClientSession() as session:
                async with session.get(source_text) as response:
                    response.raise_for_status()
                    data = await response.read()
            image = Image.open(BytesIO(data)).convert("RGBA")
    except (OSError, aiohttp.ClientError, UnidentifiedImageError, ValueError):
        image = None

    if image is None:
        if DEFAULT_AVATAR.exists():
            image = Image.open(DEFAULT_AVATAR).convert("RGBA")
        else:
            image = Image.new("RGBA", size, (190, 190, 190, 255))

    return ImageOps.fit(image, size, Image.LANCZOS)


def _circular_avatar(base_avatar: Image.Image, *, border_color: tuple[int, int, int, int]) -> Image.Image:
    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, AVATAR_SIZE - 1, AVATAR_SIZE - 1), fill=255)

    avatar = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (0, 0, 0, 0))
    avatar.paste(base_avatar, (0, 0), mask)

    framed = Image.new("RGBA", (AVATAR_SIZE + AVATAR_BORDER * 2, AVATAR_SIZE + AVATAR_BORDER * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(framed)
    draw.ellipse(
        (0, 0, framed.width - 1, framed.height - 1),
        fill=(255, 255, 255, 255),
        outline=border_color,
        width=AVATAR_BORDER,
    )
    framed.paste(avatar, (AVATAR_BORDER, AVATAR_BORDER), avatar)
    return framed


def _fit_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text

    clipped = text
    while clipped:
        candidate = clipped[:-1].rstrip() + "..."
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            return candidate
        clipped = clipped[:-1]
    return "..."


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = str(text or "").split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _parse_effect_tokens(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    for part in EFFECT_TOKEN_RE.split(str(text or "")):
        if not part:
            continue
        if part in ICON_MAP:
            tokens.append(("icon", part))
        else:
            tokens.append(("text", part))
    return tokens


def _token_width(draw: ImageDraw.ImageDraw, token: tuple[str, str], font, icon_size: int) -> int:
    token_type, value = token
    if token_type == "icon":
        return icon_size + 8
    return draw.textbbox((0, 0), value, font=font)[2]


def _wrap_effect_tokens(draw: ImageDraw.ImageDraw, tokens: list[tuple[str, str]], font, max_width: int, icon_size: int) -> list[list[tuple[str, str]]]:
    lines: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    current_width = 0
    for token in tokens:
        width = _token_width(draw, token, font, icon_size)
        if current and current_width + width > max_width:
            lines.append(current)
            current = [token]
            current_width = width
            continue
        current.append(token)
        current_width += width
    if current:
        lines.append(current)
    return lines


def _paste_icon(canvas: Image.Image, icon_key: str, pos: tuple[int, int], size: int) -> int:
    icon_path = ICON_MAP.get(icon_key)
    if not icon_path or not icon_path.exists():
        return 0
    icon = Image.open(icon_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    canvas.alpha_composite(icon, pos)
    return icon.width


def _draw_effect_token_line(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    tokens: list[tuple[str, str]],
    font,
    fill: tuple[int, int, int, int],
    *,
    icon_size: int = 24,
) -> None:
    x, y = pos
    for token_type, value in tokens:
        if token_type == "icon":
            drawn = _paste_icon(canvas, value, (x, y + 2), icon_size)
            if drawn:
                x += drawn + 8
                continue
        draw.text(
            (x, y),
            value,
            font=font,
            fill=fill,
            stroke_width=2,
            stroke_fill=GREEN,
        )
        x += draw.textbbox((x, y), value, font=font, stroke_width=2)[2] - x


def _sanitize_effect_text(text: str) -> str:
    cleaned = CUSTOM_EMOJI_RE.sub(lambda match: match.group(1).upper(), str(text or ""))
    replacements = {
        "STAMINA": "STA",
        "SPEED": "SPD",
        "POWER": "POW",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    return cleaned


def _build_scoreboard_rows(ranked_players: list[tuple[Any, dict]]) -> list[dict[str, Any]]:
    rows = []
    for index, (user_id, info) in enumerate(ranked_players, start=1):
        name = (
            info.get("display_name")
            or info.get("username")
            or info.get("name")
            or str(user_id)
        )
        rows.append({
            "rank": index,
            "user_id": user_id,
            "name": str(name),
            "style": str(info.get("style") or "-"),
            "score": int(info.get("score", 0) or 0),
            "lane": max(1, min(6, int(info.get("current_lane", info.get("entry_number", 1)) or 1))),
            "gold": is_in_gold_range(user_id, info, ranked_players),
            "info": info,
        })
    return rows


def _position_x(score: int, min_score: int, max_score: int) -> int:
    if max_score <= min_score:
        return (TRACK_LEFT + TRACK_RIGHT) // 2

    ratio = (score - min_score) / float(max_score - min_score)
    return int(round(TRACK_LEFT + (TRACK_RIGHT - TRACK_LEFT) * ratio))


def _apply_lane_offsets(rows: list[dict[str, Any]]) -> None:
    lane_groups: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        lane_groups.setdefault(row["lane"], []).append(row)

    cluster_offsets = {
        1: [(0, 0)],
        2: [(-10, -10), (10, 10)],
        3: [(0, 0), (-14, -12), (14, 12)],
        4: [(-10, -10), (10, 10), (-22, -20), (22, 20)],
        5: [(0, 0), (-12, -10), (12, 10), (-24, -20), (24, 20)],
        6: [(-8, -8), (8, 8), (-20, -16), (20, 16), (-30, -24), (30, 24)],
    }
    for lane_rows in lane_groups.values():
        lane_rows.sort(key=lambda item: item["track_x"])
        cluster: list[dict[str, Any]] = []

        def flush_cluster() -> None:
            offsets = cluster_offsets.get(len(cluster), cluster_offsets[6])
            for idx, item in enumerate(cluster):
                x_offset, y_offset = offsets[idx] if idx < len(offsets) else offsets[-1]
                item["track_offset_x"] = x_offset
                item["lane_offset"] = y_offset

        for item in lane_rows:
            if not cluster:
                cluster = [item]
                continue

            if item["track_x"] - cluster[-1]["track_x"] <= AVATAR_SIZE + 10:
                cluster.append(item)
                continue

            flush_cluster()
            cluster = [item]

        if cluster:
            flush_cluster()


async def create_turn_result_card(game: dict, ranked_players: list[tuple[Any, dict]]) -> Image.Image:
    canvas = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    rows = _build_scoreboard_rows(ranked_players)
    if not rows:
        return canvas

    scores = [row["score"] for row in rows]
    min_score = min(scores)
    max_score = max(scores)

    for row in rows:
        row["track_x"] = _position_x(row["score"], min_score, max_score)
        row["lane_y"] = LANE_Y.get(row["lane"], LANE_Y[6])
        row["track_offset_x"] = 0
        row["lane_offset"] = 0

    _apply_lane_offsets(rows)

    avatar_sources = [
        resolve_player_render_image(row["info"], row["info"].get("avatar", ""))
        for row in rows
    ]
    avatars = await asyncio.gather(*[
        _load_avatar_image(source, (AVATAR_SIZE, AVATAR_SIZE))
        for source in avatar_sources
    ])

    for row, avatar in zip(rows, avatars):
        border_color = YELLOW if row["gold"] else BLACK
        framed = _circular_avatar(avatar, border_color=border_color)
        paste_x = row["track_x"] - framed.width // 2 + int(row["track_offset_x"])
        paste_y = row["lane_y"] - framed.height // 2 + int(row["lane_offset"])
        canvas.paste(framed, (paste_x, paste_y), framed)

    row_count = len(rows)
    available_height = RIGHT_PANEL_BOTTOM - RIGHT_PANEL_Y
    line_height = max(17, min(28, available_height // max(1, row_count)))
    font_size = max(16, min(27, line_height + 2))
    font = _font(font_size, bold=True)
    score_font = _font(font_size, bold=False)

    for idx, row in enumerate(rows):
        y = RIGHT_PANEL_Y + idx * line_height
        if y + line_height > RIGHT_PANEL_BOTTOM:
            break

        text_color = YELLOW if row["gold"] else WHITE
        rank_text = f"{row['rank']}."
        draw.text(
            (RIGHT_PANEL_X, y),
            rank_text,
            font=font,
            fill=text_color,
            stroke_width=2,
            stroke_fill=GREEN,
        )

        rank_box = draw.textbbox((RIGHT_PANEL_X, y), rank_text, font=font, stroke_width=2)
        label = _fit_text(draw, f"{row['name']} | {row['style']}", font, NAME_MAX_WIDTH)
        draw.text(
            (rank_box[2] + 10, y),
            label,
            font=font,
            fill=text_color,
            stroke_width=2,
            stroke_fill=GREEN,
        )

        score_text = str(row["score"])
        draw.text(
            (RIGHT_PANEL_X + RIGHT_PANEL_WIDTH, y),
            score_text,
            font=score_font,
            fill=text_color,
            anchor="ra",
            stroke_width=2,
            stroke_fill=GREEN,
        )

    if game and game.get("path"):
        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "-")
        effect_title_font = _font(30, bold=True)
        effect_body_font = _font(24, bold=True)
        effect_small_font = _font(21, bold=False)

        draw.text(
            (RIGHT_PANEL_X, EFFECT_BOX_TOP),
            "Effect Turn",
            font=effect_small_font,
            fill=(220, 255, 185, 255),
        )
        draw.text(
            (RIGHT_PANEL_X, EFFECT_BOX_TOP + 24),
            path_label,
            font=effect_title_font,
            fill=WHITE,
            stroke_width=2,
            stroke_fill=GREEN,
        )

        effect_text = _sanitize_effect_text(build_path_effect_text(path_type))
        effect_lines = [segment.strip() for segment in effect_text.split("•") if segment.strip()]
        text_y = EFFECT_BOX_TOP + 68
        for segment in effect_lines:
            tokens = _parse_effect_tokens(segment)
            wrapped_token_lines = _wrap_effect_tokens(draw, tokens, effect_body_font, RIGHT_PANEL_WIDTH - 10, 24)
            for token_line in wrapped_token_lines:
                if text_y + 26 > EFFECT_BOX_BOTTOM:
                    break
                _draw_effect_token_line(
                    canvas,
                    draw,
                    (RIGHT_PANEL_X, text_y),
                    token_line,
                    effect_body_font,
                    (244, 247, 221, 255),
                    icon_size=24,
                )
                text_y += 30
            if text_y + 26 > EFFECT_BOX_BOTTOM:
                break

    return canvas
