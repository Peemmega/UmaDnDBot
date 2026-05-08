import os
import asyncio
from contextlib import asynccontextmanager

import discord
from discord.ext import commands
from dotenv import load_dotenv

import bot_instance
from api_server import app as fastapi_app
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
        await self.load_extension("cogs.admin")

        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged on as {self.user}!")


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)
bot_instance.bot = client

bot_task = None


async def start_discord_bot():
    while True:
        try:
            await client.start(TOKEN)
        except Exception as e:
            print(f"Discord bot crashed: {e}")
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app):
    global bot_task

    bot_task = asyncio.create_task(start_discord_bot())

    yield

    if bot_task:
        bot_task.cancel()

    if not client.is_closed():
        await client.close()


fastapi_app.router.lifespan_context = lifespan
app = fastapi_app