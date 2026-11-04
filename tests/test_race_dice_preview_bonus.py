import unittest

from utils.race_dice_preview import combine_race_velocity_bonus


class RaceDicePreviewBonusTests(unittest.TestCase):
    def test_combines_race_and_velocity_without_affecting_other_bonuses(self):
        self.assertEqual(
            combine_race_velocity_bonus("+4Speed +20<:Velocity:123> +3RACE -10%Block"),
            "+4Speed +23<:Velocity:123> -10%Block",
        )
        self.assertEqual(combine_race_velocity_bonus("+4Speed +3RACE"), "+4Speed +3Velocity")
        self.assertEqual(combine_race_velocity_bonus("+20Velocity +5Velocity"), "+20Velocity +5Velocity")


if __name__ == "__main__":
    unittest.main()
