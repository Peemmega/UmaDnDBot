import discord
from io import BytesIO

from utils.race.race_presets import (
    RACE_PRESET,
    get_race_distance_type,
    get_race_turns,
    render_path,
)
from utils.race_room_preview import create_racing_room_image
from utils.database import get_race_rankings
from views.join_view import LobbyView

from utils.game_manager import create_game, get_game

TRAINING_TRACK_STAGE_KEYS = (
    "Training Track Short",
    "Training Track Medium",
    "Training Track Long",
)

STAGE_PAGE_SIZE = 25


def get_preview_rankings(stage_key: str) -> list[dict]:
    try:
        return get_race_rankings(stage_key, limit=3)
    except Exception as e:
        print(f"failed loading race rankings for {stage_key}: {e}")
        return []


def build_lobby_preview_file(stage_key: str, stage_data: dict) -> discord.File:
    preview_stage = {
        "name": stage_data.get("name", stage_key),
        "turns": get_race_turns(stage_data),
        "track": stage_data.get("track", ""),
        "distance": get_race_distance_type(stage_data),
        "path": stage_data.get("path", []),
        "race_key": stage_key,
        "thumbnail_key": stage_data.get("preview_thumbnail_key", stage_key),
        "thumbnail": stage_data.get("thumbnail") or stage_data.get("thumnail"),
        "background": stage_data.get("background"),
        "track_image": stage_data.get("track_image"),
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
        return discord.Embed(title="ไม่พบข้อมูลเกม", color=discord.Color.red())

    stage_key = game["stage_key"]
    stage_data = RACE_PRESET[stage_key]

    embed = discord.Embed(
        title="สนาม: " + stage_data["name"],
        description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
        color=discord.Color.green(),
    )

    embed.set_thumbnail(url=stage_data["thumnail"])
    embed.add_field(name="👑 ผู้ดูแล", value=f"<@{game['owner_id']}>", inline=False)
    embed.add_field(name="จำนวนเทิร์น", value=f"⏱️ {get_race_turns(stage_data)}", inline=False)
    embed.add_field(
        name="🗺️ เส้นทาง", value=render_path(stage_data["path"]), inline=False
    )
    embed.set_image(url=stage_data["image"])

    embed.add_field(
        name="📢 วิธีเล่น",
        value=("กดปุ่ม Join เพื่อเข้าร่วม\n" "ผู้สร้างใช้กดปุ่ม Start เพื่อเริ่มเกม"),
        inline=False,
    )

    mob_lines = []
    for user_id, info in game["players"].items():
        if str(user_id).startswith("mob_"):
            mob_lines.append(
                f"🤖 {info.get('display_name', info.get('username', 'Mob'))} | {info['style']}"
            )

    if not mob_lines:
        mob_lines.append("ไม่มี")

    embed.add_field(name="🤖 Auto Mobs", value="\n".join(mob_lines), inline=False)

    embed.set_footer(text="Game Status: Waiting for players")
    return embed


def get_stages_by_distance(distance):
    return {
        key: stage
        for key, stage in RACE_PRESET.items()
        if get_race_distance_type(stage) == distance
    }


def build_stage_preview_embed(stage, *, is_legend=False):
    embed = discord.Embed(
        title=f"🏟️ {'Legend Race · ' if is_legend else ''}{stage['name']}",
        description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
        color=discord.Color.green(),
    )

    embed.set_thumbnail(url=stage["thumnail"])
    embed.set_image(url=stage["image"])

    embed.add_field(name="⏱️ เทิร์น", value=get_race_turns(stage))
    embed.add_field(name="🗺️ เส้นทาง", value=render_path(stage["path"]), inline=False)

    return embed


def build_create_menu_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🏟️ Create Game",
        description=(
            "เลือกระยะของสนามก่อน\n\n" "• Sprint\n" "• Mile\n" "• Medium\n" "• Long"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="เลือกระยะเพื่อดูรายชื่อสนาม")
    return embed


def build_legend_create_menu_embed() -> discord.Embed:
    embed = build_create_menu_embed()
    embed.title = "🏟️ Create Legend Race"
    embed.description = "เลือกสนามปกติเพื่อใช้สร้าง Legend Race\n\n" + embed.description.split("\n\n", 1)[-1]
    embed.color = discord.Color.gold()
    embed.set_footer(text="สนามที่เลือกจะถูกบันทึกในประวัติเป็น Legend Race")
    return embed


def build_training_track_menu_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🏟️ Create Training Track",
        description=(
            "เลือกสนาม Training Track ที่ต้องการสร้าง\n\n"
            "• Training Track Short\n"
            "• Training Track Medium\n"
            "• Training Track Long"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="เลือก Training Track จากรายการด้านล่าง")
    return embed


class StageSelectView(discord.ui.View):
    def __init__(self, channel_id, owner_id, distance, page=0, *, is_legend=False):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.is_legend = is_legend
        self.distance = distance
        self.page = page
        self.stage_keys = list(get_stages_by_distance(distance))
        self.page_count = max(1, (len(self.stage_keys) + STAGE_PAGE_SIZE - 1) // STAGE_PAGE_SIZE)

        start = page * STAGE_PAGE_SIZE
        page_stage_keys = self.stage_keys[start : start + STAGE_PAGE_SIZE]
        self.add_item(StageDropdown(page_stage_keys))
        self.add_item(StagePageButton("ก่อนหน้า", page - 1, disabled=page <= 0, row=1))
        self.add_item(StagePageButton(f"หน้า {page + 1}/{self.page_count}", page, disabled=True, row=1))
        self.add_item(StagePageButton("ถัดไป", page + 1, disabled=page + 1 >= self.page_count, row=1))
        self.add_item(StagePageButton("เลือกระยะใหม่", None, row=1, back=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.is_legend and interaction.user.id != self.owner_id:
            await interaction.response.send_message("เมนู Legend Race นี้ใช้ได้เฉพาะผู้สร้างคำสั่ง", ephemeral=True)
            return False
        return True

    def build_embed(self):
        start = self.page * STAGE_PAGE_SIZE
        page_keys = self.stage_keys[start : start + STAGE_PAGE_SIZE]
        page_names = [RACE_PRESET[key]["name"] for key in page_keys]
        embed = discord.Embed(
            title=f"📍 ระยะ: {self.distance.title()} · หน้า {self.page + 1}/{self.page_count}",
            description="\n".join(f"• {name}" for name in page_names),
            color=discord.Color.blue(),
        )
        if self.page_count > 1:
            embed.set_footer(text=f"มีสนามทั้งหมด {len(self.stage_keys)} แห่ง ใช้ปุ่มก่อนหน้า/ถัดไปเพื่อดูหน้าอื่น")
        return embed


class StagePageButton(discord.ui.Button):
    def __init__(self, label, target_page, *, disabled=False, row=1, back=False):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, disabled=disabled, row=row)
        self.target_page = target_page
        self.back = back

    async def callback(self, interaction: discord.Interaction):
        current_view: StageSelectView = self.view
        if self.back:
            await interaction.response.edit_message(
                embed=build_legend_create_menu_embed() if current_view.is_legend else build_create_menu_embed(),
                view=CreateGameView(current_view.channel_id, current_view.owner_id, is_legend=current_view.is_legend),
            )
            return

        new_view = StageSelectView(
            current_view.channel_id,
            current_view.owner_id,
            current_view.distance,
            page=self.target_page,
            is_legend=current_view.is_legend,
        )
        await interaction.response.edit_message(embed=new_view.build_embed(), view=new_view)


class ConfirmCreateView(discord.ui.View):
    def __init__(self, channel_id, owner_id, stage_key, *, training_tracks_only=False, is_legend=False):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.stage_key = stage_key
        self.training_tracks_only = training_tracks_only
        self.is_legend = is_legend

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.is_legend and interaction.user.id != self.owner_id:
            await interaction.response.send_message("เมนู Legend Race นี้ใช้ได้เฉพาะผู้สร้างคำสั่ง", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="สร้าง", style=discord.ButtonStyle.success)
    async def create(self, interaction: discord.Interaction, button):
        channel_id = self.channel_id
        owner_id = interaction.user.id
        stage_key = self.stage_key

        success = create_game(channel_id, stage_key, owner_id, is_legend=self.is_legend)
        if not success:
            await interaction.response.send_message("สร้างไม่สำเร็จ", ephemeral=True)
            return

        embed, file = build_lobby_message_payload(channel_id)

        # ✅ ตอบก่อน (กัน error interaction timeout)
        await interaction.response.defer()
        try:
            await interaction.message.delete()
        except discord.NotFound:
            pass

        if file:
            await interaction.channel.send(file=file, view=LobbyView(channel_id))
        else:
            await interaction.channel.send(embed=embed, view=LobbyView(channel_id))

    @discord.ui.button(label="ย้อนกลับ", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button):
        if self.training_tracks_only:
            await interaction.response.edit_message(
                embed=build_training_track_menu_embed(),
                view=TrainingTrackSelectView(self.channel_id, self.owner_id),
            )
            return

        await interaction.response.edit_message(
            embed=build_legend_create_menu_embed() if self.is_legend else build_create_menu_embed(),
            view=CreateGameView(self.channel_id, self.owner_id, is_legend=self.is_legend),
        )


class StageDropdown(discord.ui.Select):
    def __init__(self, stage_keys):
        options = [
            discord.SelectOption(label=RACE_PRESET[key]["name"], value=key)
            for key in stage_keys
        ]

        if not options:
            options = [discord.SelectOption(label="ไม่มีสนาม", value="__empty__")]

        super().__init__(
            placeholder="เลือกสนาม",
            options=options,
            disabled=(options[0].value == "__empty__"),
        )

    async def callback(self, interaction: discord.Interaction):
        stage_key = self.values[0]

        if stage_key == "__empty__":
            await interaction.response.send_message(
                "ไม่มีสนามในหมวดนี้", ephemeral=True
            )
            return

        stage = RACE_PRESET[stage_key]
        embed = build_stage_preview_embed(stage, is_legend=self.view.is_legend)

        view = ConfirmCreateView(interaction.channel_id, self.view.owner_id, stage_key, is_legend=self.view.is_legend)

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
    def __init__(self, channel_id: int, owner_id: int, *, is_legend=False):
        super().__init__(timeout=300)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.is_legend = is_legend
        self.selected_distance = None
        self.selected_stage = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.is_legend and interaction.user.id != self.owner_id:
            await interaction.response.send_message("เมนู Legend Race นี้ใช้ได้เฉพาะผู้สร้างคำสั่ง", ephemeral=True)
            return False
        return True

    async def select_distance(self, interaction, distance):
        self.selected_distance = distance

        stages = get_stages_by_distance(distance)

        if not stages:
            embed = discord.Embed(
                title=f"📍 ระยะ: {distance.title()}",
                description="ไม่มีสนามในหมวดนี้",
                color=discord.Color.red(),
            )

            await interaction.response.edit_message(
                embed=embed, view=CreateGameView(self.channel_id, self.owner_id, is_legend=self.is_legend)
            )
            return

        view = StageSelectView(self.channel_id, self.owner_id, distance, is_legend=self.is_legend)
        await interaction.response.edit_message(embed=view.build_embed(), view=view)

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
