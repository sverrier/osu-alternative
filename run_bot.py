import discord
from discord.ext import commands
import logging
from datetime import datetime
import os
from bot.util.config_manager import load_config
from util.db import db
import asyncio

config = load_config("botconfig.txt")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="~", case_insensitive=True, intents=intents, help_command=None)

os.makedirs('logs', exist_ok=True)
log_filename = f"logs/osu_bot_{datetime.now().strftime('%Y%m%d')}.log"

file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# shared db instance
bot.db = db(config, logger)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Loaded {len(bot.commands)} commands:")
    for command in bot.commands:
        print(f"  - {command.name}")

async def load_cogs():
    for file in os.listdir("bot/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            try:
                await bot.load_extension(f"bot.cogs.{file[:-3]}")
                print(f"✓ Loaded cog: {file[:-3]}")
            except Exception as e:
                print(f"✗ Failed to load cog {file[:-3]}: {e}")

asyncio.run(load_cogs())
bot.run(config["DISCORD_TOKEN"])
