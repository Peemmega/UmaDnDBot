import os
import threading

import discord
import uvicorn
from discord.ext import commands
from dotenv import load_dotenv

import bot_instance
from api_server import app
from utils.database import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("ไม่พบ DISCORD_TOKEN ในไฟล์ .env")


def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)


class Client(commands.Bot):
    async def setup_hook(self):
        init_db()

        await self.load_extension("cogs.profile")
        await self.load_extension("cogs.training")
        await self.load_extension("cogs.game")
        await self.load_extension("cogs.skill")
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.music")
        await self.load_extension("cogs.admin")
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("โอกุริเป็นเกรับ"):
            await message.channel.send(f"จริงค่ะ {message.author}")

        await self.process_commands(message)


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)

# ให้ api_server เรียกใช้ bot ตัวนี้ได้
bot_instance.bot = client

threading.Thread(target=run_api, daemon=True).start()

client.run(TOKEN)