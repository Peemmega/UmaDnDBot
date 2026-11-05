import unittest
from unittest.mock import AsyncMock, patch

from PIL import Image

from utils import race_dice_preview
from utils.race_dice_preview import create_race_dice_preview


class SunnyDicePreviewTests(unittest.IsolatedAsyncioTestCase):
    async def render(self, payload, result, **kwargs):
        player = {
            "style": "Front", "current_max_speed": 20, "current_lane": 2,
            "stamina_left": 500, "last_stamina_drain": 110,
        }
        with patch("utils.race_dice_preview.load_image_url", new=AsyncMock(return_value=Image.new("RGBA", (480, 500), "white"))), patch("utils.race_dice_preview.draw_sun_icon", wraps=race_dice_preview.draw_sun_icon) as sun:
            image = await create_race_dice_preview(
                game_player=player, result=result, payload=payload,
                path_label="Straight", character_image_url="local", **kwargs,
            )
        return image, sun.call_count

    async def test_sunny_game_draws_overlay_and_sun_without_explicit_flag(self):
        result = {"total": 50}
        sunny, sun_count = await self.render({"new_score": 50, "game": {"weather": "sunny"}}, result)
        normal, normal_sun_count = await self.render({"new_score": 50, "game": {"weather": "none"}}, result)
        self.assertNotEqual(sunny.getpixel((10, 10)), normal.getpixel((10, 10)))
        self.assertEqual(sun_count, 1)
        self.assertEqual(normal_sun_count, 0)

    async def test_weather_cost_supports_payload_without_game(self):
        _, sun_count = await self.render({"new_score": 50}, {"weather_stamina_cost": 10})
        self.assertEqual(sun_count, 1)

    async def test_explicit_override_is_preserved(self):
        _, sun_count = await self.render({"new_score": 50, "game": {"weather": "sunny"}}, {}, sunny_overlay=False)
        self.assertEqual(sun_count, 0)


if __name__ == "__main__":
    unittest.main()
