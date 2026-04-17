import discord

from utils.dice.race_dice import roll_race_dice
from utils.game_manager import get_game, get_player_in_game, update_player_score, use_reroll
from utils.database import ensure_player

class RunRerollView(discord.ui.View):
    def __init__(
        self,
        *,
        owner_id: int,
        channel_id: int,
        old_total: int,
    ):
        super().__init__(timeout=60)
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.old_total = old_total
        self.used = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "มีแค่คนที่ใช้คำสั่งนี้เท่านั้นที่กดปุ่มได้",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="สุ่มใหม่", style=discord.ButtonStyle.primary, emoji="🎲")
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ไม่พบเกมนี้แล้ว",
                ephemeral=True
            )
            return

        player = get_player_in_game(self.channel_id, self.owner_id)
        if player is None:
            await interaction.response.send_message(
                "ไม่พบผู้เล่นในเกม",
                ephemeral=True
            )
            return

        success, reroll_left = use_reroll(self.channel_id, self.owner_id)
        if not success:
            await interaction.response.send_message(
                reroll_left,
                ephemeral=True
            )
            return

        snapshot_scores = game["turn_snapshot_scores"]
        db_player = ensure_player(self.owner_id, interaction.user.name)

        success, _ = update_player_score(
            self.channel_id,
            self.owner_id,
            -self.old_total
        )
        if not success:
            await interaction.response.send_message(
                "ไม่สามารถลบคะแนนเดิมได้",
                ephemeral=True
            )
            return

        result = roll_race_dice(
            style=player["style"],
            player=db_player,
            player_id=self.owner_id,
            score_map=snapshot_scores,
            turn=game["turn"],
            max_turn=game["max_turn"]
        )

        success, new_score = update_player_score(
            self.channel_id,
            self.owner_id,
            result["total"]
        )
        if not success:
            await interaction.response.send_message(
                "ไม่สามารถอัปเดตคะแนนใหม่ได้",
                ephemeral=True
            )
            return

        self.old_total = result["total"]

        embed = discord.Embed(
            title=f"{interaction.user.display_name} สุ่มใหม่สำเร็จ",
            color=discord.Color.orange()
        )
        embed.add_field(name="Style", value=player["style"], inline=True)
        embed.add_field(name="Phase", value=result["phase"], inline=True)
        embed.add_field(name="Distance", value=result["distance_color"], inline=True)
        embed.add_field(name="🎲 Dice", value=result["display"], inline=False)
        embed.add_field(name="✨ Total ใหม่", value=result["total_display"], inline=True)
        embed.add_field(name="🏁 Score ใหม่", value=new_score, inline=True)
        embed.set_footer(text=f"Reroll คงเหลือ {reroll_left}")

        if reroll_left <= 0:
            button.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)