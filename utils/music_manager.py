import os
import shutil
import platform
import discord

DEFAULT_MUSIC_KEY = "lastspurt"

MUSICS = {
    "lastspurt": "assets/music/LastSpurt.mp3",
    "arima_kinen": "assets/music/arima_kinen.mp3",
    "g1_race": "assets/music/g1_race.mp3",
    "girl_legend_u": "assets/music/girl_legend_u.mp3",
    "l_arc": "assets/music/l_arc.mp3",
    "glorious_moment": "assets/music/glorious_moment.mp3",
    "cingrey_ost_01": "assets/music/cingrey_ost_01.mp3",
    "SpecialWeekAura": "assets/music/SpecialWeekAura.mp3",
}

if platform.system() == "Windows":
    FFMPEG_EXECUTABLE = r"C:\Users\peemm_a8kwyjd\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
else:
    FFMPEG_EXECUTABLE = "/usr/bin/ffmpeg"

print(f"Checking FFmpeg Path: {FFMPEG_EXECUTABLE}")
print(f"Default BGM Path: {os.path.abspath(MUSICS[DEFAULT_MUSIC_KEY])}")
print(f"FFmpeg file exists: {os.path.exists(FFMPEG_EXECUTABLE)}")
print(f"which ffmpeg: {shutil.which('ffmpeg')}")


def get_music_path(music_key: str) -> str | None:
    return MUSICS.get(music_key)


def get_music_choices() -> list[str]:
    return list(MUSICS.keys())


async def join_user_voice(interaction: discord.Interaction) -> tuple[bool, str]:
    if interaction.guild is None:
        return False, "คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์"

    if interaction.user.voice is None or interaction.user.voice.channel is None:
        return False, "คุณต้องอยู่ในห้องเสียงก่อน"

    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    try:
        if voice_client is None:
            await channel.connect()
            return True, f"เข้าห้องเสียง {channel.name} แล้ว"

        if voice_client.channel and voice_client.channel.id == channel.id:
            return True, f"บอทอยู่ในห้อง {channel.name} อยู่แล้ว"

        await voice_client.move_to(channel)
        return True, f"ย้ายไปห้องเสียง {channel.name} แล้ว"

    except Exception as e:
        return False, f"ไม่สามารถเข้าห้องเสียงได้: {e}"


async def leave_voice(guild: discord.Guild | None) -> tuple[bool, str]:
    if guild is None:
        return False, "ไม่พบเซิร์ฟเวอร์"

    voice_client = guild.voice_client
    if voice_client is None:
        return False, "บอทยังไม่ได้อยู่ในห้องเสียง"

    try:
        if voice_client.is_playing():
            voice_client.stop()

        await voice_client.disconnect()
        return True, "ออกจากห้องเสียงแล้ว"

    except Exception as e:
        return False, f"ไม่สามารถออกจากห้องเสียงได้: {e}"


def play_bgm(guild: discord.Guild | None, music_key: str = DEFAULT_MUSIC_KEY) -> tuple[bool, str]:
    if guild is None:
        return False, "ไม่พบเซิร์ฟเวอร์"

    voice_client = guild.voice_client
    if voice_client is None:
        return False, "บอทยังไม่ได้อยู่ในห้องเสียง"

    music_path = get_music_path(music_key)
    if music_path is None:
        return False, f"ไม่พบเพลงชื่อ: {music_key}"

    if not os.path.exists(music_path):
        return False, f"ไม่พบไฟล์เพลง: {music_path}"

    if platform.system() == "Windows" and not os.path.exists(FFMPEG_EXECUTABLE):
        return False, f"ไม่พบ ffmpeg: {FFMPEG_EXECUTABLE}"

    try:
        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(
            music_path,
            executable=FFMPEG_EXECUTABLE,
            options="-vn"
        )
        voice_client.play(source)
        return True, f"เริ่มเล่นเพลง: {music_key}"
    except Exception as e:
        return False, f"ไม่สามารถเปิดเพลงได้: {e}"


def stop_bgm(guild: discord.Guild | None) -> tuple[bool, str]:
    if guild is None:
        return False, "ไม่พบเซิร์ฟเวอร์"

    voice_client = guild.voice_client
    if voice_client is None:
        return False, "บอทยังไม่ได้อยู่ในห้องเสียง"

    try:
        if voice_client.is_playing():
            voice_client.stop()
        return True, "หยุดเพลงแล้ว"

    except Exception as e:
        return False, f"ไม่สามารถหยุดเพลงได้: {e}"