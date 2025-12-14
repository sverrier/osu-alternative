from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.presets import PRESETS
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.helpers import separate_beatmap_filters

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    async def _set_defaults(self, ctx, di):
        discordid = ctx.author.id

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


    @commands.command(aliases=["u"])
    async def users(self, ctx, *args):
        """Count of users"""
        di = get_args(args)
        query = QueryBuilder(di, "count(*)", "userLive")
        sql = query.getQuery()
        result, _ = await self.bot.db.executeQuery(sql)
        await ctx.reply(str(result[0][0]))

    @commands.command(aliases=["ul", "leaderboard", "l"])
    async def userlist(self, ctx, *args):
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
        
        preset_key = di.get("-o")
        if preset_key in PRESETS:
            preset = PRESETS[preset_key]
            columns = preset["columns"]
            title = preset["title"]
            for k, v in preset.items():
                if k.startswith("-"):
                    di[k] = v

            await self._set_defaults(ctx, di)

            if di.get("-include") == "d":
                di.pop("-grade-not", None)
        else:
            columns = di.get("-columns", f"username,{di.get("-o", "total_ranked_score")}")
            title = "Leaderboard"
            di.setdefault("-order", di.get("-o", "total_ranked_score"))
        
        sql = QueryBuilder(di, columns, table).getQuery()
        result, elapsed = await self.bot.db.executeQuery(sql)
        if di.get("-o") == "sets":
            columns = "DISTINCT beatmapLive.beatmapset_id"
        else:
            columns = "DISTINCT beatmapLive.beatmap_id"
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
            user=username
        )
        await ctx.reply(embed=embed)

    @commands.command(aliases=["uniquess", "uss"])
    async def unique_ss(self, ctx, *args):
        di = get_args(args)

        di["-o"] = "unique_ss"

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.userlist(ctx, *args)

    @commands.command()
    async def clears(self, ctx, *args):
        di = get_args(args)

        di["-o"] = "clears"

        args = []
        for k, v in di.items():
            if k.startswith("-"):
                args.extend([k, str(v)])
        await self.userlist(ctx, *args)

async def setup(bot):
    await bot.add_cog(Users(bot))
