ZONE_FIELDS = {"flat", "add_d", "add_kh", "floor", "selected_die", "cap"}
DEFAULT_ZONE_IMAGE = "https://media.discordapp.net/attachments/697810514448744448/1495378081085657162/tm_zone.gif"

ZONE_POINT_COST = {
    "flat": 1,
    "add_d": 3,
    "add_kh": 4,
    "floor": 1,
    "selected_die": 2,
    "cap": 1,
}

ZONE_VALUE = {
    "flat": 10,
    "add_d": 1,
    "add_kh": 1,
    "floor": 2,
    "selected_die": 2,
    "cap": 3,
}

DEFAULT_ZONE = {
    "name": "Default Zone",
    "image_url": "",
    "points": 5,
    "build": {
        "flat": 0,
        "add_d": 0,
        "add_kh": 0,
        "floor": 0,
        "selected_die": 0,
        "cap": 0,
    }
}