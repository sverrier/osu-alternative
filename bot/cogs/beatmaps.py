from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.presets import *
from bot.util.formatting import format_field
from datetime import datetime
from datetime import datetime, timedelta, timezone

class Beatmaps(commands.Cog):
    """
    Beatmap query commands for searching and analyzing osu! beatmaps.
    
    This cog provides commands to count, list, and analyze beatmaps from the database
    using various filters like difficulty, status, artist, and more.
    """
    def __init__(self, bot):
        self.bot = bot

    async def _set_defaults(self, ctx, di):
        discordid = ctx.author.id

        if di.get("-mode") is None and di.get("-mode-in") is None:
            #default to user set mode
            query = f"SELECT mode FROM registrations WHERE discordid = '{discordid}'"
            rows, _ = await self.bot.db.executeQuery(query)
            if not rows:
                return
        
            di["-mode-in"] = rows[0]["mode"]

        if di.get("-include") != "loved":
            di.setdefault("-status-not", "loved")
        


    @commands.command(
        aliases=["b"],
        brief="Count beatmaps matching filters"
    )
    async def beatmaps(self, ctx, *args):
        """
        Count beatmaps matching specified filters.
        
        Usage: !beatmaps [filters] [-o preset]
        
        Examples:
        - !beatmaps -stars-min 5 -stars-max 7
        - !beatmaps -mode 0 -status ranked
        - !beatmaps -artist-like demetori -o count
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like: Search by artist name
        - -o: Output preset (count, length, etc.)
        
        Notes: Requires registration for default mode filtering.
        """
        di = get_args(args)
        table = "beatmapLive"

        await self._set_defaults(ctx, di)

        if di.get("-o", "count") in BEATMAP_PRESETS:
            preset = get_beatmap_preset(di.get("-o", "count"))
            columns = preset["columns"]
            for k, v in preset.items():
                if k.startswith("-"):
                    di[k] = v
            alias = preset.get("alias", "result")
        else:
            await ctx.reply("Preset not allowed. See valid presets with !help presets")

        sql = QueryBuilder(di, columns, "beatmapLive").getQuery()
        result, _ = await self.bot.db.executeQuery(sql)

        val = result[0][0]
        msg = format_field(alias, val, table=table, alias=alias)
        
        await ctx.reply(msg)

    @commands.command(
        aliases=["bl"],
        brief="List beatmaps with detailed information"
    )
    async def beatmaplist(self, ctx, *args):
        """
        List beatmaps with detailed information matching specified filters.
        
        Usage: !beatmaplist [filters] [-page N] [-limit N]
        
        Examples:
        - !beatmaplist -stars-min 6 -mode 0 -l 15
        - !beatmaplist -artist-like touhou -status ranked
        - !beatmaplist -bpm-min 180 -page 2
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like/-title-like: Search by artist or title
        - -page/-limit: Pagination controls
        - -order: Sort by column (e.g., stars, pp, accuracy)
        - -direction: Sort direction (ASC/DESC)
        
        Notes: Displays beatmap details including artist, title, version, and IDs.
        """
        di = get_args(args)

        await self._set_defaults(ctx, di)

        order_col = di.get("-order")
        columns = "stars, artist, title, version, beatmap_id, beatmapset_id, mode"
        table = "beatmapLive"

        # Select the column if ordering by it
        if order_col:
            columns = f"{columns}, {order_col}"

        query = QueryBuilder(di, columns, table)
        result, elapsed = await self.bot.db.executeQuery(query.getQuery())

        formatter = Formatter(title=f"Total beatmaps: {len(result)}")

        extra_key = None

        if order_col:
            extra_key = order_col                # which column to display

        embed = formatter.as_beatmap_list(
            result,
            page=int(di.get("-page", 1)),
            page_size=int(di.get("-limit", 10)),
            elapsed=elapsed,
            extra_key=extra_key,
        )

        await ctx.reply(embed=embed)

    @commands.command(
        aliases=["bsl"],
        brief="List beatmap sets with aggregated information"
    )
    async def beatmapsetlist(self, ctx, *args):
        """
        List beatmap sets with aggregated information matching specified filters.
        
        Usage: !beatmapsetlist [filters] [-page N] [-limit N]
        
        Examples:
        - !beatmapsetlist -stars-min 5 -mode 0
        - !beatmapsetlist -artist-like demetori -l 10
        - !beatmapsetlist -status ranked -page 2
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like/-title-like: Search by artist or title
        - -page/-limit: Pagination controls
        - -order: Sort by column (e.g., beatmap_count, min_sr, max_sr)
        - -direction: Sort direction (ASC/DESC)
        
        Notes: Groups beatmaps by beatmapset_id, showing artist, title, 
        beatmap count, and star rating range for each set.
        """
        di = get_args(args)

        await self._set_defaults(ctx, di)

        columns = (
            "beatmapset_id, "
            "MIN(artist) AS artist, "
            "MIN(title) AS title, "
            "COUNT(*) AS beatmap_count, "
            "MIN(stars) AS min_sr, "
            "MAX(stars) AS max_sr"
        )

        # Default grouping and ordering by set
        di.setdefault("-group", "beatmapset_id")
        di.setdefault("-order", "beatmapset_id")
        di.setdefault("-direction", "asc")

        query = QueryBuilder(di, columns, "beatmapLive")
        result, elapsed = await self.bot.db.executeQuery(query.getQuery())

        # You'd add a formatter for sets, similar to as_beatmap_list
        formatter = Formatter(title=f"Total beatmapsets: {len(result)}")
        embed = formatter.as_beatmapset_list(
            result,
            page=int(di.get("-page", 1)),
            page_size=int(di.get("-limit", 10)),
            elapsed=elapsed,
        )
        await ctx.reply(embed=embed)

    @commands.command(
        brief="Add beatmaps matching filters to user's queue"
    )
    async def queue(self, ctx, *args):
        """
        Add beatmaps matching filters to a user's queue.
        
        Usage: !queue [filters] -user <user_id>
        
        Examples:
        - !queue -stars-min 6 -stars-max 8 -user 123456
        - !queue -mode 0 -status ranked -user 789012
        - !queue -artist-like touhou -user 345678
        
        Key parameters:
        - [filters]: Any beatmap filters (stars, mode, status, etc.)
        - -user: Target user ID to add beatmaps to queue
        
        Notes: 
        - Maximum 1000 beatmaps can be queued at once
        - Beatmaps are added with current timestamp
        - Conflicts (duplicate beatmaps) are ignored
        - Requires specifying a user ID
        """
        di = get_args(args)

        await self._set_defaults(ctx, di)

        # 2) Build beatmap query (same logic as beatmaplist)
        columns = "beatmap_id"
        table = "beatmapLive"

        query = QueryBuilder(di, columns, table)
        result, _ = await self.bot.db.executeQuery(query.getQuery())

        if not result:
            await ctx.reply("No beatmaps matched your query.")
            return
        
        if len(result) > 1000:
            await ctx.reply("Please limit your set to 1000 maps.")
            return
        
        user_id = di.get("-user")

        if not user_id:
            await ctx.reply("Please specify a user with -user.")
            return

        # 3) Insert into queue
        values = ",".join(
            f"({user_id}, {row['beatmap_id']}, NOW())"
            for row in result
        )

        insert_query = f"""
            INSERT INTO public.queue (user_id, beatmap_id, insertionTime)
            VALUES {values}
            ON CONFLICT (user_id, beatmap_id) DO NOTHING
        """

        await self.bot.db.executeQuery(insert_query)

        await ctx.reply(f"Queued **{len(result)}** beatmaps.")


    @commands.command(
        aliases=["nbss", "neverbeenssed"],
        brief="Find beatmaps never SS'd (perfect score)"
    )
    async def never_been_ssed(self, ctx, *args):
        """
        Find beatmaps that have never been SS'd (perfect score).
        
        Usage: !never_been_ssed [filters]
        
        Examples:
        - !never_been_ssed -stars-min 6 -mode 0
        - !never_been_ssed -artist-like demetori
        - !never_been_ssed -status ranked
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like/-title-like: Search by artist or title
        
        Notes: 
        - Automatically filters to beatmaps ranked within last 30 days
        - Orders results by star rating (ascending)
        - Shows beatmaps with ss_count = 0
        """
        di = get_args(args)

        di["-ss_count"] = 0
        di.setdefault("-order", "stars")
        di.setdefault("-direction", "asc")
        di.setdefault(
            "-ranked_date-max",
            (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        )

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.beatmaplist(ctx, *args)

    @commands.command(
        aliases=["leastssed"],
        brief="Find beatmaps with fewest SS scores"
    )
    async def least_ssed(self, ctx, *args):
        """
        Find beatmaps with the fewest SS scores.
        
        Usage: !least_ssed [filters]
        
        Examples:
        - !least_ssed -stars-min 6 -mode 0
        - !least_ssed -artist-like touhou
        - !least_ssed -status ranked
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like/-title-like: Search by artist or title
        
        Notes: 
        - Orders results by ss_count (ascending)
        - Shows beatmaps with the lowest number of SS scores
        """
        di = get_args(args)

        di.setdefault("-order", "ss_count")
        di.setdefault("-direction", "asc")

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.beatmaplist(ctx, *args)

    @commands.command(
        aliases=["nbfc", "neverbeenfced"],
        brief="Find beatmaps never FC'd (full combo)"
    )
    async def never_been_fced(self, ctx, *args):
        """
        Find beatmaps that have never been FC'd (full combo).
        
        Usage: !never_been_fced [filters]
        
        Examples:
        - !never_been_fced -stars-min 6 -mode 0
        - !never_been_fced -artist-like demetori
        - !never_been_fced -status ranked
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like/-title-like: Search by artist or title
        
        Notes: 
        - Automatically filters to beatmaps ranked within last 7 days
        - Orders results by star rating (ascending)
        - Shows beatmaps with fc_count = 0
        """
        di = get_args(args)

        di["-fc_count"] = 0
        di.setdefault("-order", "stars")
        di.setdefault("-direction", "asc")
        di.setdefault(
            "-ranked_date-max",
            (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        )

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.beatmaplist(ctx, *args)

    @commands.command(
        aliases=["leastfced"],
        brief="Find beatmaps with fewest FC scores"
    )
    async def least_fced(self, ctx, *args):
        """
        Find beatmaps with the fewest FC scores.
        
        Usage: !least_fced [filters]
        
        Examples:
        - !least_fced -stars-min 6 -mode 0
        - !least_fced -artist-like touhou
        - !least_fced -status ranked
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -status: Beatmap status (ranked, approved, loved, etc.)
        - -artist-like/-title-like: Search by artist or title
        
        Notes: 
        - Orders results by fc_count (ascending)
        - Shows beatmaps with the lowest number of FC scores
        """
        di = get_args(args)

        di.setdefault("-order", "fc_count")
        di.setdefault("-direction", "asc")

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.beatmaplist(ctx, *args)

async def setup(bot):
    await bot.add_cog(Beatmaps(bot))
