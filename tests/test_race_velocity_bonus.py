import unittest
from unittest.mock import patch

from utils.game import manager


class RaceVelocityBonusTests(unittest.TestCase):
    def test_skill_stacks_and_bonus_applies_to_rolls_and_rerolls(self):
        player = {
            "style": "Pace", "score": 0, "wit_mana": 200,
            "skills": {1: "vel_033"}, "skill_cooldowns": {},
            "race_profile": {"stamina": 1, "gut": 0},
            "stamina_stat": 1, "max_stamina": 900, "stamina_left": 50,
            "turn_stamina_before_roll": 50, "current_lane": 2,
        }
        game = {"turn": 4, "max_turn": 12, "path": [1] * 12, "players": {"runner": player}}
        with patch.object(manager, "get_game", return_value=game):
            self.assertTrue(manager.execute_skill_core(1, "runner", "vel_033")[0])
            self.assertEqual(player["race_velocity_bonus"], 3)
            self.assertTrue(manager.execute_skill_core(1, "runner", "vel_033", ignore_cooldown=True)[0])
        self.assertEqual(player["race_velocity_bonus"], 6)

        totals = []
        for consume in (True, False, False):
            result = {"total": 100, "bonus_display": "-", "dice_preview_bonus_display": "-"}
            manager.apply_lane_tactics_to_result(
                game=game, user_id="runner", game_player=player, result=result,
                path_effect={}, score_map={"runner": 0}, consume_stamina=consume,
            )
            totals.append(result["total"])
            self.assertIn("+6RACE", result["bonus_display"])
        self.assertEqual(totals[0], totals[1])
        self.assertEqual(totals[1], totals[2])
        player["race_velocity_bonus"] = 0
        result = {"total": 100, "bonus_display": "-"}
        manager.apply_lane_tactics_to_result(
            game=game, user_id="runner", game_player=player, result=result,
            path_effect={}, score_map={"runner": 0}, consume_stamina=False,
        )
        self.assertEqual(totals[0] - result["total"], 6)


if __name__ == "__main__":
    unittest.main()
