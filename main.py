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


def print_registered_routes():
    print("Registered FastAPI routes:")
    for route in app.routes:
        methods = ",".join(sorted(getattr(route, "methods", []) or []))
        print(f"{methods:12} {route.path}")


def run_api():
    port = int(os.getenv("PORT", "8000"))
    print_registered_routes()
    uvicorn.run(app, host="0.0.0.0", port=port)


class Client(commands.Bot):
    async def setup_hook(self):
        try:
            init_db()
        except Exception as exc:
            print(f"Database init failed during bot setup: {exc!r}")

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

        if message.content.startswith("โอกุริเป็นแกรับ"):
            await message.channel.send(f"จริงค่ะ {message.author}")

        await self.process_commands(message)


intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)

# Allow api_server routes to access the bot when the bot thread is healthy.
bot_instance.bot = client


def run_bot():
    if not TOKEN:
        print("DISCORD_TOKEN is not set; starting API without Discord bot")
        return

    try:
        client.run(TOKEN)
    except Exception as exc:
        print(f"Discord bot failed to start: {exc!r}")


if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_api()
