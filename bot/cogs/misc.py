# bot/cogs/misc.py
from discord.ext import commands
import discord
from bot.util.helpers import get_args
from bot.util.schema import TABLE_METADATA, get_column_info, generate_help_text

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
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
        await self.bot.db.executeParametrized(query, int(user), discord_name, discord_id)
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

    @commands.command(aliases=["h"])
    async def help(self, ctx, *args):
        """Display help for available columns and parameters"""
        
        if not args:
            # General help overview
            embed = discord.Embed(
                title="🎮 osu! Query Bot Help",
                description="Query osu! beatmaps, scores, and user data with powerful filters and parameters.",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📚 Help Topics",
                value=(
                    "`!help commands` - List all available commands\n"
                    "`!help operators` - Query operators and filters\n"
                    "`!help parameters` - Common parameters (pagination, ordering)\n"
                    "`!help presets` - Predefined query presets\n"
                    "`!help examples` - Usage examples\n"
                    "`!help <column>` - Info about a specific column"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📊 Database Tables",
                value=(
                    "`!help beatmap` - Beatmap columns\n"
                    "`!help score` - Score columns\n"
                    "`!help user` - User columns"
                ),
                inline=False
            )
            
            embed.add_field(
                name="🚀 Quick Start",
                value=(
                    "**Basic query:** `!beatmaps -stars-min 5 -stars-max 7`\n"
                    "**View list:** `!beatmaplist -mode 0 -status ranked -l 15`\n"
                    "**Your scores:** `!scores` (requires registration)\n"
                    "**Register:** `!register -u <osu_user_id>`"
                ),
                inline=False
            )
            
            embed.set_footer(text="Use !help <topic> for detailed information")
            await ctx.reply(embed=embed)
            return
        
        query = args[0].lower()
        
        # Help topics
        if query == "commands":
            await self._send_commands_help(ctx)
        elif query in ["operator", "operators", "filter", "filters"]:
            await self._send_operators_help(ctx)
        elif query in ["parameter", "parameters", "param", "params"]:
            await self._send_parameters_help(ctx)
        elif query in ["preset", "presets"]:
            await self._send_presets_help(ctx)
        elif query in ["example", "examples"]:
            await self._send_examples_help(ctx)
        # Help for specific tables
        elif query in ["beatmap", "beatmaps", "beatmaplive"]:
            await self._send_table_help(ctx, "beatmapLive", "Beatmap Columns")
        elif query in ["score", "scores", "scorelive"]:
            await self._send_table_help(ctx, "scoreLive", "Score Columns")
        elif query in ["user", "users", "userlive"]:
            await self._send_table_help(ctx, "userLive", "User Columns")
        else:
            # Help for specific column
            column_info = get_column_info(query)
            if column_info:
                help_text = generate_help_text(query)
                
                embed = discord.Embed(
                    title=f"Column: {query}",
                    description=column_info.get("description", "No description available"),
                    color=discord.Color.green()
                )
                
                # Add type info
                embed.add_field(name="Type", value=column_info.get("type", "unknown"), inline=True)
                
                # Add table info
                from bot.util.schema import get_table_for_column
                table = get_table_for_column(query)
                if table:
                    embed.add_field(name="Table", value=table, inline=True)
                
                # Add range if exists
                if "range" in column_info:
                    min_val, max_val = column_info["range"]
                    range_str = f"{min_val or '∞'} to {max_val or '∞'}"
                    embed.add_field(name="Range", value=range_str, inline=True)
                
                # Add enum if exists
                if "enum" in column_info:
                    enum_str = ", ".join(map(str, column_info["enum"]))
                    embed.add_field(name="Valid Values", value=enum_str, inline=False)
                
                # Add usage examples
                examples = []
                examples.append(f"`-{query} <value>` - Exact match")
                if column_info.get("type") in ["int", "float"]:
                    examples.append(f"`-{query}-min <value>` - Greater than or equal")
                    examples.append(f"`-{query}-max <value>` - Less than")
                if column_info.get("type") == "str":
                    examples.append(f"`-{query}-like <text>` - Contains text")
                examples.append(f"`-{query}-not <value>` - Not equal to")
                
                embed.add_field(name="Usage", value="\n".join(examples), inline=False)
                
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(f"❌ Unknown column or topic: `{query}`\nUse `!help` for available options.")
    
    async def _send_commands_help(self, ctx):
        """Send help for all available commands"""
        embed = discord.Embed(
            title="📚 Available Commands",
            description="All commands available in the bot",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🗺️ Beatmap Commands",
            value=(
                "`!beatmaps [filters]` - Count beatmaps matching filters\n"
                "`!beatmaplist [filters]` - List beatmaps with details\n"
                "• Filters: `-stars`, `-ar`, `-cs`, `-od`, `-hp`, `-bpm`, `-mode`, `-status`, etc."
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Score Commands",
            value=(
                "`!scores [filters]` - Count your scores (requires registration)\n"
                "`!scorelist [filters]` - List your scores with details\n"
                "`!scores -o score` - Sum of classic_total_score\n"
                "`!scores -o legacy` - Sum of legacy_total_score\n"
                "• Filters: `-pp`, `-accuracy`, `-grade`, `-mods`, `-beatmap_id`, etc.\n"
                "• Use `-user_id` or `-username` to query other users"
            ),
            inline=False
        )
        
        embed.add_field(
            name="👥 User Commands",
            value=(
                "`!users [filters]` - Count users matching filters\n"
                "`!userlist [filters]` - User leaderboard\n"
                "`!userlist -o <preset>` - Use a preset (see `!help presets`)\n"
                "• Filters: `-pp`, `-country_code`, `-global_rank`, etc.\n"
                "• Presets: plays, clears, hardclears, playcount, playtime"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📦 Collection Commands",
            value=(
                "`!generateosdb [filters] -name <name>` - Create .osdb collection file\n"
                "`!generateosdbs` - Generate multiple collections from .txt file\n"
                "• Upload a .txt file with one command per line"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Utility Commands",
            value=(
                "`!register -u <osu_user_id>` - Register & link Discord account\n"
                "`!link -u <osu_user_id>` - Update linked osu! account\n"
                "`!help [topic]` - Show help information"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use !help <topic> for detailed information on filters and parameters")
        await ctx.reply(embed=embed)
    
    async def _send_operators_help(self, ctx):
        """Send help for query operators"""
        embed = discord.Embed(
            title="🔍 Query Operators",
            description="Operators for filtering data",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Comparison Operators",
            value=(
                "`-column value` - Exact match\n"
                "`-column-min value` - Greater than or equal (≥)\n"
                "`-column-max value` - Less than (<)\n"
                "`-column-not value` - Not equal to (≠)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="List Operators",
            value=(
                "`-column-in val1,val2,val3` - Match any value in list\n"
                "`-column-notin val1,val2` - Exclude values in list"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Text Operators",
            value=(
                "`-column-like text` - Contains text (case-insensitive)\n"
                "`-title-like anime` - Find beatmaps with 'anime' in title\n"
                "`-artist-like touhou` - Find beatmaps by artist"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Special Parameters",
            value=(
                "`-tags <text>` - Search across artist, title, source, version, tags\n"
                "`-username <name>` - Filter by username\n"
                "`-user_id <id>` - Filter by user ID\n"
                "`-unplayed <user_id>` - Beatmaps not played by user\n"
                "`-is_fa` or `-is_fa-true` - Featured Artist beatmaps only\n"
                "`-not_fa` or `-is_fa-false` - Exclude Featured Artists\n"
                "`-year <year>` - Beatmaps ranked in specific year\n"
                "`-highest_score true` - Only highest score per beatmap\n"
                "`-show all` - Show all scores (overrides highest_score)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Examples",
            value=(
                "`-stars-min 6 -stars-max 8` - 6★ to 8★\n"
                "`-mode 0 -status ranked` - Ranked osu!standard maps\n"
                "`-grade-in SS,S,SSH,SH` - S rank or better\n"
                "`-country_code-notin US,JP` - Exclude US and JP"
            ),
            inline=False
        )
        
        embed.set_footer(text="Operators are case-insensitive for text fields")
        await ctx.reply(embed=embed)
    
    async def _send_parameters_help(self, ctx):
        """Send help for common parameters"""
        embed = discord.Embed(
            title="⚙️ Common Parameters",
            description="Parameters that work with most list commands",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="Pagination",
            value=(
                "`-p <page>` - Page number (default: 1)\n"
                "`-l <limit>` - Results per page (default: 10)\n"
                "**Example:** `-p 2 -l 20` - Page 2, 20 results per page"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Ordering",
            value=(
                "`-order <column>` - Sort by column (default: DESC)\n"
                "`-direction ASC|DESC` - Sort direction\n"
                "**Example:** `-order pp -direction DESC` - Highest PP first"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Grouping & Aggregation",
            value=(
                "`-group <column>` - Group results by column\n"
                "`-limit <n>` - Limit total results\n"
                "**Example:** `-group username -order COUNT(*) -limit 100`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Output Options (userlist)",
            value=(
                "`-o <preset>` - Use preset configuration\n"
                "`-columns <col1,col2>` - Custom columns to display\n"
                "`-include d` - Include D rank scores\n"
                "**Example:** `-columns username,pp,play_count -order pp`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Score Filters",
            value=(
                "`-o score` - Sum classic_total_score (scores command)\n"
                "`-o legacy` - Sum legacy_total_score (scores command)\n"
                "`-highest_score true` - Filter to highest scores only"
            ),
            inline=False
        )
        
        embed.set_footer(text="Parameter order doesn't matter")
        await ctx.reply(embed=embed)
    
    async def _send_presets_help(self, ctx):
        """Send help for presets"""
        embed = discord.Embed(
            title="🎯 Query Presets",
            description="Predefined configurations for userlist command",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="`-o plays`",
            value=(
                "**Total plays** - Count of all plays\n"
                "• Columns: username, COUNT(*)\n"
                "• Filters: Highest scores, excludes D ranks by default"
            ),
            inline=False
        )
        
        embed.add_field(
            name="`-o clears`",
            value=(
                "**Total clears** - Passed plays only\n"
                "• Columns: username, COUNT(*)\n"
                "• Filters: No difficulty removing mods, excludes D ranks by default"
            ),
            inline=False
        )
        
        embed.add_field(
            name="`-o hardclears`",
            value=(
                "**Hard clears** - No difficulty affecting mods\n"
                "• Columns: username, COUNT(*)\n"
                "• Filters: No EZ/NF/HT, excludes D ranks by default"
            ),
            inline=False
        )
        
        embed.add_field(
            name="`-o playcount`",
            value=(
                "**Total playcount** - User playcount leaderboard\n"
                "• Columns: username, total_play_count\n"
                "• Ordered by total_play_count"
            ),
            inline=False
        )
        
        embed.add_field(
            name="`-o playtime`",
            value=(
                "**Total playtime** - Total hours played\n"
                "• Columns: username, total_play_time/3600\n"
                "• Ordered by total_play_time"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Usage Example",
            value="`!userlist -o plays -stars-min 6 -p 1 -l 10`",
            inline=False
        )
        
        embed.set_footer(text="You can combine presets with additional filters")
        await ctx.reply(embed=embed)
    
    async def _send_examples_help(self, ctx):
        """Send usage examples"""
        embed = discord.Embed(
            title="💡 Usage Examples",
            description="Common query examples to get you started",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="Beatmap Queries",
            value=(
                "```\n"
                "!beatmaps -stars-min 6 -stars-max 8\n"
                "!beatmaplist -mode 0 -status ranked -ar-min 9\n"
                "!beatmaplist -artist-like demetori -l 20\n"
                "!beatmaps -is_fa -year 2024\n"
                "!beatmaplist -tags anime -bpm-min 180\n"
                "```"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Score Queries",
            value=(
                "```\n"
                "!scores -pp-min 400\n"
                "!scorelist -grade-in SS,S -l 15\n"
                "!scores -stars-min 7 -accuracy-min 98\n"
                "!scorelist -year 2024 -order pp\n"
                "!scores -o score -beatmap_id 123456\n"
                "```"
            ),
            inline=False
        )
        
        embed.add_field(
            name="User Queries",
            value=(
                "```\n"
                "!userlist -o plays -stars-min 6\n"
                "!userlist -o hardclears -l 50\n"
                "!users -country_code US -osu_pp-min 8000\n"
                "!userlist -o playtime -p 2\n"
                "```"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Collection Generation",
            value=(
                "```\n"
                "!generateosdb -stars-min 6 -mode 0 -name \"6* Maps\"\n"
                "!generateosdb -is_fa -status ranked -name \"FA Ranked\"\n"
                "!generateosdb -tags touhou -name \"Touhou Collection\"\n"
                "```"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Advanced Queries",
            value=(
                "```\n"
                "!beatmaplist -length-min 300 -drain_time-max 180\n"
                "!scorelist -statistics_miss-max 5 -pp-min 300\n"
                "!userlist -columns username,osu_pp,osu_global_rank -order osu_pp\n"
                "```"
            ),
            inline=False
        )
        
        embed.set_footer(text="Mix and match filters to create custom queries!")
        await ctx.reply(embed=embed)
    
    async def _send_table_help(self, ctx, table_name, title):
        """Send paginated help for a table's columns"""
        metadata = TABLE_METADATA.get(table_name, {})
        
        if not metadata:
            await ctx.reply(f"❌ No metadata found for table: {table_name}")
            return
        
        # Get all columns from metadata
        all_columns = list(metadata.keys())
        
        # Create chunks of columns for better readability (25 per field to stay under Discord limits)
        chunk_size = 25
        chunks = [all_columns[i:i + chunk_size] for i in range(0, len(all_columns), chunk_size)]
        
        embed = discord.Embed(
            title=f"📖 {title}",
            description=f"Available columns for `{table_name}`. Use `!help <column>` for details.",
            color=discord.Color.blue()
        )
        
        for i, chunk in enumerate(chunks, 1):
            col_list = ", ".join([f"`{c}`" for c in chunk])
            field_name = f"Columns ({(i-1)*chunk_size + 1}-{(i-1)*chunk_size + len(chunk)})" if len(chunks) > 1 else "Columns"
            embed.add_field(name=field_name, value=col_list, inline=False)
        
        embed.set_footer(text=f"Total columns: {len(metadata)} | Use !help <column> for details")
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))
