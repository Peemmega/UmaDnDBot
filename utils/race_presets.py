from utils.dice_presets import MAX_DICE_VALUE
from utils.icon_presets import Status_Icon_Type

PATH_TYPE = {
    1: "STRAIGHT",
    2: "CURVE",
    3: "UPHILL",
    4: "DOWNHILL"
}

PATH_TYPE_TEXT = {
    1: "➡️ ทางตรง",
    2: "⤵️ ทางโค้ง",
    3: "↗️ เนินขึ้น",
    4: "↘️ เนินลง",
}

def get_current_path_type(game: dict) -> int:
    turn = game["turn"]
    path = game["path"]

    if not path:
        return 1

    index = max(0, min(turn - 1, len(path) - 1))
    return path[index]

def build_path_effect_text(path_type: int) -> str:
    if path_type == 1:
        return f"หัก 1 {Status_Icon_Type["STA"]}"
    if path_type == 2:
        return f"หัก 1 {Status_Icon_Type["STA"]} • แต้มสูงสุดลูกเต๋าลดลง 5"
    if path_type == 3:
        return f"หัก 2 {Status_Icon_Type["STA"]} • {Status_Icon_Type["SPD"]} เหลือครึ่งหนึ่ง • {Status_Icon_Type["POW"]} โบนัสรวม x3"
    if path_type == 4:
        return f"ไม่เสีย {Status_Icon_Type["STA"]} • เพิ่มแต้มสูงสุดลูกเต๋าตามค่า {Status_Icon_Type["WIT"]}"
    return "-"

def get_path_effect(path_type: int, player: dict) -> dict:
    effect = {
        "stamina_cost": 0,
        "stamina_gain": 0,
        "max_dice_value": MAX_DICE_VALUE,
        "spd_multiplier": 1.0,
        "power_total_multiplier": 1.0,
        "extra_max_from_wit": 0,
        "label": PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง"),
    }

    if path_type == 1:  # ทางตรง
        effect["stamina_cost"] = 1

    elif path_type == 2:  # ทางโค้ง
        effect["stamina_cost"] = 1
        effect["max_dice_value"] = (MAX_DICE_VALUE - 5)

    elif path_type == 3:  # เนินขึ้น
        effect["stamina_cost"] = 2
        effect["spd_multiplier"] = 0.5
        effect["power_total_multiplier"] = 3.0

    elif path_type == 4:  # เนินลง
        # effect["stamina_gain"] = 1
        effect["stamina_cost"] = 0
        effect["extra_max_from_wit"] = player.get("wit", 0)

    return effect

RACE_PRESET = {
      "NHK": {
        "name": "NHK Mile Cup 1600m",
        "thumnail": "https://media.discordapp.net/attachments/1493695524812095489/1494219182676512858/thum_race_rt_000_1007_00.png?ex=69e1cf8e&is=69e07e0e&hm=b343ae355428ebe48951cadbae8cd18e5870346e5efb6eef401f613faa449997&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1493695524812095489/1494219216809627789/10602.png?ex=69e1cf96&is=69e07e16&hm=579e4e375f156ce70ee13c5cb16687e279c952a42776c9df1273960d85bb9c76&=&format=webp&quality=lossless&width=1440&height=929",
        "turn": 8,
        "path": [1, 3, 4, 2, 2, 3, 1, 1]
    },

    "TakarazukaKinen": {
        "name": "Takarazuka Kinen 2200m",
        "thumnail": "https://media.discordapp.net/attachments/1493695524812095489/1494219500743163954/thum_race_rt_000_1012_00.png?ex=69e1cfda&is=69e07e5a&hm=9aaa79075889b9f8a5fad33f09a31c72c252e586b3f753d472bff3ea15422de2&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1493695524812095489/1494219501019992196/10906.png?ex=69e1cfda&is=69e07e5a&hm=89bf0bdf5173efa05fe2a6f91ac19dae5dee0499b0f4296f6a4fa24c50c5073c&=&format=webp&quality=lossless&width=1359&height=984",
        "turn": 12,
        "path": [4, 3, 1, 2, 2, 1, 4, 2, 2, 1, 3, 1]
    },

    "TennoShoSpring": {
        "name": "Tenno Sho Spring 3200m",
        "thumnail": "https://media.discordapp.net/attachments/1493695524812095489/1494219631861432391/thum_race_rt_000_1006_00.png?ex=69e1cff9&is=69e07e79&hm=c8eb47ad4d7d54d2369332b321100cd08b37b014505a00f27b2f046e6f3be98e&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1493695524812095489/1494219666858704996/10811.png?ex=69e1d001&is=69e07e81&hm=2753992d6a484e9b83f1311b9e0c6488fa1108828c537d6ec3e1156d3beee76d&=&format=webp&quality=lossless&width=1532&height=890",
        "turn": 16,
        "path": [1, 3, 3, 4, 2, 2, 1, 1, 2, 2, 1, 3, 3, 4, 2, 2, 1, 1]
    },
}
