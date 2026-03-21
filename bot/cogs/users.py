from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.presets import *
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.helpers import separate_beatmap_filters, separate_user_filters
from bot.util.schema import TABLE_METADATA

class Users(commands.Cog):
    """
    User query commands for analyzing player statistics and leaderboards.
    
    This cog provides commands to count users, view leaderboards, and analyze
    user statistics like play counts, clear counts, and performance metrics.
    Requires user registration for most commands to filter by specific users.
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

        # Parse -includes, set defaults
        include_raw = di.get("-include", "")
        include_set = {x.strip().lower() for x in include_raw.split(",") if x.strip()}

        if "loved" not in include_set:
            di.setdefault("-status-not", "loved")

        if "converts" not in include_set:
            di.setdefault("-convertless", "true")

    @commands.command(
        aliases=["u"],
        brief="Count users matching filters"
    )
    async def users(self, ctx, *args):
        """
        Count users matching specified filters.
        
        Usage: !users [filters]
        
        Examples:
        - !users -country_code US
        - !users -osu_pp-min 8000
        - !users -global_rank-min 1000
        
        Key parameters:
        - -country_code: Filter by country code (US, JP, DE, etc.)
        - -osu_pp-min/-osu_pp-max: Filter by osu! performance points
        - -global_rank-min/-global_rank-max: Filter by global rank
        - -username-like: Search by username
        - -mode: Filter by preferred game mode
        
        Notes: 
        - Counts distinct users from the userLive table
        - Supports all userLive table columns as filters
        - Case-insensitive username search with -username-like
        """
        di = get_args(args)
        query = QueryBuilder(di, "count(*)", "userLive")
        sql = query.getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        await ctx.reply(str(result[0][0]))

    @commands.command(
        aliases=["l"],
        brief="Display user leaderboard"
    )
    async def leaderboard(self, ctx, *args):
        """
        Display score-based leaderboards with various metrics.
        
        Usage: !leaderboard [filters] [-o preset] [-page N] [-limit N]
        
        Examples:
        - !leaderboard -o plays -stars-min 6
        - !leaderboard -o hardclears -mode 0 -l 25
        - !leaderboard -o ss -country_code US
        
        Key parameters:
        - -o: Leaderboard preset (plays, hardclears, ss, fc, etc.)
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -country_code: Filter by country
        - -page/-limit: Pagination controls
        - -include: Include specific grades (d, everyone, etc.)
        
        Available presets:
        - plays: Total distinct beatmaps played
        - hardclears: Beatmaps cleared with score ≥400k and B+ rank
        - ss: Total SS scores achieved
        - fc: Total full combos achieved
        - unique_ss: Beatmaps where user has only SS
        
        Notes:
        - Automatically resolves user for "me" page functionality
        - Shows user's position if they appear in results
        - Based on scoreLive table aggregations
        """
        di = get_args(args)
        table = "userLive"
        # Get user_id if not specified
        discordid = ctx.author.id
        username = None
        if "-user_id" not in di and "-username" not in di:
            query = f"SELECT r.user_id, ul.username FROM registrations r inner join userLive ul on r.user_id = ul.user_id WHERE discordid = '{discordid}'"
            result, _ = await self.bot.db.executeQuery(query)
            if result and result[0]:
                username = result[0][1] if len(result[0]) > 1 else None
        
        preset = get_leaderboard_preset(di.get("-o", "clears"))

        if preset is not None:
            columns = preset["columns"]
            title = preset["title"]
            alias = preset.get("alias")
            for k, v in preset.items():
                if k.startswith("-"):
                    di[k] = v

            await self._set_defaults(ctx, di)

            if di.get("-include") == "d":
                di.pop("-grade-not", None)
        else:
            await ctx.reply("Preset not allowed. See valid presets with !help presets")           
            return
        
        sql = QueryBuilder(di, columns, table).getQuery()
        result, elapsed = await self.bot.db.executeQuery(sql)
        if di.get("-o") == "sets":
            columns = "DISTINCT beatmapset_id"
        else:
            columns = "DISTINCT beatmap_id"
        beatmap_args = separate_beatmap_filters(di)
        sql = QueryBuilder(beatmap_args, columns, "beatmapLive").getQuery()
        beatmaps, elapsed = await self.bot.db.executeQuery(sql)

        formatter = Formatter(title=title, footer=f"Based on Scores • took {elapsed:.2f}s")

        page_size = int(di.get("-limit", 10))
        page_arg = di.get("-page", "1")
        
        if page_arg.lower() == "me" and username is not None:
            user_page = formatter.calculate_user_page(result, username, page_size)
            if user_page is not None:
                page = user_page
            else:
                page = 1  # Default to page 1 if user not found
        else:
            page = int(page_arg)

        count = len(beatmaps)
        
        embed = formatter.as_leaderboard(
            result, count, 
            page=page, 
            page_size=page_size, 
            elapsed=elapsed,
            user=username,
            metric_alias=alias
        )
        await ctx.reply(embed=embed)

    @commands.command(
        aliases=["ul"],
        brief="Display user leaderboard"
    )
    async def userlist(self, ctx, *args):
        """
        Display user-based leaderboards with various statistics.
        
        Usage: !userlist [filters] [-o preset] [-page N] [-limit N]
        
        Examples:
        - !userlist -o playcount -country_code US
        - !userlist -o playtime -osu_pp-min 5000
        - !userlist -o score -global_rank-max 1000
        
        Key parameters:
        - -o: User statistic preset (playcount, playtime, score)
        - -country_code: Filter by country code
        - -osu_pp-min/-osu_pp-max: Filter by performance points
        - -global_rank-min/-global_rank-max: Filter by global rank
        - -username-like: Search by username
        - -page/-limit: Pagination controls
        
        Available presets:
        - playcount: Total play count
        - playtime: Total play time (in hours)
        - score: Total ranked score
        
        Notes:
        - Automatically resolves user for "me" page functionality
        - Shows user's position if they appear in results
        - Based on userLive table statistics
        - Supports custom column selection with -columns
        """
        di = get_args(args)
        table = "userLive"
        # Get user_id if not specified
        discordid = ctx.author.id
        username = None
        if "-user_id" not in di and "-username" not in di:
            query = f"SELECT r.user_id, ul.username FROM registrations r inner join userLive ul on r.user_id = ul.user_id WHERE discordid = '{discordid}'"
            result, _ = await self.bot.db.executeQuery(query)
            if result and result[0]:
                username = result[0][1] if len(result[0]) > 1 else None
        
        preset_key = di.get("-o", "total_ranked_score")

        user_columns = set(TABLE_METADATA["userLive"].keys())

        preset = get_user_preset(di.get("-o"))

        print(di["-o"])
        print(preset)

        if preset_key in user_columns:
            columns = di.get("-columns", f"username,COALESCE({preset_key}, 0)")
            title = "Leaderboard"
            di.setdefault("-order", f"COALESCE({preset_key}, 0)")
        elif preset is not None:
            columns = preset["columns"]
            title = preset["title"]
            for k, v in preset.items():
                if k.startswith("-"):
                    di[k] = v

            di = separate_user_filters(di)           
        else:
            await ctx.reply("Preset not allowed. See valid presets with !help presets or !help user")
            return
        
        sql = QueryBuilder(di, columns, table).getQuery()
        result, elapsed = await self.bot.db.executeQuery(sql)

        user_args = separate_user_filters(di)
        sql = QueryBuilder(user_args, columns, "userLive").getQuery()
        beatmaps, elapsed = await self.bot.db.executeQuery(sql)

        formatter = Formatter(title=title, footer=f"Based on Users • took {elapsed:.2f}s")

        page_size = int(di.get("-limit", 10))
        page_arg = di.get("-page", "1")
        
        if page_arg.lower() == "me" and username is not None:
            user_page = formatter.calculate_user_page(result, username, page_size)
            if user_page is not None:
                page = user_page
            else:
                page = 1  # Default to page 1 if user not found
        else:
            page = int(page_arg)

        count = len(beatmaps)
        
        embed = formatter.as_leaderboard(
            result, count, 
            page=page, 
            page_size=page_size, 
            elapsed=elapsed,
            user=username,
            total_label='users',
            metric_alias=preset_key
        )
        await ctx.reply(embed=embed)

    @commands.command(
        aliases=["uniquess", "uss"],
        brief="Display unique SS leaderboard"
    )
    async def unique_ss(self, ctx, *args):
        """
        Display leaderboard for users with unique SS scores.
        
        Usage: !unique_ss [filters]
        
        Examples:
        - !unique_ss -stars-min 6 -mode 0
        - !unique_ss -country_code US
        - !unique_ss -grade SS
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -country_code: Filter by country
        - -grade: Filter by grade (SS, SSH, etc.)
        
        Notes:
        - Shows users who have the only SS on beatmaps
        - Uses the unique_ss leaderboard preset
        - Automatically resolves user for "me" page functionality
        - Based on scoreLive table aggregations
        """
        di = get_args(args)

        di["-o"] = "unique_ss"

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.leaderboard(ctx, *args)

    @commands.command(
        brief="Display clear statistics leaderboard"
    )
    async def clears(self, ctx, *args):
        """
        Display leaderboard for user clear statistics.
        
        Usage: !clears [filters]
        
        Examples:
        - !clears -stars-min 5 -mode 0
        - !clears -country_code JP
        - !clears -grade-not D
        
        Key parameters:
        - -stars-min/-stars-max: Filter by star rating range
        - -mode: Game mode (0=osu, 1=taiko, 2=fruits, 3=mania)
        - -country_code: Filter by country
        - -grade-not: Exclude specific grades (D, etc.)
        - -include: Include specific grades or converts
        
        Notes:
        - Shows total clear counts per user
        - Uses the clears user preset
        - Automatically resolves user for "me" page functionality
        - Based on userLive table statistics
        """
        di = get_args(args)

        di["-o"] = "clears"

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.userlist(ctx, *args)

async def setup(bot):
    await bot.add_cog(Users(bot))
