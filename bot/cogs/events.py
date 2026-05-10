# bot/cogs/events.py

import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone

CHANNEL_ID = 793594664262303814


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("INIT")
        self.event_loop.start()

    def cog_unload(self):
        self.event_loop.cancel()

    @tasks.loop(seconds=10)
    async def event_loop(self):
        print("LOOP")
        try:
            events = await self.bot.db.fetchParametrized(
                """
                SELECT event_id,
                       event_type,
                       beatmap_id,
                       score_id
                FROM events
                WHERE processed = False
                    and event_type = 'first_ss'
                ORDER BY created_at ASC
                LIMIT 1
                """
            )

            if not events:
                return
            
            print(events)

            channel = self.bot.get_channel(CHANNEL_ID)

            if channel is None:
                self.bot.logger.error(
                    f"Could not find channel {CHANNEL_ID}"
                )
                return

            for event in events:
                try:
                    embed = await self.build_embed(event)

                    if embed is not None:
                        await channel.send(embed=embed)

                    await self.bot.db.executeParametrized(
                        """
                        UPDATE events
                        SET processed = True, lchg_time = NOW()
                        WHERE event_id = $1
                        """,
                        event["event_id"]
                    )

                except Exception as e:
                    self.bot.logger.exception(
                        f"Failed processing event "
                        f"{event['event_id']}: {e}"
                    )

        except Exception as e:
            self.bot.logger.exception(
                f"Event loop failure: {e}"
            )

    @event_loop.before_loop
    async def before_event_loop(self):
        print("WAITING")
        await self.bot.wait_until_ready()
        print("READY")

    async def build_embed(self, event):
        if event["event_type"] == "first_ss":
            return await self.build_first_ss_embed(event)

        return None

    async def build_first_ss_embed(self, event):
        rows = await self.bot.db.fetchParametrized(
            """
            SELECT
                s.id,
                s.user_id_fk,
                s.pp,
                s.accuracy,
                s.total_score,
                s.ended_at,
                s.rank,
                s.mod_acronyms,

                u.username,

                ue.avatar_url,

                b.artist,
                b.title,
                b.version,
                b.stars,
                b.cs,
                b.ar,
                b.od,
                b.hp,
                b.max_combo,
                b.drain_time,
                b.ranked_date,
                b.beatmap_id,

                FLOOR(
                    EXTRACT(
                        EPOCH FROM (
                            s.ended_at - b.ranked_date
                        )
                    ) / 86400
                )::int AS days_since_ranked

            FROM scoreLive s

            JOIN beatmapLive b
                ON b.beatmap_id = s.beatmap_id_fk

            LEFT JOIN userLive u
                ON u.user_id = s.user_id_fk

            LEFT JOIN userExtended ue
                ON ue.id = s.user_id_fk
            AND ue.ruleset_id = s.ruleset_id

            WHERE s.id = $1
            """,
            event["score_id"]
        )

        if not rows:
            return None

        row = rows[0]

        # Ignore recent ranked maps
        if row["days_since_ranked"] < 30:
            return None

        mods = "".join(row["mod_acronyms"]) \
            if row["mod_acronyms"] else "NM"

        score = f"{int(row['total_score']):,}"

        accuracy = f"{float(row['accuracy']) * 100:.2f}%"

        pp = f"{float(row['pp']):.2f}pp" \
            if row["pp"] is not None else "0pp"

        stars = f"{float(row['stars']):.2f}★"

        combo = f"{row['max_combo']} combo"

        drain_time = self.format_length(row["drain_time"])

        ranked_date = row["ranked_date"].strftime(
            "%B %-d, %Y %-I:%M %p"
        )

        days_since = int(row["days_since_ranked"])

        time_of_play = self.relative_time(row["ended_at"])

        title_line = (
            f"{row['artist']} - "
            f"{row['title']} "
            f"[{row['version']}]"
        )

        embed = discord.Embed(
            description=(
                f"## {row['username']} - {pp}\n"
                f"**A map has been SSed "
                f"for the first time after "
                f"{days_since:,} days!**\n\n"
                f"**{title_line}**\n"
                f"{mods} • {score} • "
                f"{accuracy} • {pp}\n"
                f"Time of play: {time_of_play}\n"
                f"Date ranked: {ranked_date}\n\n"
                f"**Beatmap information**\n"
                f"CS {row['cs']} • "
                f"AR {row['ar']} • "
                f"OD {row['od']} • "
                f"HP {row['hp']} • "
                f"{stars}\n"
                f"{drain_time} • {combo}"
            ),
            color=0xF1E05A
        )

        embed.url = (
            f"https://osu.ppy.sh/beatmaps/"
            f"{row['beatmap_id']}"
        )

        if row["avatar_url"]:
            embed.set_thumbnail(url=row["avatar_url"])

        return embed

    def format_length(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m{secs}s"

    def relative_time(self, dt):
        now = datetime.now(timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        diff = now - dt

        seconds = int(diff.total_seconds())

        days = seconds // 86400
        hours = seconds // 3600
        minutes = seconds // 60

        if days > 0:
            return f"{days} day{'s' if days != 1 else ''} ago"

        if hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

        if minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

        return "just now"


async def setup(bot):
    await bot.add_cog(Events(bot))