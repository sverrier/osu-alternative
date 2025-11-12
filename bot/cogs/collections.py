# bot/cogs/collections.py
import discord
from discord.ext import commands
import aiohttp
from bot.util.helpers import get_args
from bot.util.osu_collections import CollectionBeatmap, CollectionSingle, CollectionDatabase
from bot.util.querybuilder import QueryBuilder

class Collections(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def generateosdb(self, ctx, *args):
        di = get_args(args)
        columns = "checksum as hash, beatmapLive.beatmap_id, beatmapset_id, artist, title, version, mode, stars"
        sql = QueryBuilder(di, columns).getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        beatmaps = {CollectionBeatmap(**row) for row in result}

        filename = f"{di.get('-name', 'collection')}.osdb"
        collections = CollectionDatabase([CollectionSingle("collection", beatmaps)])
        collections.encode_collections_osdb(open(filename, "wb"))

        with open(filename, "rb") as file:
            await ctx.reply("Your file is:", file=discord.File(file, filename))

    @commands.command()
    async def generateosdbs(self, ctx):
        if not ctx.message.attachments:
            await ctx.reply("Please attach a .txt file with commands.")
            return
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
            args = command.split()
            di = get_args(args)
            columns = "checksum as hash, beatmapLive.beatmap_id, beatmapset_id, artist, title, version, mode, stars"
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
