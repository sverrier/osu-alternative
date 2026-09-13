import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone

SS_CHANNEL_ID = 793594664262303814
FC_CHANNEL_ID = 793570054008340511
MAP_CHANNEL_ID = 792817863731576852


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
                    AND event_type IN (
                        'first_ss',
                        'first_fc',
                        'new_beatmapset'
                    )
                ORDER BY created_at ASC
                LIMIT 1
                """
            )

            if not events:
                return

            for event in events:
                channel = None

                if event["event_type"] == "first_ss":
                    channel = self.bot.get_channel(SS_CHANNEL_ID)

                elif event["event_type"] == "first_fc":
                    channel = self.bot.get_channel(FC_CHANNEL_ID)

                elif event["event_type"] == "new_beatmapset":
                    channel = self.bot.get_channel(MAP_CHANNEL_ID)

                if channel is None:
                    self.bot.logger.error(
                        "Could not find channel"
                    )
                    return

                try:
                    embed = await self.build_embed(event)

                    if embed is not None:
                        await channel.send(embed=embed)

                    await self.bot.db.executeParametrized(
                        """
                        UPDATE events
                        SET processed = True,
                            lchg_time = NOW()
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
                "headline": (
                    "A map has been SSed for the first time "
                    "after {days:,} days!"
                ),
                "color": 0xF1E05A
            },

            "first_fc": {
                "headline": (
                    "A map has been FCed for the first time "
                    "after {days:,} days!"
                ),
                "color": 0x58A6FF
            },

            "new_beatmapset": {
                "color": 0x58A6FF
            }
        }

        config = event_config.get(event["event_type"])

        if config is None:
            return None

        if event["event_type"] == "new_beatmapset":
            return await self.build_new_beatmapset_embed(event)

        return await self.build_first_completion_embed(
            event,
            config
        )

    async def build_new_beatmapset_embed(self, event):
        """
        Build an embed for a newly ranked beatmapset.

        events.beatmap_id contains the beatmapset_id for this event.
        """

        beatmapset_id = event["beatmap_id"]

        # Get the beatmap data for the set.
        # This is intentionally not optimized heavily since this happens
        # only once per newly ranked beatmapset.
        beatmaps = await self.bot.db.fetchParametrized(
            """
            SELECT *
            FROM beatmap
            WHERE beatmapset_id = $1
            ORDER BY difficulty_rating DESC
            """,
            beatmapset_id
        )

        if not beatmaps:
            return None

        # Highest-starred beatmap.
        # We use this both for the thumbnail and as the source of the
        # set-level metadata.
        highest = beatmaps[0]

        # Get the corresponding beatmapLive rows for the difficulties
        # that are actually being announced.
        live_rows = await self.bot.db.fetchParametrized(
            """
            SELECT *
            FROM beatmapLive
            WHERE beatmapset_id = $1
            ORDER BY mode, stars, beatmap_id
            """,
            beatmapset_id
        )

        if not live_rows:
            return None

        # ---------------------------------------------------------
        # Basic set information
        # ---------------------------------------------------------

        artist = highest["beatmapset_artist"]
        title = highest["beatmapset_title"]

        mapper = highest["beatmapset_creator"]
        mapper_id = highest["beatmapset_user_id"]

        mapper_url = (
            f"https://osu.ppy.sh/users/{mapper_id}"
        )

        beatmapset_url = (
            f"https://osu.ppy.sh/beatmapsets/{beatmapset_id}"
        )

        # The beatmap length should be identical across the set.
        length = highest["total_length"]

        # beatmapset_bpm is preferable here because this is set-level
        # metadata.
        bpm = highest["beatmapset_bpm"]

        # ---------------------------------------------------------
        # Mode / download information
        # ---------------------------------------------------------

        mode_names = {
            0: "osu",
            1: "taiko",
            2: "fruits",
            3: "mania"
        }

        mode_display_names = {
            0: "Standard",
            1: "Taiko",
            2: "Catch",
            3: "Mania"
        }

        # Use the highest-star beatmap's mode as the primary mode.
        primary_mode = mode_names.get(
            highest["mode_int"],
            "osu"
        )

        download_url = (
            f"https://osu.ppy.sh/d/{beatmapset_id}"
        )

        download_no_video_url = (
            f"https://osu.ppy.sh/d/{beatmapset_id}n"
        )

        # ---------------------------------------------------------
        # Cover image
        # ---------------------------------------------------------

        covers = highest["beatmapset_covers"]

        # Depending on your PostgreSQL driver/type configuration,
        # jsonb may already be returned as a dict or may be a string.
        if isinstance(covers, str):
            import json
            covers = json.loads(covers)

        cover_url = covers.get("list@2x")

        # ---------------------------------------------------------
        # Group difficulties by ruleset
        # ---------------------------------------------------------

        difficulties_by_mode = {}

        for row in live_rows:
            mode = row["mode"]

            if mode not in difficulties_by_mode:
                difficulties_by_mode[mode] = []

            mode_name = mode_names.get(mode, "osu")

            beatmap_url = (
                f"https://osu.ppy.sh/beatmapsets/"
                f"{beatmapset_id}#"
                f"{mode_name}/"
                f"{row['beatmap_id']}"
            )

            stars = self.format_number(row["stars"])
            cs = self.format_number(row["cs"])
            ar = self.format_number(row["ar"])
            od = self.format_number(row["od"])
            hp = self.format_number(row["hp"])

            max_combo = (
                f"{int(row['max_combo'])}x"
                if row["max_combo"] is not None
                else "?"
            )

            # Difficulty name on its own line, followed by stats.
            difficulty = (
                f"[{row['version']}]({beatmap_url})"
                f" • **{stars}**★\n"
                f"▸ CS **{cs}**"
                f" • AR **{ar}**"
                f" • OD **{od}**"
                f" • HP **{hp}**"
                f" • **{max_combo}**"
            )

            difficulties_by_mode[mode].append(difficulty)

        # ---------------------------------------------------------
        # Description
        # ---------------------------------------------------------

        description = (
            f"**{self.format_length(length)}** • "
            f"**{self.format_number(bpm)}**bpm "
            f"[{primary_mode}]({download_url})"
        )

        # Video/download links.
        if highest["beatmapset_video"]:
            description += (
                f" • [no video]({download_no_video_url})"
            )
        else:
            description += " • no video"

        description += "\n\n"

        # Rulesets and difficulties.
        for mode, difficulties in difficulties_by_mode.items():
            mode_name = mode_display_names.get(
                mode,
                "Unknown"
            )

            description += (
                f"```text\n"
                f"{mode_name}\n"
                f"```\n"
            )

            description += "\n".join(difficulties)
            description += "\n\n"

        # ---------------------------------------------------------
        # Ranked date
        # ---------------------------------------------------------

        ranked_date = highest["beatmapset_ranked_date"]

        if ranked_date is not None:
            ranked_ts = int(ranked_date.timestamp())

            description += (
                f"**Ranked at <t:{ranked_ts}:f>**"
            )

        # ---------------------------------------------------------
        # Embed
        # ---------------------------------------------------------

        embed = discord.Embed(
            # This is rendered larger than description text.
            title=f"{artist} - {title}",
            url=beatmapset_url,
            description=description,
            color=0x58A6FF
        )

        # Mapper in the author line.
        embed.set_author(
            name=f"New ranked map by {mapper}",
            url=mapper_url
        )

        # Highest-star difficulty's list@2x cover.
        if cover_url:
            embed.set_thumbnail(url=cover_url)

        return embed

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

        if (
            row["days_since_ranked"] < 30
            and event["event_type"] == "first_ss"
        ):
            return None

        if (
            row["days_since_ranked"] < 7
            and event["event_type"] == "first_fc"
        ):
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

        profile_pp_col = profile_pp_columns.get(
            row["mode"],
            "osu_pp"
        )

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

        description = (
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

    @staticmethod
    def format_number(value):
        if value is None:
            return "?"

        value = float(value)

        if value.is_integer():
            return str(int(value))

        return f"{value:.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def format_length(seconds):
        if seconds is None:
            return "?"

        seconds = int(seconds)
        minutes = seconds // 60
        secs = seconds % 60

        return f"{minutes}m{secs:02d}s"


async def setup(bot):
    await bot.add_cog(Events(bot))