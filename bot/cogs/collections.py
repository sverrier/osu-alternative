# bot/cogs/collections.py
import discord
from discord.ext import commands
import aiohttp
from bot.util.helpers import get_args
from bot.util.osu_collections import CollectionBeatmap, CollectionSingle, CollectionDatabase
from bot.util.querybuilder import QueryBuilder
from bot.util.presets import *

class Collections(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _set_defaults(self, ctx, di):
        discordid = ctx.author.id

        #Use user's preferred mode set by default
        if di.get("-mode") is None and di.get("-mode-in") is None:
            query = f"SELECT mode FROM registrations WHERE discordid = '{discordid}'"
            rows, _ = await self.bot.db.executeQuery(query)
            if not rows:
                return
        
            di["-mode-in"] = rows[0]["mode"]

        # Parse -include into a set of values
        include_raw = di.get("-include", "")
        include_set = {x.strip().lower() for x in include_raw.split(",") if x.strip()}

        if "loved" not in include_set:
            di.setdefault("-status-not", "loved")

        if "converts" not in include_set:
            di.setdefault("-convertless", "true")
        
        if "all" not in include_set:
            di.setdefault("-highest_score", "true")
        
        if "everyone" not in include_set:
            if "-user_id" not in di and "-username" not in di:
                query = f"SELECT user_id FROM registrations WHERE discordid = '{discordid}'"
                result, _ = await self.bot.db.executeQuery(query)
                if result and result[0]:
                    di["-user_id"] = result[0][0]

    @commands.command()
    async def generateosdb(self, ctx, *args):
        di = get_args(args)
        columns = "checksum as hash, beatmapLive.beatmap_id, beatmapset_id, artist, title, version, mode, stars"

        await self._set_defaults(ctx, di)

        preset = get_leaderboard_preset(di.get("-o", "scores"))

        if preset is not None:
            for k, v in preset.items():
                if k.startswith("-") and k not in ('-group', '-order'):
                    di[k] = v
        else:
            await ctx.reply("Preset not allowed. See valid presets with !help presets")           
            return
        
        sql = QueryBuilder(di, columns).getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        beatmaps = {CollectionBeatmap(**row) for row in result}

        filename = f"{di.get('-name', 'collection')}.osdb"
        collections = CollectionDatabase([CollectionSingle("collection", beatmaps)])
        collections.encode_collections_osdb(open(filename, "wb"))

        with open(filename, "rb") as file:
            await ctx.reply("Your file is:", file=discord.File(file, filename))

    @commands.command(aliases=["gen"])
    async def generateosdbs(self, ctx, *args):
        # If no file attached, behave like generateosdb
        if not ctx.message.attachments:
            di = get_args(args)
            columns = "checksum as hash, beatmapLive.beatmap_id, beatmapset_id, artist, title, version, mode, stars"

            await self._set_defaults(ctx, di)

            preset = get_leaderboard_preset(di.get("-o", "scores"))

            if preset is not None:
                for k, v in preset.items():
                    if k.startswith("-") and k not in ('-group', '-order'):
                        di[k] = v
            else:
                await ctx.reply("Preset not allowed. See valid presets with !help presets")           
                return
            
            sql = QueryBuilder(di, columns).getQuery()
            result, _ = await self.bot.db.executeQuery(sql)
            beatmaps = {CollectionBeatmap(**row) for row in result}

            filename = f"{di.get('-name', 'collection')}.osdb"
            collections = CollectionDatabase([CollectionSingle("collection", beatmaps)])
            collections.encode_collections_osdb(open(filename, "wb"))

            with open(filename, "rb") as file:
                await ctx.reply("Your file is:", file=discord.File(file, filename))
            return

        # Original file-based logic
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".txt"):
            await ctx.reply("The attached file must be a .txt file.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status == 200:
                    file_content = await resp.text()
                else:
                    await ctx.reply("Failed to download the file.")
                    return

        commands_list = file_content.strip().split("\n")
        collections = []

        for command in commands_list:
            args_list = command.split()
            di = get_args(args_list)
            columns = "checksum as hash, beatmapLive.beatmap_id, beatmapset_id, artist, title, version, mode, stars"

            await self._set_defaults(ctx, di)

            preset = get_leaderboard_preset(di.get("-o", "scores"))

            if preset is not None:
                for k, v in preset.items():
                    if k.startswith("-") and k not in ('-group', '-order'):
                        di[k] = v
            else:
                await ctx.reply("Preset not allowed. See valid presets with !help presets")           
                return

            sql = QueryBuilder(di, columns).getQuery()
            result, _ = await self.bot.db.executeQuery(sql)
            beatmaps = {CollectionBeatmap(**row) for row in result}
            collection_name = di.get("-name", "collection")
            collections.append(CollectionSingle(collection_name, beatmaps))

        if not collections:
            await ctx.reply("No valid collections were generated.")
            return

        merged_collections = CollectionDatabase(collections)
        filename = "db.osdb"
        with open(filename, "wb") as f:
            merged_collections.encode_collections_osdb(f)

        with open(filename, "rb") as file:
            await ctx.reply("Here is your merged collection file:", file=discord.File(file, filename))

async def setup(bot):
    await bot.add_cog(Collections(bot))