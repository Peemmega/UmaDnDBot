import discord
from io import BytesIO

from utils.race.race_presets import RACE_PRESET, render_path
from utils.race_room_preview import create_racing_room_image
from utils.database import get_race_rankings
from views.join_view import LobbyView

from utils.game_manager import (
    create_game,get_game
)

TRAINING_TRACK_STAGE_KEYS = (
    "Training Track Short",
    "Training Track Mediem",
    "Training Track Long",
)


def get_preview_rankings(stage_key: str) -> list[dict]:
    try:
        return get_race_rankings(stage_key, limit=3)
    except Exception as e:
        print(f"failed loading race rankings for {stage_key}: {e}")
        return []


def build_lobby_preview_file(stage_key: str, stage_data: dict) -> discord.File:
    preview_stage = {
        "name": stage_data.get("name", stage_key),
        "turns": stage_data.get("turn", "-"),
        "track": stage_data.get("track", ""),
        "distance": stage_data.get("distance", ""),
        "path": stage_data.get("path", []),
        "race_key": stage_key,
        "thumbnail_key": stage_data.get("preview_thumbnail_key", stage_key),
        "background": stage_data.get("background"),
        "aptitude_bonus": stage_data.get("aptitude_bonus"),
        "top_rankings": get_preview_rankings(stage_key),
    }

    image = create_racing_room_image(preview_stage)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return discord.File(buffer, filename="race_room_preview.png")


def build_lobby_message_payload(channel_id: int):
    game = get_game(channel_id)

    if game is None:
        return build_lobby_embed(channel_id), None

    stage_key = game["stage_key"]
    stage_data = RACE_PRESET[stage_key]

    try:
        file = build_lobby_preview_file(stage_key, stage_data)
    except Exception as e:
        print(f"failed creating race room preview: {e}")
        return build_lobby_embed(channel_id), None

    return None, file

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
        title="สนาม: " + stage_data['name'],
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
        if stage.get("distance") == distance
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

def build_create_menu_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🏟️ Create Game",
        description=(
            "เลือกระยะของสนามก่อน\n\n"
            "• Sprint\n"
            "• Mile\n"
            "• Medium\n"
            "• Long"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="เลือกระยะเพื่อดูรายชื่อสนาม")
    return embed


def build_training_track_menu_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🏟️ Create Training Track",
        description=(
            "เลือกสนาม Training Track ที่ต้องการสร้าง\n\n"
            "• Training Track Short\n"
            "• Training Track Mediem\n"
            "• Training Track Long"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="เลือก Training Track จากรายการด้านล่าง")
    return embed

class StageSelectView(discord.ui.View):
    def __init__(self, channel_id, owner_id, distance):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.distance = distance

        self.add_item(StageDropdown(distance))

class ConfirmCreateView(discord.ui.View):
    def __init__(self, channel_id, owner_id, stage_key, *, training_tracks_only=False):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.stage_key = stage_key
        self.training_tracks_only = training_tracks_only

    @discord.ui.button(label="สร้าง", style=discord.ButtonStyle.success)
    async def create(self, interaction: discord.Interaction, button):
        channel_id = self.channel_id
        owner_id = interaction.user.id
        stage_key = self.stage_key

        success = create_game(channel_id, stage_key, owner_id)
        if not success:
            await interaction.response.send_message(
                "สร้างไม่สำเร็จ",
                ephemeral=True
            )
            return

        embed, file = build_lobby_message_payload(channel_id)

        # ✅ ตอบก่อน (กัน error interaction timeout)
        await interaction.response.defer()
        try:
            await interaction.message.delete()
        except discord.NotFound:
            pass

        if file:
            await interaction.channel.send(
                file=file,
                view=LobbyView(channel_id)
            )
        else:
            await interaction.channel.send(
                embed=embed,
                view=LobbyView(channel_id)
            )

    @discord.ui.button(label="ย้อนกลับ", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button):
        if self.training_tracks_only:
            await interaction.response.edit_message(
                embed=build_training_track_menu_embed(),
                view=TrainingTrackSelectView(self.channel_id, self.owner_id),
            )
            return

        await interaction.response.edit_message(
            embed=build_create_menu_embed(),
            view=CreateGameView(self.channel_id, self.owner_id)
        )

class StageDropdown(discord.ui.Select):
    def __init__(self, distance):
        stages = get_stages_by_distance(distance)

        options = [
            discord.SelectOption(
                label=stage['name'],
                value=key
            )
            for key, stage in stages.items()
        ]

        if not options:
            options = [
                discord.SelectOption(
                    label="ไม่มีสนาม",
                    value="__empty__"
                )
            ]

        super().__init__(
            placeholder="เลือกสนาม",
            options=options[:25],
            disabled=(options[0].value == "__empty__")
        )

    async def callback(self, interaction: discord.Interaction):
        stage_key = self.values[0]

        if stage_key == "__empty__":
            await interaction.response.send_message("ไม่มีสนามในหมวดนี้", ephemeral=True)
            return

        stage = RACE_PRESET[stage_key]
        embed = build_stage_preview_embed(stage)

        view = ConfirmCreateView(
            interaction.channel_id,
            interaction.user.id,
            stage_key
        )

        await interaction.response.edit_message(embed=embed, view=view)


class TrainingTrackDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=stage_key, value=stage_key)
            for stage_key in TRAINING_TRACK_STAGE_KEYS
            if stage_key in RACE_PRESET
        ]
        super().__init__(
            placeholder="เลือก Training Track",
            options=options,
            disabled=not options,
        )

    async def callback(self, interaction: discord.Interaction):
        stage_key = self.values[0]
        stage = RACE_PRESET[stage_key]
        await interaction.response.edit_message(
            embed=build_stage_preview_embed(stage),
            view=ConfirmCreateView(
                interaction.channel_id,
                interaction.user.id,
                stage_key,
                training_tracks_only=True,
            ),
        )


class TrainingTrackSelectView(discord.ui.View):
    def __init__(self, channel_id: int, owner_id: int):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.add_item(TrainingTrackDropdown())


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

        if not stages:
            embed = discord.Embed(
                title=f"📍 ระยะ: {distance.title()}",
                description="ไม่มีสนามในหมวดนี้",
                color=discord.Color.red()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=CreateGameView(self.channel_id, self.owner_id)
            )
            return

        embed = discord.Embed(
            title=f"📍 ระยะ: {distance.title()}",
            description="\n".join([f"• {stage['name']}" for stage in stages.values()]),
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
