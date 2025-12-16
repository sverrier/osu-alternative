# bot/cogs/scores.py
from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter

class Scores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _set_defaults(self, ctx, di):
        discordid = ctx.author.id

        if "-user_id" not in di and "-username" not in di:
            query = f"SELECT user_id FROM registrations WHERE discordid = '{discordid}'"
            result, _ = await self.bot.db.executeQuery(query)
            if result and result[0]:
                di["-user_id"] = result[0][0]

        if di.get("-mode") is None and di.get("-mode-in") is None:
            #default to user set mode
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

        if "d" not in include_set:
            di.setdefault("-grade-not", "d")
        
        if "all" not in include_set:
            di.setdefault("-highest_score", "true")

    @commands.command(aliases=["s"])
    async def scores(self, ctx, *args):
        di = get_args(args)
        columns = "count(*)"
        if di.get("-o") == "score":
            columns = "sum(classic_total_score)"
        elif di.get("-o") == "legacy":
            columns = "sum(legacy_total_score)"
        table = "scoreLive"

        await self._set_defaults(ctx, di)

        sql = QueryBuilder(di, columns, table).getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        await ctx.reply(str(result[0][0]))

    @commands.command(aliases=["sl"])
    async def scorelist(self, ctx, *args):
        di = get_args(args)
        table = "scoreLive"
        columns = "stars, artist, title, version, beatmap_id, beatmapset_id, mode, accuracy, pp, grade, mod_acronyms"

        await self._set_defaults(ctx, di)

        query = QueryBuilder(di, columns, table)
        result, elapsed = await self.bot.db.executeQuery(query.getQuery())
        formatter = Formatter(title=f"Total scores: {len(result)}")
        embed = formatter.as_score_list(result, page=int(di.get("-page", 1)), page_size=int(di.get("-limit", 10)), elapsed=elapsed)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Scores(bot))
