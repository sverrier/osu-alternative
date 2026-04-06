# bot/cogs/misc.py
from discord.ext import commands
import discord
from bot.util.helpers import *
from bot.util.schema import *
from bot.util.presets import *

class Misc(commands.Cog):
    """
    Miscellaneous utility commands for general bot functionality.
    
    This cog provides various utility commands including help,
    registration, and other general-purpose functions that don't
    fit into the other specialized cogs.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Execute manual SQL query and export to CSV"
    )
    async def manual_query(self, ctx, *args):
        """
        Execute a manual SQL query and export results to CSV.
        
        Usage: !manual_query "SELECT * FROM table LIMIT 10"
        
        Examples:
        - !manual_query "SELECT * FROM beatmapLive WHERE stars > 6"
        - !manual_query "SELECT username, pp FROM userLive ORDER BY pp DESC"
        
        Key parameters:
        - [query]: Raw SQL query string (must be quoted)
        
        Output:
        - Exports query results to temp.csv and sends as Discord attachment
        - Shows "Here is your response:" message with file
        
        Notes:
        - Direct SQL access for advanced users
        - Results are temporary and stored in temp.csv
        - Use with caution - no validation of query safety
        """
        await self.bot.db.export_to_csv(args[0], "temp.csv")
        attach = discord.File("temp.csv")
        await ctx.reply(file=attach, content="Here is your response:")

    @commands.command(
        brief="Register and link Discord account to osu! user"
    )
    async def register(self, ctx, user: int):
        """
        Register and link your Discord account to an osu! user ID.
        
        Usage: !register <osu_user_id>
        
        Examples:
        - !register 123456
        - !register 987654
        
        Key parameters:
        - <osu_user_id>: Your osu! user ID number
        
        Process:
        1. Checks if Discord account is already linked to another user
        2. Checks if target user is already registered
        3. Handles various edge cases for linking/unlinking
        4. Provides clear status messages throughout
        
        Output:
        - Success message with registration/linking status
        - Warning if Discord is already linked elsewhere
        - Progress indicator during database operations
        
        Notes:
        - Safe handling of concurrent database operations
        - Prevents overwriting existing Discord links
        - Supports both new registration and linking existing accounts
        - Uses ON CONFLICT DO NOTHING for safe inserts
        """
        discord_name = ctx.author.name
        discord_id = str(ctx.author.id)
        user_id = int(user)

        # 1) Check if this discord is already linked to some (possibly different) user_id
        q_discord_link = "SELECT user_id FROM registrations WHERE discordid = $1 LIMIT 1"
        linked_row = await self.bot.db.fetchParametrized(q_discord_link, discord_id)
        linked_user_id = None
        if linked_row:
            linked_user_id = linked_row[0]["user_id"] if isinstance(linked_row[0], dict) else linked_row[0][0]

        discord_is_linked_elsewhere = (linked_user_id is not None and linked_user_id != user_id)

        # 2) Check if the target user is already registered and whether it already has a discordid
        q_user_reg = "SELECT discordid FROM registrations WHERE user_id = $1 LIMIT 1"
        user_row = await self.bot.db.fetchParametrized(q_user_reg, user_id)

        user_is_registered = bool(user_row)
        user_discordid = None
        if user_row:
            user_discordid = user_row[0].get("discordid") if isinstance(user_row[0], dict) else user_row[0][0]
        user_has_discord = user_discordid is not None and str(user_discordid) != ""

        # Tell the user BEFORE any insert/update that might block due to triggers/locks
        status_msg = await ctx.reply(
            f"Starting registration for user ID `{user_id}`… this can take a bit if the database is busy."
        )

        # ---- CASE A: user is NOT registered yet ----
        if not user_is_registered:
            if discord_is_linked_elsewhere:
                # Register WITHOUT linking
                q_insert = """
                    INSERT INTO registrations (user_id, registrationdate)
                    VALUES ($1, NOW())
                    ON CONFLICT (user_id) DO NOTHING
                """
                await self.bot.db.executeParametrized(q_insert, user_id)

                await status_msg.edit(
                    content=(
                        f"✅ Registered user ID `{user_id}`.\n"
                        f"⚠️ Your Discord is already linked to user ID `{linked_user_id}`, "
                        f"so I did **not** link it here."
                    )
                )
                return

            # Register + link
            q_insert = """
                INSERT INTO registrations (user_id, discordname, discordid, registrationdate)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id) DO NOTHING
            """
            await self.bot.db.executeParametrized(q_insert, user_id, discord_name, discord_id)

            await status_msg.edit(content=f"✅ Registered user ID `{user_id}` and linked your Discord account.")
            return

        # ---- CASE B: user IS registered already ----
        if user_has_discord:
            # Already linked (to someone). Do nothing.
            await status_msg.edit(content=f"✅ User ID `{user_id}` is already registered and linked. Nothing to do.")
            return

        # User registered but discord not linked
        if discord_is_linked_elsewhere:
            # Caller discord is linked elsewhere -> do NOT link, but registration already exists
            await status_msg.edit(
                content=(
                    f"✅ User ID `{user_id}` is already registered.\n"
                    f"⚠️ Your Discord is already linked to user ID `{linked_user_id}`, "
                    f"so I did **not** link it here."
                )
            )
            return

        # Link discord to this already-registered user (only if still NULL to avoid overwriting)
        q_link = """
            UPDATE registrations
               SET discordname = $2,
                   discordid   = $3
             WHERE user_id     = $1
               AND discordid IS NULL
        """
        await self.bot.db.executeParametrized(q_link, user_id, discord_name, discord_id)

        await status_msg.edit(content=f"✅ Linked your Discord account to already-registered user ID `{user_id}`.")

    @commands.command(
        brief="Link Discord account to osu! user"
    )
    async def link(self, ctx, user):
        """
        Link or update your Discord account to an osu! user ID.
        
        Usage: !link <osu_user_id>
        
        Examples:
        - !link 123456
        - !link 987654
        
        Key parameters:
        - <osu_user_id>: Your osu! user ID number
        
        Process:
        - Inserts new registration or updates existing one
        - Uses ON CONFLICT DO UPDATE to handle existing records
        - Overwrites existing Discord links (unlike register command)
        
        Output:
        - "Updated!" confirmation message
        
        Notes:
        - Overwrites existing Discord links (less safe than register)
        - Always updates discordname and discordid fields
        - Use !register for safer linking that preserves existing links
        """
        discordname = ctx.author.name
        discordid = ctx.author.id

        query = (f"INSERT INTO registrations VALUES ({user}, '{discordname}', '{discordid}', NOW()) on conflict (user_id) do UPDATE SET discordname = EXCLUDED.discordname, discordid = EXCLUDED.discordid")
        await self.bot.db.executeQuery(query)

        await ctx.reply(content="Updated!")

    @commands.command(
        brief="Display osu! data fetcher URL"
    )
    async def fetcher(self, ctx):
        """
        Display the osu! data fetcher URL.
        
        Usage: !fetcher
        
        Output:
        - Shows "https://osualtv2.respektive.pw/" as Discord message
        
        Notes:
        - Provides link to the data fetching service
        - Static response, no parameters required
        """
        await ctx.reply(content="https://osualtv2.respektive.pw/")

    @commands.command(
        brief="Display GitHub repository URL"
    )
    async def repo(self, ctx):
        """
        Display the GitHub repository URL.
        
        Usage: !repo
        
        Output:
        - Shows "https://github.com/sverrier/osu-alternative" as Discord message
        
        Notes:
        - Provides link to the project's source code
        - Static response, no parameters required
        """
        await ctx.reply(content="https://github.com/sverrier/osu-alternative")

    @commands.command(
        brief="Set preferred osu! game modes for default filtering"
    )
    async def setmode(self, ctx, *, mode_arg):
        """
        Set your preferred osu! game modes for default filtering.
        
        Usage: !setmode <mode1>,<mode2>,...
        
        Examples:
        - !setmode osu
        - !setmode taiko,mania
        - !setmode 0,1,2,3
        
        Key parameters:
        - <mode_arg>: Comma-separated list of modes (names or numbers)
        - Valid modes: osu(0), taiko(1), fruits/catch/ctb(2), mania(3)
        
        Process:
        1. Parses mode names/numbers into numeric values
        2. Validates all modes are valid
        3. Removes duplicates and sorts
        4. Converts to PostgreSQL tuple format
        5. Updates user's registration record
        
        Output:
        - Success message with updated modes
        - Error if modes are invalid or user not registered
        
        Notes:
        - Modes are stored as comma-separated tuple in database
        - Used as default for commands when no -mode specified
        - Case-insensitive mode name matching
        """
        discordid = ctx.author.id

        # Mapping names → numeric modes
        mode_map = {
            "osu": 0,
            "0": 0,

            "taiko": 1,
            "1": 1,

            "fruits": 2,
            "catch": 2,
            "ctb": 2,
            "2": 2,

            "mania": 3,
            "3": 3,
        }

        # Split on commas, strip spaces
        parts = [p.strip().lower() for p in mode_arg.split(",")]

        mode_vals = []
        for p in parts:
            if p not in mode_map:
                await ctx.reply(
                    "Invalid mode detected. Valid values: 0,1,2,3 or osu, taiko, fruits, mania.\n"
                    f"Bad value: `{p}`"
                )
                return
            mode_vals.append(mode_map[p])

        # Remove duplicates and sort for cleanliness
        mode_vals = sorted(set(mode_vals))

        # Convert into Postgres tuple form: (0,1,3)
        mode_tuple = f"{','.join(str(v) for v in mode_vals)}"

        # 1) Find user_id for this Discord account
        query_find = f"""
            SELECT user_id
            FROM registrations
            WHERE discordid = '{discordid}'
        """

        rows, _ = await self.bot.db.executeQuery(query_find)

        if not rows:
            await ctx.reply("You are not registered. Use !link first.")
            return

        user_id = rows[0]["user_id"]

        # 2) Update mode column with numeric tuple
        query_update = f"""
            UPDATE registrations
            SET mode = '{mode_tuple}'
            WHERE user_id = {user_id}
        """

        await self.bot.db.executeQuery(query_update)

        await ctx.reply(f"Updated modes to **{mode_tuple}**!")



    @commands.command(
        aliases=["h"],
        brief="Display comprehensive help information"
    )
    async def help(self, ctx, *args):
        """
        Display comprehensive help information for all bot features.
        
        Usage: !help [topic] or !help <column>
        
        Examples:
        - !help - Show general overview and available topics
        - !help commands - List all available commands
        - !help operators - Show query operators and filters
        - !help parameters - Show common parameters (pagination, ordering)
        - !help presets - Show predefined query presets
        - !help examples - Show usage examples
        - !help beatmap - Show beatmap table columns
        - !help score - Show score table columns
        - !help user - Show user table columns
        - !help stars - Show help for specific column
        
        Key parameters:
        - [topic]: Help topic (commands, operators, parameters, presets, examples)
        - [table]: Database table (beatmap, score, user)
        - [column]: Specific column name for detailed information
        
        Output:
        - Comprehensive help information based on requested topic
        - Discord embeds with organized information
        - Usage examples and parameter descriptions
        - Column details with types, ranges, and valid values
        
        Notes:
        - Supports both general topics and specific column queries
        - Automatically detects presets and provides detailed information
        - Paginates large column lists for readability
        - Provides usage examples for all major features
        """
        
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

        if query in ["commands", "cmds"]:
            await self._send_commands_help(ctx)
            return

        if query in ["operators", "ops"]:
            await self._send_operators_help(ctx)
            return

        if query in ["parameters", "params"]:
            # Show general parameter overview instead of requiring "-param"
            embed = discord.Embed(
                title="⚙️ Parameters Overview",
                description="Common parameters used across queries",
                color=discord.Color.gold()
            )

            embed.add_field(
                name="Pagination",
                value=(
                    "`-l <limit>` - Number of results (default varies)\n"
                    "`-p <page>` - Page number"
                ),
                inline=False
            )

            embed.add_field(
                name="Ordering",
                value=(
                    "`-order <column>` - Sort by column\n"
                    "`-direction asc|desc` - Sort direction"
                ),
                inline=False
            )

            embed.add_field(
                name="Output Control",
                value=(
                    "`-columns col1,col2` - Select output columns\n"
                    "`-o <preset>` - Use preset output format"
                ),
                inline=False
            )

            embed.set_footer(text="Use !help -<parameter> for detailed info")
            await ctx.reply(embed=embed)
            return

        if query in ["presets"]:
            await self._send_presets_help(ctx)
            return

        if query in ["examples", "example"]:
            await self._send_examples_help(ctx)
            return
        
        cmd = self.bot.get_command(query)
        if cmd:
            await self._send_command_help(ctx, cmd)
            return

        resolved = resolve_any_preset(query)
        if resolved:
            await self._send_single_preset_help(ctx, query)
            return

        if query in ["beatmap", "beatmaps", "beatmaplive"]:
            await self._send_table_help(ctx, "beatmapLive", "Beatmap Columns")
            return

        if query in ["score", "scores", "scorelive"]:
            await self._send_table_help(ctx, "scoreLive", "Score Columns")
            return

        if query in ["user", "users", "userlive"]:
            await self._send_table_help(ctx, "userLive", "User Columns")
            return
        
        if query.startswith("-"):
            handled = await self._send_parameter_help(ctx, query)
            if handled:
                return

        column_info = get_column_info(query)
        if column_info:
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
        embed = discord.Embed(
            title="📚 Available Commands",
            description="All commands available in the bot",
            color=discord.Color.blue()
        )

        cmds = sorted(self.bot.commands, key=lambda c: c.name)

        lines = []
        for cmd in cmds:
            if cmd.hidden:
                continue
            desc = cmd.brief or "No description"
            lines.append(f"`!{cmd.name}` - {desc}")

        # -------------------------
        # Chunk into <=1024 chars
        # -------------------------
        chunks = []
        current = ""

        for line in lines:
            # +1 for newline
            if len(current) + len(line) + 1 > 1024:
                chunks.append(current)
                current = line
            else:
                current = f"{current}\n{line}" if current else line

        if current:
            chunks.append(current)

        # Add chunks as separate fields
        for i, chunk in enumerate(chunks):
            name = "Commands" if i == 0 else "Commands (cont.)"
            embed.add_field(name=name, value=chunk, inline=False)

        await ctx.reply(embed=embed)

    async def _send_command_help(self, ctx, cmd: commands.Command):
        doc = cmd.help or "No help available."

        def parse_help(doc: str):
            sections = {}
            current = "description"
            sections[current] = []

            for line in doc.splitlines():
                line = line.strip()

                if not line:
                    continue

                if line.endswith(":"):
                    current = line[:-1].lower()
                    sections[current] = []
                else:
                    sections[current].append(line)

            return {k: "\n".join(v).strip() for k, v in sections.items()}

        parsed = parse_help(doc)

        embed = discord.Embed(
            title=f"⚙️ Command: !{cmd.name}",
            description=parsed.get("description", ""),
            color=discord.Color.blue()
        )

        # Aliases
        if cmd.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(f"`{a}`" for a in cmd.aliases),
                inline=False
            )

        # Usage
        if "usage" in parsed:
            embed.add_field(name="Usage", value=f"```\n{parsed['usage']}\n```", inline=False)

        # Examples
        if "examples" in parsed:
            embed.add_field(name="Examples", value=f"```\n{parsed['examples']}\n```", inline=False)

        # Key params
        if "key parameters" in parsed:
            embed.add_field(name="Parameters", value=parsed["key parameters"], inline=False)

        # Notes
        if "notes" in parsed:
            embed.add_field(name="Notes", value=parsed["notes"], inline=False)

        embed.set_footer(text="Syntax: !command [filters] [options]")

        await ctx.reply(embed=embed)

    async def _send_parameter_help(self, ctx, query: str):
        # 1Manual meta params first
        if query in PARAMETER_HELP:
            info = PARAMETER_HELP[query]

            embed = discord.Embed(
                title=f"⚙️ Parameter: {query}",
                description=info["description"],
                color=discord.Color.gold()
            )

            if "usage" in info:
                embed.add_field(name="Usage", value=info["usage"], inline=False)

            await ctx.reply(embed=embed)
            return True

        # Dynamic resolution
        resolved = resolve_parameter(query)
        if not resolved:
            return False

        embed = discord.Embed(
            title=f"⚙️ Parameter: {query}",
            color=discord.Color.gold()
        )

        # -------------------------
        # COLUMN-BASED
        # -------------------------
        if resolved[0] in ("column", "column_suffix"):
            column = resolved[1]
            col_info = get_column_info(column)

            embed.description = col_info.get("description", "No description")

            embed.add_field(name="Column", value=f"`{column}`", inline=True)
            embed.add_field(name="Type", value=col_info.get("type", "unknown"), inline=True)

            ops = [
                f"`-{column}` = value",
                f"`-{column}-min` ≥ value",
                f"`-{column}-max` < value",
                f"`-{column}-not` ≠ value",
                f"`-{column}-in` list match",
                f"`-{column}-notin` exclude list",
            ]

            if col_info.get("type") == "str":
                ops.append(f"`-{column}-like` contains text")
                ops.append(f"`-{column}-regex` regex match")

            embed.add_field(name="Operators", value="\n".join(ops), inline=False)

            # Example
            embed.add_field(
                name="Example",
                value=f"`!beatmaplist -{column}-min 5`",
                inline=False
            )

        # -------------------------
        # VALUED PARAMS
        # -------------------------
        elif resolved[0] == "valued":
            param = resolved[1]
            template, deps = VALUED_PARAMS[param]

            embed.description = "Special parameter with custom query behavior."

            if deps:
                embed.add_field(
                    name="Uses Columns",
                    value=", ".join(f"`{c}`" for c in deps),
                    inline=False
                )

            # Optional: hide raw SQL if you want cleaner UX
            embed.add_field(
                name="Behavior",
                value="Custom filtering logic (see operators or examples).",
                inline=False
            )

        # -------------------------
        # VALUELESS PARAMS
        # -------------------------
        elif resolved[0] == "valueless":
            param = resolved[1]
            clause, deps = VALUELESS_PARAMS[param]

            embed.description = "Boolean flag (no value required)."

            if deps:
                embed.add_field(
                    name="Affects Columns",
                    value=", ".join(f"`{c}`" for c in deps),
                    inline=False
                )

        await ctx.reply(embed=embed)
        return True
        
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
    
    async def _send_presets_help(self, ctx):
        """Send help for presets (auto-generated from bot.utils.presets)"""

        def invert_synonyms(syn_map: dict) -> dict:
            """
            canonical -> sorted list of aliases (excluding the canonical key itself if present)
            """
            out = {}
            for alias, canonical in syn_map.items():
                out.setdefault(canonical, set()).add(alias)
            # sort + remove canonical key if it appears in aliases
            cleaned = {}
            for canonical, aliases in out.items():
                aliases = set(aliases)
                aliases.discard(canonical)
                cleaned[canonical] = sorted(aliases)
            return cleaned

        def preset_line(key: str, preset: dict, alias_map: dict) -> str:
            title = preset.get("title", "").strip()
            title_part = f" — {title}" if title else ""
            aliases = alias_map.get(key, [])
            alias_part = f"\n  Aliases: {', '.join(f'`{a}`' for a in aliases[:12])}" if aliases else ""
            more = f" (+{len(aliases)-12} more)" if len(aliases) > 12 else ""
            return f"• `-o {key}`{title_part}{alias_part}{more}"

        lb_aliases = invert_synonyms(LEADERBOARD_PRESET_SYNONYMS)
        user_aliases = invert_synonyms(USER_PRESET_SYNONYMS)
        bm_aliases = invert_synonyms(BEATMAP_PRESET_SYNONYMS)

        embed = discord.Embed(
            title="🎯 Presets (`-o <preset>`)",
            description=(
                "Presets are predefined output configs.\n"
                "Use them like: `!userlist -o plays` or `!userlist -o playtime`\n"
                "For beatmaps/users/scores, the command decides which preset group is used."
            ),
            color=discord.Color.green()
        )

        # LEADERBOARD presets (used by userlist / leaderboard-style commands)
        if LEADERBOARD_PRESETS:
            lines = [preset_line(k, LEADERBOARD_PRESETS[k], lb_aliases) for k in sorted(LEADERBOARD_PRESETS.keys())]
            # Discord embed field limits: keep each field reasonably sized
            chunk = "\n".join(lines[:20])
            embed.add_field(name="🏆 Leaderboard presets", value=chunk, inline=False)
            if len(lines) > 20:
                embed.add_field(
                    name="🏆 Leaderboard presets (more)",
                    value="\n".join(lines[20:40]),
                    inline=False
                )

        # USER presets
        if USER_PRESETS:
            lines = [preset_line(k, USER_PRESETS[k], user_aliases) for k in sorted(USER_PRESETS.keys())]
            embed.add_field(name="👤 User presets", value="\n".join(lines), inline=False)

        # BEATMAP presets
        if BEATMAP_PRESETS:
            lines = [preset_line(k, BEATMAP_PRESETS[k], bm_aliases) for k in sorted(BEATMAP_PRESETS.keys())]
            embed.add_field(name="🎵 Beatmap presets", value="\n".join(lines), inline=False)

        embed.add_field(
            name="Examples",
            value=(
                "`!userlist -o plays -stars-min 6 -l 10`\n"
                "`!userlist -o normalclears -mode 0 -l 25`\n"
                "`!beatmaps -o count -mode 0 -status ranked`"
            ),
            inline=False
        )

        embed.set_footer(text="Tip: aliases like `clears` → `normalclears`, `ec` → `easyclears`, etc. work too.")
        await ctx.reply(embed=embed)

    async def _send_single_preset_help(self, ctx, preset_name: str):
        resolved = resolve_any_preset(preset_name)
        if not resolved:
            await ctx.reply(f"❌ Unknown preset: `{preset_name}`\nTry `!help presets` to list them.")
            return

        category, canonical, preset, aliases = resolved

        title = preset.get("title", canonical)
        desc = preset.get("description", "No description available.")

        embed = discord.Embed(
            title=f"🎯 Preset: {canonical}",
            description=f"**{title}**\n{desc}",
            color=discord.Color.green()
        )

        embed.add_field(name="Category", value=category, inline=True)
        if "columns" in preset:
            embed.add_field(name="Columns", value=f"`{preset['columns']}`", inline=False)

        # show default filters (everything starting with '-' except group/order)
        filter_lines = []
        for k, v in preset.items():
            if not k.startswith("-"):
                continue
            if k in ("-group", "-order"):
                continue
            filter_lines.append(f"`{k}` = `{v}`")

        if filter_lines:
            embed.add_field(name="Default Filters", value="\n".join(filter_lines), inline=False)

        if aliases:
            # keep it readable
            shown = aliases[:20]
            extra = f" (+{len(aliases)-20} more)" if len(aliases) > 20 else ""
            embed.add_field(name="Aliases", value=", ".join(f"`{a}`" for a in shown) + extra, inline=False)

        embed.add_field(
            name="Usage",
            value=f"`!userlist -o {canonical}` (leaderboards)\n`!help preset {canonical}` (this page)",
            inline=False
        )

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
