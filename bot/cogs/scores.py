# bot/cogs/scores.py
from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.formatting import format_field
from bot.util.presets import *

class Scores(commands.Cog):
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

    @commands.command(aliases=["s"])
    async def scores(self, ctx, *args):
        di = get_args(args)
        table = "scoreLive"
        preset = get_score_preset(di.get("-o", "count"))
        await self._set_defaults(ctx, di)

        if preset is None:
            await ctx.reply("Preset not allowed. See valid presets with !help presets or !help user")
            return

        columns = preset["columns"]

        # apply preset flags
        for k, v in preset.items():
            if k.startswith("-"):
                di[k] = v

        # ensure we can format by a stable output name
        alias = preset.get("alias", "result")
        columns_aliased = f"{columns} AS {alias}"

        sql = QueryBuilder(di, columns_aliased, table).getQuery()
        result, _ = await self.bot.db.executeQuery(sql)

        val = None
        if result:
            # supports both list-of-tuples and list-of-dicts patterns
            row0 = result[0]
            val = row0[alias] if dict else row0[0]

        msg = format_field(alias, val, table=table, alias=alias)
        await ctx.reply(msg)

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
