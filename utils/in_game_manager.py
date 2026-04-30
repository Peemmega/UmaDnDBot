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

    speed_cap_base = MAX_SPEED_PHASE[player["style"]]["last_spurt" if phase == 4 else "max"]

    max_speed_cap = (
        speed_cap_base
        + race_profile.get("speed", 0)
    )

    scale_up = 0.30 if phase == 4 else 0.2
    increase_speed = 1 + (scale_up * power_stat) * multiple

    new_speed = min(max_speed_cap, current_max_speed + increase_speed)
    player["current_max_speed"] = new_speed
    print(power_stat , increase_speed)