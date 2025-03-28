import discord
from discord.ext import commands
import os
import sys
import traceback
from osu_collections import CollectionBeatmap, CollectionSingle, CollectionDatabase
from db import Database

# File name
config_file = "botconfig.txt"

# Function to create the configuration file
def create_config_file(file_name):
    print("Config file not found. Let's create one.")
    config = {}
    config["DBNAME"] = input("Enter the DBNAME value (Postgres DB name): ").strip()
    config["USERNAME"] = input("Enter the USERNAME value (Postgres username): ").strip()
    config["PASSWORD"] = input("Enter the PASSWORD value (Postgres password): ").strip()
    config["PORT"] = input("Enter the PORT value: ").strip()
    config["DISCORD_TOKEN"] = input("Enter the DISCORD_TOKEN value: ").strip()

    
    # Write to file
    with open(file_name, "w") as file:
        for key, value in config.items():
            file.write(f"[{key}]={value}\n")
    print(f"Configuration file '{file_name}' created successfully.")
    return config


# Function to read the configuration file
def read_config_file(file_name):
    config = {}
    with open(file_name, "r") as file:
        for line in file:
            # Parse lines of the format [KEY]=value
            if "=" in line:
                key, value = line.strip().split("=", 1)
                key = key.strip("[]")  # Remove square brackets
                config[key] = value
    return config

# Main logic
if os.path.exists(config_file):
    print(f"Found '{config_file}'. Reading configuration...")
    config_values = read_config_file(config_file)
else:
    config_values = create_config_file(config_file)

# Print the stored configuration
print("\nConfiguration values:")
for key, value in config_values.items():
    print(f"{key} = {value}")

# Function to read the configuration file
def read_config_file(file_name):
    config = {}
    with open(file_name, "r") as file:
        for line in file:
            # Parse lines of the format [KEY]=value
            if "=" in line:
                key, value = line.strip().split("=", 1)
                key = key.strip("[]")  # Remove square brackets
                config[key] = value
    return config

DISCORD_TOKEN = config_values["DISCORD_TOKEN"]

db = Database(config_values["PORT"],config_values["DBNAME"],config_values["USERNAME"],config_values["PASSWORD"])

intents = discord.Intents.default()
intents.message_content = True
allowed_mentions = discord.AllowedMentions(
    users=True,  # Whether to ping individual user @mentions
    everyone=False,  # Whether to ping @everyone or @here mentions
    roles=True,  # Whether to ping role @mentions
    replied_user=True,  # Whether to ping on replies to messages
)
bot = commands.Bot(
    command_prefix="~",
    case_insensitive=True,
    intents=intents,
    allowed_mentions=allowed_mentions,
    help_command=None,
)

def escape_string(s):
    """
    Escapes special characters for use in SQL queries
    """
    special_chars = {"'": "''", "\\": "\\\\", '"': ""}
    for char, escaped in special_chars.items():
        s = s.replace(char, escaped)
    return s

def get_args(arg=None):
    args = []
    if arg != None:
        args = arg
    di = {}
    for i in range(0, len(args) - 1):
        if args[i].startswith("-"):
            key = args[i].lower()
            value = args[i + 1].lower()
            if key == "-u":
                di[key] = escape_string(value)
            elif " " in value:
                raise ValueError("spaces are not allowed for argument " + key)
            else:
                di[key] = value

    # replace underscores on numbers
    for key, value in di.items():
        if value.isdigit() or (value.replace("_", "").isdigit() and "." not in value):
            # value is a number with underscores as thousand separators
            di[key] = value.replace("_", "")  # remove the underscores

    return di


@bot.event
async def on_ready():
    print("Python Version: " + sys.version)
    print("Ready")


@bot.event
async def on_member_join(member):
    print(f"{member} just joined the server.")


@bot.event
async def on_command_error(ctx, error):
    print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    if isinstance(error, commands.MissingPermissions):
        error = "You don't have permission to use this command!"
    elif isinstance(error, ValueError):
        error = error.original
    else:
        error = error

    embed = discord.Embed(title="Error", colour=discord.Colour(0xCC5288))
    embed.description = "```\n" + f"{error}" + "\n```"

    await ctx.reply(embed=embed)

@bot.command(aliases=["b"])
async def beatmaps(ctx, *args):
    """Returns statistics of a set of beatmaps"""

    print(args[0])

    await db.export_to_csv(args[0], "temp.csv")

    attach = discord.File("temp.csv")

    await ctx.reply(file=attach, content="Here is your response:")

@bot.command(pass_context=True)
async def generateosdb(ctx, *, arg=None):
    di = get_args(arg)

    query = "SELECT checksum as hash, beatmap_id, beatmapset_id, artist, title, version, mode, stars FROM beatmapLive limit 10"
    result = await db.execute_query(query)

    print(result)
    
    # Convert result rows into CollectionBeatmap instances
    beatmaps = {CollectionBeatmap(**row) for row in result}

    collections = CollectionDatabase([CollectionSingle("collection", beatmaps)])
    collections.encode_collections_osdb(open("collection.osdb", 'wb'))

    with open("collection.osdb", "rb") as file:
        await ctx.reply("Your file is:", file=discord.File(file, "collection.osdb"))

bot.run(DISCORD_TOKEN)
