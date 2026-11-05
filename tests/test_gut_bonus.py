import unittest
from unittest.mock import patch

from utils.race.race_dice import roll_by_rule, roll_race_dice
from utils.race.turn_engine import TurnEngine


class GutBonusTests(unittest.TestCase):
    def setUp(self):
        self.player = {"style": "Pace", "score": 0, "current_lane": 1, "current_max_speed": 40}
        self.stats = {"speed": 1, "stamina": 1, "power": 1, "gut": 5}
        self.game = {"turn": 5, "max_turn": 8, "players": {"runner": self.player}}

    def roll(self, nearby, color="Gold", phase=3):
        with patch("utils.race.race_dice.random.randint", return_value=10):
            return roll_by_rule({"d": 1}, self.stats, self.player, {
                "phase": phase, "nearby_count": nearby, "distance_color": color,
            })

    def advance(self):
        TurnEngine.advance(
            self.game, lane_system_enabled=False,
            record_lane_change=lambda *_: None,
            record_turn_snapshot=lambda *_: None,
            after_advance=lambda: None,
        )

    def test_carry_halves_each_turn_without_going_below_base(self):
        first = self.roll(2)
        self.assertEqual(first["gut_bonus"], 30)
        self.assertEqual(first["total"], 44)
        self.player["gut_bonus_current"] = first["gut_bonus"]
        self.advance()
        second = self.roll(0, "White")
        self.assertEqual(second["gut_bonus"], 15)
        self.player["gut_bonus_current"] = second["gut_bonus"]
        self.advance()
        third = self.roll(0, "White")
        self.assertEqual(third["gut_carried_bonus"], 7)
        self.assertEqual(third["gut_bonus"], 10)

    def test_new_pack_bonus_replaces_smaller_carry(self):
        self.player["gut_bonus_carried"] = 15
        result = self.roll(1)
        self.assertEqual(result["gut_bonus"], 20)
        self.player["gut_bonus_current"] = result["gut_bonus"]
        self.advance()
        self.assertEqual(self.player["gut_bonus_carried"], 10)

    def test_repeated_rolls_do_not_halve_or_mutate_carry(self):
        self.player["gut_bonus_carried"] = 15
        self.player["gut_bonus_current"] = 15
        for _ in range(3):
            self.assertEqual(self.roll(0, "White")["gut_bonus"], 15)
            self.assertEqual(self.player["gut_bonus_carried"], 15)
            self.assertEqual(self.player["gut_bonus_current"], 15)

    def test_phase_one_and_two_do_not_award_gut(self):
        self.player["gut_bonus_carried"] = 30
        self.assertEqual(self.roll(2, phase=2)["gut_bonus"], 0)

    def test_roll_race_dice_exposes_bonus_components(self):
        other = {"score": 5, "current_lane": 1}
        result = roll_race_dice(
            game_player=self.player, player_stats=self.stats, player_id="runner",
            score_map={"runner": 0, "other": 5}, turn=5, max_turn=8,
            player_map={"runner": self.player, "other": other},
        )
        self.assertEqual(result["gut_base_bonus"], 10)
        self.assertEqual(result["gut_pack_bonus"], 10)
        self.assertEqual(result["gut_bonus"], 20)

    def test_wit_reroll_attempts_do_not_consume_carry(self):
        self.player["gut_bonus_carried"] = 15
        self.player["gut_bonus_current"] = 15
        result = roll_race_dice(
            game_player=self.player, player_stats=self.stats, player_id="runner",
            score_map={"runner": 0}, turn=6, max_turn=8,
            minimum_total=100000, player_map={"runner": self.player},
        )
        self.assertEqual(result["gut_bonus"], 15)
        self.assertEqual(self.player["gut_bonus_carried"], 15)
        self.assertEqual(self.player["gut_bonus_current"], 15)


if __name__ == "__main__":
    unittest.main()
