from discord.ext import commands
from bot.util.helpers import get_args
from bot.util.presets import *
from bot.util.querybuilder import QueryBuilder
from bot.util.formatter import Formatter
from bot.util.helpers import separate_beatmap_filters, separate_user_filters
from bot.util.schema import TABLE_METADATA

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ----------------------------
    # helpers
    # ----------------------------
    def _norm(self, v):
        return None if v is None else str(v).strip().lower()

    def _parse_bucket(self, val, *, kind: str):
        """
        Returns (bucket_value:int, error_msg:str|None)
        kind: 'fa', 'diff', 'mode'
        """
        v = self._norm(val)

        if kind == "fa":
            # 0 false, 1 true, 2 total
            if v is None:
                return 2, None
            if v in ("0", "false", "f", "no", "n"):
                return 0, None
            if v in ("1", "true", "t", "yes", "y"):
                return 1, None
            if v in ("2", "all", "total"):
                return 2, None
            return 2, "Invalid -fa/-is_fa. Use 0/false, 1/true, or 2/all."

        if kind == "diff":
            # 0 easy, 1 hard, 2 total
            if v is None:
                return 2, None
            if v in ("0", "easy", "e"):
                return 0, None
            if v in ("1", "hard", "h"):
                return 1, None
            if v in ("2", "all", "total"):
                return 2, None
            return 2, "Invalid -diff/-difficulty. Use 0/easy, 1/hard, or 2/all."

        if kind == "mode":
            # 0 osu, 1 taiko, 2 fruits/catch/ctb, 3 mania, 4 total
            if v is None:
                return 4, None
            if v in ("0", "osu", "o"):
                return 0, None
            if v in ("1", "taiko", "t"):
                return 1, None
            if v in ("2", "fruits", "catch", "ctb"):
                return 2, None
            if v in ("3", "mania", "m"):
                return 3, None
            if v in ("4", "all", "total"):
                return 4, None
            return 4, "Invalid -mode. Use 0/osu, 1/taiko, 2/fruits|catch|ctb, 3/mania, or 4/all."

        return 0, f"Unknown bucket kind: {kind}"

    def _parse_order(self, val):
        v = self._norm(val) or "count"
        if v in ("count", "value"):
            return "value", None
        if v in ("date", "completed", "completed_up_to", "upto", "up_to"):
            return "completed_up_to", None
        if v in ("total",):
            return "total", None
        return "value", "Invalid -order. Use count, date, or total."

    def _parse_direction(self, val):
        v = self._norm(val) or "desc"
        if v in ("asc", "ascending", "a"):
            return "ASC", None
        if v in ("desc", "descending", "d"):
            return "DESC", None
        return "DESC", "Invalid -direction. Use asc or desc."

    @commands.command(aliases=["ustats", "stats"])
    async def userstats(self, ctx, *args):
        di = get_args(args)

        # ----------------------------
        # resolve user_id like other commands
        # ----------------------------
        discordid = ctx.author.id
        username = None

        user_id = di.get("-user_id")

        if user_id is None:
            # Same idea as leaderboard/userlist: resolve from registrations by discordid
            query = (
                "SELECT r.user_id, ul.username "
                "FROM registrations r "
                "INNER JOIN userLive ul ON r.user_id = ul.user_id "
                f"WHERE discordid = '{discordid}'"
            )
            rows, _ = await self.bot.db.executeQuery(query)
            if rows:
                # handle dict-row vs tuple-row
                if isinstance(rows[0], dict):
                    user_id = rows[0].get("user_id")
                    username = rows[0].get("username")
                else:
                    user_id = rows[0][0]
                    username = rows[0][1] if len(rows[0]) > 1 else None

        if user_id is None:
            await ctx.reply("Could not auto-resolve your user. Please provide `-user_id <id>`.")
            return

        # ----------------------------
        # parse buckets / ordering
        # ----------------------------
        fa_bucket, err = self._parse_bucket(di.get("-fa", di.get("-is_fa")), kind="fa")
        if err:
            await ctx.reply(err)
            return

        diff_bucket, err = self._parse_bucket(di.get("-diff", di.get("-difficulty")), kind="diff")
        if err:
            await ctx.reply(err)
            return

        mode_bucket, err = self._parse_bucket(di.get("-mode"), kind="mode")
        if err:
            await ctx.reply(err)
            return

        # ----------------------------
        # query userstats
        # ----------------------------
        # IMPORTANT: order_col is whitelisted above; direction_sql is ASC/DESC only.
        sql = f"""
            SELECT
              user_id,
              mode_bucket,
              fa_bucket,
              diff_bucket,
              metric_type,
              value,
              total,
              completed_up_to
            FROM userstats
            WHERE user_id = {int(user_id)}
              AND fa_bucket = {int(fa_bucket)}
              AND mode_bucket = {int(mode_bucket)}
              AND diff_bucket = {int(diff_bucket)}
        """

        result, elapsed = await self.bot.db.executeQuery(sql)

        # If you want total row count for footer/page calc, do a lightweight count:
        count_sql = f"""
            SELECT COUNT(*)
            FROM userstats
            WHERE user_id = {int(user_id)}
              AND fa_bucket = {int(fa_bucket)}
              AND mode_bucket = {int(mode_bucket)}
              AND diff_bucket = {int(diff_bucket)}
        """
        count_rows, _ = await self.bot.db.executeQuery(count_sql)
        total_rows = count_rows[0]["count"] if count_rows and isinstance(count_rows[0], dict) else (count_rows[0][0] if count_rows else 0)

        # ----------------------------
        # format
        # ----------------------------
        # Prefer showing the resolved username if available
        title_user = username or f"user {user_id}"
        formatter = Formatter(title=f"{title_user} • stats", footer=f"Based on userstats • took {elapsed:.2f}s")

        # This assumes you added Formatter.as_userstats_table(result, ...)
        embed = formatter.as_userstats(
            result,
            elapsed=elapsed,
        )
        await ctx.reply(embed=embed)

    @commands.command(aliases=["clb", "completionlb"])
    async def completionleaderboard(self, ctx, *args):
        """
        ~completionleaderboard
        -metric: scores|plays|easyclears|normalclears|hardclears|extraclears|ultraclears|overclears|fc|ss   (required)
        -fa / -is_fa: 0|false, 1|true, 2|all (default 2)
        -diff / -difficulty: 0|easy, 1|hard, 2|all (default 2)
        -mode: 0|osu, 1|taiko, 2|fruits|catch|ctb, 3|mania, 4|all (default 4)
        -order: count|date|total (default count)
        -direction: asc|desc (default desc)
        -page/-limit (synonyms -p/-l handled by get_args via PARAM_SYNONYM_MAP)
        """
        di = get_args(args)

        # ----------------------------
        # resolve caller username (for -page me and "me row" footer behavior)
        # ----------------------------
        discordid = ctx.author.id
        my_username = None
        q_me = (
            "SELECT ul.username "
            "FROM registrations r "
            "INNER JOIN userLive ul ON r.user_id = ul.user_id "
            f"WHERE r.discordid = '{discordid}'"
        )
        me_rows, _ = await self.bot.db.executeQuery(q_me)
        if me_rows:
            my_username = me_rows[0]["username"] if isinstance(me_rows[0], dict) else me_rows[0][0]

        # ----------------------------
        # parse metric (required)
        # ----------------------------
        metric = self._norm(di.get("-metric", "normalclears"))
        allowed_metrics = {
            "scores", "plays", "easyclears", "normalclears", "hardclears",
            "extraclears", "ultraclears", "overclears", "fc", "ss",
        }
        if not metric or metric not in allowed_metrics:
            await ctx.reply(
                "Missing/invalid `-metric`. Allowed: "
                "scores, plays, easyclears, normalclears, hardclears, extraclears, ultrclears, overclears, fc, ss"
            )
            return

        # ----------------------------
        # parse buckets / ordering
        # ----------------------------
        fa_bucket, err = self._parse_bucket(di.get("-fa", di.get("-is_fa")), kind="fa")
        if err:
            await ctx.reply(err)
            return

        diff_bucket, err = self._parse_bucket(di.get("-diff", di.get("-difficulty")), kind="diff")
        if err:
            await ctx.reply(err)
            return

        mode_bucket, err = self._parse_bucket(di.get("-mode"), kind="mode")
        if err:
            await ctx.reply(err)
            return

        order_col, err = self._parse_order(di.get("-order"))
        if err:
            await ctx.reply(err)
            return

        direction_sql, err = self._parse_direction(di.get("-direction"))
        if err:
            await ctx.reply(err)
            return

        # ----------------------------
        # fetch FULL ordered leaderboard (no LIMIT/OFFSET)
        # ----------------------------
        # IMPORTANT: order_col is whitelisted; direction_sql is ASC/DESC only.
        sql = f"""
            SELECT
            ul.username AS username,
            us.value AS value,
            us.total AS total,
            us.completed_up_to AS completed_up_to
            FROM userstats us
            JOIN userLive ul ON ul.user_id = us.user_id
            WHERE us.metric_type = '{metric}'
            AND us.mode_bucket = {int(mode_bucket)}
            AND us.fa_bucket = {int(fa_bucket)}
            AND us.diff_bucket = {int(diff_bucket)}
            ORDER BY {order_col} {direction_sql}, ul.username ASC
        """
        result, elapsed = await self.bot.db.executeQuery(sql)

        # ----------------------------
        # pagination args (like other commands)
        # ----------------------------
        page_size = int(di.get("-limit", 10))
        page_size = max(page_size, 1)

        page_arg = self._norm(di.get("-page")) or "1"

        if page_arg == "me" and my_username is not None:
            # compute page from FULL ordered list
            me_rank = None
            for idx, row in enumerate(result, start=1):
                uname = row["username"] if isinstance(row, dict) else row[0]
                if uname == my_username:
                    me_rank = idx
                    break
            page = ((me_rank - 1) // page_size) + 1 if me_rank else 1
        else:
            try:
                page = int(page_arg)
            except ValueError:
                page = 1
            page = max(page, 1)

        # ----------------------------
        # title labels
        # ----------------------------
        MODE_LABELS = {0: "Osu", 1: "Taiko", 2: "Fruits", 3: "Mania", 4: "All"}
        FA_LABELS = {0: "Not FA", 1: "FA", 2: "All"}
        DIFF_LABELS = {0: "Easy", 1: "Hard", 2: "All"}

        mode_label = MODE_LABELS.get(int(mode_bucket), str(mode_bucket))
        fa_label = FA_LABELS.get(int(fa_bucket), str(fa_bucket))
        diff_label = DIFF_LABELS.get(int(diff_bucket), str(diff_bucket))
        metric_label = metric.upper()

        title = f"Completion | {mode_label} | {fa_label} | {diff_label} | {metric_label}"

        formatter = Formatter(title=title, footer=f"Based on userstats")
        embed = formatter.as_completion_leaderboard(
            result,
            page=page,
            page_size=page_size,
            elapsed=elapsed,
            user=my_username
        )
        await ctx.reply(embed=embed)




async def setup(bot):
    await bot.add_cog(Stats(bot))
