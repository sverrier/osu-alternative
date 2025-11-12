import discord
from discord.ext import commands
import os
from utils.config_manager import load_config
from util.db import Database
import asyncio

config = load_config("botconfig.txt")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="~", case_insensitive=True, intents=intents, help_command=None)

# shared db instance
bot.db = Database(config["PORT"], config["DBNAME"], config["USERNAME"], config["PASSWORD"])

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
                await bot.load_extension(f"cogs.{file[:-3]}")
                print(f"✓ Loaded cog: {file[:-3]}")
            except Exception as e:
                print(f"✗ Failed to load cog {file[:-3]}: {e}")

asyncio.run(load_cogs())
bot.run(config["DISCORD_TOKEN"])
