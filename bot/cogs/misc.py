# bot/cogs/misc.py
from discord.ext import commands
import discord
from bot.util.helpers import get_args

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["b"])
    async def manual_query(self, ctx, *args):
        """Exports query results to CSV"""
        await self.bot.db.export_to_csv(args[0], "temp.csv")
        attach = discord.File("temp.csv")
        await ctx.reply(file=attach, content="Here is your response:")

    @commands.command()
    async def register(self, ctx, *args):
        di = get_args(args)
        user = di["-u"]
        discord_name = ctx.author.name
        discord_id = str(ctx.author.id)
        query = "SELECT user_id FROM registrations WHERE discordid = $1"
        existing = await self.bot.db.fetchParametrized(query, discord_id)
        if existing:
            query = """
                INSERT INTO registrations (user_id, registrationdate)
                VALUES ($1, NOW())
                ON CONFLICT DO NOTHING
            """
            await self.bot.db.executeParametrized(query, int(user))
            await ctx.reply(f"Registered user ID {user}")
            return
        query = """
            INSERT INTO registrations (user_id, discordname, discordid, registrationdate)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT DO NOTHING
        """
        await self.bot.db.executeParametrized(query, user, discord_name, discord_id)
        await ctx.reply("Registered and linked your Discord account!")

    @commands.command()
    async def link(self, ctx, *args):
        di = get_args(args)

        user = di["-u"]

        discordname = ctx.author.name
        discordid = ctx.author.id

        query = (f"INSERT INTO registrations VALUES ({user}, '{discordname}', '{discordid}', NOW()) on conflict (user_id) do UPDATE SET discordname = EXCLUDED.discordname, discordid = EXCLUDED.discordid")
        await self.bot.db.executeQuery(query)

        await ctx.reply(content="Updated!")

async def setup(bot):
    await bot.add_cog(Misc(bot))
