from utils.race.race_dice import (
    get_phase_from_turn,
)
from utils.dice.dice_presets import (
    MAX_SPEED_PHASE
)
from utils.race.race_weather import is_wet_lane

def incrase_speed_by_acceleration(game ,player: dict, multiple):
    race_profile = player.get("race_profile", {})
    effective_stats = player.get("effective_race_stats") or {}
    style = player["style"]
    current_max_speed = player.get("current_max_speed", 0)

    power_stat = effective_stats.get("effective_power", race_profile.get("power", 1)) * 1.5

    speed_cap_base = 0
    phase = get_phase_from_turn(game["turn"], game["max_turn"])

    style_rule = MAX_SPEED_PHASE[style]
    scale_up = 0.1

    if phase == 4:
        speed_cap_base = style_rule["last_spurt"]
        if style == "End":
            scale_up = 0.14
    elif phase == 3:
        speed_cap_base = style_rule["late"]
        if style == "Late":
            scale_up = 0.12
    else:
        speed_cap_base = style_rule["mid"]
        if phase == 1 and style == "Front":
            scale_up = 0.12

    if style == "Pace":
        scale_up = 0.11

    max_speed_cap = (
        speed_cap_base
        + effective_stats.get("effective_speed", race_profile.get("speed", 0))
    )

    increase_speed = 0.3 + (scale_up * power_stat * multiple)
    if is_wet_lane(game, player.get("current_lane")):
        # Wet lanes affect only this turn's acceleration.  They never reduce
        # the dice result or the score that was already gained.
        increase_speed *= 0.50

    new_speed = min(max_speed_cap, current_max_speed + increase_speed)
    player["current_max_speed"] = new_speed
