from discord.ext import commands
from bot.util.helpers import get_args

class Projects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def projectdemetori(self, ctx, *args):
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
