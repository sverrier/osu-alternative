import asyncio
import logging
import os
from datetime import datetime

from api.util.scoreOsu import ScoreOsu
from api.util.scoreFruits import ScoreFruits
from api.util.scoreMania import ScoreMania
from api.util.scoreTaiko import ScoreTaiko
from api.util.api import util_api
from util.db import db
from util.crypto import get_fernet


class Fetcher:
    """
    Standalone fetcher that runs the 'sync_registered_user_scores' routine
    in an infinite loop, using its own config file: fetcher.txt
    """

    def __init__(self, config_file: str = "fetcher.txt", default_delay_seconds: int = 10):
        self.config_file = config_file
        self._setup_logging()
        self.logger.info("Initializing FetcherLoop...")

        # Load DB/API config from its own file
        self.config_values = self._load_or_create_config()

        # Default delay between iterations (can be overridden by DELAY in config)
        self.delay = float(default_delay_seconds)
        if "DELAY" in self.config_values:
            try:
                # DELAY is in ms, convert to seconds
                self.delay = int(self.config_values["DELAY"]) / 1000.0
            except ValueError:
                self.logger.warning(
                    f"Invalid DELAY value '{self.config_values['DELAY']}', "
                    f"falling back to {self.delay} seconds."
                )

        # Create DB and API helpers
        self.db = db(self.config_values, self.logger)
        self.apiv2 = util_api(self.config_values)

    # ------------------------------------------------------------------ #
    # LOGGING
    # ------------------------------------------------------------------ #

    def _setup_logging(self):
        os.makedirs("logs", exist_ok=True)
        log_path = f"logs/fetcher_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        console_handler.setLevel(logging.INFO)

        self.logger = logging.getLogger("FetcherLoop")
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers if re-imported
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        else:
            # Clear and re-add to be safe
            self.logger.handlers.clear()
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    # ------------------------------------------------------------------ #
    # CONFIG MANAGEMENT  (fetcher.txt)
    # ------------------------------------------------------------------ #

    def _create_config_file(self):
        """
        Create a new config file (fetcher.txt) with encrypted KEY and PASSWORD,
        same style as the main OsuDataFetcher config.
        """
        self.logger.info("Creating new configuration file for FetcherLoop...")

        config = {}
        config["KEY"] = input("Enter the KEY value (client_secret): ").strip()
        config["CLIENT"] = input("Enter the CLIENT ID value (client_public): ").strip()
        config["DELAY"] = input("Enter the DELAY value (ms): ").strip()
        config["DBNAME"] = input("Enter the DBNAME value: ").strip()
        config["USERNAME"] = input("Enter the USERNAME value: ").strip()
        config["PASSWORD"] = input("Enter the PASSWORD value: ").strip()
        config["PORT"] = input("Enter the PORT value: ").strip()
        config["HOST"] = input("Enter the HOST value (default: localhost): ").strip() or "localhost"

        f = get_fernet()

        # Encrypt sensitive fields
        config["KEY"] = f.encrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.encrypt(config["PASSWORD"].encode()).decode()

        with open(self.config_file, "w", encoding="utf-8") as file:
            for k, v in config.items():
                file.write(f"[{k}]={v}\n")

        # Decrypt into runtime config
        config["KEY"] = f.decrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.decrypt(config["PASSWORD"].encode()).decode()

        self.logger.info(f"Configuration file '{self.config_file}' created successfully.")
        return config

    def _read_config_file(self):
        """
        Read existing fetcher.txt and decrypt KEY/PASSWORD.
        """
        self.logger.info(f"Reading configuration file '{self.config_file}'...")
        config = {}
        f = get_fernet()

        with open(self.config_file, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k.strip("[]")] = v

        # Decrypt secret values
        config["KEY"] = f.decrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.decrypt(config["PASSWORD"].encode()).decode()
        return config

    def _load_or_create_config(self):
        if os.path.exists(self.config_file):
            self.logger.info(f"Found '{self.config_file}'. Reading configuration...")
            return self._read_config_file()
        else:
            return self._create_config_file()
    
    async def sync_registered_user_scores(self):
        """
        Sync scores for the next unsynced user in `registrations`, using:

        - registrations (is_synced flag)
        - beatmapLive
        - logger (logType = 'FETCHER')
        - score tables via ScoreOsu/Taiko/Fruits/Mania helpers
        """
        query = """
            SELECT user_id
            FROM registrations
            WHERE is_synced = false
            ORDER BY registrationdate
            LIMIT 1
        """
        rs, elapsed = await self.db.executeQuery(query)

        if not rs:
            self.logger.info("All registered users are synced.")
            return

        user_id = rs[0]["user_id"] if isinstance(rs[0], dict) else rs[0][0]

        all_beatmaps = []
        limit = 100
        offset = 0

        self.logger.info(f"Fetching all most-played beatmaps for user {user_id}...")

        # Page through user's most-played beatmaps
        while True:
            page = self.apiv2.get_user_beatmaps_most_played(user_id, limit, offset)
            if not page:
                break
            all_beatmaps.extend(page)
            offset += limit
            self.logger.info(f"Fetched beatmaps up to offset {offset} for user {user_id}...")

        beatmap_ids = [b["beatmap_id"] for b in all_beatmaps]
        self.logger.info(f"Fetched {len(beatmap_ids)} total beatmaps for user {user_id}")

        # Determine which beatmaps still need syncing, based on logger
        query = """
            SELECT beatmap_id
            FROM beatmapLive
            WHERE beatmap_id > (
                SELECT COALESCE(MAX(beatmap_id), 0)
                FROM logger
                WHERE logType = 'FETCHER' AND user_id = $1
            )
        """
        rs = await self.db.fetchParametrized(query, user_id)
        existing_ids = {
            (row["beatmap_id"] if isinstance(row, dict) else row[0]) for row in rs
        }

        target_ids = sorted([bid for bid in beatmap_ids if bid in existing_ids])
        total = len(target_ids)
        self.logger.info(f"{total} beatmaps pending sync for user {user_id}")

        # Process beatmaps in batches
        batch_size = 100
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch_ids = target_ids[batch_start:batch_end]

            self.logger.info(
                f"Processing batch {batch_start // batch_size + 1}: "
                f"beatmaps {batch_start + 1}-{batch_end} of {total}"
            )

            # Accumulate all scores in this batch
            score_groups = {0: [], 1: [], 2: [], 3: []}

            for idx, beatmap_id in enumerate(batch_ids, start=batch_start + 1):
                self.logger.info(
                    f"[{idx}/{total}] Fetching scores for beatmap {beatmap_id} (user {user_id})..."
                )

                scores = self.apiv2.get_beatmap_user_scores(beatmap_id, user_id)

                # Group scores by ruleset
                for score_data in scores:
                    ruleset_id = score_data["ruleset_id"]
                    score_groups[ruleset_id].append(score_data)

            # Batch insert all scores from this batch of beatmaps
            total_scores = 0
            for ruleset_id, ruleset_scores in score_groups.items():
                if not ruleset_scores:
                    continue

                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][ruleset_id]
                insert_query = score_cls.get_insert_query_template()
                params_list = [score_cls(s).get_insert_params() for s in ruleset_scores]
                await self.db.executemany(insert_query, params_list)
                total_scores += len(ruleset_scores)

            # Update logger to the last beatmap in this batch
            last_beatmap_id = batch_ids[-1]
            await self.db.executeParametrized(
                """
                INSERT INTO logger (logtype, user_id, beatmap_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (logtype, user_id)
                DO UPDATE SET beatmap_id = EXCLUDED.beatmap_id
                """,
                "FETCHER",
                user_id,
                last_beatmap_id,
            )

            self.logger.info(
                f"Completed batch {batch_start // batch_size + 1}: "
                f"Processed {len(batch_ids)} beatmaps, {total_scores} scores"
            )

        # Mark user as fully synced
        await self.db.executeParametrized(
            "UPDATE registrations SET is_synced = true WHERE user_id = $1",
            user_id,
        )

        self.logger.info(
            f"Sync complete for user {user_id} ({total} beatmaps processed)."
        )


    # ------------------------------------------------------------------ #
    # LOOP RUNNER
    # ------------------------------------------------------------------ #

    async def run(self):
        """
        Initialize DB + API, then repeatedly run sync_registered_user_scores
        with a delay in between iterations.
        """
        # Initial setup
        await self.db.get_pool()
        await self.db.execSetupFiles()
        self.apiv2.refresh_token()

        self.logger.info(
            f"FetcherLoop started. Running sync_registered_user_scores() "
            f"every {self.delay} seconds."
        )

        while True:
            try:
                await self.sync_registered_user_scores()
            except Exception as e:
                self.logger.error(f"Error in fetcher loop: {e}")

            self.logger.info(f"Sleeping {self.delay} seconds before next iteration...")
            await asyncio.sleep(self.delay)
