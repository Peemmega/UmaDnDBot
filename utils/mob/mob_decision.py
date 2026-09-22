"""Compatibility facade for focused Mob AI decision modules."""

from utils.mob.mob_board_state import (
    get_current_path_type,
    get_distance_to_front,
    get_nearby_count,
    get_position_groups,
)
from utils.mob.mob_lane_decision import decide_mob_target_lane
from utils.mob.mob_profiles import AI_LEVEL_CONFIG, get_ai_profile
from utils.mob.mob_skill_decision import (
    analyze_skill_effects,
    decide_mob_skill_combo,
    estimate_roll_value,
    estimate_rule_value,
    evaluate_skill_combo_score,
    evaluate_skill_score,
    get_current_dice_context,
    get_effect_value,
    get_future_dice_context,
)


def has_position(position_groups, *targets):
    return any(target in position_groups for target in targets)
