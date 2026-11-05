import unittest

from utils.mob.mob_lane_decision import decide_mob_target_lane
from utils.mob.mob_stamina import forecast_stamina


def runner(**overrides):
    player = {
        "is_mob": True, "mob_preset_key": "rookie_front", "style": "Front",
        "score": 100, "current_lane": 1, "current_max_speed": 30,
        "race_profile": {"stamina": 1, "wit": 2, "power": 2},
        "stamina_left": 900, "max_stamina": 900,
    }
    player.update(overrides)
    return player


class MobStaminaTests(unittest.TestCase):
    def test_sunny_uphill_downhill_and_first_turn_use_real_costs(self):
        player = runner()
        game = {"turn": 1, "max_turn": 4, "weather": "sunny", "path": [1, 3, 4, 1], "players": {"p": player}}
        forecast = forecast_stamina(game, "p", 2)
        self.assertEqual([step["cost"] for step in forecast["turns"]], [110, 210, 10, 110])
        self.assertEqual(forecast["estimated_remaining"], 460)

    def test_next_turn_draft_uses_queued_lanes_and_sunny_cost(self):
        player = runner(last_roll_turn=1)
        other = runner(score=110, current_lane=3, pending_lane=1)
        game = {"turn": 1, "max_turn": 2, "weather": "sunny", "path": [1, 3], "players": {"p": player, "other": other}}
        forecast = forecast_stamina(game, "p", 1)
        self.assertEqual(len(forecast["turns"]), 1)
        self.assertTrue(forecast["turns"][0]["draft"])
        self.assertEqual(forecast["turns"][0]["cost"], 171)

    def test_forecast_identifies_exhaustion_without_assuming_future_draft(self):
        player = runner(stamina_left=200, max_stamina=900)
        other = runner(score=110, current_lane=1)
        game = {"turn": 1, "max_turn": 4, "path": [1, 1, 1, 1], "players": {"p": player, "other": other}}
        forecast = forecast_stamina(game, "p", 1)
        self.assertTrue(forecast["turns"][0]["draft"])
        self.assertTrue(forecast["turns"][1]["draft"])
        self.assertFalse(forecast["turns"][2]["draft"])
        self.assertEqual(forecast["shortage_turns"], [3, 4])

    def test_avoids_heavy_block_even_with_low_stamina(self):
        player = runner(stamina_left=150, current_lane=1)
        others = {str(i): runner(score=105 + i, current_lane=1) for i in range(3)}
        game = {"turn": 1, "max_turn": 8, "path": [1] * 8, "players": {"p": player, **others}}
        self.assertNotEqual(decide_mob_target_lane(game, "p"), 1)

    def test_low_stamina_makes_ai_seek_draft_early(self):
        player = runner(style="Pace", current_lane=2, stamina_left=100)
        other = runner(score=105, current_lane=1)
        game = {"turn": 1, "max_turn": 12, "path": [3] * 12, "players": {"p": player, "other": other}}
        self.assertEqual(decide_mob_target_lane(game, "p"), 1)
        self.assertTrue(player["mob_stamina_forecast"]["turns"][1]["draft"])
        player["stamina_left"] = 5000
        self.assertEqual(decide_mob_target_lane(game, "p"), 2)

    def test_sunny_weather_can_cause_forecast_shortfall(self):
        player = runner(stamina_left=400)
        game = {"turn": 1, "max_turn": 4, "path": [1] * 4, "players": {"p": player}}
        self.assertEqual(forecast_stamina(game, "p", 2)["shortfall"], 0)
        game["weather"] = "sunny"
        self.assertEqual(forecast_stamina(game, "p", 2)["shortfall"], 40)


if __name__ == "__main__":
    unittest.main()
