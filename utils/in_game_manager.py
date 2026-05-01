from utils.race.race_dice import (
    get_phase_from_turn,
)
from utils.dice.dice_presets import (
    MAX_SPEED_PHASE
)

def incrase_speed_by_acceleration(game ,player: dict, multiple):
    race_profile = player.get("race_profile", {})
    current_max_speed = player.get("current_max_speed", 0)

    power_stat = race_profile.get("power", 1)

    speed_cap_base = 0
    phase = get_phase_from_turn(game["turn"], game["max_turn"])

    style_rule = MAX_SPEED_PHASE[player["style"]]
    scale_up = 0.2

    if phase == 4:
        speed_cap_base = style_rule["last_spurt"]
        scale_up = 0.25
    elif phase == 3:
        speed_cap_base = style_rule["late"]
        scale_up = 0.25
    else:
        speed_cap_base = style_rule["mid"]

    max_speed_cap = (
        speed_cap_base
        + race_profile.get("speed", 0)
    )

    increase_speed = 0.5 + (scale_up * power_stat * multiple) 

    new_speed = min(max_speed_cap, current_max_speed + increase_speed)
    player["current_max_speed"] = new_speed
    print(power_stat , increase_speed)