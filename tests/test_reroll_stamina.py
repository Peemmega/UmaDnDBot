import unittest

from utils.game.manager import apply_lane_tactics_to_result, apply_wit_reroll_minimum


class RerollStaminaTests(unittest.TestCase):
    def resolve(self, player, game, *, consume_stamina):
        result = {"total": 100, "bonus_display": "-", "dice_preview_bonus_display": "-"}
        outcome = apply_lane_tactics_to_result(
            game=game, user_id="runner", game_player=player, result=result,
            path_effect={}, score_map={"runner": 0}, consume_stamina=consume_stamina,
        )
        return result, outcome

    def test_penalty_persists_across_rerolls_without_spending_stamina_again(self):
        player = {"race_profile": {"stamina": 1, "gut": 0}, "stamina_stat": 1,
                  "max_stamina": 900, "stamina_left": 50, "turn_stamina_before_roll": 50,
                  "score": 0, "current_lane": 2}
        game = {"turn": 1, "players": {"runner": player}}
        first, _ = self.resolve(player, game, consume_stamina=True)
        self.assertEqual(player["stamina_left"], 0)
        for _ in range(2):
            result, outcome = self.resolve(player, game, consume_stamina=False)
            self.assertTrue(outcome["stamina_penalty_active"])
            self.assertTrue(player["takeStaminaDebuff"])
            self.assertEqual(result["total"], first["total"])
            self.assertIn("%STA", result["bonus_display"])
            self.assertEqual(player["stamina_left"], 0)

    def test_no_penalty_when_stamina_was_sufficient_before_roll(self):
        player = {"race_profile": {"stamina": 1, "gut": 0}, "stamina_stat": 1,
                  "max_stamina": 900, "stamina_left": 0, "turn_stamina_before_roll": 100,
                  "score": 0, "current_lane": 2}
        game = {"turn": 1, "players": {"runner": player}}
        result, outcome = self.resolve(player, game, consume_stamina=False)
        self.assertFalse(outcome["stamina_penalty_active"])
        self.assertEqual(result["total"], 100)

    def test_wit_guarantee_applies_after_penalty(self):
        result = {"total": 30, "bonus_display": "-70%STA", "dice_preview_bonus_display": "-70%STA"}
        apply_wit_reroll_minimum(result, 35)
        self.assertEqual(result["total"], 36)
        self.assertIn("-70%STA", result["bonus_display"])
        self.assertIn("+6WIT", result["bonus_display"])


if __name__ == "__main__":
    unittest.main()
