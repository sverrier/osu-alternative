# bot/cogs/scores.py
from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.formatting import format_field
from bot.util.presets import *

class Scores(commands.Cog):
    """
    Score query commands for analyzing user performance and statistics.
    
    This cog provides commands to count, list, and analyze scores from the database
    using various filters like accuracy, PP, grade, and more. Requires user registration
    for most commands to filter by specific users.
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

    @commands.command(
        aliases=["s"],
        brief="Count scores matching filters"
    )
    async def scores(self, ctx, *args):
        """
        Count scores matching specified filters.
        
        Usage: !scores [filters] [-o preset]
        
        Examples:
        - !scores -pp-min 400 -mode 0
        - !scores -accuracy-min 98 -grade-in SS,S
        - !scores -stars-min 7 -o score
        
        Key parameters:
        - -pp-min/-pp-max: Filter by PP range
        - -accuracy-min/-accuracy-max: Filter by accuracy range
        - -grade-in/-grade-not: Filter by grade (SS, S, A, B, etc.)
        - -mods: Filter by mods (HD, DT, HR, etc.)
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -o: Output preset (count, score, classicscore, legacyscore)
        - -user_id/-username: Filter by specific user
        
        Notes: 
        - Requires registration for default user filtering
        - Defaults to highest score per beatmap only
        - Supports score aggregation presets (sum of scores)
        """
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

        val = result[0][0]
        msg = format_field(alias, val, table=table, alias=alias)
        
        await ctx.reply(msg)

    @commands.command(
        aliases=["sl"],
        brief="List scores with detailed information"
    )
    async def scorelist(self, ctx, *args):
        """
        List scores with detailed information matching specified filters.
        
        Usage: !scorelist [filters] [-page N] [-limit N]
        
        Examples:
        - !scorelist -pp-min 400 -mode 0 -l 15
        - !scorelist -grade-in SS,S -accuracy-min 99
        - !scorelist -mods HD,DT -page 2
        
        Key parameters:
        - -pp-min/-pp-max: Filter by PP range
        - -accuracy-min/-accuracy-max: Filter by accuracy range
        - -grade-in/-grade-not: Filter by grade (SS, S, A, B, etc.)
        - -mods: Filter by mods (HD, DT, HR, etc.)
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -user_id/-username: Filter by specific user
        - -page/-limit: Pagination controls
        - -order: Sort by column (e.g., pp, accuracy, stars)
        - -direction: Sort direction (ASC/DESC)
        
        Notes: 
        - Displays score details including PP, accuracy, grade, and mods
        - Defaults to highest score per beatmap only
        - Supports leaderboard presets for common score aggregations
        """
        di = get_args(args)
        table = "scoreLive"
        columns = "stars, artist, title, version, beatmap_id, beatmapset_id, mode, accuracy, pp, grade, mod_acronyms"

        await self._set_defaults(ctx, di)

        preset = get_leaderboard_preset(di.get("-o", "scores"))

        if preset is not None:
            for k, v in preset.items():
                if k.startswith("-") and k not in ('-group', '-order'):
                    di[k] = v
        else:
            await ctx.reply("Preset not allowed. See valid presets with !help presets")           
            return

        query = QueryBuilder(di, columns, table)
        result, elapsed = await self.bot.db.executeQuery(query.getQuery())
        formatter = Formatter(title=f"Total scores: {len(result)}")
        embed = formatter.as_score_list(result, page=int(di.get("-page", 1)), page_size=int(di.get("-limit", 10)), elapsed=elapsed)
        await ctx.reply(embed=embed)

    @commands.command(
        aliases=["ussl", "uniquesslist"],
        brief="List unique SS (perfect score) plays"
    )
    async def unique_ss_list(self, ctx, *args):
        """
        List scores that are unique SS (perfect score) plays.
        
        Usage: !unique_ss_list [filters]
        
        Examples:
        - !unique_ss_list -stars-min 6 -mode 0
        - !unique_ss_list -mods HD -grade SS
        - !unique_ss_list -user_id 123456
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -pp-min/-pp-max: Filter by PP range
        - -mods: Filter by mods (HD, DT, HR, etc.)
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -user_id/-username: Filter by specific user
        - -grade: Filter by grade (SS, SSH, etc.)
        
        Notes: 
        - Shows scores where the user has the only SS on the beatmap
        - Uses the unique_ss leaderboard preset
        - Requires registration for default user filtering
        """
        di = get_args(args)

        di["-o"] = "unique_ss"
        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.scorelist(ctx, *args)

async def setup(bot):
    await bot.add_cog(Scores(bot))
