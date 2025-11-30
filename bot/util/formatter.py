import discord
from io import StringIO
import csv
import textwrap

class Formatter:
    def __init__(self, title, total=None, footer=None, color=0x5865F2):
        self.title = title
        self.total = total
        self.footer = footer
        self.color = color
    
    def as_beatmap_list(self, result, page=1, page_size=10, elapsed=None):
        """
        Format beatmap list into a Discord embed.
        Expects rows with: stars, artist, title, version, beatmap_id, beatmapset_id
        """
        start = (page - 1) * page_size
        end = start + page_size
        subset = result[start:end]

        embed = discord.Embed(
            title=f"{self.title}",
            description="",
            color=self.color
        )

        # Build formatted lines
        lines = []
        for row in subset:
            stars = f"{row['stars']:.2f}★"
            artist = row['artist']
            title = row['title']
            version = row['version']
            bset_id = row['beatmapset_id']
            bid = row['beatmap_id'] 
            mode  = row['mode']

            url = f"https://osu.ppy.sh/beatmapsets/{bset_id}#{mode}/{bid}"
            lines.append(f"{stars} | [{artist} - {title} [{version}]]({url})")

        embed.description = "\n".join(lines)
        total = len(result)
        page_count = (total + page_size - 1) // page_size
        embed.set_footer(
            text=f"Page {page} of {page_count} • Amount: {total:,} • took {elapsed:.2f}s"
            if elapsed is not None
            else f"Page {page} of {page_count} • Amount: {total:,}"
        )

        return embed

    def as_leaderboard(self, result, total, page=1, page_size=10, elapsed=None):
        """
        Render leaderboard from DB query result into a Discord embed with aligned columns.
        Now supports pagination with -page and -limit flags.
        """
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        subset = result[start:end]

        leaderboard = []
        for row in subset:
            username, count = row
            leaderboard.append({"username": username, "count": int(count)})

        # Calculate differences within the current page
        for i in range(1, len(leaderboard)):
            diff = leaderboard[i]["count"] - leaderboard[i - 1]["count"]
            leaderboard[i]["difference"] = diff
        if leaderboard:
            leaderboard[0]["difference"] = None

        embed = discord.Embed(
            title=f"{self.title} | {total:,} beatmaps",
            color=self.color
        )

        # Determine consistent column widths
        width_name = max(len(d["username"]) for d in leaderboard) if leaderboard else 10
        width_count = max(len(f"{d['count']:,}") for d in leaderboard) if leaderboard else 5

        lines = []
        for i, d in enumerate(leaderboard, start=start+1):  # Use actual rank number
            diff = d.get("difference")
            diff_str = f"{diff:+,}" if diff is not None else ""
            lines.append(
                f"#{i:<2} | {d['username']:<{width_name}} | {d['count']:<{width_count},} | {diff_str:<6}"
            )

        embed.description = f"```\n" + "\n".join(lines) + "\n```"

        # Update footer with pagination info
        total_results = len(result)
        page_count = (total_results + page_size - 1) // page_size
        footer_text = f"Page {page} of {page_count} • Amount: {total_results:,}"
        if elapsed is not None:
            footer_text += f" • took {elapsed:.2f}s"
        if self.footer:
            footer_text = f"{self.footer} • {footer_text}"
        
        embed.set_footer(text=footer_text)

        return embed
    
    def as_completion(self, data, elapsed=None):
        """
        Format completion statistics into a Discord embed.
        
        Args:
            data: List of dicts with keys: range, percentage, played, total, missing
            elapsed: Optional query execution time
        
        Returns:
            discord.Embed with formatted completion table
        """
        embed = discord.Embed(
            title=self.title,
            color=self.color
        )
        
        # Calculate column widths
        width_range = max(len(d["range"]) for d in data) if data else 10
        width_percentage = 8
        width_fraction = max(len(f"{d['played']:,}/{d['total']:,}") for d in data) if data else 10
        width_missing = max(len(f"{d['missing']:,}") for d in data) if data else 5
        
        # Build table lines
        lines = []
        for d in data:
            range_str = d["range"].ljust(width_range)
            percentage_str = f"{d['percentage']:06.3f}%".rjust(width_percentage)
            fraction_str = f"{d['played']:,}/{d['total']:,}".rjust(width_fraction)
            missing_str = f"-{d['missing']:,}".replace("-0", "✓").rjust(width_missing + 1)
            
            lines.append(f"{range_str} | {percentage_str} | {fraction_str} | {missing_str}")
        
        embed.description = "```\n" + "\n".join(lines) + "\n```"
        
        # Set footer
        footer_text = "Based on Scores in the database"
        if elapsed is not None:
            footer_text += f" • took {elapsed:.2f}s"
        if self.footer:
            footer_text = f"{self.footer} • {footer_text}"
        
        embed.set_footer(text=footer_text)
        
        return embed
    
    def as_score_list(self, result, page=1, page_size=10, elapsed=None):
        """
        Format score list into a Discord embed with pagination.
        Groups scores by beatmap and supports -page and -limit flags.
        """
        # Group all scores by beatmap first
        from collections import defaultdict
        beatmap_groups = defaultdict(list)
        
        for row in result:
            beatmap_groups[row['beatmap_id']].append(row)
        
        # Convert to list of beatmap groups for pagination
        beatmap_list = list(beatmap_groups.items())
        
        # Apply pagination to beatmap groups
        start = (page - 1) * page_size
        end = start + page_size
        subset = beatmap_list[start:end]

        embed = discord.Embed(
            title=f"{self.title}",
            description="",
            color=self.color
        )

        # Build formatted lines
        lines = []
        for beatmap_id, scores in subset:
            # Use first score for beatmap info (all scores share same beatmap)
            first = scores[0]
            artist = first['artist']
            title = first['title']
            version = first['version']
            bset_id = first['beatmapset_id']
            mode = first['mode']
            stars_val = first.get('stars')
            stars = f"{float(stars_val or 0):.2f}★"
            
            # Build beatmap link
            url = f"https://osu.ppy.sh/beatmapsets/{bset_id}#{mode}/{beatmap_id}"
            
            # Add beatmap header
            lines.append(f"[{artist} - {title} [{version}]]({url}) ({stars})")
            
            # Add each score as indented item
            for row in scores:
                grade = row['grade']
                mods = row.get("mod_acronyms", [])
                accuracy_val = row.get("accuracy")
                accuracy = float(accuracy_val or 0.0) * 100
                pp_val = row.get("pp")
                pp = float(pp_val or 0.0)
                
                # Format mods as +HDHRFL
                if mods and isinstance(mods, (list, tuple)):
                    mods_str = f"+{''.join(str(m) for m in mods)}"
                else:
                    mods_str = ""
                
                # Indented score line
                score_line = f"  ↳ {mods_str} {accuracy:.2f}% | {pp:.2f}pp | {grade}"
                lines.append(score_line)

        embed.description = "\n".join(lines) if lines else "No scores found"

        # Calculate pagination info based on beatmap groups
        total_beatmaps = len(beatmap_list)
        page_count = (total_beatmaps + page_size - 1) // page_size
        embed.set_footer(
            text=f"Page {page} of {page_count} • Beatmaps: {total_beatmaps:,} • took {elapsed:.2f}s"
            if elapsed is not None
            else f"Page {page} of {page_count} • Beatmaps: {total_beatmaps:,}"
        )

        return embed

    def as_csv_file(self, data, filename="leaderboard.csv"):
        """Write data to a temporary in-memory CSV for attachment."""
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        csv_buffer.seek(0)
        return discord.File(fp=StringIO(csv_buffer.read()), filename=filename)