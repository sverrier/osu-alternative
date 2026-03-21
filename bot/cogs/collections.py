# bot/cogs/collections.py
import discord
from discord.ext import commands
import aiohttp
from bot.util.helpers import get_args
from bot.util.osu_collections import CollectionBeatmap, CollectionSingle, CollectionDatabase
from bot.util.querybuilder import QueryBuilder
from bot.util.presets import *

class Collections(commands.Cog):
    """
    Collection generation commands for creating osu! collection files.
    
    This cog provides commands to generate .osdb collection files from
    beatmap queries, allowing users to export beatmaps matching specific
    criteria for use in the osu! client.
    """
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

    @commands.command(
        brief="Generate single .osdb collection file"
    )
    async def generateosdb(self, ctx, *args):
        """
        Generate a single .osdb collection file from beatmap filters.
        
        Usage: !generateosdb [filters] [-name collection_name]
        
        Examples:
        - !generateosdb -stars-min 6 -stars-max 8 -name "6-8 Star Maps"
        - !generateosdb -mode 0 -status ranked -name "Ranked Osu Maps"
        - !generateosdb -artist-like demetori -name "Demetori Collection"
        
        Key parameters:
        - [filters]: Any beatmap filters (stars, mode, status, artist, etc.)
        - -name: Name for the collection (defaults to "collection")
        - -o: Leaderboard preset to apply (plays, hardclears, etc.)
        
        Notes:
        - Generates a .osdb file compatible with osu! client
        - File is sent directly to Discord as an attachment
        - Supports all beatmapLive table columns as filters
        - Automatically applies user's default mode if not specified
        """
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

    @commands.command(
        aliases=["gen"],
        brief="Generate multiple collections from file"
    )
    async def generateosdbs(self, ctx, *args):
        """
        Generate multiple .osdb collection files from a text file or single command.
        
        Usage: !generateosdbs [filters] [-name collection_name]
        Or: Upload a .txt file with one command per line
        
        Examples:
        - !generateosdbs -stars-min 6 -name "Hard Maps"
        - Upload file with content:
          -stars-min 5 -name "Easy Maps"
          -stars-max 3 -name "Beginner Maps"
        
        Key parameters:
        - [filters]: Any beatmap filters (stars, mode, status, artist, etc.)
        - -name: Name for each collection
        - -o: Leaderboard preset to apply
        
        File format:
        Each line should contain a valid generateosdb command without the command name.
        Example file content:
        -stars-min 5 -mode 0 -name "Osu Maps"
        -artist-like touhou -name "Touhou Collection"
        
        Notes:
        - If no file is attached, behaves like generateosdb
        - If file is attached, processes each line as a separate collection
        - Merges all collections into a single .osdb file
        - File must be .txt format with UTF-8 encoding
        """
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