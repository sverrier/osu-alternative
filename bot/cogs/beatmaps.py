from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.presets import BEATMAP_PRESETS

class Beatmaps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["b"])
    async def beatmaps(self, ctx, *args):
        di = get_args(args)

        preset_key = di.get("-o")
        if preset_key in BEATMAP_PRESETS:
            preset = BEATMAP_PRESETS[preset_key]
            columns = preset["columns"]
            title = preset["title"]
            for k, v in preset.items():
                if k.startswith("-"):
                    di[k] = v
        else:
            columns = "count(*)"
        sql = QueryBuilder(di, columns, "beatmapLive").getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        await ctx.reply(str(result[0][0]))

    @commands.command(aliases=["bl"])
    async def beatmaplist(self, ctx, *args):
        di = get_args(args)
        query = QueryBuilder(di, "stars, artist, title, version, beatmap_id, beatmapset_id, mode", "beatmapLive")
        result, elapsed = await self.bot.db.executeQuery(query.getQuery())
        formatter = Formatter(title=f"Total beatmaps: {len(result)}")
        embed = formatter.as_beatmap_list(result, page=int(di.get("-p", 1)), page_size=int(di.get("-l", 10)), elapsed=elapsed)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Beatmaps(bot))
