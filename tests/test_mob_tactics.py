import copy
import unittest
from unittest.mock import patch

from utils.game.manager import should_mob_use_endgame_zone
from utils.mob.mob_lane_decision import decide_mob_target_lane
from utils.mob.mob_skill_decision import _simulate_combo_gain, get_future_dice_context


def player(**overrides):
    result = {
        "is_mob": True, "mob_preset_key": "tamamo_cross", "style": "Late",
        "score": 100, "current_lane": 1, "current_max_speed": 40,
        "race_profile": {"wit": 2}, "stamina_left": 1200, "max_stamina": 1600,
        "zone_left": 1, "zone": {"build": {"add_dkh": 3}},
    }
    result.update(overrides)
    return result


class MobTacticsTests(unittest.TestCase):
    def test_lane_uses_next_turn_phase(self):
        game = {"turn": 3, "max_turn": 12, "path": [1, 1, 1, 3], "players": {"mob": player()}}
        with patch("utils.mob.mob_lane_decision.get_phase_from_turn", return_value=2) as phase:
            decide_mob_target_lane(game, "mob")
        phase.assert_called_once_with(4, 12)

    def test_cap_skill_simulation_counts_increase_with_zone_dice(self):
        mob = player(next_roll_add_d=3, next_roll_add_kh=3)
        game = {"turn": 8, "max_turn": 12, "path": [1] * 12, "players": {"mob": mob}}
        combo = [{"skill_id": "cap", "skill": {"effects": [{"type": "modify_roll_cap", "value": 10}]}}]
        self.assertGreater(_simulate_combo_gain(game, "mob", combo, 500), 0)

    def test_zone_considers_current_lanes_and_turn_snapshot(self):
        mob = player(pending_lane=2)
        opponent = player(score=400, current_lane=1, pending_lane=3)
        game = {"turn": 8, "max_turn": 12, "players": {"mob": mob, "other": opponent}, "turn_snapshot_scores": {"mob": 100, "other": 130}}
        self.assertFalse(should_mob_use_endgame_zone(game, "mob", mob, 3))
        opponent["current_lane"] = 2
        with patch("utils.mob.mob_skill_decision.get_future_dice_context", return_value={"has_much_better_future_dice": False}):
            self.assertTrue(should_mob_use_endgame_zone(game, "mob", mob, 3))

    def test_zone_preview_uses_selected_affordable_combo_without_mutation(self):
        mob = player(skill_point=20)
        game = {"turn": 7, "max_turn": 12, "players": {"mob": mob}}
        before = copy.deepcopy(game)
        skills = [("cap", {"cost": 10, "effects": [{"type": "modify_roll_cap", "value": 10}]})]
        with patch("utils.mob.mob_skill_decision.get_future_dice_context", return_value={"has_much_better_future_dice": True}), patch("utils.game.manager.decide_mob_skill_combo", return_value=["cap"]) as choose:
            self.assertTrue(should_mob_use_endgame_zone(game, "mob", mob, 3, skills))
        preview = choose.call_args.args[0]["players"]["mob"]
        self.assertGreater(preview["next_roll_add_d"], 0)
        self.assertEqual(game, before)
        with patch("utils.mob.mob_skill_decision.get_future_dice_context", return_value={"has_much_better_future_dice": True}), patch("utils.game.manager.decide_mob_skill_combo", return_value=[]):
            self.assertFalse(should_mob_use_endgame_zone(game, "mob", mob, 3, skills))

    def test_future_forecast_does_not_assume_other_pack_color(self):
        mob = player()
        game = {"turn": 7, "max_turn": 12, "players": {"mob": mob, "other": player(score=101)}}
        with patch("utils.mob.mob_skill_decision.get_dice_rule", wraps=__import__("utils.mob.mob_skill_decision", fromlist=["get_dice_rule"]).get_dice_rule) as rule:
            context = get_future_dice_context(game, "mob")
        self.assertTrue(all(call.args[1] == context["distance_color"] for call in rule.call_args_list))


if __name__ == "__main__":
    unittest.main()
