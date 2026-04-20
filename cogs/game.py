import discord
from discord.ext import commands
from discord import app_commands

from views.confirmDeleteGameView import ConfirmDeleteView
from views.join_view import LobbyView
from utils.icon_presets import Status_Icon_Type
from utils.skill.skill_presets import SKILLS, ICON
from utils.narrater import (
    generate_commentary,
    build_narrator_players_from_ranked,
    generate_finish_commentary,
)
from utils.music_manager import play_bgm, stop_bgm

from utils.dice.race_presets import RACE_PRESET, PATH_TYPE_ICON, build_track_progress_text, build_current_track_text
from utils.dice.roll_service import (
    execute_player_roll
)
from views.use_skill_view import UseSkillView
from utils.database import ensure_player, get_player_skill_slots
from utils.dice.race_presets import (
    get_current_path_type, 
    build_path_effect_text, 
    PATH_TYPE_TEXT
)

from utils.skill.skill_manager import build_skill_card_text

from utils.dice.race_dice import (
    get_phase_from_turn,
)

from utils.game_manager import (
    create_game,
    get_game,
    is_owner,
    next_turn,
    get_player_in_game,
    get_players,
    delete_game,
    can_player_roll, 
    get_ranked_players,
    have_all_players_rolled,
    start_turn_confirmation,
    is_skill_on_cooldown,
    add_mob_from_preset
)

def render_path(path: list[int]) -> str:
    return "".join(PATH_TYPE_ICON.get(x, "⬜") for x in path)

def build_game_end_embed(ranked_players, commentary_text: str | None = None):
    rank_lines = []
    for index, (user_id, info) in enumerate(ranked_players, start=1):
        rank_lines.append(
            f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
        )

    if not rank_lines:
        rank_lines.append("ยังไม่มีผู้เล่น")

    winner_text = "ไม่มีผู้ชนะ"
    if ranked_players:
        winner_id, winner_info = ranked_players[0]
        winner_text = (
            f"🏆 ผู้ชนะ: <@{winner_id}>\n"
            f"Style: {winner_info['style']}\n"
            f"Score: {winner_info['score']}"
        )

    embed = discord.Embed(
        title="🏁 เกมจบแล้ว",
        color=discord.Color.red(),
        description=(
            f"{winner_text}\n\n"
            f"อันดับสุดท้าย:\n" + "\n".join(rank_lines)
        )
    )

    if commentary_text:
        embed.add_field(
            name="📢 Narrator",
            value=commentary_text[:1000],
            inline=False
        )

    embed.set_image(
        url="https://media.discordapp.net/attachments/1493575422007447622/1493676112952426629/i-won-taurus-cup-with-tm-opera-o-v0-w2a0zxpycglf1.gif"
    )
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1493575422007447622/1493678180702355568/utx_txt_order_00.png"
    )

    return embed

def build_slot_display(skill_id: str | None, channel_id: int, user_id: int) -> str:
    if not skill_id:
        return "➖ ว่าง"

    on_cd, cd_left = is_skill_on_cooldown(channel_id, user_id, skill_id)

    skill = SKILLS.get(skill_id)
    emoji = ICON.get(skill.get("icon"), "❓")
    name = skill["name"]
    
    if on_cd:
        return (
            f"{emoji} `{skill_id}` **{name}**\n"
            f"⏳ **คูลดาวน์ {cd_left} เทิร์น**\n"
            f"--------------------------------------"
        )

    return build_skill_card_text(skill_id)

class GameCog(commands.GroupCog, name="game"):
    def __init__(self, bot):
        self.bot = bot

    def can_use_roll_skill(self, channel_id: int, user_id: int):
        from utils.game_manager import can_player_roll
        can_roll, message = can_player_roll(channel_id, user_id)
        if not can_roll:
            return False, "คุณใช้สิทธิ์ทอยในเทิร์นนี้ไปแล้ว จึงใช้สกิลประเภท Active Roll ไม่ได้"
        return True, None

    async def handle_after_roll(self, interaction: discord.Interaction, game: dict):
        if have_all_players_rolled(interaction.channel_id):
            if not game["awaiting_turn_confirm"]:
                start_turn_confirmation(interaction.channel_id)

                ranked_players = get_ranked_players(interaction.channel_id)
                phase = get_phase_from_turn(game["turn"], game["max_turn"])

                rank_lines = []
                for index, (user_id, info) in enumerate(ranked_players, start=1):
                    rank_lines.append(
                        f"#{index} <@{user_id}> | {info['style']} | Score: {info['score']}"
                    )

                if not rank_lines:
                    rank_lines.append("ยังไม่มีผู้เล่น")

                confirm_embed = discord.Embed(
                    title=f"📊 จบเทิร์น {game['turn']}",
                    color=discord.Color.blurple(),
                    description=(
                        f"Phase: {phase}\n\n"
                        f"อันดับคะแนน:\n" + "\n".join(rank_lines)
                    )
                )
                confirm_embed.set_footer(text="ทุกคนต้องกดยืนยันก่อนจะไปเทิร์นถัดไป")

                from views.turn_confirm_view import TurnConfirmView
                view = TurnConfirmView(self, interaction.channel_id)
                msg = await interaction.followup.send(embed=confirm_embed, view=view)
                view.message = msg

    @app_commands.command(name="create", description="สร้างเกมใหม่")
    @app_commands.describe(stage="เลือกสนาม")
    @app_commands.choices(stage=[
        app_commands.Choice(name=RACE_PRESET["NHK"]["name"], value="NHK"),
        app_commands.Choice(name=RACE_PRESET["TakarazukaKinen"]["name"], value="TakarazukaKinen"),
        app_commands.Choice(name=RACE_PRESET["TennoShoSpring"]["name"], value="TennoShoSpring"),
        app_commands.Choice(name=RACE_PRESET["SatsukiSho"]["name"], value="SatsukiSho"),
        app_commands.Choice(name=RACE_PRESET["JapaneseDerby"]["name"], value="JapaneseDerby"),
        app_commands.Choice(name=RACE_PRESET["ArimaKinen"]["name"], value="ArimaKinen"),
        app_commands.Choice(name=RACE_PRESET["JapanCup"]["name"], value="JapanCup"),
        app_commands.Choice(name=RACE_PRESET["OsakaHai"]["name"], value="OsakaHai"),
        app_commands.Choice(name=RACE_PRESET["TennoShoAutumn"]["name"], value="TennoShoAutumn"),
        app_commands.Choice(name=RACE_PRESET["OkaSho"]["name"], value="OkaSho"),
        app_commands.Choice(name=RACE_PRESET["MileChampionship"]["name"], value="MileChampionship"),
        app_commands.Choice(name="Random", value="Random"),
    ])
    async def create(self, interaction: discord.Interaction, stage: app_commands.Choice[str]):
        channel_id = interaction.channel_id
        owner_id = interaction.user.id
        stage_key = stage.value

        success = create_game(channel_id, stage_key, owner_id)
        if not success:
            await interaction.response.send_message(
                "ห้องนี้มีเกมอยู่แล้ว หรือสนามไม่ถูกต้อง",
                ephemeral=True
            )
            return

        stage_data = RACE_PRESET[stage_key]

        embed = discord.Embed(
            title="สนาม: " + stage_data["name"],
            description="เตรียมตัวเข้าสู่สนามแข่ง 🏇",
            color=discord.Color.green()

        )

        embed.set_thumbnail(url=stage_data["thumnail"])

        embed.add_field(name="👑 ผู้ดูแล", value=interaction.user.mention, inline=False)
        embed.add_field(name="จำนวนเทิร์น", value=f"⏱️ {stage_data['turn']}", inline=False)
        embed.add_field(
            name="🗺️ เส้นทาง",
            value=render_path(stage_data["path"]),
            inline=False
        )

        embed.set_image(
            url=stage_data["image"]
        )

        embed.add_field(
            name="📢 วิธีเล่น",
            value=(
                "กดปุ่ม Join เพื่อเข้าร่วม\n"
                "ผู้สร้างใช้กดปุ่ม Start เพื่อเริ่มเกม"
            ),
            inline=False
        )
        
        embed.set_footer(text="Game Status: Waiting for players")

        await interaction.response.send_message(
            embed=embed,
            view=LobbyView(channel_id)
        )

    @discord.app_commands.command(name="add_mob", description="เพิ่ม mob preset เข้าการแข่งขัน")
    @discord.app_commands.describe(preset="preset ของ mob")
    @discord.app_commands.choices(preset=[
        discord.app_commands.Choice(name="Rookie Front", value="rookie_front"),
        discord.app_commands.Choice(name="Field Pace", value="runner_pace"),
        discord.app_commands.Choice(name="Shadow Chaser", value="chaser_late"),
        discord.app_commands.Choice(name="Sprint Phantom", value="sprinter_end"),
        discord.app_commands.Choice(name="Champion Alpha", value="boss_champion"),
    ])
    async def add_mob(self, interaction: discord.Interaction, preset: discord.app_commands.Choice[str]):
        success, message = add_mob_from_preset(interaction.channel_id, preset.value)
        await interaction.response.send_message(message, ephemeral=True)


    async def process_next_turn(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.followup.send("เกมยังไม่เข้าร่วม race", ephemeral=True)
            return

        # เก็บสถานะก่อนขึ้นเทิร์น
        previous_ranked_players = get_ranked_players(interaction.channel_id)
        previous_players = build_narrator_players_from_ranked(previous_ranked_players)

        new_turn, mob_embeds = next_turn(interaction.channel_id)
        # เกมจบ
        if new_turn > game["max_turn"]:
            ranked_players = get_ranked_players(interaction.channel_id)

            commentary_text = None
            try:
                final_players = build_narrator_players_from_ranked(ranked_players)
                commentary_text = await generate_finish_commentary(
                    final_players,
                    stage_name=game.get("stage_name")
                )
            except Exception as e:
                print("Finish narrator error:", e)

            embed = build_game_end_embed(ranked_players, commentary_text=commentary_text)
            await interaction.followup.send(embed=embed)
            stop_bgm(interaction.guild)
            delete_game(interaction.channel_id)
            return

        # ดึง game ใหม่หลังเปลี่ยน state
        game = get_game(interaction.channel_id)

        phase = get_phase_from_turn(new_turn, game["max_turn"])
        ranked_players = get_ranked_players(interaction.channel_id)
        current_players = build_narrator_players_from_ranked(ranked_players)

        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            rank_lines.append(
                f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
            )

        if not rank_lines:
            rank_lines.append("ยังไม่มีผู้เล่น")

        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

        track_preview = build_track_progress_text(game["path"], new_turn)
        current_track_text = build_current_track_text(game["path"], new_turn)

        commentary_text = None
        try:
            commentary_text = await generate_commentary(
                previous_players,
                current_players,
                turn=new_turn,
                max_turn=game["max_turn"],
                event_text=f"เริ่มเทิร์น {new_turn} เส้นทางเป็น {path_label}"
            )
        except Exception as e:
            print("Narrator error:", e)

        embed = discord.Embed(
            title=f"เข้าสู่เทิร์น {new_turn}",
            color=discord.Color.green(),
            description=(
                f"Phase: {phase}\n"
                f"เส้นทางเทิร์นนี้:\n{track_preview}\n{current_track_text}\n\n"
                f"อันดับคะแนน:\n" + "\n".join(rank_lines)
            )
        )

        embed.add_field(
            name="Effect",
            value=build_path_effect_text(path_type),
            inline=False
        )

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1494733536656097340/1495342542470778983/utx_ico_itemlist_roommatch_00.png?ex=69e5e5c4&is=69e49444&hm=8dcadb111d4f0a7cd59d85e3c2023bc491ba78c8edd65ba2ac3f1471e89d0656&=&format=webp&quality=lossless&width=228&height=200")

        if commentary_text:
            embed.add_field(
                name="📢 Narrator",
                value=commentary_text[:1000],
                inline=False
            )

        # lastPhase, Phase = is_first_turn_of_phase(new_turn, game["max_turn"])
        # print(lastPhase, Phase)

        # if (Phase == 4 and lastPhase):
        #     ok,msg = play_bgm(interaction.guild) 
        #     print(msg)

        await interaction.followup.send(embed=embed)
        for mob_embed in mob_embeds:
            await interaction.followup.send(embed=mob_embed)

    async def process_next_turn_from_timeout(self, channel: discord.TextChannel):
        game = get_game(channel.id)
        if game is None:
            return

        # เก็บสถานะก่อนขึ้นเทิร์น
        previous_ranked_players = get_ranked_players(channel.id)
        previous_players = build_narrator_players_from_ranked(previous_ranked_players)

        new_turn, mob_embeds = next_turn(channel.id)

        # เกมจบ
        if new_turn > game["max_turn"]:
            ranked_players = get_ranked_players(channel.id)

            commentary_text = None
            try:
                final_players = build_narrator_players_from_ranked(ranked_players)
                commentary_text = await generate_finish_commentary(
                    final_players,
                    stage_name=game.get("stage_name")
                )
            except Exception as e:
                print("Finish narrator error:", e)

            embed = build_game_end_embed(ranked_players, commentary_text=commentary_text)
            await channel.send(embed=embed)

            ok, msg = stop_bgm(channel.guild)
            print(f"[Music] stop on timeout turn end: {msg}")

            delete_game(channel.id)
            return

        # ดึง game ใหม่หลังเปลี่ยน state
        game = get_game(channel.id)

        phase = get_phase_from_turn(new_turn, game["max_turn"])
        ranked_players = get_ranked_players(channel.id)
        current_players = build_narrator_players_from_ranked(ranked_players)

        rank_lines = []
        for index, (user_id, info) in enumerate(ranked_players, start=1):
            rank_lines.append(
                f"{index}. <@{user_id}> | {info['style']} | Score: {info['score']}"
            )

        if not rank_lines:
            rank_lines.append("ยังไม่มีผู้เล่น")

        path_type = get_current_path_type(game)
        path_label = PATH_TYPE_TEXT.get(path_type, "➡️ ทางตรง")

        track_preview = build_track_progress_text(game["path"], new_turn)
        current_track_text = build_current_track_text(game["path"], new_turn)

        commentary_text = None
        try:
            commentary_text = await generate_commentary(
                previous_players,
                current_players,
                turn=new_turn,
                max_turn=game["max_turn"],
                event_text=f"เริ่มเทิร์น {new_turn} เส้นทางเป็น {path_label}"
            )
        except Exception as e:
            print("Narrator error:", e)

        embed = discord.Embed(
            title=f"เข้าสู่เทิร์น {new_turn} (Auto)",
            color=discord.Color.green(),
            description=(
                f"Phase: {phase}\n"
                f"เส้นทางเทิร์นนี้:\n{track_preview}\n{current_track_text}\n\n"
                f"อันดับคะแนน:\n" + "\n".join(rank_lines)
            )
        )

        embed.add_field(
            name="Effect",
            value=build_path_effect_text(path_type),
            inline=False
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1494733536656097340/1495342542470778983/utx_ico_itemlist_roommatch_00.png?ex=69e5e5c4&is=69e49444&hm=8dcadb111d4f0a7cd59d85e3c2023bc491ba78c8edd65ba2ac3f1471e89d0656&=&format=webp&quality=lossless&width=228&height=200")

        if commentary_text:
            embed.add_field(
                name="📢 Narrator",
                value=commentary_text[:1000],
                inline=False
            )

        # lastPhase, Phase = is_first_turn_of_phase(new_turn, game["max_turn"])
        # if Phase == 4 and lastPhase:
        #     ok, msg = play_bgm(channel.guild)
        #     print(f"[Music] play on timeout turn: {msg}")

        await channel.send(embed=embed)

    @app_commands.command(name="myinfo", description="ดูข้อมูลของตัวเองในเกม")
    async def myinfo(self, interaction: discord.Interaction):
        player = get_player_in_game(interaction.channel_id, interaction.user.id)
        if player is None:
            await interaction.response.send_message(
                "คุณยังไม่ได้เข้าร่วมเกมนี้",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"ข้อมูลของ {interaction.user.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Style", value=player["style"], inline=True)
        embed.add_field(name="Score", value=player["score"], inline=True)
        embed.add_field(name="Reroll คงเหลือ", value=player["reroll_left"], inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="ดูข้อมูลเกมในห้องนี้")
    async def info(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)
        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return
        
        status_text = "Started" if game["started"] else "Waiting"
        players = get_players(interaction.channel_id)
        player_lines = []

        if players:
            for user_id, info in players.items():
                player_lines.append(
                    f"<@{user_id}> | Style: {info['style']} | Score: {info['score']}"
                )
        else:
            player_lines.append("ยังไม่มีผู้เล่น")

        embed = discord.Embed(
            title=f"Race: {game['stage_name']}",
            color=discord.Color.green(),
            description=(
                f"เจ้าของเกม: <@{game['owner_id']}>\n"
                f"สถานะ: {status_text}\n"
                f"เทิร์น: {game['turn']}\n\n"
                f"ผู้เล่น:\n" + "\n".join(player_lines)
            )
        )

        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/697810514448744448/1493624841989914714/utx_ico_itemlist_dailyrace_00.png"
        )

        await interaction.response.send_message(embed=embed)

    

    @app_commands.command(name="close", description="ลบหรือจบเกมในห้องนี้")
    async def close(self, interaction: discord.Interaction):
        game = get_game(interaction.channel_id)

        if game is None:
            await interaction.response.send_message(
                "ยังไม่มีเกมในห้องนี้",
                ephemeral=True
            )
            return

        if not is_owner(interaction.channel_id, interaction.user.id):
            await interaction.response.send_message(
                "มีแค่ผู้สร้างเกมเท่านั้นที่ลบเกมได้",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "คุณแน่ใจหรือไม่ว่าจะลบเกมนี้?",
            view=ConfirmDeleteView(interaction.channel_id),
            ephemeral=True
        )

    @app_commands.command(name="run", description="ทอยเต๋าเดินในเทิร์นนี้")
    async def run(self, interaction: discord.Interaction):
        await interaction.response.defer()

        can_roll, message = can_player_roll(interaction.channel_id, interaction.user.id)
        if not can_roll:
            await interaction.followup.send(message, ephemeral=True)
            return

        success, payload = await execute_player_roll(
            interaction,
            title_prefix="วิ่งในเทิร์นนี้",
            mark_roll=True,
            allow_reroll_view=True,
        )

        if not success:
            await interaction.followup.send(payload["message"], ephemeral=True)
            return

        send_kwargs = {
            "content": f"🎯 <@{interaction.user.id}> กำลังวิ่ง!",
            "embed": payload["embed"],
        }
        if payload["view"] is not None:
            send_kwargs["view"] = payload["view"]

        await interaction.followup.send(**send_kwargs)

        game = payload["game"]
        await self.handle_after_roll(interaction, game)


    @discord.app_commands.command(name="skill", description="เปิดเมนูใช้สกิล")
    async def skill(self, interaction: discord.Interaction):
        ensure_player(interaction.user.id, interaction.user.name)

        playerInGame = get_player_in_game(
            interaction.channel_id,
            interaction.user.id
        )

        if playerInGame and playerInGame.get("skills"):
            slots = {
                "slot_1": playerInGame["skills"].get(1),
                "slot_2": playerInGame["skills"].get(2),
                "slot_3": playerInGame["skills"].get(3),
            }
            wit_mana = playerInGame.get("wit_mana", 0)
        else:
            slots = get_player_skill_slots(interaction.user.id)
            wit_mana = "ยังไม่อยู่ในเกม"

        if playerInGame is None:
            await interaction.response.send_message("เกมยังไม่เข้าร่วม race", ephemeral=True)
            return

        if slots is None:
            await interaction.response.send_message("ไม่พบข้อมูลผู้เล่น", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📘 Skill Menu: {interaction.user.display_name}",
            color=discord.Color.blurple()
        )

        zone = playerInGame.get("zone")
        if not zone:
            return False, "ไม่พบข้อมูล Zone"

        zone_text = "ยังไม่อยู่ในเกม"
        if playerInGame:
            zone_name = zone.get("name", "Default Zone")

            zone_left = playerInGame.get("zone_left", 0)
            zone_text = f"{zone_name}\nคงเหลือ: {zone_left}"


        embed.add_field(
            name="🌌 Zone",
            value=zone_text,
            inline=False
        )

        embed.add_field(
            name="🎯 Skill Slot 1",
            value=build_slot_display(slots["slot_1"], interaction.channel_id, interaction.user.id),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 2",
            value=build_slot_display(slots["slot_2"], interaction.channel_id, interaction.user.id),
            inline=False
        )
        embed.add_field(
            name="🎯 Skill Slot 3",
            value=build_slot_display(slots["slot_3"], interaction.channel_id, interaction.user.id),
            inline=False
        )

        embed.add_field(
            name=f"{Status_Icon_Type['WIT']} Skill pt",
            value=str(wit_mana),
            inline=True
        )

        embed.set_footer(text="กดปุ่ม 1 / 2 / 3 เพื่อใช้สกิล หรือกด 🌌 เพื่อใช้ Zone")

        await interaction.response.send_message(
            embed=embed,
            view=UseSkillView(self, interaction.user.id, interaction.channel_id),
            ephemeral=True
        )
   
async def setup(bot: commands.Bot):
    await bot.add_cog(GameCog(bot))