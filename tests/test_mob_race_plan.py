import unittest
from unittest.mock import patch

from utils.mob.mob_lane_decision import decide_mob_target_lane
from utils.mob.mob_race_plan import _action_value, build_race_plan


def runner(**overrides):
    player = {
        "is_mob": True, "mob_preset_key": "rookie_front", "style": "Front",
        "score": 100, "current_lane": 1, "current_max_speed": 16,
        "race_profile": {"power": 5, "speed": 5, "wit": 5},
        "stamina_left": 1500, "max_stamina": 1500, "wit_mana": 100,
        "skills": {}, "skill_cooldowns": {}, "zone_left": 1,
        "zone": {"build": {"cap_floor": 3}},
    }
    player.update(overrides)
    return player


class RacePlanTests(unittest.TestCase):
    def test_zone_waits_for_best_dice_and_downhill(self):
        player = runner(style="End")
        game = {"turn": 1, "max_turn": 8, "path": [1] * 7 + [4], "players": {"p": player}}
        plan = build_race_plan(game, "p", [])
        self.assertEqual([turn for turn, action in plan.items() if action["zone"]], [8])

    def test_front_zone_is_not_forced_on_first_turn(self):
        player = runner(zone={"build": {"add_dkh": 3}})
        game = {"turn": 1, "max_turn": 8, "path": [1] * 7 + [4], "players": {"p": player}}
        plan = build_race_plan(game, "p", [])
        self.assertFalse(plan[1]["zone"])

    def test_skills_and_zone_combine_on_high_dice_turn(self):
        skill = {"cost": 30, "cooldown": 99, "effects": [{"type": "add_dkh", "value": 2}]}
        player = runner(style="End", skills={1: "dice"})
        game = {"turn": 1, "max_turn": 8, "path": [1] * 8, "players": {"p": player}}
        with patch("utils.mob.mob_race_plan.SKILLS", {"dice": skill}):
            plan = build_race_plan(game, "p", [("dice", skill)])
        skill_turn = next(turn for turn, action in plan.items() if action["skills"])
        self.assertTrue(plan[skill_turn]["zone"])
        self.assertGreaterEqual(skill_turn, 7)

    def test_acceleration_value_uses_style_phase_scale(self):
        player = runner(style="Late", current_max_speed=10)
        game = {"turn": 1, "max_turn": 8, "path": [1] * 8, "players": {"p": player}}
        effect = [{"type": "modify_current_speed", "value": 2}]
        rule = {"d": 2}
        self.assertGreater(_action_value(game, player, 5, rule, effect, None), _action_value(game, player, 3, rule, effect, None))

    def test_replans_when_position_skill_becomes_usable(self):
        skill = {"cost": 30, "cooldown": 99, "trigger": {"position_group": "front", "turn_max": 2}, "effects": [{"type": "modify_velocity", "value": 50}]}
        player = runner(skills={1: "position"}, zone_left=0)
        game = {"turn": 1, "max_turn": 8, "path": [1] * 8, "players": {"p": player}}
        with patch("utils.mob.mob_race_plan.SKILLS", {"position": skill}):
            first = build_race_plan(game, "p", [])
            self.assertEqual(first[1]["skills"], [])
            game["turn"] = 2
            second = build_race_plan(game, "p", [("position", skill)])
        self.assertEqual(second[2]["skills"], ["position"])

    def test_plan_respects_mana_and_cooldown(self):
        skill = {"cost": 60, "cooldown": 3, "effects": [{"type": "modify_velocity", "value": 50}]}
        player = runner(skills={1: "one", 2: "two"}, wit_mana=60, zone_left=0, effective_race_stats={"effective_wit_gain": 0})
        game = {"turn": 1, "max_turn": 4, "path": [1] * 4, "players": {"p": player}}
        with patch("utils.mob.mob_race_plan.SKILLS", {"one": skill, "two": skill}):
            plan = build_race_plan(game, "p", [("one", skill), ("two", skill)])
        self.assertEqual(sum(len(action["skills"]) for action in plan.values()), 1)

    def test_lane_prefers_better_dice_color(self):
        player = runner(style="Pace", current_lane=4, current_max_speed=40)
        other = runner(score=99, current_lane=1)
        game = {"turn": 5, "max_turn": 8, "path": [1] * 8, "players": {"p": player, "o": other}}
        self.assertLessEqual(decide_mob_target_lane(game, "p"), 2)


if __name__ == "__main__":
    unittest.main()
