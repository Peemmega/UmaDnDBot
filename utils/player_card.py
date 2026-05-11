from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import aiohttp

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATE_PATH = ASSETS_DIR / "umaCard_temp.png"
GRADES_DIR = ASSETS_DIR / "grades"
FONT_PATH = ASSETS_DIR / "fonts" / "ArialBold.ttf"
FRAME_PATH = ASSETS_DIR / "ImageFrame.png"
FRAME_Item = ASSETS_DIR / "utx_btn_s_00_sl.png"
SKILL_POINT_ICON = ASSETS_DIR / "skillPoint.png"
STATS_POINT_ICON = ASSETS_DIR / "statsPoint.png"
UMACOIN_ICON = ASSETS_DIR / "umaCoin.png"

GRADE_IMAGE_MAP = {
    1: "G.png",
    2: "F.png",
    3: "E.png",
    4: "D.png",
    5: "C.png",
    6: "B.png",
    7: "A.png",
    8: "S.png",
}

POS = {
    "title_center": (522, 38),

    "main_image": (35, 88),
    "main_image_size": (380, 300),

    "name_center": (745, 155),

    "speed_rank": (42, 455),
    "speed_value": (130, 465),

    "stamina_rank": (225, 455),
    "stamina_value": (340, 465),

    "power_rank": (435, 455),
    "power_value": (550, 465),

    "gut_rank": (645, 455),
    "gut_value": (760, 465),

    "wit_rank": (850, 455),
    "wit_value": (970, 465),

    "turf_grade": (370, 554),
    "dirt_grade": (562, 554),

    "sprint_grade": (370, 614),
    "mile_grade": (562, 614),
    "medium_grade": (755, 614),
    "long_grade": (942, 614),

    "front_grade": (370, 674),
    "pace_grade": (562, 674),
    "late_grade": (755, 674),
    "end_grade": (942, 674),

    "avatar": (89, 128),
    "avatar_frame": (70, 110),

    "frame_1": (450, 300),
    "frame_2": (650, 300),
    "frame_3": (850, 300),

    "umaCoin": (568, 306),
    "statsPoint": (768, 306),
    "skillPoint": (968, 306),

    "umaCoin_Val": (470, 308),
    "statsPoint_Val": (670, 308),
    "skillPoint_Val": (870, 308),
}


def get_grade_image(value: int, size=(64, 64)) -> Image.Image:
    value = max(1, min(value, 8))
    filename = GRADE_IMAGE_MAP[value]
    img = Image.open(GRADES_DIR / filename).convert("RGBA")
    return img.resize(size)


def paste_grade(card: Image.Image, value: int, pos: tuple[int, int], size=(64, 64)):
    grade_img = get_grade_image(value, size)
    card.paste(grade_img, pos, grade_img)


def draw_debug_grid(draw):
    for x in range(0, 1044, 50):
        draw.line((x, 0, x, 741), fill=(255, 0, 0, 90), width=1)
        draw.text((x + 2, 2), str(x), fill=(255, 0, 0))

    for y in range(0, 741, 50):
        draw.line((0, y, 1044, y), fill=(0, 0, 255, 90), width=1)
        draw.text((2, y + 2), str(y), fill=(0, 0, 255))

async def get_circle_avatar(url: str, size=(250, 250)) -> Image.Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()

    avatar = Image.open(BytesIO(data)).convert("RGBA")
    avatar = avatar.resize(size)

    # ทำวงกลม
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    result = Image.new("RGBA", size)
    result.paste(avatar, (0, 0), mask)

    return result

def get_avatar_frame(size=(320, 320)) -> Image.Image:
    frame = Image.open(FRAME_PATH).convert("RGBA")
    return frame.resize(size)

def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    text: str,
    font,
    fill=(120, 70, 35),
    outline_fill=(255, 255, 255),
    outline_width=2,
):
    x, y = pos

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)

    draw.text((x, y), text, font=font, fill=fill)

def draw_centered_text_with_outline(
    draw: ImageDraw.ImageDraw,
    center_pos: tuple[int, int],
    text: str,
    font,
    fill=(120, 70, 35),
    outline_fill=(255, 255, 255),
    outline_width=2,
):
    center_x, y = center_pos

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    x = center_x - (text_width // 2)

    draw_text_with_outline(
        draw,
        (x, y),
        text,
        font=font,
        fill=fill,
        outline_fill=outline_fill,
        outline_width=outline_width,
    )

def get_ui_image(path: Path, size: tuple[int, int] | None = None) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    if size is not None:
        img = img.resize(size)
    return img

async def create_stats_card(player: dict, avatar_url: str):
    card = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(card)

    try:
        name_font = ImageFont.truetype(str(FONT_PATH), 60)
        value_font = ImageFont.truetype(str(FONT_PATH), 42)
    except OSError:
        name_font = ImageFont.load_default()
        value_font = ImageFont.load_default()

    # ชื่อผู้เล่น
    draw_centered_text_with_outline(
        draw,
        POS["name_center"],
        player["username"],
        font=name_font,
        fill=(120, 70, 35),
        outline_fill=(255, 255, 255),
        outline_width=2,
    )

    # Main stats rank
    paste_grade(card, player["speed"], POS["speed_rank"], (56, 62))
    paste_grade(card, player["stamina"], POS["stamina_rank"], (56, 62))
    paste_grade(card, player["power"], POS["power_rank"], (56, 62))
    paste_grade(card, player["gut"], POS["gut_rank"], (56, 62))
    paste_grade(card, player["wit"], POS["wit_rank"], (56, 62))

    # Main stats value
    draw.text(POS["speed_value"], str(player["speed"]), fill=(120, 70, 35), font=value_font)
    draw.text(POS["stamina_value"], str(player["stamina"]), fill=(120, 70, 35), font=value_font)
    draw.text(POS["power_value"], str(player["power"]), fill=(120, 70, 35), font=value_font)
    draw.text(POS["gut_value"], str(player["gut"]), fill=(120, 70, 35), font=value_font)
    draw.text(POS["wit_value"], str(player["wit"]), fill=(120, 70, 35), font=value_font)

    # Track
    subIconSize = (33, 36)
    paste_grade(card, player["turf"], POS["turf_grade"], subIconSize)
    paste_grade(card, player["dirt"], POS["dirt_grade"], subIconSize)

    # Distance
    paste_grade(card, player["sprint"], POS["sprint_grade"], subIconSize)
    paste_grade(card, player["mile"], POS["mile_grade"], subIconSize)
    paste_grade(card, player["medium"], POS["medium_grade"], subIconSize)
    paste_grade(card, player["long"], POS["long_grade"], subIconSize)

    # Style
    paste_grade(card, player["front"], POS["front_grade"], subIconSize)
    paste_grade(card, player["pace"], POS["pace_grade"], subIconSize)
    paste_grade(card, player["late"], POS["late_grade"], subIconSize)
    paste_grade(card, player["end_style"], POS["end_grade"], subIconSize)

    # Frame
    frame_img = get_avatar_frame((240, 265))
    card.paste(frame_img, POS["avatar_frame"], frame_img)

    avatar_img = await get_circle_avatar(avatar_url, (200, 200))
    card.paste(avatar_img, POS["avatar"], avatar_img)
   
    button_img = get_ui_image(FRAME_Item, (180, 70))

    card.paste(button_img, POS["frame_1"], button_img)
    card.paste(button_img, POS["frame_2"], button_img)
    card.paste(button_img, POS["frame_3"], button_img)

    button_img = get_ui_image(UMACOIN_ICON, (50,50))
    card.paste(button_img, POS["umaCoin"], button_img)
    button_img = get_ui_image(STATS_POINT_ICON, (50,50))
    card.paste(button_img, POS["statsPoint"], button_img)
    button_img = get_ui_image(SKILL_POINT_ICON, (50,50))
    card.paste(button_img, POS["skillPoint"], button_img)
    
    draw.text(POS["umaCoin_Val"], str(player["uma_coin"]), fill=(120, 70, 35), font=value_font)
    draw.text(POS["statsPoint_Val"], str(player["stats_point"]), fill=(120, 70, 35), font=value_font)
    draw.text(POS["skillPoint_Val"], str(player["skill_point"]), fill=(120, 70, 35), font=value_font)
    
    topicFont = ImageFont.truetype(str(FONT_PATH), 24)

    draw.text((470, 270), "Uma Coins", fill=(120, 70, 35), font=topicFont)
    draw.text((670, 270), "Stats Points", fill=(120, 70, 35), font=topicFont)
    draw.text((870, 270), "Skill Points", fill=(120, 70, 35), font=topicFont)

    # draw_debug_grid(draw)
    return card