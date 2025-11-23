import os
import logging
from datetime import datetime
import asyncio

import discord
from discord.ext import commands
from cryptography.fernet import Fernet
from util.crypto import get_fernet
from util.db import db


class BotRunner:
    def __init__(self, config_file: str = "botconfig.txt"):
        self.config_file = config_file
        self._setup_logging()
        self.logger.info("Initializing Discord bot...")

        # Load or create config
        self.config = self._load_or_create_config()

        # Discord setup
        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = commands.Bot(
            command_prefix="~",
            case_insensitive=True,
            intents=intents,
            help_command=None,
        )

        # Shared DB instance on the bot, like before
        self.bot.db = db(self.config, self.logger)
        self.bot.logger = self.logger

        @self.bot.event
        async def on_ready():
            self.logger.info(f"Logged in as {self.bot.user}")
            self.logger.info(f"Loaded {len(self.bot.commands)} commands:")
            for command in self.bot.commands:
                self.logger.info(f"  - {command.name}")

    # ------------- LOGGING -------------

    def _setup_logging(self):
        os.makedirs("logs", exist_ok=True)
        log_filename = f"logs/osu_bot_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        self.logger = logging.getLogger("osu_bot")
        self.logger.setLevel(logging.INFO)
        # Avoid duplicate handlers if re-instantiated
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    # ------------- CONFIG MANAGEMENT -------------

    def _create_config_file(self) -> dict:
        """Interactive config creator, similar in spirit to OsuDataFetcher."""
        self.logger.info("Creating new bot configuration file...")
        config: dict[str, str] = {}

        config["DISCORD_TOKEN"] = input("Enter your Discord bot token: ").strip()
        config["DBNAME"] = input("Enter the DBNAME value: ").strip()
        config["USERNAME"] = input("Enter the DB USERNAME value: ").strip()
        config["PASSWORD"] = input("Enter the DB PASSWORD value: ").strip()
        config["PORT"] = input("Enter the DB PORT value (default: 5433): ").strip() or "5433"
        config["HOST"] = (
            input("Enter the DB HOST value (default: localhost): ").strip() or "localhost"
        )

        f = get_fernet()
        enc_token = f.encrypt(config["DISCORD_TOKEN"].encode()).decode()
        enc_password = f.encrypt(config["PASSWORD"].encode()).decode()

        # Persist encrypted values and encryption key
        to_write = dict(config)
        to_write["DISCORD_TOKEN"] = enc_token
        to_write["PASSWORD"] = enc_password

        with open(self.config_file, "w", encoding="utf-8") as file:
            for k, v in to_write.items():
                file.write(f"[{k}]={v}\n")

        # Keep decrypted in memory for runtime use
        return config

    def _read_config_file(self) -> dict:
        """Read existing config and decrypt sensitive values."""
        self.logger.info(f"Reading bot configuration from '{self.config_file}'...")
        config: dict[str, str] = {}

        with open(self.config_file, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k.strip("[]")] = v

        f = get_fernet()

        # Decrypt sensitive fields
        config["DISCORD_TOKEN"] = f.decrypt(config["DISCORD_TOKEN"].encode()).decode()
        config["PASSWORD"] = f.decrypt(config["PASSWORD"].encode()).decode()

        return config

    def _load_or_create_config(self) -> dict:
        if os.path.exists(self.config_file):
            return self._read_config_file()
        else:
            return self._create_config_file()

    # ------------- COG LOADING & RUN -------------

    async def _load_cogs(self):
        """Load all bot cogs from bot/cogs, like in the original script."""
        for file in os.listdir("bot/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                name = file[:-3]
                try:
                    await self.bot.load_extension(f"bot.cogs.{name}")
                    self.logger.info(f"Loaded cog: {name}")
                except Exception as e:
                    self.logger.exception(f"Failed to load cog {name}: {e}")

    def run(self):
        """Entry point for running the Discord bot."""
        asyncio.run(self._load_cogs())
        self.bot.run(self.config["DISCORD_TOKEN"])


if __name__ == "__main__":
    BotRunner().run()
