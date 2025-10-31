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

    def as_embed(self, data):
        """Render a Discord embed styled like your leaderboard."""
        embed = discord.Embed(
            title=f"{self.title} | {self.total:,} beatmaps" if self.total else self.title,
            color=self.color
        )

        # Format leaderboard as a code block
        lines = []
        width_name = max(len(d["username"]) for d in data)
        for i, d in enumerate(data, start=1):
            diff = d.get("difference")
            diff_str = f"{diff:+,}" if diff is not None else ""
            lines.append(f"#{i:<2} | {d['username']:<{width_name}} | {d['count']:,} | {diff_str:>6}")

        code_block = f"```\n" + "\n".join(lines) + "\n```"
        embed.description = code_block

        if self.footer:
            embed.set_footer(text=self.footer)

        return embed

    def as_csv_file(self, data, filename="leaderboard.csv"):
        """Write data to a temporary in-memory CSV for attachment."""
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        csv_buffer.seek(0)
        return discord.File(fp=StringIO(csv_buffer.read()), filename=filename)