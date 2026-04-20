import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.database import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("ไม่พบ DISCORD_TOKEN ในไฟล์ .env")

class Client(commands.Bot):
    async def setup_hook(self):
        init_db()

        await self.load_extension("cogs.profile")
        await self.load_extension("cogs.training")
        await self.load_extension("cogs.game")
        await self.load_extension("cogs.skill")
        await self.load_extension("cogs.general")
        await self.load_extension("cogs.music")
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
client.run(TOKEN)