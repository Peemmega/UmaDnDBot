import discord
from utils.game_manager import (
    add_player,
    is_game_started,
    get_game,
    is_owner,
    start_game,
)
from utils.dice_presets import DICE_PRESET, MAX_DICE_VALUE
import math

STYLES = ["Front", "Pace", "Late", "End"]
PHASES = [1, 2, 3, 4]

def build_phase_text(max_turn: int) -> str:
    phase_size = max_turn / 4

    lines = []
    start_turn = 1

    for phase in range(1, 5):
        end_turn = math.ceil(phase * phase_size)

        if phase == 4:
            end_turn = max_turn

        lines.append(f"Phase {phase} = Turn {start_turn}-{end_turn}")
        start_turn = end_turn + 1

    return "\n".join(lines)

def format_rule(rule: dict) -> str:
    d = rule["d"]
    kh = rule.get("kh")

    text = f"d{MAX_DICE_VALUE}" if d == 1 else f"{d}d{MAX_DICE_VALUE}"
    if kh is not None:
        text += f"kh{kh}"
    return text


def build_style_table(color_type: str) -> str:
    lines = []
    for style in STYLES:
        p1 = format_rule(DICE_PRESET[style][color_type][1])
        p2 = format_rule(DICE_PRESET[style][color_type][2])
        p3 = format_rule(DICE_PRESET[style][color_type][3])
        p4 = format_rule(DICE_PRESET[style][color_type][4])

        lines.append(
            f"**{style}** | {p1} | {p2} | {p3} | {p4}"
        )

    return "\n".join(lines)


def build_join_style_embed(max_turn: int) -> discord.Embed:
    embed = discord.Embed(
        title="🏇 เลือกสายวิ่ง",
        description=(
            "เลือกสายวิ่งก่อนเข้าร่วมการแข่งขัน\n\n"
            f"**Phase จะเปลี่ยนตามสนาม ({max_turn} เทิร์น)**\n"
            f"{build_phase_text(max_turn)}"
        ),
        color=discord.Color.gold()
    )

    embed.add_field(
        name="⚪ White Roll",
        value=(
            "**Style | P1 | P2 | P3 | P4**\n"
            f"{build_style_table('White')}"
        ),
        inline=False
    )

    embed.add_field(
        name="🟡 Gold Roll",
        value=(
            "**Style | P1 | P2 | P3 | P4**\n"
            f"{build_style_table('Gold')}"
        ),
        inline=False
    )

    embed.add_field(
        name="📘 คำอธิบาย",
        value=(
            "**d** = จำนวนลูกเต๋าที่ทอย\n"
            "**d20** = ลูกเต๋าแต่ละลูกสุ่ม 1-20\n"
            "**kh** = เลือกค่ามากสุดจำนวนที่กำหนด\n"
            f"เช่น `6d20kh2` = ทอย 6 ลูก แล้วเลือก 2 ลูกที่มากสุดมารวม\n"
            "**White / Gold** = ประเภทการทอยตามระยะห่างกับผู้เล่นอื่น"
        ),
        inline=False
    )

    embed.set_footer(text="กดปุ่มด้านล่างเพื่อเลือก Front / Pace / Late / End")
    return embed


class StyleSelectView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=60)
        self.channel_id = channel_id

    async def pick_style(self, interaction: discord.Interaction, style: str):
        if is_game_started(self.channel_id):
            await interaction.response.send_message(
                "เกมเริ่มแล้ว ไม่สามารถเข้าร่วมได้",
                ephemeral=True
            )
            return

        success, message = add_player(
            self.channel_id,
            interaction.user.id,
            style
        )

        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="เลือกสายเรียบร้อยแล้ว",
            embed=None,
            view=self
        )

        embed = discord.Embed(
            title="🏇 ผู้เล่นเข้าร่วม!",
            color=discord.Color.green()
        )
        embed.add_field(name="ผู้เล่น", value=interaction.user.mention, inline=True)
        embed.add_field(name="Style", value=style, inline=True)
        embed.add_field(name="Score", value="0", inline=True)

        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Front", style=discord.ButtonStyle.grey)
    async def front_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.pick_style(interaction, "Front")

    @discord.ui.button(label="Pace", style=discord.ButtonStyle.grey)
    async def pace_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.pick_style(interaction, "Pace")

    @discord.ui.button(label="Late", style=discord.ButtonStyle.grey)
    async def late_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.pick_style(interaction, "Late")

    @discord.ui.button(label="End", style=discord.ButtonStyle.grey)
    async def end_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.pick_style(interaction, "End")


class LobbyView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=300)
        self.channel_id = channel_id

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="🏇")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if is_game_started(self.channel_id):
            await interaction.response.send_message(
                "เกมเริ่มแล้ว ไม่สามารถเข้าร่วมได้",
                ephemeral=True
            )
            return

        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=build_join_style_embed(game["max_turn"]),
            view=StyleSelectView(self.channel_id),
            ephemeral=True
        )

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary, emoji="▶️")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = get_game(self.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return

        if not is_owner(self.channel_id, interaction.user.id):
            await interaction.response.send_message(
                "มีแค่ผู้สร้างเกมเท่านั้นที่เริ่มเกมได้",
                ephemeral=True
            )
            return

        success, message = start_game(self.channel_id)
        if not success:
            await interaction.response.send_message(message, ephemeral=True)
            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            view=self
        )

        game = get_game(self.channel_id)

        embed = discord.Embed(
            title="🏁 เกมเริ่มแล้ว!",
            description=f"ด่าน: {game['stage_name']}",
            color=discord.Color.gold()
        )
        embed.add_field(name="เทิร์นปัจจุบัน", value=str(game["turn"]), inline=True)
        embed.add_field(name="ผู้เริ่มเกม", value=interaction.user.mention, inline=True)

        await interaction.followup.send(embed=embed)