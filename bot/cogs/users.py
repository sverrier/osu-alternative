from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.presets import PRESETS
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["u"])
    async def users(self, ctx, *args):
        """Count of users"""
        di = get_args(args)
        query = QueryBuilder(di, "count(*)", "userLive")
        sql = query.getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        await ctx.reply(str(result[0][0]))

    @commands.command(aliases=["ul"])
    async def userlist(self, ctx, *args):
        di = get_args(args)
        table = "userLive"
        preset_key = di.get("-o")
        if preset_key in PRESETS:
            preset = PRESETS[preset_key]
            columns = preset["columns"]
            title = preset["title"]
            for k, v in preset.items():
                if k.startswith("-"):
                    di[k] = v
        else:
            columns = di.get("-columns", "username,total_ranked_score")
            title = "Leaderboard"
            di.setdefault("-order", "total_ranked_score")
        if di.get("-include") == "d":
            di.pop("-grade-not", None)
        sql = QueryBuilder(di, columns, table).getQuery()
        result, elapsed = await self.bot.db.executeQuery(sql)
        columns = "DISTINCT beatmaplive.beatmap_id"
        di.pop("-group", None)
        di.pop("-order", None)
        di.pop("-limit", None)
        sql = QueryBuilder(di, columns, "beatmapLive").getQuery()
        beatmaps, elapsed = await self.bot.db.executeQuery(sql)
        count = len(beatmaps)
        formatter = Formatter(title=title, footer=f"Based on Scores • took {elapsed:.2f}s")
        embed = formatter.as_leaderboard(result, count, page=int(di.get("-p", 1)), page_size=int(di.get("-l", 10)), elapsed=elapsed)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Users(bot))
