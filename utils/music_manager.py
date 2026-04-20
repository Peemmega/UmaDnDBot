import discord
import os
import platform
import shutil

BGM_PATH = "assets/music/LastSpurt.mp3"

if platform.system() == "Windows":
    FFMPEG_EXECUTABLE = r"C:\Users\peemm_a8kwyjd\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
else:
    # บน Railway/Linux เราจะหา ffmpeg จาก 3 แหล่ง: 
    # 1. shutil.which 2. /usr/bin 3. คำว่า "ffmpeg" เฉยๆ
    FFMPEG_EXECUTABLE = shutil.which("ffmpeg") or "/usr/bin/ffmpeg"

print(f"Checking BGM Path: {os.path.abspath(BGM_PATH)}")
print(f"Checking FFmpeg Path: {FFMPEG_EXECUTABLE}")

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

def play_bgm(guild: discord.Guild | None) -> tuple[bool, str]:
    if guild is None:
        return False, "ไม่พบเซิร์ฟเวอร์"

    voice_client = guild.voice_client
    if voice_client is None:
        return False, "บอทยังไม่ได้อยู่ในห้องเสียง"

    if not os.path.exists(BGM_PATH):
        return False, f"ไม่พบไฟล์เพลง: {BGM_PATH}"

    if platform.system() == "Windows" and not os.path.exists(FFMPEG_EXECUTABLE):
        return False, f"ไม่พบ ffmpeg: {FFMPEG_EXECUTABLE}"

    try:
        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(
            BGM_PATH,
            executable=FFMPEG_EXECUTABLE,
            options="-vn"
        )
        voice_client.play(source)
        return True, "เริ่มเล่นเพลงแล้ว"
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