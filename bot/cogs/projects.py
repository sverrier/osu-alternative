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
        brief="Special Demetori artist analysis project"
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
        
        # First userlist: plays with -include d
        args_plays = []
        for k, v in di.items():
            if k.startswith("-"):
                args_plays.extend([k, str(v)])
        args_plays.extend(["-o", "plays", "-include", "d"])
        
        await users_cog.userlist(ctx, *args_plays)
        
        # Second userlist: hardclears
        args_hardclears = []
        for k, v in di.items():
            if k.startswith("-"):
                args_hardclears.extend([k, str(v)])
        args_hardclears.extend(["-o", "hardclears"])
        
        await users_cog.userlist(ctx, *args_hardclears)

        

async def setup(bot):
    await bot.add_cog(Projects(bot))
