# bot/cogs/scores.py
from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
import time
from bot.util.schema import TABLE_METADATA

class Completion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # bot/cogs/scores.py - Add these helper methods to your Scores class

    def _get_completion_field_config(self, field):
        """
        Get configuration for a completion field.
        Returns: (is_string, config_data)
        """
        numeric_field_map = {
            "ar": [0, 10, 1],
            "cs": [0, 10, 1], 
            "od": [0, 10, 1],
            "hp": [0, 10, 1],
            "stars": [0, 10.1, 1],
            "year": [2007, 2026, 1],
            "length": [0, 601, 60],
            "drain": [0, 601, 60],
            "drain_time": [0, 601, 60],
            "bpm": [0, 301, 20],
            "objects": [0, 3001, 150],
            "combo": [0, 5001, 500]
        }
        
        string_fields = ["artist", "title", "version", "source", "status"]
        
        if field in numeric_field_map:
            return False, numeric_field_map[field]
        elif field in string_fields:
            return True, None
        else:
            return None, None

    def _generate_numeric_ranges(self, min_val, max_val, precision):
        """Generate numeric ranges based on min, max, and precision."""
        ranges = []
        current = min_val
        while current < max_val:
            next_val = current + precision
            if next_val >= max_val:
                ranges.append((current, None))
                break
            ranges.append((current, next_val))
            current = next_val
        return ranges

    def _format_range_label(self, field, range_min, range_max, precision):
        """Format a range label for display."""
        display_field = field.upper()
        
        if field == "year":
            if range_max is None:
                return f"{display_field} {int(range_min)}+"
            else:
                return f"{display_field} {int(range_min)}-{int(range_max)}"
        else:
            if range_max is None:
                if precision >= 1:
                    return f"{display_field} {range_min:.0f}+"
                else:
                    return f"{display_field} {range_min:.2f}+"
            else:
                if precision >= 1:
                    return f"{display_field} {range_min:.0f}-{range_max:.0f}"
                else:
                    return f"{display_field} {range_min:.2f}-{range_max:.2f}"

    def _separate_beatmap_filters(self, di):
        """Separate beatmap-only filters from all filters."""
        beatmap_columns = set(TABLE_METADATA["beatmapLive"].keys())
        beatmap_args = {}
        
        for key, value in di.items():
            if key.startswith("-"):
                raw_key = key.lstrip("-")
                base_key = raw_key
                
                # Remove suffixes to get base column name
                for suffix in ["-min", "-max", "-not", "-in", "-notin", "-like", "-regex"]:
                    if raw_key.endswith(suffix):
                        base_key = raw_key[:-len(suffix)]
                        break
                
                # Check if this is a beatmap column or special parameter
                if base_key in beatmap_columns or key in ["-field", "-precision", "-val-min", "-val-max", "-search", "-is_fa", "-not_fa", "-year"]:
                    beatmap_args[key] = value
        
        return beatmap_args

    async def _query_completion_counts(self, beatmap_args, score_args):
        """
        Query both played and total counts for a given filter set.
        Returns: (played_count, total_count)
        """
        # Query 1: Count played beatmaps
        played_query = QueryBuilder(
            score_args,
            columns="count(DISTINCT scoreLive.beatmap_id)",
            table="scoreLive"
        )
        played_result, _ = await self.bot.db.executeQuery(played_query.getQuery())
        played = played_result[0][0] if played_result else 0
        
        # Query 2: Count total beatmaps
        total_query = QueryBuilder(
            beatmap_args,
            columns="count(DISTINCT beatmapLive.beatmap_id)",
            table="beatmapLive"
        )
        total_result, _ = await self.bot.db.executeQuery(total_query.getQuery())
        total = total_result[0][0] if total_result else 0
        
        return played, total

    async def _build_numeric_completion(self, di, field, beatmap_args, ranges):
        """Build completion data for numeric fields."""
        completion_data = []
        precision = float(di.get("-precision", 1))
        
        for range_min, range_max in ranges:
            range_beatmap_args = beatmap_args.copy()
            range_score_args = di.copy()
            
            min_key = f"-{field}-min"
            max_key = f"-{field}-max"
            
            if range_min is not None:
                range_beatmap_args[min_key] = str(range_min)
                range_score_args[min_key] = str(range_min)
            if range_max is not None:
                range_beatmap_args[max_key] = str(range_max)
                range_score_args[max_key] = str(range_max)
            
            played, total = await self._query_completion_counts(range_beatmap_args, range_score_args)
            
            missing = total - played
            percentage = (played / total * 100) if total > 0 else 100.0
            range_label = self._format_range_label(field, range_min, range_max, precision)
            
            completion_data.append({
                "range": range_label,
                "percentage": percentage,
                "played": played,
                "total": total,
                "missing": missing
            })
        
        return completion_data

    async def _build_string_completion(self, di, field, beatmap_args):
        """Build completion data for string fields grouped by first character."""
        # Define letter ranges: symbols/numbers, then A-Z
        letter_ranges = ['0-9'] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        
        completion_data = []
        
        for letter in letter_ranges:
            range_beatmap_args = beatmap_args.copy()
            range_score_args = di.copy()
            
            if letter == '0-9':
                # Match anything that doesn't start with A-Z (case insensitive)
                range_beatmap_args[f"-{field}-regex"] = "^[^A-Za-z]"
                range_score_args[f"-{field}-regex"] = "^[^A-Za-z]"
            else:
                # Match items starting with this letter (case insensitive)
                # ^A means "starts with A"
                range_beatmap_args[f"-{field}-regex"] = f"^{letter}"
                range_score_args[f"-{field}-regex"] = f"^{letter}"
            
            played, total = await self._query_completion_counts(range_beatmap_args, range_score_args)
            
            missing = total - played
            percentage = (played / total * 100) if total > 0 else 100.0
            display_label = letter if letter != '0-9' else '#'
            
            completion_data.append({
                "range": display_label,
                "percentage": percentage,
                "played": played,
                "total": total,
                "missing": missing
            })
        
        return completion_data if completion_data else None

    async def _get_username_for_display(self, di, user_id, ctx):
        """Get username for display in title."""
        username = di.get("-username", ctx.author.display_name)
        if user_id and "-username" not in di:
            user_query = f"SELECT username FROM userLive WHERE user_id = {user_id}"
            user_result, _ = await self.bot.db.executeQuery(user_query)
            if user_result and user_result[0]:
                username = user_result[0][0]
        return username

    @commands.command(aliases=["comp"])
    async def completion(self, ctx, *args):
        """
        Display completion statistics grouped by a field (e.g., AR, SR, CS, year).
        Examples:
        !completion -field ar -precision 0.5 -val-min 6 -val-max 10
        !completion -field stars -precision 0.5 -username peppy
        !completion -field year -stars-min 5
        !completion -field cs -precision 0.25 -status ranked
        !completion -field artist -limit 20
        !completion -field title -search anime
        """
        start_time = time.time()
        di = get_args(args)
        
        # Get user_id if not specified
        discordid = ctx.author.id
        user_id = None
        if "-user_id" not in di and "-username" not in di:
            query = f"SELECT user_id FROM registrations WHERE discordid = '{discordid}'"
            result, _ = await self.bot.db.executeQuery(query)
            if result and result[0]:
                user_id = result[0][0]
                di["-user_id"] = user_id
            else:
                await ctx.reply(f"Please register or specify a user")
                return
        
        # Get field configuration
        field = di.get("-field", "year").lower()
        is_string, config = self._get_completion_field_config(field)
        
        if is_string is None:
            numeric_fields = ["ar", "cs", "od", "hp", "stars", "year", "length", "drain", "drain_time", "bpm"]
            string_fields = ["artist", "title", "version", "source", "status"]
            all_fields = numeric_fields + string_fields
            await ctx.reply(f"Unknown field: {field}. Available: {', '.join(all_fields)}")
            return
        
        display_field = field.upper()
        beatmap_args = self._separate_beatmap_filters(di)
        
        # Handle string vs numeric fields
        if is_string:
            completion_data = await self._build_string_completion(di, field, beatmap_args)
            if completion_data is None:
                await ctx.reply(f"No {field} values found matching your criteria.")
                return
        else:
            # Numeric field
            min_val = float(di.get("-val-min", config[0]))
            max_val = float(di.get("-val-max", config[1]))
            precision = float(di.get("-precision", config[2]))
            
            ranges = self._generate_numeric_ranges(min_val, max_val, precision)
            
            if len(ranges) > 30:
                await ctx.reply(f"Too many ranges ({len(ranges)}). Limit your ranges to 30 or less using -val-min and -val-max.")
                return
            
            completion_data = await self._build_numeric_completion(di, field, beatmap_args, ranges)
        
        # Get username and format response
        username = await self._get_username_for_display(di, user_id, ctx)
        elapsed = time.time() - start_time
        
        formatter = Formatter(title=f"{display_field} Completion for {username}")
        embed = formatter.as_completion(completion_data, elapsed=elapsed)
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Completion(bot))
