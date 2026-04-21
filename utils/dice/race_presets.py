from utils.dice.dice_presets import MAX_DICE_VALUE
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

PATH_TYPE_ICON = {
    1: "➡️",  # ทางตรง
    2: "⤵️",  # โค้ง
    3: "↗️",  # เนินขึ้น
    4: "↘️",  # เนินลง
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
        return f"หัก 1 {Status_Icon_Type['STA']}"
    if path_type == 2:
        return f"หัก 1 {Status_Icon_Type['STA']} • แต้มสูงสุดลูกเต๋าลดลง 5"
    if path_type == 3:
        return f"หัก 2 {Status_Icon_Type['STA']} • {Status_Icon_Type['SPD']} เหลือครึ่งหนึ่ง • {Status_Icon_Type['POW']} โบนัสรวม x3"
    if path_type == 4:
        return f"ไม่เสีย {Status_Icon_Type['STA']} • เพิ่มแต้มสูงสุดลูกเต๋าตามค่า {Status_Icon_Type['WIT']}"
    return "-"

def build_track_progress_text(path: list[int], current_turn: int) -> str:
    parts = []

    for i, path_type in enumerate(path, start=1):
        icon = PATH_TYPE_ICON.get(path_type, "➡️")

        if i == current_turn:
            parts.append(f"【{icon}】")
        else:
            parts.append(icon)

    return " ".join(parts)

def build_current_track_text(path: list[int], current_turn: int) -> str:
    if not path:
        return "ไม่พบข้อมูลสนาม"

    current_turn = max(1, min(current_turn, len(path)))
    path_type = path[current_turn - 1]
    path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

    return f"ตอนนี้อยู่ช่วงที่ {current_turn}/{len(path)} : {path_label}"

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
        "track": "turf",
        "distance": "mile",
        "turn": 8,
        "path": [1, 3, 4, 2, 2, 3, 1, 1]
    },

    "TakarazukaKinen": {
        "name": "Takarazuka Kinen 2200m",
        "thumnail": "https://media.discordapp.net/attachments/1493695524812095489/1494219500743163954/thum_race_rt_000_1012_00.png?ex=69e1cfda&is=69e07e5a&hm=9aaa79075889b9f8a5fad33f09a31c72c252e586b3f753d472bff3ea15422de2&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1493695524812095489/1494219501019992196/10906.png?ex=69e1cfda&is=69e07e5a&hm=89bf0bdf5173efa05fe2a6f91ac19dae5dee0499b0f4296f6a4fa24c50c5073c&=&format=webp&quality=lossless&width=1359&height=984",
        "track": "turf",
        "distance": "medium",
        "turn": 12,
        "path": [4, 3, 1, 2, 2, 1, 4, 2, 2, 1, 3, 1]
    },

    "TennoShoSpring": {
        "name": "Tenno Sho (Spring) 3200m",
        "thumnail": "https://media.discordapp.net/attachments/1493695524812095489/1494219631861432391/thum_race_rt_000_1006_00.png?ex=69e1cff9&is=69e07e79&hm=c8eb47ad4d7d54d2369332b321100cd08b37b014505a00f27b2f046e6f3be98e&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1493695524812095489/1494219666858704996/10811.png?ex=69e1d001&is=69e07e81&hm=2753992d6a484e9b83f1311b9e0c6488fa1108828c537d6ec3e1156d3beee76d&=&format=webp&quality=lossless&width=1532&height=890",
        "track": "turf",
        "distance": "long",
        "turn": 16,
        "path": [1, 3, 3, 4, 2, 2, 1, 1, 2, 3, 3, 4, 2, 2, 1, 1]
    },

    "SatsukiSho": {
        "name": "Satsuki Sho 2000m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1494730962477519049/thum_race_rt_000_1005_00.png?ex=69e454f0&is=69e30370&hm=7e84d8f95186e443c0e78149ac3dcee1be20600fb14f672bf37e781a94bbb9fa&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1494730963538804886/10504.png?ex=69e454f0&is=69e30370&hm=1534a1ad5575876856ca045835669f89bb38a510e064c5ab028c3697d3fb46d2&=&format=webp&quality=lossless&width=1433&height=812",
        "track": "turf",
        "distance": "medium",
        "turn": 12,
        "path": [3, 1, 3, 2, 4, 2, 1, 1, 2, 2, 3, 1]
    },

    "JapaneseDerby": {
        "name": "Tokyo Yushun (Japanese Derby) 2400m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1494731127385100428/thum_race_rt_000_1010_00.png?ex=69e45517&is=69e30397&hm=c31d08d5c4f4b6abf6a4d31e4331ff2459a9903aff29d6eadefdd553f78eff5e&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1494731127682760825/10606.png?ex=69e45517&is=69e30397&hm=f33351514052039ff0bf65d941f40771384d694427afe961be403fe0fa84b4e4&=&format=webp&quality=lossless&width=1607&height=927",
        "track": "turf",
        "distance": "medium",
        "turn": 12,
        "path": [3, 3, 2, 2, 2, 4, 1, 3, 1, 2, 2, 2]
    },

    "ArimaKinen": {
        "name": "Arima Kinen 2500m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1494752842714710156/thum_race_rt_000_1023_00.png?ex=69e46950&is=69e317d0&hm=039c53a2ecceb4dadd4503f9ef11694182db84d3d7a514566fd5875cb11f2a24&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1494752843184209930/10506.png?ex=69e46950&is=69e317d0&hm=e1434749606b63deb19bbd9f520fb7eb4e7b9ec09a236e0805f822e1de5eb1aa&=&format=webp&quality=lossless&width=1433&height=875",
        "track": "turf",
        "distance": "long",
        "turn": 16,
        "path": [1, 2, 2, 1, 3, 1, 3, 2, 4, 2, 1, 1, 2, 2, 3, 1]
    },

    "JapanCup": {
        "name": "Japan Cup 2400m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1495036145363320903/thum_race_rt_000_1019_00.png?ex=69e4c869&is=69e376e9&hm=f940df4979f39cbe2532b6170ad84b0562f72193fbd0fac4aec78fa498f9048f&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1495036145900195930/10606.png?ex=69e4c869&is=69e376e9&hm=2fea0f4fba9309b9b9374e873a8fa581847e7a86f2c69d56bebfdea9a20ea8e6&=&format=webp&quality=lossless&width=1607&height=927",
        "track": "turf",
        "distance": "medium",
        "turn": 12,
        "path": [3, 3, 2, 2, 2, 4, 1, 3, 1, 2, 2, 2]
    },

    "OsakaHai": {
        "name": "Osaka Hai 2000m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1495036503619797082/thum_race_rt_000_1003_00.png?ex=69e4c8be&is=69e3773e&hm=ad4fa8db3cd21e0e73c01cacb03d76c77d8faa4f5cca48dd68b274a762b9b569&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1495036503917723739/10905.png?ex=69e4c8be&is=69e3773e&hm=42d5d562d0ff0c090347a983d78de62e5f108732ed3331d8dc09ad6b25f26b74&=&format=webp&quality=lossless&width=1359&height=932",
        "track": "turf",
        "distance": "medium",
        "turn": 12,
        "path": [3, 1, 2, 2, 1, 1, 2, 2, 4, 3, 1, 1]
    },

    
    "TennoShoAutumn": {
        "name": "Tenno Sho (Autumn) 2000m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1495035900818751598/thum_race_rt_000_1016_00.png?ex=69e4c82f&is=69e376af&hm=9dfb903aa4a2ca5c03acf2d67c32ee70d04ef389eeb251ff7ddb64596ad2b796&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1495035901087318036/10604.png?ex=69e4c82f&is=69e376af&hm=89286fb782c955579e4cedc8c44c0b4ab54afed16ff6b88bd6ec8967b05eb7e6&=&format=webp&quality=lossless&width=1745&height=930",
        "track": "turf",
        "distance": "medium",
        "turn": 12,
        "path": [1, 3, 2, 2, 4, 1, 3, 1, 1, 2, 2, 1]
    },

    "OkaSho": {
        "name": "Oka Sho 1600m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1495054919999291593/thum_race_rt_000_1004_00.png?ex=69e4d9e5&is=69e38865&hm=43e097df171288de94a09c609093567b36f63d96492082d1912cb59068534280&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1495054920347422842/10903.png?ex=69e4d9e5&is=69e38865&hm=3896e24d0545c6aa3b3c7e288cdb72c8a42bda905ed39dd8b605ecf65daeebaf&=&format=webp&quality=lossless&width=1479&height=995",
        "track": "turf",
        "distance": "mile",
        "turn": 8,
        "path": [1, 1, 2, 2, 4, 1, 3, 1]
    },

    "MileChampionship": {
        "name": "Mile Championship 1600m",
        "thumnail": "https://media.discordapp.net/attachments/1494730857259471030/1495055108503769119/thum_race_rt_000_1018_00.png?ex=69e4da12&is=69e38892&hm=9759f8c8444de9fdd8a4b4caefdb30ab909e4df33d7e66dae61f97e4b444912d&=&format=webp&quality=lossless&width=192&height=96",
        "image": "https://media.discordapp.net/attachments/1494730857259471030/1495055108877189201/10805.png?ex=69e4da12&is=69e38892&hm=a6887c5def45a878eccb079f4aaaa57b027538a8161909939e488a87e0a3651a&=&format=webp&quality=lossless&width=1700&height=890",
        "track": "turf",
        "distance": "mile",
        "turn": 8,
        "path": [1, 3, 3, 4, 2, 2, 1, 1]
    },


    "SteelBallRun": {
        "name": "Steel Ball Run 4000000m",
        "thumnail": "https://media.discordapp.net/attachments/697810514448744448/1496124802065371156/2026-04-21_192453.png?ex=69e8be4d&is=69e76ccd&hm=5b70ed31363207dd1453202f3657a698a98f8842aaf382b3360c0fa4ec3f4517&=&format=webp&quality=lossless&width=884&height=479",
        "image": "https://media.discordapp.net/attachments/697810514448744448/1496124786143924304/Steel-Ball-Run-1-580x326.png?ex=69e8be49&is=69e76cc9&hm=c2aa1c996100f886b9eed318fad5b9ff35222dbecb78706b5c075aa382544bf4&=&format=webp&quality=lossless&width=870&height=489",
        "track": "dirt",
        "distance": "long",
        "turn": 40,
        "path": [1, 3, 3, 4, 2, 2, 1, 1,1, 3, 3, 4, 2, 2, 1, 1,1, 3, 3, 4, 2, 2, 1, 1,1, 3, 3, 4, 2, 2, 1, 1,1, 3, 3, 4, 2, 2, 1, 1]
    },

    # "TennoShoSpring": {
    #     "name": "Tenno Sho Spring 3200m",
    #     "thumnail": "",
    #     "image": "",
    #     "turn": 16,
    #     "path": [1, 3, 3, 4, 2, 2, 1, 1, 2, 3, 3, 4, 2, 2, 1, 1]
    # },

}
