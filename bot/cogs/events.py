# bot/cogs/events.py

import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone

SS_CHANNEL_ID = 793594664262303814
FC_CHANNEL_ID = 793570054008340511

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
                    AND event_type IN ('first_ss', 'first_fc')
                ORDER BY created_at ASC
                LIMIT 1
                """
            )

            if not events:
                return

            for event in events:
                channel = None
            
                if event["event_type"] == 'first_ss':
                    channel = self.bot.get_channel(SS_CHANNEL_ID)
                elif event["event_type"] == 'first_fc':
                    channel = self.bot.get_channel(FC_CHANNEL_ID)

                if channel is None:
                    self.bot.logger.error(
                        f"Could not find channel"
                    )
                    return
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
        event_config = {
            "first_ss": {
                "headline": "A map has been SSed for the first time after {days:,} days!",
                "color": 0xF1E05A
            },
            "first_fc": {
                "headline": "A map has been FCed for the first time after {days:,} days!",
                "color": 0x58A6FF
            }
        }

        config = event_config.get(event["event_type"])

        if config is None:
            return None

        return await self.build_first_completion_embed(
            event,
            config
        )
    
    async def build_first_completion_embed(
        self,
        event,
        config
    ):
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
                u.osu_pp,
                u.taiko_pp,
                u.fruits_pp,
                u.mania_pp,

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
                b.beatmapset_id,
                b.mode,

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
        if row["days_since_ranked"] < 30 and event["event_type"] == 'first_ss':
            return None
        
        # Ignore recent ranked maps
        if row["days_since_ranked"] < 7 and event["event_type"] == 'first_fc':
            return None

        mods = "".join(row["mod_acronyms"]) \
            if row["mod_acronyms"] else "NM"
        
        pp = f"{float(row['pp']):.2f}pp" \
            if row["pp"] is not None else "0pp"

        score = f"{int(row['total_score']):,}"
        accuracy = f"{float(row['accuracy']) * 100:.2f}%"
        stars = f"{float(row['stars']):.2f}★"
        combo = f"{row['max_combo']} combo"
        drain_time = self.format_length(row["drain_time"])
        days_since = int(row["days_since_ranked"])
        ended_ts = int(row["ended_at"].timestamp())
        ranked_ts = int(row["ranked_date"].timestamp())

        mode_names = {
            0: "osu",
            1: "taiko",
            2: "fruits",
            3: "mania"
        }

        mode = mode_names.get(row["mode"], "osu")

        profile_pp_columns = {
            0: "osu_pp",
            1: "taiko_pp",
            2: "fruits_pp",
            3: "mania_pp",
        }

        profile_pp_col = profile_pp_columns.get(row["mode"], "osu_pp")
        profile_pp = row[profile_pp_col]

        profile_pp_str = (
            f"{float(profile_pp):,.0f}pp"
            if profile_pp is not None
            else "0pp"
        )

        beatmap_url = (
            f"https://osu.ppy.sh/beatmapsets/"
            f"{row['beatmapset_id']}#{mode}/"
            f"{row['beatmap_id']}"
        )

        title_line = (
            f"{row['artist']} - "
            f"{row['title']} "
            f"[{row['version']}]"
        )

        description=(
            f"**{config['headline'].format(days=days_since)}**\n\n"
            f"**[{title_line}]({beatmap_url})**\n"
            f"**{mods}** • {score} • {accuracy} • {pp}\n"
            f"**Time of play:** <t:{ended_ts}:R>\n"
            f"**Date ranked:** <t:{ranked_ts}:f>\n\n"
            f"**Beatmap information**\n"
            f"CS {row['cs']} • AR {row['ar']} • "
            f"OD {row['od']} • HP {row['hp']} • {stars}\n"
            f"{drain_time} • {combo}"
        )

        embed = discord.Embed(
            description=description,
            color=config["color"]
        )

        embed.url = beatmap_url

        if row["avatar_url"]:
            embed.set_author(
                name=f"{row['username']} - {profile_pp_str}",
                icon_url=row["avatar_url"]
            )
        else:
            embed.set_author(
                name=f"{row['username']} - {profile_pp_str}"
            )


        return embed

    def format_length(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m{secs:02d}s"


async def setup(bot):
    await bot.add_cog(Events(bot))