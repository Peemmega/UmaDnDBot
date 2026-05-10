from utils.icon_presets import STAT_EMOJIS, Status_Icon_Type


def get_stat_emoji(value: int) -> str:
    value = max(1, min(value, 8))
    return STAT_EMOJIS[value]


def get_stat_icon(value: str) -> str:
    return Status_Icon_Type[value]
