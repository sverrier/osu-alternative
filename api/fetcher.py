import asyncio
import logging
import os
import json
from datetime import datetime

from api.util.scoreOsu import ScoreOsu
from api.util.scoreFruits import ScoreFruits
from api.util.scoreMania import ScoreMania
from api.util.scoreTaiko import ScoreTaiko
from api.util.api import util_api
from util.db import db
from util.crypto import get_fernet


class Fetcher:
    def __init__(self, client_config="fetcher.txt", user_config="userfetcher.txt"):
        self.client_config_file = client_config
        self.user_config_file = user_config

        self._setup_logging()
        self.logger.info("Initializing Fetcher...")

        self.client_config = self._load_or_create_config(self.client_config_file)
        self.user_config = self._load_or_create_config(self.user_config_file)

        self.client_delay = int(self.client_config["DELAY"]) / 1000.0
        self.user_delay = int(self.user_config["DELAY"]) / 1000.0

        self.db = db(self.client_config, self.logger)

    # -----------------------
    # Logging
    # -----------------------
    def _setup_logging(self):
        os.makedirs("logs", exist_ok=True)
        log_path = f"logs/fetcher_{datetime.now().strftime('%Y%m%d')}.log"

        self.logger = logging.getLogger("Fetcher")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        fh = logging.FileHandler(log_path)
        ch = logging.StreamHandler()

        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    # -----------------------
    # Config
    # -----------------------
    def _load_or_create_config(self, path):
        if os.path.exists(path):
            return self._read_config(path)
        return self._create_config(path)

    def _read_config(self, path):
        config = {}
        f = get_fernet()

        with open(path, "r") as file:
            for line in file:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k.strip("[]")] = v

        config["KEY"] = f.decrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.decrypt(config["PASSWORD"].encode()).decode()
        return config

    def _create_config(self, path):
        self.logger.info(f"Creating config: {path}")
        config = {}

        config["KEY"] = input("KEY: ").strip()
        config["CLIENT"] = input("CLIENT: ").strip()
        config["DELAY"] = input("DELAY(ms): ").strip()
        config["DBNAME"] = input("DBNAME: ").strip()
        config["USERNAME"] = input("USERNAME: ").strip()
        config["PASSWORD"] = input("PASSWORD: ").strip()
        config["PORT"] = input("PORT: ").strip()
        config["HOST"] = input("HOST: ").strip() or "localhost"

        f = get_fernet()

        enc = config.copy()
        enc["KEY"] = f.encrypt(config["KEY"].encode()).decode()
        enc["PASSWORD"] = f.encrypt(config["PASSWORD"].encode()).decode()

        with open(path, "w") as file:
            for k, v in enc.items():
                file.write(f"[{k}]={v}\n")

        return config

    # -----------------------
    # API Builders
    # -----------------------
    def _build_client_api(self):
        api = util_api(self.client_config)
        api.use_client_token()
        api._set_delay(self.client_delay * 1000)
        api.refresh_client_token()
        return api

    def _build_user_api(self):
        api = util_api(self.user_config)
        api._set_delay(self.user_delay * 1000)
        return api

    # -----------------------
    # Logging (JSON checkpoint)
    # -----------------------
    async def _get_last_state(self, user_id):
        row = await self.db.fetchParametrized(
            """
            SELECT data
            FROM public.logging
            WHERE logtype = 'FETCHER'
            AND logkey = $1
            ORDER BY entrytime DESC
            LIMIT 1
            """,
            str(user_id)
        )

        if not row:
            return {
                "max_beatmap_id": 0,
                "fetched": 0,
                "total": 0
            }

        data = row[0]["data"]
        if isinstance(data, str):
            data = json.loads(data)

        return data

    async def _log_progress(self, user_id, fetched, total, max_beatmap_id):
        data = {
            "user_id": str(user_id),
            "fetched": fetched,
            "total": total,
            "max_beatmap_id": max_beatmap_id
        }

        await self.db.executeParametrized(
            """
            INSERT INTO public.logging (entrytime, logtype, logkey, severity, message, data)
            VALUES (NOW(), $1, $2, $3, $4, $5::jsonb)
            """,
            "FETCHER",
            str(user_id),
            "INFO",
            "batch complete",
            json.dumps(data)
        )

    # -----------------------
    # Token handling
    # -----------------------
    async def _load_user_token(self, user_id):
        rows = await self.db.fetchParametrized(
            "SELECT token FROM tokens WHERE user_id = $1 ORDER BY lchg_time DESC LIMIT 1",
            user_id
        )

        if not rows:
            raise RuntimeError(f"No token for user {user_id}")

        token = rows[0]["token"]
        if not isinstance(token, dict):
            token = json.loads(token)

        return token

    def _apply_user_token(self, api, token):
        api.use_user_token(token["access_token"], token.get("refresh_token"))

    def _should_scan_all_maps(self, user_id: int, api) -> bool:
        """
        Old osu profiles may have incomplete 'most_played' data.
        For those users, we must scan all beatmaps instead.
        """
        return (user_id < 4_000_000) #and api._auth_mode == "user") #removed as queue is empty

    # -----------------------
    # Core Sync
    # -----------------------
    async def sync_registered_user_scores(self, api, user_id=None):
        if user_id is None:
            rs, _ = await self.db.executeQuery(
                "SELECT user_id FROM registrations WHERE is_synced = false ORDER BY registrationdate LIMIT 1"
            )

            if not rs:
                return

            user_id = rs[0]["user_id"] if isinstance(rs[0], dict) else rs[0][0]

        scan_all_maps = self._should_scan_all_maps(user_id, api)

        state = await self._get_last_state(user_id)
        last_id = state.get("max_beatmap_id", 0)

        if scan_all_maps:
            self.logger.info(
                f"[user:{user_id}] hybrid scan mode (pre-2016 full + post-2016 most_played)"
            )

            # -----------------------
            # 1. Pre-2016: full DB scan
            # -----------------------
            db_rows = await self.db.fetchParametrized(
                """
                SELECT beatmap_id
                FROM beatmapLive
                WHERE ranked_date < '2016-01-01'
                AND beatmap_id > $1
                ORDER BY beatmap_id
                """,
                last_id
            )

            db_ids = [r["beatmap_id"] for r in db_rows]

            # -----------------------
            # 2. Post-2016: most_played
            # -----------------------
            beatmaps = []
            offset = 0

            while True:
                page = await asyncio.to_thread(
                    api.get_user_beatmaps_most_played,
                    user_id,
                    100,
                    offset
                )
                if not page:
                    break

                beatmaps.extend(page)
                offset += 100

            beatmap_ids = [b["beatmap_id"] for b in beatmaps]

            # Validate + filter by ranked_date >= 2016
            rows = await self.db.fetchParametrized(
                """
                SELECT beatmap_id
                FROM beatmapLive
                WHERE beatmap_id = ANY($1)
                AND ranked_date >= '2016-01-01'
                """,
                beatmap_ids
            )

            mp_ids = {r["beatmap_id"] for r in rows}

            # -----------------------
            # 3. Combine + filter
            # -----------------------
            target_ids = sorted(
                set(db_ids) | {bid for bid in beatmap_ids if bid in mp_ids and bid > last_id}
            )

        else:
            self.logger.info(
                f"Gathering most played beatmaps for user {user_id}"
            )

            beatmaps = []
            offset = 0

            while True:
                page = await asyncio.to_thread(
                    api.get_user_beatmaps_most_played,
                    user_id,
                    100,
                    offset
                )
                if not page:
                    break

                beatmaps.extend(page)
                offset += 100

                self.logger.info(f"Fetched beatmaps up to offset {offset} for user {user_id}...")

            beatmap_ids = [b["beatmap_id"] for b in beatmaps]

            rows = await self.db.fetchParametrized(
                """
                SELECT beatmap_id
                FROM beatmapLive
                WHERE beatmap_id = ANY($1)
                """,
                beatmap_ids
            )

            valid_ids = {r["beatmap_id"] for r in rows}

            target_ids = [bid for bid in beatmap_ids if bid in valid_ids and bid > last_id]

        total = len(target_ids)

        target_ids = sorted(target_ids)

        batch_size = 100
        index = 0

        for i in range(0, total, batch_size):
            batch = target_ids[i:i+batch_size]

            grouped = {0: [], 1: [], 2: [], 3: []}

            for idx, beatmap_id in enumerate(batch, start=i + 1):
                self.logger.info(
                    f"[{idx}/{total}] Fetching scores for beatmap {beatmap_id} (user {user_id})..."
                )
                scores = await asyncio.to_thread(api.get_beatmap_user_scores, beatmap_id, user_id)
                for s in scores:
                    grouped[s["ruleset_id"]].append(s)

            total_scores = 0
            for ruleset_id, data in grouped.items():
                if not data:
                    continue

                cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][ruleset_id]
                query = cls.get_insert_query_template()
                params = [cls(s).get_insert_params() for s in data]

                await self.db.executemany(query, params)
                total_scores += len(data)

            await self._log_progress(
                user_id=user_id,
                fetched=i + len(batch),
                total=total,
                max_beatmap_id=batch[-1]
            )

            self.logger.info(
                f"[{user_id}] {i+len(batch)}/{total} | {total_scores} scores"
            )

        # Mark user as fully synced
        await self.db.executeParametrized(
            "UPDATE registrations SET is_synced = true WHERE user_id = $1",
            user_id,
        )

        await self.db.executeParametrized(
            "DELETE FROM tokens WHERE user_id = $1",
            user_id,
        )

        self.logger.info(
            f"Sync complete for user {user_id} ({total} beatmaps processed)."
        )

    async def sync_user(self, api, user_id):
        token = await self._load_user_token(user_id)
        self._apply_user_token(api, token)
        await self.sync_registered_user_scores(api, user_id)

    # -----------------------
    # Loops
    # -----------------------
    async def client_loop(self, api):
        while True:
            try:
                await self.sync_registered_user_scores(api)
            except Exception as e:
                self.logger.error(e)

            await asyncio.sleep(self.client_delay)

    async def user_loop(self, api):
        while True:
            try:
                rows = await self.db.fetchParametrized("SELECT user_id FROM tokens LIMIT 1")
                if rows:
                    await self.sync_user(api, rows[0]["user_id"])
            except Exception as e:
                self.logger.error(e)

            await asyncio.sleep(self.user_delay)

    # -----------------------
    # Entry
    # -----------------------
    async def run(self):
        await self.db.get_pool()
        await self.db.execSetupFiles()

        api_client = self._build_client_api()
        api_user = self._build_user_api()

        print("1=client 2=user 3=both")
        choice = input().strip()

        if choice == "1":
            await self.client_loop(api_client)
        elif choice == "2":
            await self.user_loop(api_user)
        else:
            await asyncio.gather(
                self.client_loop(api_client),
                self.user_loop(api_user)
            )
