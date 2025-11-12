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

    def as_leaderboard(self, result, total):
        """Render leaderboard from DB query result into a Discord embed with aligned columns."""

        leaderboard = []
        for row in result:
            username, count = row
            leaderboard.append({"username": username, "count": int(count)})

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
        width_name = max(len(d["username"]) for d in leaderboard)
        width_count = max(len(f"{d['count']:,}") for d in leaderboard)

        lines = []
        for i, d in enumerate(leaderboard, start=1):
            diff = d.get("difference")
            diff_str = f"{diff:+,}" if diff is not None else ""
            lines.append(
                f"#{i:<2} | {d['username']:<{width_name}} | {d['count']:<{width_count},} | {diff_str:<6}"
            )

        embed.description = f"```\n" + "\n".join(lines) + "\n```"

        if self.footer:
            embed.set_footer(text=self.footer)

        return embed
    
    def as_score_list(self, result, page=1, page_size=10, elapsed=None):
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

        # Group scores by beatmap
        from collections import defaultdict
        beatmap_groups = defaultdict(list)
        
        for row in subset:
            beatmap_groups[row['beatmap_id']].append(row)

        # Build formatted lines
        lines = []
        for beatmap_id, scores in beatmap_groups.items():
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
                mods = ",".join(str(x) for x in row["mod_acronyms"]) if row["mod_acronyms"] else ""
                accuracy_val = row.get("accuracy")
                accuracy = float(accuracy_val or 0.0) * 100
                pp_val = row.get("pp")
                pp = float(pp_val or 0.0)
                
                # Format mods as +HDHRFL
                mods_str = (
                    f"+{''.join(mods)}" if isinstance(mods, (list, tuple)) and mods else ""
                )
                
                # Indented score line
                score_line = f"  ↳ {mods_str} {accuracy:.2f}% | {pp:.2f}pp | {grade}"
                lines.append(score_line)

        embed.description = "\n".join(lines)

        total = len(result)
        page_count = (total + page_size - 1) // page_size
        embed.set_footer(
            text=f"Page {page} of {page_count} • Amount: {total:,} • took {elapsed:.2f}s"
            if elapsed is not None
            else f"Page {page} of {page_count} • Amount: {total:,}"
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