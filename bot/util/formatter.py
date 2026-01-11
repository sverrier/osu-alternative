import discord
from io import StringIO
import csv
import textwrap
from dataclasses import dataclass

from bot.util.formatting import format_field
from bot.util.helpers import MODE_LABELS, FA_LABELS, DIFF_LABELS


class Formatter:
    def __init__(self, title, total=None, footer=None, color=0x5865F2):
        self.title = title
        self.total = total
        self.footer = footer
        self.color = color

    def calculate_user_page(self, result, user, page_size):
        """
        Calculate which page the user appears on.
        Returns the page number, or None if user not found.
        """
        if user is None:
            return None
        
        for idx, row in enumerate(result, start=1):
            username, _ = row
            if username == user:
                # Calculate page number from rank
                return (idx + page_size - 1) // page_size
        
        return None
    
    def as_beatmap_list(
        self,
        result,
        page: int = 1,
        page_size: int = 10,
        elapsed: float | None = None,
        extra_key: str | None = None
    ):
        """
        Format beatmap list into a Discord embed.

        Expects rows with:
            stars, artist, title, version, beatmap_id, beatmapset_id, mode
        Optionally:
            extra_key: name of a column in row to display between stars and link.
        """

        start = (page - 1) * page_size
        end = start + page_size
        subset = result[start:end]

        embed = discord.Embed(
            title=str(self.title),
            description="",
            color=self.color,
        )

        lines = []
        for row in subset:
            stars = f"{row['stars']:.2f}★"

            # Optional extra stat from the same row
            extra_part = ""
            if extra_key is not None:
                value = row.get(extra_key)
                if value is not None:
                    # centralized formatting
                    extra_str = format_field(extra_key, value, table="beatmapLive")
                    extra_part = f" | {extra_str}"

            mode_name = ['osu', 'taiko', 'fruits', 'mania'][row['mode']]
            url = (
                f"https://osu.ppy.sh/beatmapsets/{row['beatmapset_id']}"
                f"#{mode_name}/{row['beatmap_id']}"
            )

            lines.append(
                f"{stars}{extra_part} | "
                f"[{row['artist']} - {row['title']} [{row['version']}]]({url})"
            )

        embed.description = "\n".join(lines)

        total = len(result)
        page_count = (total + page_size - 1) // page_size
        time_part = f" • took {elapsed:.2f}s" if elapsed is not None else ""
        embed.set_footer(
            text=f"Page {page} of {page_count} • Amount: {format_field('count', total)}{time_part}"
        )

        return embed
    
    def as_beatmapset_list(self, result, page=1, page_size=10, elapsed=None):
        """
        Format beatmapset list into a Discord embed.

        Expected row keys (at minimum):
        - beatmapset_id
        - artist
        - title
        - beatmap_count      (COUNT(*))
        - min_sr             (MIN(stars))
        - max_sr             (MAX(stars))
        """
        # Pagination
        page = max(int(page), 1)
        page_size = max(int(page_size), 1)

        start = (page - 1) * page_size
        end = start + page_size
        subset = result[start:end]

        embed = discord.Embed(
            title=f"{self.title}",
            description="",
            color=self.color
        )

        lines = []
        for row in subset:
            bset_id = row["beatmapset_id"]

            # Basic metadata with safe fallbacks
            artist = row.get("artist") or "Unknown artist"
            title = row.get("title") or "Unknown title"

            # Beatmap count (number of diffs)
            beatmap_count = (
                row.get("beatmap_count")
                or row.get("count")
                or 0
            )

            # Star range with flexible key names
            min_sr = (
                row.get("min_sr")
                or row.get("min_stars")
                or row.get("min_star_rating")
            )
            max_sr = (
                row.get("max_sr")
                or row.get("max_stars")
                or row.get("max_star_rating")
            )

            sr_str = ""
            try:
                if min_sr is not None and max_sr is not None:
                    min_f = float(min_sr)
                    max_f = float(max_sr)
                    if abs(min_f - max_f) < 1e-6:
                        # Single diff or all same SR
                        sr_str = f"{min_f:.2f}★"
                    else:
                        sr_str = f"{min_f:.2f}–{max_f:.2f}★"
            except (TypeError, ValueError):
                # If something weird sneaks in, just leave SR blank
                sr_str = ""

            # osu! set URL (no specific mode/beatmap)
            url = f"https://osu.ppy.sh/beatmapsets/{bset_id}"

            # Example line:
            # 4.12–6.37★ | [Artist - Title](https://osu.ppy.sh/beatmapsets/123456) • 5 diffs
            count_str = format_field("beatmap_count", beatmap_count)
            if sr_str:
                lines.append(f"{sr_str} | [{artist} - {title}]({url}) • {count_str} diffs")
            else:
                lines.append(f"[{artist} - {title}]({url}) • {count_str} diffs")

        embed.description = "\n".join(lines) if lines else "No beatmapsets found."

        total = len(result)
        page_count = max((total + page_size - 1) // page_size, 1)
        footer_text = f"Page {page} of {page_count} • Sets: {format_field('count', total)}"
        if elapsed is not None:
            footer_text += f" • took {elapsed:.2f}s"
        if self.footer:
            footer_text = f"{self.footer} • {footer_text}"

        embed.set_footer(text=footer_text)

        return embed

    def as_leaderboard(
        self,
        result,
        total,
        page=1,
        page_size=10,
        elapsed=None,
        user=None,
        *,
        metric_alias: str | None = None, # optional alias for format_field
        total_label: str = "beatmaps",
    ):
        """
        Render leaderboard from DB query result into a Discord embed with aligned columns.
        raw queried metric values are numeric; formatting is applied on top.
        """

        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size

        leaderboard = []
        user_found = False
        user_data = None

        # Build leaderboard and check if user is present
        for idx, row in enumerate(result, start=1):
            username, value = row  # value is numeric (int/float)
            if idx >= start + 1 and idx <= end:
                leaderboard.append({"username": username, "value": value, "rank": idx})

            if user is not None and username == user:
                user_data = {"username": username, "value": value, "rank": idx}
                if idx >= start + 1 and idx <= end:
                    user_found = True

        # Calculate differences within the current page (numeric)
        for i in range(1, len(leaderboard)):
            leaderboard[i]["difference"] = leaderboard[i]["value"] - leaderboard[i - 1]["value"]
        if leaderboard:
            leaderboard[0]["difference"] = None

        embed = discord.Embed(
            title=f"{self.title} | {format_field('count', total)} {total_label}",
            color=self.color
        )

        # Determine consistent column widths (include user_data if adding them)
        all_data = leaderboard if user_found or user_data is None else leaderboard + [user_data]
        width_name = max(len(d["username"]) for d in all_data) if all_data else 10
        width_val = max(len(format_field(metric_alias, d["value"])) for d in all_data) if all_data else 5

        # format diff using the same formatter + sign
        def fmt_diff(dv):
            if dv is None:
                return ""
            sign = "+" if dv >= 0 else "-"
            return sign + format_field(metric_alias, abs(dv))

        width_diff = max(len(fmt_diff(d.get("difference"))) for d in leaderboard) if leaderboard else 0
        width_diff = max(width_diff, 6)  # keep a minimum so the column doesn't jitter

        lines = []
        for d in leaderboard:
            diff_str = fmt_diff(d.get("difference"))
            lines.append(
                f"#{d['rank']:<2} | {d['username']:<{width_name}} | {format_field(metric_alias, d['value']):<{width_val}} | {diff_str:<{width_diff}}"
            )

        # Add user at the bottom if not found in current page
        if user_data is not None and not user_found:
            lines.append("..." + "-" * (width_name + width_val + width_diff + 12))
            lines.append(
                f"#{user_data['rank']:<2} | {user_data['username']:<{width_name}} | {format_field(metric_alias, user_data['value']):<{width_val}} | {'':<{width_diff}}"
            )

        embed.description = "```\n" + "\n".join(lines) + "\n```"

        # Footer
        total_results = len(result)
        page_count = (total_results + page_size - 1) // page_size
        footer_text = f"Page {page} of {page_count} • Amount: {format_field('count', total_results)}"
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
        width_fraction = max(len(f"{format_field('count', d['played'])}/{format_field('count', d['total'])}") for d in data) if data else 10
        width_missing = max(len(format_field("count", d["missing"])) for d in data) if data else 5
        
        # Build table lines
        lines = []
        for d in data:
            range_str = d["range"].ljust(width_range)
            percentage_str = f"{d['percentage']:06.3f}%".rjust(width_percentage)
            fraction_str = f"{format_field('count', d['played'])}/{format_field('count', d['total'])}".rjust(width_fraction)
            missing_str = ("✓" if int(d.get("missing") or 0) == 0 else "-" + format_field("count", d["missing"])).rjust(width_missing + 1)
            
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
            mode_name = ['osu', 'taiko', 'fruits', 'mania'][mode]
            stars_val = first.get('stars')
            stars = f"{float(stars_val or 0):.2f}★"
            
            # Build beatmap link
            url = f"https://osu.ppy.sh/beatmapsets/{bset_id}#{mode_name}/{beatmap_id}"
            
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
            text=f"Page {page} of {page_count} • Beatmaps: {format_field('count', total_beatmaps)} • took {elapsed:.2f}s"
            if elapsed is not None
            else f"Page {page} of {page_count} • Beatmaps: {format_field('count', total_beatmaps)}"
        )

        return embed

    def as_userstats(self, result, elapsed=None):
        """
        Format userstats rows into a Discord embed.

        Expects rows with keys:
        - mode_bucket
        - fa_bucket
        - diff_bucket
        - metric_type
        - value
        - total
        - completed_up_to
        """

        if not result:
            embed = discord.Embed(
                title=self.title,
                description="No statistics found for this user/bucket.",
                color=self.color
            )
            return embed

        # Desired display order
        METRIC_ORDER = [
            "overclears",
            "ultraclears",
            "extraclears",
            "hardclears",
            "normalclears",
            "easyclears",
            "plays",
            "scores",
            "fc",
            "ss",
        ]

        order_index = {name: idx for idx, name in enumerate(METRIC_ORDER)}

        # Sort result in-place according to desired order
        result_sorted = sorted(
            result,
            key=lambda r: order_index.get(r["metric_type"].lower(), 999)
        )

        # All rows share the same buckets (because you filtered in SQL)
        first = result_sorted[0]
        mode_bucket = first["mode_bucket"]
        fa_bucket = first["fa_bucket"]
        diff_bucket = first["diff_bucket"]

        mode_label = MODE_LABELS.get(mode_bucket, str(mode_bucket))
        fa_label = FA_LABELS.get(fa_bucket, str(fa_bucket))
        diff_label = DIFF_LABELS.get(diff_bucket, str(diff_bucket))

        header = f"{mode_label} | {fa_label} | {diff_label}"

        embed = discord.Embed(
            title=f"{self.title}",
            description=f"**{header}**",
            color=self.color
        )

        # Compute column widths (based on full result set)
        metric_width = max(len(row["metric_type"]) for row in result_sorted)
        frac_width = max(
            len(f"{format_field('count', row['value'])}/{format_field('count', row['total'])}")
            for row in result_sorted
        )
        date_width = max(len(str(row["completed_up_to"])) for row in result_sorted)

        lines = []

        for row in result_sorted:
            metric = row["metric_type"].ljust(metric_width)

            val = format_field("count", row["value"])
            tot = format_field("count", row["total"])
            frac = f"{val}/{tot}".rjust(frac_width)

            date_str = str(row["completed_up_to"]).rjust(date_width)

            lines.append(f"{metric} | {frac} | {date_str}")

            # Insert blank line between SCORES and FC
            if row["metric_type"].lower() == "scores":
                lines.append("")

        embed.description += "\n```" + "\n".join(lines).rstrip() + "\n```"

        # Footer (match your existing style)
        footer_text = "User statistics"
        if elapsed is not None:
            footer_text += f" • took {elapsed:.2f}s"
        if self.footer:
            footer_text = f"{self.footer} • {footer_text}"

        embed.set_footer(text=footer_text)

        return embed
    
    def as_completion_leaderboard(self, result, page=1, page_size=10, elapsed=None, user=None):
        """
        Render completion leaderboard with pagination done in formatter (like as_leaderboard).

        Expects result rows (dict or tuple) ordered already:
        - username
        - value
        - total
        - completed_up_to
        """
        page = max(int(page), 1)
        page_size = max(int(page_size), 1)

        total_results = len(result)
        page_count = max((total_results + page_size - 1) // page_size, 1)

        start = (page - 1) * page_size
        end = start + page_size

        # helper to read row regardless of dict/tuple
        def get_field(row, key, idx):
            if isinstance(row, dict):
                return row.get(key)
            return row[idx] if len(row) > idx else None

        # build page subset and capture user row if present anywhere
        rows = []
        user_data = None
        user_found = False

        for idx, row in enumerate(result, start=1):
            username = get_field(row, "username", 0)
            value = get_field(row, "value", 1)
            total = get_field(row, "total", 2)
            completed = get_field(row, "completed_up_to", 3)

            if user is not None and username == user:
                user_data = {
                    "rank": idx,
                    "username": username,
                    "value": value,
                    "total": total,
                    "completed_up_to": completed
                }
                if start + 1 <= idx <= end:
                    user_found = True

            if start + 1 <= idx <= end:
                rows.append({
                    "rank": idx,
                    "username": username,
                    "value": value,
                    "total": total,
                    "completed_up_to": completed
                })

        embed = discord.Embed(
            title=f"{self.title}",
            color=self.color
        )

        if not rows:
            embed.description = "No results found."
            footer_text = f"Page {page} of {page_count} • Amount: {format_field('count', total_results)}"
            if elapsed is not None:
                footer_text += f" • took {elapsed:.2f}s"
            if self.footer:
                footer_text = f"{self.footer} • {footer_text}"
            embed.set_footer(text=footer_text)
            return embed

        # Formatting helpers
        def fmt_count(v):
            return format_field("count", v)

        def fmt_frac(v, t):
            v = int(v or 0)
            t = int(t or 0)
            return f"{fmt_count(v)}/{fmt_count(t)}"

        def fmt_pct(v, t):
            v = float(v or 0)
            t = float(t or 0)
            if t <= 0:
                return "0.0%"
            return f"{(v / t) * 100:0.1f}%"

        # widths (include user_data if it will be appended)
        all_rows = rows if (user_data is None or user_found) else rows + [user_data]

        width_rank = max(len(str(r["rank"])) for r in all_rows)
        width_name = max(len(str(r["username"] or "")) for r in all_rows)
        width_val = max(len(fmt_count(r["value"])) for r in all_rows)
        width_frac = max(len(fmt_frac(r["value"], r["total"])) for r in all_rows)
        width_pct = max(len(fmt_pct(r["value"], r["total"])) for r in all_rows)
        width_date = max(len(str(r["completed_up_to"] or "")) for r in all_rows)

        header = (
            f"{'#':<{width_rank}} | "
            f"{'Username':<{width_name}} | "
            f"{'Value':<{width_val}} | "
            f"{'Value/Total':<{width_frac}} | "
            f"{'%':<{width_pct}} | "
            f"{'Up to':<{width_date}}"
        )

        lines = [header]

        for r in rows:
            lines.append(
                f"{str(r['rank']).rjust(width_rank)} | "
                f"{str(r['username'] or '').ljust(width_name)} | "
                f"{fmt_count(r['value']).rjust(width_val)} | "
                f"{fmt_frac(r['value'], r['total']).rjust(width_frac)} | "
                f"{fmt_pct(r['value'], r['total']).rjust(width_pct)} | "
                f"{str(r['completed_up_to'] or '').rjust(width_date)}"
            )

        # append user row at bottom if not in current page
        if user_data is not None and not user_found:
            lines.append("." + "-" * (len(header) - 1))
            lines.append(
                f"{str(user_data['rank']).rjust(width_rank)} | "
                f"{str(user_data['username'] or '').ljust(width_name)} | "
                f"{fmt_count(user_data['value']).rjust(width_val)} | "
                f"{fmt_frac(user_data['value'], user_data['total']).rjust(width_frac)} | "
                f"{fmt_pct(user_data['value'], user_data['total']).rjust(width_pct)} | "
                f"{str(user_data['completed_up_to'] or '').rjust(width_date)}"
            )

        embed.description = "```\n" + "\n".join(lines) + "\n```"

        footer_text = f"Page {page} of {page_count} • Amount: {format_field('count', total_results)}"
        if elapsed is not None:
            footer_text += f" • took {elapsed:.2f}s"
        if self.footer:
            footer_text = f"{self.footer} • {footer_text}"
        embed.set_footer(text=footer_text)

        return embed




    def as_csv_file(self, data, filename="leaderboard.csv"):
        """Write data to a temporary in-memory CSV for attachment."""
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        csv_buffer.seek(0)
        return discord.File(fp=StringIO(csv_buffer.read()), filename=filename)