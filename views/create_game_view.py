import discord

from utils.dice.race_presets import RACE_PRESET, render_path
from views.join_view import LobbyView

from utils.game_manager import (
    create_game,get_game
)

def build_lobby_embed(channel_id: int) -> discord.Embed:
    game = get_game(channel_id)
    if game is None:
        return discord.Embed(
            title="ไม่พบข้อมูลเกม",
            color=discord.Color.red()
        )

    stage_key = game["stage_key"]
    stage_data = RACE_PRESET[stage_key]

    embed = discord.Embed(
        title="สนาม: " + stage_data["name"],
        description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=stage_data["thumnail"])
    embed.add_field(name="👑 ผู้ดูแล", value=f"<@{game['owner_id']}>", inline=False)
    embed.add_field(name="จำนวนเทิร์น", value=f"⏱️ {stage_data['turn']}", inline=False)
    embed.add_field(
        name="🗺️ เส้นทาง",
        value=render_path(stage_data["path"]),
        inline=False
    )
    embed.set_image(url=stage_data["image"])

    embed.add_field(
        name="📢 วิธีเล่น",
        value=(
            "กดปุ่ม Join เพื่อเข้าร่วม\n"
            "ผู้สร้างใช้กดปุ่ม Start เพื่อเริ่มเกม"
        ),
        inline=False
    )

    mob_lines = []
    for user_id, info in game["players"].items():
        if str(user_id).startswith("mob_"):
            mob_lines.append(
                f"🤖 {info.get('display_name', info.get('username', 'Mob'))} | {info['style']}"
            )

    if not mob_lines:
        mob_lines.append("ไม่มี")

    embed.add_field(
        name="🤖 Auto Mobs",
        value="\n".join(mob_lines),
        inline=False
    )

    embed.set_footer(text="Game Status: Waiting for players")
    return embed

def get_stages_by_distance(distance):
    return {
        key: stage
        for key, stage in RACE_PRESET.items()
        if stage.get("distance_type") == distance
    }

def build_stage_preview_embed(stage):
    embed = discord.Embed(
        title=f"🏟️ {stage['name']}",
        description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=stage["thumnail"])
    embed.set_image(url=stage["image"])

    embed.add_field(name="⏱️ เทิร์น", value=stage["turn"])
    embed.add_field(name="🗺️ เส้นทาง", value=render_path(stage["path"]), inline=False)

    return embed

class StageSelectView(discord.ui.View):
    def __init__(self, channel_id, owner_id, distance):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.distance = distance

        self.add_item(StageDropdown(distance))

class ConfirmCreateView(discord.ui.View):
    def __init__(self, channel_id, owner_id, stage_key):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.stage_key = stage_key

    @discord.ui.button(label="Create", style=discord.ButtonStyle.success)
    async def create(self, interaction: discord.Interaction, button):
        success = create_game(
            self.channel_id,
            self.stage_key,
            self.owner_id
        )

        if not success:
            await interaction.response.send_message("สร้างไม่สำเร็จ", ephemeral=True)
            return

        # reuse lobby UI เดิมของคุณ
        embed = build_lobby_embed(self.channel_id)
        await interaction.response.edit_message(
            embed=embed,
            view=LobbyView(self.channel_id)
        )

    @discord.ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button):
        await interaction.response.edit_message(
            embed=discord.Embed(title="เลือกระยะ"),
            view=CreateGameView(self.channel_id, self.owner_id)
        )

class StageDropdown(discord.ui.Select):
    def __init__(self, distance):
        stages = get_stages_by_distance(distance)

        options = [
            discord.SelectOption(
                label=stage["name"],
                value=key
            )
            for key, stage in stages.items()
        ]

        super().__init__(
            placeholder="เลือกสนาม",
            options=options[:25]
        )

    async def callback(self, interaction: discord.Interaction):
        stage_key = self.values[0]
        stage = RACE_PRESET[stage_key]

        embed = build_stage_preview_embed(stage)

        view = ConfirmCreateView(
            interaction.channel_id,
            interaction.user.id,
            stage_key
        )

        await interaction.response.edit_message(embed=embed, view=view)

class CreateGameView(discord.ui.View):
    def __init__(self, channel_id: int, owner_id: int):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.selected_distance = None
        self.selected_stage = None

    async def select_distance(self, interaction, distance):
        self.selected_distance = distance

        stages = get_stages_by_distance(distance)

        embed = discord.Embed(
            title=f"📍 ระยะ: {distance.title()}",
            description="\n".join([f"• {s['name']}" for s in stages]) or "ไม่มีสนาม",
            color=discord.Color.blue()
        )

        view = StageSelectView(self.channel_id, self.owner_id, distance)

        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Sprint", style=discord.ButtonStyle.primary)
    async def sprint(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_distance(interaction, "sprint")

    @discord.ui.button(label="Mile", style=discord.ButtonStyle.primary)
    async def mile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_distance(interaction, "mile")

    @discord.ui.button(label="Medium", style=discord.ButtonStyle.primary)
    async def medium(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_distance(interaction, "medium")

    @discord.ui.button(label="Long", style=discord.ButtonStyle.primary)
    async def long(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_distance(interaction, "long")