from discord.ext import commands
from bot.util.helpers import get_args

class Projects(commands.Cog):
    """
    Special project commands for specific artist or theme-based queries.
    
    This cog provides commands for specialized projects that combine
    multiple queries or have specific themes, such as artist-specific
    leaderboards or themed beatmap collections.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Leaderboard aggregate for all demetori maps"
    )
    async def projectdemetori(self, ctx, *args):
        """
        Special project command for Demetori artist analysis.
        
        Usage: !projectdemetori [filters]
        
        Examples:
        - !projectdemetori -stars-min 6 -mode 0
        - !projectdemetori -status ranked
        - !projectdemetori -country_code US
        
        Key parameters:
        - [filters]: Any beatmap filters (stars, mode, status, etc.)
        - Automatically filters to artist containing "demetori"
        
        Output:
        - First leaderboard: Total plays on Demetori maps (including D rank)
        - Second leaderboard: Hard clears on Demetori maps
        
        Notes:
        - Combines two userlist queries with Demetori artist filter
        - Shows both play counts and clear statistics for the artist
        - Useful for analyzing performance on Demetori's music
        """
        di = get_args(args)
        di["-artist-like"] = "demetori"
        
        # Get the Users cog to access userlist
        users_cog = self.bot.get_cog("Users")
        if not users_cog:
            await ctx.reply("Users cog not loaded.")
            return
        
        # First userlist: Completion points
        args_plays = []
        for k, v in di.items():
            if k.startswith("-"):
                args_plays.extend([k, str(v)])
        args_plays.extend(["-o", "completion"])
        
        await users_cog.leaderboard(ctx, *args_plays)

        # Second userlist: FCs
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "overclears"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)
        
        # Third userlist: Score
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "classicscore"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)

    @commands.command(
        brief="Leaderboard aggregate for 2026"
    )
    async def project2026(self, ctx, *args):
        """
        Special project command for hitogata.
        """
        di = get_args(args)
        di["-year"] = "2026"
        
        # Get the Users cog to access userlist
        users_cog = self.bot.get_cog("Users")
        if not users_cog:
            await ctx.reply("Users cog not loaded.")
            return
        
        # First userlist: Completion points
        args_plays = []
        for k, v in di.items():
            if k.startswith("-"):
                args_plays.extend([k, str(v)])
        args_plays.extend(["-o", "completion"])
        
        await users_cog.leaderboard(ctx, *args_plays)

        # Second userlist: FCs
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "fc"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)
        
        # Third userlist: Score
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "score"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)

    @commands.command(
        brief="Leaderboard aggregate for the legendary hitogata set"
    )
    async def projecthitogata(self, ctx, *args):
        """
        Special project command for hitogata.
        """
        di = get_args(args)
        di["-beatmapset_id"] = "942714"
        
        # Get the Users cog to access userlist
        users_cog = self.bot.get_cog("Users")
        if not users_cog:
            await ctx.reply("Users cog not loaded.")
            return
        
        # First userlist: Completion points
        args_plays = []
        for k, v in di.items():
            if k.startswith("-"):
                args_plays.extend([k, str(v)])
        args_plays.extend(["-o", "completion"])
        
        await users_cog.leaderboard(ctx, *args_plays)

        # Second userlist: FCs
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "fc"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)
        
        # Third userlist: Score
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "score"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)

    @commands.command(
        brief="Leaderboard aggregate for hit anime sword art online",
        aliases=["projectsao",]
    )
    async def projectswordartonline(self, ctx, *args):
        """
        Special project command for sword art online.
        """
        di = get_args(args)
        di["-search"] = "%sword%art%online%"
        
        # Get the Users cog to access userlist
        users_cog = self.bot.get_cog("Users")
        if not users_cog:
            await ctx.reply("Users cog not loaded.")
            return
        
        # First userlist: Completion points
        args_plays = []
        for k, v in di.items():
            if k.startswith("-"):
                args_plays.extend([k, str(v)])
        args_plays.extend(["-o", "completion"])
        
        await users_cog.leaderboard(ctx, *args_plays)

        # Second userlist: FCs
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "fc"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)
        
        # Third userlist: Score
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "score"])
        
        await users_cog.leaderboard(ctx, *args_hardclears)

        

async def setup(bot):
    await bot.add_cog(Projects(bot))
