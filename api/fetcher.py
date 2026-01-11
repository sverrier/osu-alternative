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
    """
    Standalone fetcher that runs the 'sync_registered_user_scores' routine
    in an infinite loop, using its own config file: fetcher.txt
    """

    def __init__(self, config_file: str = "fetcher.txt"):
        self.config_file = config_file
        self._setup_logging()
        self.logger.info("Initializing FetcherLoop...")

        # Load DB/API config from its own file
        self.config_values = self._load_or_create_config()
        self.delay = int(self.config_values["DELAY"]) / 1000.0

        # Create DB and API helpers
        self.db = db(self.config_values, self.logger)

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
        
    
    async def _log_batch_complete_to_db(self, user_id: int, fetched: int, total: int):
        """
        Mirror console progress into public.logging.

        logtype: 'FETCHER'
        logkey: 'user_id' (text key label)
        severity: 'INFO'
        message: 'batch complete'
        data: {"user_id": "<user_id>", "fetched": <batch_start>, "total": <batch_size>}
                """
        try:
            data = {"user_id": str(user_id), "fetched": fetched, "total": total}

            await self.db.executeParametrized(
                """
                INSERT INTO public.logging (entrytime, logtype, logkey, severity, message, "data")
                VALUES (NOW(), $1, $2, $3, $4, $5::jsonb)
                """,
                "FETCHER",
                str(user_id),
                "INFO",
                "batch complete",
                json.dumps(data),
            )
        except Exception as e:
            self.logger.error(f"Failed to write batch log to public.logging: {e}")

    async def _load_user_token_from_db(self, user_id: int, mode: int | None = None):
        """
        Fetch the most recent token row for a user (optionally filtered by mode).
        Returns: (user_id, mode, token_dict)
        """
        if mode is None:
            query = """
                SELECT user_id, mode, token
                FROM tokens
                WHERE user_id = $1
                ORDER BY lchg_time DESC
                LIMIT 1
            """
            rows = await self.db.fetchParametrized(query, user_id)
        else:
            query = """
                SELECT user_id, mode, token
                FROM tokens
                WHERE user_id = $1 AND mode = $2
                ORDER BY lchg_time DESC
                LIMIT 1
            """
            rows = await self.db.fetchParametrized(query, user_id, mode)

        if not rows:
            raise RuntimeError(f"No token found in tokens table for user_id={user_id}, mode={mode}")

        row = rows[0]

        # asyncpg Record supports dict-style access
        db_user_id = row["user_id"]
        db_mode = row["mode"]
        token_val = row["token"]

        # token might already be json/jsonb (dict), or stored as text
        if isinstance(token_val, (dict, list)):
            token_obj = token_val
        else:
            token_obj = json.loads(token_val)

        if "access_token" not in token_obj:
            raise RuntimeError(f"Token row missing access_token for user_id={db_user_id}, mode={db_mode}")

        return db_user_id, db_mode, token_obj

    def _apply_access_token_to_api(self, api, access_token: str):
        """
        Apply a bearer token to util_api object.

        This assumes util_api reads self.token when building Authorization headers.
        If your util_api uses a different attribute/method, adjust here only.
        """
        api.token = access_token

    async def sync_user_scores_from_tokens(self, api, user_id: int, mode: int | None = None):
        """
        Loads (user_id, mode, token) from tokens table, applies the access token,
        then runs the normal sync routine for that specific user.
        """
        db_user_id, db_mode, token_obj = await self._load_user_token_from_db(user_id, mode)
        self._apply_access_token_to_api(api, token_obj["access_token"])

        self.logger.info(f"Using user token from tokens table for user {db_user_id} (mode={db_mode})")
        await self.sync_registered_user_scores(user_id=db_user_id, api=api)
    
    async def sync_registered_user_scores(self, api, user_id: int | None = None):
        """
        Sync scores for:
          - the provided user_id, OR
          - the next unsynced user in registrations (original behavior).
        """
        scan_all_maps = False
        if user_id is None:
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
        else:
            # When explicitly passed, we do NOT require them to be unsynced.
            self.logger.info(f"Explicit user_id provided: syncing user {user_id}")
            if user_id < 4000000:
                self.logger.info(
                    f"user-token mode + user_id < 4,000,000: scanning ALL maps (filtered by logger) for user {user_id}"
                )
                scan_all_maps = True

        all_beatmaps = []
        limit = 100
        offset = 0

        if scan_all_maps:

            # Pull only the beatmaps that are beyond logger progress (no need to use most_played)
            query = """
                SELECT beatmap_id
                FROM beatmapLive
                WHERE beatmap_id > (
                    SELECT COALESCE(MAX(beatmap_id), 0)
                    FROM logger
                    WHERE logType = 'FETCHER' AND user_id = $1
                )
                ORDER BY beatmap_id
            """
            rs = await self.db.fetchParametrized(query, user_id)
            target_ids = [row["beatmap_id"] for row in rs]

            total = len(target_ids)
            self.logger.info(f"{total} beatmaps pending sync for user {user_id} (all-maps scan)")
        else:
            all_beatmaps = []
            limit = 100
            offset = 0

            self.logger.info(f"Fetching all most-played beatmaps for user {user_id}...")

            # Page through user's most-played beatmaps
            while True:
                page = await asyncio.to_thread(api.get_user_beatmaps_most_played, user_id, limit, offset)
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
            existing_ids = {row["beatmap_id"] for row in rs}

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

                scores = await asyncio.to_thread(api.get_beatmap_user_scores, beatmap_id, user_id)

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

            await self._log_batch_complete_to_db(
                user_id=user_id,
                fetched=idx,
                total=total
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

    async def sync_user_scores_from_tokens_queue(self, api):
        query = """
            SELECT user_id, mode
            FROM tokens
            ORDER BY lchg_time
            LIMIT 1
        """
        rows = await self.db.fetchParametrized(query)

        if not rows:
            self.logger.info("No users found in tokens table.")
            return

        row = rows[0]
        await self.sync_user_scores_from_tokens(
            user_id=row["user_id"],
            mode=row["mode"],
            api=api
        )

    async def _client_loop(self, api_client):
        self.logger.info("Client loop started.")
        while True:
            try:
                await self.sync_registered_user_scores(api=api_client)
            except Exception as e:
                self.logger.error(f"Error in client loop: {e}")

            self.logger.info(f"[client] Sleeping {self.delay} seconds before next iteration...")
            await asyncio.sleep(self.delay)


    async def _user_loop(self, api_user):
        self.logger.info("User loop started.")
        while True:
            try:
                await self.sync_user_scores_from_tokens_queue(api=api_user)
            except Exception as e:
                self.logger.error(f"Error in user loop: {e}")

            self.logger.info(f"[user] Sleeping {self.delay} seconds before next iteration...")
            await asyncio.sleep(self.delay)

    async def run(self):
        """
        Modes:
        [1] client loop (client_credentials, api delay 1000ms)
        [2] user loop   (tokens table, api delay 10ms)
        [3] main loop   (client + user in parallel)
        """
        await self.db.get_pool()
        await self.db.execSetupFiles()

        print("")
        print("Select fetcher mode:")
        print("  [1] client  (client_credentials)")
        print("  [2] user    (user tokens from tokens table)")
        print("  [3] main loop (client + user in parallel)")
        choice = input("Enter choice (1/2/3): ").strip()

        # ----------------------------------------
        # Build 2 independent API objects
        # ----------------------------------------
        api_client = util_api(self.config_values)
        api_user = util_api(self.config_values)

        # 🔥 Wipe client credentials from memory
        api_user.client = None
        api_user.key = None

        # 🔒 Lock auth mode to user only
        api_user._auth_mode = "user"

        # 🔒 Disable client refresh entirely
        api_user.refresh_client_token = lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("SECURITY: client token refresh called in user API instance")
        )

        # Set fast delay for user API
        api_user._set_delay(100)

        # ----------------------------------------
        # Initialize client API (normal)
        # ----------------------------------------
        api_client.use_client_token()
        api_client._set_delay(1000)
        api_client.refresh_client_token()

        # ----------------------------------------
        # Mode selection
        # ----------------------------------------
        if choice == "1":
            mode = "client"
        elif choice == "2":
            mode = "user"
        elif choice == "3":
            mode = "main"
        else:
            return

        self.logger.info(f"Fetcher starting in '{mode}' mode")
        self.logger.info(f"FetcherLoop started ({mode} mode). Running every {self.delay} seconds.")

        # ----------------------------------------
        # Dispatch
        # ----------------------------------------
        if mode == "client":
            await self._client_loop(api_client)

        elif mode == "user":
            await self._user_loop(api_user)

        else:
            # Run both forever, in parallel
            await asyncio.gather(
                self._client_loop(api_client),
                self._user_loop(api_user),
            )
