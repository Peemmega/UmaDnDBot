import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from cogs.game import GameCog
from views.create_game_view import ConfirmCreateView
from views.lobby_management_views import SettingsView
from views.join_view import LobbyView


def interaction(user_id=1, admin=False, channel_id=42):
    return SimpleNamespace(
        user=SimpleNamespace(id=user_id, guild_permissions=SimpleNamespace(administrator=admin)),
        guild=object(), channel_id=channel_id,
        response=SimpleNamespace(send_message=AsyncMock()),
    )


class GamePermissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_rejects_non_admin(self):
        ctx = interaction()
        await GameCog.create.callback(GameCog(None), ctx)
        ctx.response.send_message.assert_awaited_once()
        self.assertTrue(ctx.response.send_message.await_args.kwargs["ephemeral"])

    async def test_confirm_rechecks_admin_permission(self):
        ctx = interaction()
        view = ConfirmCreateView(42, 1, "stage")
        with patch("views.create_game_view.create_game") as create_game:
            await view.create.callback(ctx)
        create_game.assert_not_called()
        ctx.response.send_message.assert_awaited_once()

    async def test_set_owner_requires_admin_and_existing_game(self):
        target = SimpleNamespace(id=2, bot=False, mention="<@2>")
        game = {"owner_id": 1}
        with patch("cogs.game.get_game", return_value=game):
            ctx = interaction(admin=False)
            await GameCog.set_owner.callback(GameCog(None), ctx, target)
        self.assertEqual(game["owner_id"], 1)
        with patch("cogs.game.get_game", return_value=None):
            ctx = interaction(admin=True)
            await GameCog.set_owner.callback(GameCog(None), ctx, target)
        self.assertTrue(ctx.response.send_message.await_args.kwargs["ephemeral"])

    async def test_transfer_revokes_old_settings_access(self):
        target = SimpleNamespace(id=2, bot=False, mention="<@2>")
        game = {"owner_id": 1, "started": False}
        with patch("cogs.game.get_game", return_value=game):
            await GameCog.set_owner.callback(GameCog(None), interaction(admin=True), target)
        self.assertEqual(game["owner_id"], 2)
        with patch("views.lobby_management_views.get_game", return_value=game):
            old_view = SettingsView(42, 1)
            self.assertFalse(await old_view.interaction_check(interaction(user_id=1)))
            new_view = SettingsView(42, 2)
            self.assertTrue(await new_view.interaction_check(interaction(user_id=2)))

    async def test_admin_can_open_settings_and_start_another_owners_room(self):
        game = {"owner_id": 2, "started": False}
        ctx = interaction(admin=True)
        with patch("views.join_view.get_game", return_value=game), patch(
            "views.lobby_management_views.get_game", return_value=game
        ):
            view = LobbyView(42)
            await view.settings_button.callback(ctx)
            settings = ctx.response.send_message.await_args.kwargs["view"]
            self.assertTrue(await settings.interaction_check(ctx))
        with patch("views.join_view.get_game", return_value=game), patch(
            "views.join_view.start_game", return_value=(False, "test")
        ) as start:
            await view.start_button.callback(ctx)
        start.assert_called_once_with(42)

    async def test_non_owner_cannot_manage_room_and_admin_permission_is_rechecked(self):
        game = {"owner_id": 2, "started": False}
        ctx = interaction()
        with patch("views.join_view.get_game", return_value=game), patch(
            "views.join_view.start_game"
        ) as start:
            view = LobbyView(42)
            await view.settings_button.callback(ctx)
            await view.start_button.callback(ctx)
        start.assert_not_called()
        with patch("views.lobby_management_views.get_game", return_value=game):
            settings = SettingsView(42, 1)
            self.assertFalse(await settings.interaction_check(ctx))


if __name__ == "__main__":
    unittest.main()
