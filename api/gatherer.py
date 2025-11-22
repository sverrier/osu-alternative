import os
import logging
import asyncio
from datetime import datetime
from cryptography.fernet import Fernet

from api.util.jsonDataObject import jsonDataObject
from api.util.userExtended import UserExtended
from api.util.userMaster import UserMaster
from api.util.beatmap import Beatmap
from api.util.scoreOsu import ScoreOsu
from api.util.scoreFruits import ScoreFruits
from api.util.scoreMania import ScoreMania
from api.util.scoreTaiko import ScoreTaiko
from api.util.api import util_api
from util.db import db


class OsuDataFetcher:
    def __init__(self, config_file="config.txt"):
        self._setup_logging()
        self.logger.info("Initializing OsuDataFetcher...")
        self.config_file = config_file
        self.config_values = self._load_or_create_config()
        self.db = db(self.config_values, self.logger)
        self.apiv2 = util_api(self.config_values)

    def _setup_logging(self):
        os.makedirs('logs', exist_ok=True)
        log_filename = f"logs/osu_fetcher_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    # ---------------- CONFIG MANAGEMENT ----------------
    def _create_config_file(self):
        self.logger.info("Creating new configuration file...")
        config = {}
        config["KEY"] = input("Enter the KEY value (client_secret): ").strip()
        config["CLIENT"] = input("Enter the CLIENT ID value (client_public): ").strip()
        config["DELAY"] = input("Enter the DELAY value (ms): ").strip()
        config["DBNAME"] = input("Enter the DBNAME value: ").strip()
        config["USERNAME"] = input("Enter the USERNAME value: ").strip()
        config["PASSWORD"] = input("Enter the PASSWORD value: ").strip()
        config["PORT"] = input("Enter the PORT value: ").strip()
        config["HOST"] = input("Enter the HOST value (default: localhost): ").strip() or "localhost"

        key = Fernet.generate_key()
        self.logger.info(f"Generated encryption key: {key}")
        print("SAVE THIS KEY:", key)

        f = Fernet(key)
        config["KEY"] = f.encrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.encrypt(config["PASSWORD"].encode()).decode()

        with open(self.config_file, "w") as file:
            for k, v in config.items():
                file.write(f"[{k}]={v}\n")

        config["KEY"] = f.decrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.decrypt(config["PASSWORD"].encode()).decode()
        self.logger.info(f"Configuration file '{self.config_file}' created successfully.")
        return config

    def _read_config_file(self):
        self.logger.info("Reading configuration file...")
        config = {}
        config["ENCRYPTION_KEY"] = input("Enter your encryption key: ").encode()
        f = Fernet(config["ENCRYPTION_KEY"])
        with open(self.config_file, "r") as file:
            for line in file:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k.strip("[]")] = v
        config["KEY"] = f.decrypt(config["KEY"].encode()).decode()
        config["PASSWORD"] = f.decrypt(config["PASSWORD"].encode()).decode()
        return config

    def _load_or_create_config(self):
        if os.path.exists(self.config_file):
            self.logger.info(f"Found '{self.config_file}'. Reading configuration...")
            return self._read_config_file()
        else:
            return self._create_config_file()

    # ---------------- HELPERS ----------------
    def _generate_id_batches(self, start_id, end_id, batch_size=50):
        for i in range(start_id, end_id, batch_size):
            yield list(range(i, min(i + batch_size, end_id)))

    async def _generate_id_batches_from_query(self, query, batch_size=50):
        rs, elapsed = await self.db.executeQuery(query)
        ids = sorted(row['id'] if isinstance(row, dict) else row[0] for row in rs)
        batches = []
        for i in range(0, len(ids), batch_size):
            batches.append(ids[i:i + batch_size])
        return batches

    async def _execute_sql_file(self, filename: str, subdir: str = "sql/inserts"):
        """Executes a .sql script file and logs the result."""
        file_path = os.path.join(subdir, filename)
        self.logger.info(f"Executing SQL file: {file_path}")

        if not os.path.exists(file_path):
            self.logger.error(f"SQL file not found: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as sql_file:
                sql_script = sql_file.read()
            await self.db.executeSQL(sql_script)
            self.logger.info(f"Successfully executed: {filename}")
        except Exception as e:
            self.logger.exception(f"Error executing {filename}: {e}")

    # ---------------- ROUTINES ----------------
    async def fetch_beatmaps(self):
        self.logger.info("Fetching beatmaps...")
        result, elapsed = await self.db.executeQuery("select coalesce(max(id), 1) from beatmap;")
        maxid = result[0]['coalesce'] if isinstance(result[0], dict) else result[0][0]
        
        consecutive_empty = 0  # stop only after 5 empty batches in a row
        
        for batch in self._generate_id_batches(maxid, maxid+10000, 50):
            beatmaps = self.apiv2.get_beatmaps(batch).get("beatmaps", [])
            queries = ''.join(Beatmap(l).generate_insert_query() for l in beatmaps)
            if queries:
                await self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(beatmaps)} beatmaps.")
            if len(beatmaps) == 0:
                consecutive_empty += 1
                if consecutive_empty >= 5:
                    break
            else:
                consecutive_empty = 0

    async def fetch_beatmaps_packs(self):
        self.logger.info("Fetching beatmap packs...")

        all_tags = []
        cursor_string = None
        total = 0

        while True:
            packs = self.apiv2.get_beatmap_packs(cursor_string=cursor_string)

            beatmap_packs = packs.get("beatmap_packs", [])
            if not beatmap_packs:
                break

            tags = [p.get("tag") for p in beatmap_packs if p.get("tag")]
            all_tags.extend(tags)
            total += len(tags)

            cursor_string = packs.get("cursor_string")
            self.logger.info(f"Fetched {len(tags)} packs (total: {total}).")

            if not cursor_string:
                break

        self.logger.info(f"Completed fetching all beatmap packs ({total} total).")

        for tag in all_tags:
            pack = self.apiv2.get_beatmap_pack(tag)
            queries = ''
            for map in pack.get("beatmapsets"):
                id = map.get("id")
                queries += (f"UPDATE beatmapLive SET pack = '{tag}' where beatmapset_id = {id};")
            maps = len(pack.get("beatmapsets"))
            await self.db.executeSQL(queries)
            self.logger.info(f"Updated {maps} beatmaps with pack tag '{tag}'.")

    async def fetch_users(self):
        self.logger.info("Fetching users...")
        result, elapsed = await self.db.executeQuery("select coalesce(max(id), 1) from userMaster;")
        maxid = result[0]['coalesce'] if isinstance(result[0], dict) else result[0][0]
        
        for batch in self._generate_id_batches(maxid, maxid + 100000, 50):
            users = self.apiv2.get_users(batch).get("users", [])
            queries = ''.join(UserMaster(u.copy()).generate_insert_query() for u in users)
            if queries:
                await self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(users)} users.")
            if len(users) == 0:
                break

    async def fetch_leaderboard_scores(self):
        self.logger.info("Fetching leaderboard scores...")
        rs, elapsed = await self.db.executeQuery("select beatmap_id from beatmaplive order by beatmap_id;")
        
        for row in rs:
            beatmap_id = row['beatmap_id'] if isinstance(row, dict) else row[0]
            scores = self.apiv2.get_beatmap_scores(beatmap_id)
            queries = ''
            for l in scores:
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][l['ruleset_id']]
                queries += score_cls(l).generate_insert_query()
            await self.db.executeSQL(queries)
            self.logger.info(f"Processed {len(scores)} scores for beatmap {beatmap_id}.")

    async def fetch_modded_scores(self):
        self.logger.info("Fetching modded leaderboard scores...")
        
        # Get starting point from logger
        query = """
            SELECT beatmap_id
            FROM beatmapLive
            WHERE beatmap_id > (
                SELECT COALESCE(MAX(beatmap_id), 0)
                FROM logger
                WHERE logType = 'BEATMAPS' AND user_id = -1
            )
            ORDER BY beatmap_id
        """
        rs, elapsed = await self.db.executeQuery(query)

        mods_list = [["NM"], ["HD"], ["DT"], ["FL"], ["HR"], ["HD", "HR"], ["HD", "FL"], ["HD", "DT"], ["HR", "DT"], ["HR", "DT", "HD"], ["HR", "DT", "HD", "FL"]]
        total_beatmaps = len(rs)
        
        self.logger.info(f"Found {total_beatmaps} beatmaps to process with {len(mods_list)} mod combinations each")
        
        for idx, row in enumerate(rs, start=1):
            beatmap_id = row['beatmap_id'] if isinstance(row, dict) else row[0]
            self.logger.info(f"[{idx}/{total_beatmaps}] Processing beatmap {beatmap_id}...")
            
            total_scores_for_beatmap = 0
            
            # Accumulate scores across all mod combinations
            all_score_groups = {0: [], 1: [], 2: [], 3: []}
            
            # Process each mod combination
            for mod_combo in mods_list:
                mod_str = "+".join(mod_combo) if mod_combo != ["NM"] else "NM"
                self.logger.debug(f"[{idx}/{total_beatmaps}] Beatmap {beatmap_id}: Fetching {mod_str} scores...")
                
                scores = self.apiv2.get_beatmap_modded_scores(beatmap_id, mod_combo)
                
                if not scores:
                    self.logger.debug(f"[{idx}/{total_beatmaps}] Beatmap {beatmap_id}: No scores for {mod_str}")
                    continue
                
                # Group scores by ruleset
                for score_data in scores:
                    ruleset_id = score_data['ruleset_id']
                    all_score_groups[ruleset_id].append(score_data)
                
                total_scores_for_beatmap += len(scores)
                self.logger.debug(f"[{idx}/{total_beatmaps}] Beatmap {beatmap_id}: Found {len(scores)} {mod_str} scores")
            
            # Batch insert all scores for this beatmap
            for ruleset_id, ruleset_scores in all_score_groups.items():
                if not ruleset_scores:
                    continue
                    
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][ruleset_id]
                query = score_cls.get_insert_query_template()
                params_list = [score_cls(s).get_insert_params() for s in ruleset_scores]
                await self.db.executemany(query, params_list)
            
            # Update logger after each beatmap
            await self.db.executeParametrized(
                """INSERT INTO logger (logtype, user_id, beatmap_id) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (logtype, user_id) 
                DO UPDATE SET beatmap_id = EXCLUDED.beatmap_id""",
                'BEATMAPS', -1, beatmap_id
            )
            
            self.logger.info(f"[{idx}/{total_beatmaps}] Completed beatmap {beatmap_id}: {total_scores_for_beatmap} total scores across all mod combinations")
        
        self.logger.info(f"Modded leaderboard sync complete: {total_beatmaps} beatmaps processed")


    async def sync_registered_user_scores(self):
        query = "SELECT user_id FROM registrations WHERE is_synced = false ORDER BY registrationdate LIMIT 1"
        rs, elapsed = await self.db.executeQuery(query)
        
        if not rs:
            self.logger.info(f"All registered users are synced")
            return
        
        user_id = rs[0]['user_id'] if isinstance(rs[0], dict) else rs[0][0]

        all_beatmaps = []
        limit = 100
        offset = 0

        self.logger.info(f"Fetching all beatmaps for user {user_id}...")

        while True:
            page = self.apiv2.get_user_beatmaps_most_played(user_id, limit, offset)
            if not page:
                break
            all_beatmaps.extend(page)
            offset += limit
            self.logger.info(f"Fetched beatmaps up to {offset} for user {user_id}...")

        beatmap_ids = [b["beatmap_id"] for b in all_beatmaps]
        self.logger.info(f"Fetched {len(beatmap_ids)} total beatmaps for user {user_id}")

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
        existing_ids = {(row['beatmap_id'] if isinstance(row, dict) else row[0]) for row in rs}

        target_ids = sorted([bid for bid in beatmap_ids if bid in existing_ids])
        total = len(target_ids)
        self.logger.info(f"{total} beatmaps pending sync for user {user_id}")

        # Process beatmaps in batches
        batch_size = 100
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch_ids = target_ids[batch_start:batch_end]
            
            self.logger.info(f"Processing batch {batch_start//batch_size + 1}: beatmaps {batch_start+1}-{batch_end} of {total}")
            
            # Accumulate all scores in this batch
            score_groups = {0: [], 1: [], 2: [], 3: []}
            
            for idx, beatmap_id in enumerate(batch_ids, start=batch_start+1):
                self.logger.info(f"[{idx}/{total}] Fetching scores for beatmap {beatmap_id}...")
                
                scores = self.apiv2.get_beatmap_user_scores(beatmap_id, user_id)
                
                # Group scores by ruleset
                for score_data in scores:
                    ruleset_id = score_data['ruleset_id']
                    score_groups[ruleset_id].append(score_data)
            
            # Batch insert all scores from this batch of beatmaps
            total_scores = 0
            for ruleset_id, ruleset_scores in score_groups.items():
                if not ruleset_scores:
                    continue
                    
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][ruleset_id]
                query = score_cls.get_insert_query_template()
                params_list = [score_cls(s).get_insert_params() for s in ruleset_scores]
                await self.db.executemany(query, params_list)
                total_scores += len(ruleset_scores)
            
            # Update logger to the last beatmap in this batch
            last_beatmap_id = batch_ids[-1]
            await self.db.executeParametrized(
                """INSERT INTO logger (logtype, user_id, beatmap_id) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (logtype, user_id) 
                DO UPDATE SET beatmap_id = EXCLUDED.beatmap_id""",
                'FETCHER', user_id, last_beatmap_id
            )
            
            self.logger.info(f"Completed batch {batch_start//batch_size + 1}: Processed {len(batch_ids)} beatmaps, {total_scores} scores")

        # Mark user as synced
        await self.db.executeParametrized(
            "UPDATE registrations SET is_synced = true WHERE user_id = $1",
            user_id
        )

        self.logger.info(f"Sync complete for user {user_id} ({total} beatmaps processed).")

    async def fetch_recent_scores(self):
        self.logger.info("Fetching recent scores...")
        counter = 0
        while True:
            result, elapsed = await self.db.executeQuery(
                "SELECT cursor_string FROM cursorString ORDER BY dateInserted DESC LIMIT 1"
            )
            cursor_string = (result[0]['cursor_string'] if isinstance(result[0], dict) else result[0][0]) if result else None
            
            json_response = self.apiv2.get_scores(cursor_string)
            scores = json_response["scores"]
            cursor_string = json_response["cursor_string"]
            
            # Group scores by ruleset
            score_groups = {0: [], 1: [], 2: [], 3: []}
            for score_data in scores:
                ruleset_id = score_data['ruleset_id']
                score_groups[ruleset_id].append(score_data)
            
            # Batch insert each ruleset
            for ruleset_id, ruleset_scores in score_groups.items():
                if not ruleset_scores:
                    continue
                    
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][ruleset_id]
                
                # Get template query (same for all)
                query = score_cls.get_insert_query_template()
                
                # Build params list
                params_list = [score_cls(s).get_insert_params() for s in ruleset_scores]
                
                # Execute batch
                await self.db.executemany(query, params_list)
            
            # Insert cursor
            await self.db.executeParametrized(
                "INSERT INTO cursorString (cursor_string, dateInserted) VALUES ($1, $2)",
                cursor_string, datetime.now()
            )
            
            counter += 1
            self.logger.info(f"Processed {len(scores)} scores in batch {counter}.")
            if len(scores) < 100:
                break

    async def sync_newly_ranked_maps(self):
        self.logger.info("Syncing newly ranked maps...")
        
        queries = [
            ("SELECT DISTINCT beatmap_id FROM scoreosu s WHERE ended_at >= (NOW() - INTERVAL '1 day') EXCEPT SELECT beatmap_id FROM beatmaplive b", "Standard"),
            ("SELECT DISTINCT beatmap_id FROM scoretaiko s WHERE ended_at >= (NOW() - INTERVAL '1 day') EXCEPT SELECT beatmap_id FROM beatmaplive b", "Taiko"),
            ("SELECT DISTINCT beatmap_id FROM scorefruits s WHERE ended_at >= (NOW() - INTERVAL '1 day') EXCEPT SELECT beatmap_id FROM beatmaplive b", "Fruits"),
            ("SELECT DISTINCT beatmap_id FROM scoremania s WHERE ended_at >= (NOW() - INTERVAL '1 day') EXCEPT SELECT beatmap_id FROM beatmaplive b", "Mania")
        ]
        
        for query, mode in queries:
            batches = await self._generate_id_batches_from_query(query, 50)
            for batch in batches:
                beatmaps = self.apiv2.get_beatmaps(batch).get("beatmaps", [])
                queries_str = ''.join(Beatmap(l).generate_insert_query() for l in beatmaps)
                await self.db.executeSQL(queries_str)
            self.logger.info(f"{mode} maps synced")

        await self._execute_sql_file("update_beatmapLive.sql")
        await self._execute_sql_file("insert_beatmapHistory.sql")

    async def update_registered_users(self):
        self.logger.info("Adding new registered users...")

        query = "SELECT user_id from registrations EXCEPT SELECT user_id from userLive"
        rs, elapsed = await self.db.executeQuery(query)

        for row in rs:
            user_id = row['user_id'] if isinstance(row, dict) else row[0]
            self.logger.info(f"Registering user {user_id}")
            query = (f"CALL register_user({user_id})")
            await self.db.executeSQL(query)

        self.logger.info("Updating registered users...")
        query = "SELECT user_id FROM userLive"
        batches = await self._generate_id_batches_from_query(query, 50)
        
        for batch in batches:
            users = self.apiv2.get_users(batch).get("users", [])
            queries = ''.join(UserMaster(u.copy()).generate_insert_query() for u in users)
            if queries:
                await self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(users)} users.")

        await self._execute_sql_file("update_userLive.sql")
        await self._execute_sql_file("insert_userHistory.sql")

    async def update_ranked_maps(self):
        self.logger.info("Updating ranked beatmaps...")
        query = "SELECT beatmap_id FROM beatmapLive"
        batches = await self._generate_id_batches_from_query(query, 50)
        
        for batch in batches:
            beatmaps = self.apiv2.get_beatmaps(batch).get("beatmaps", [])
            queries = ''.join(Beatmap(l).generate_insert_query() for l in beatmaps)
            if queries:
                await self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(beatmaps)} beatmaps.")

    async def standard_loop(self):
        await self.fetch_beatmaps()
        await self.fetch_users()
        await self.fetch_recent_scores()
        await self.sync_newly_ranked_maps()
        await self.update_registered_users()
        await self.sync_registered_user_scores()

    # ---------------- ENTRYPOINT ----------------
    async def run(self):
        # Connect to database on startup
        await self.db.get_pool()
        await self.db.execSetupFiles()
        self.apiv2.refresh_token()
        
        options = {
            '0': self.standard_loop,
            '1': self.fetch_beatmaps,
            '2': self.fetch_users,
            '3': self.fetch_leaderboard_scores,
            '4': self.sync_registered_user_scores,
            '5': self.fetch_recent_scores,
            '6': self.sync_newly_ranked_maps,
            '7': self.update_registered_users,
            '8': self.update_ranked_maps,
            '9': self.fetch_beatmaps_packs,
            '10': self.fetch_modded_scores
        }

        while True:
            print(
                "\n0: Standard Loop\n1: Fetch beatmaps\n2: Fetch users\n3: Fetch leaderboard scores"
                "\n4: Fetch user beatmap scores\n5: Fetch recent scores\n6: Sync newly ranked maps"
                "\n7: Update registered users\n8: Update ranked maps\n9: Fetch beatmap packs" \
                "\n10: Fetch modded leaderboard scores\nQ: Quit"
            )
            choice = input("Choose an option: ").strip().lower()

            if choice == 'q':
                self.logger.info("Exiting application.")
                print("Exiting application.")
                await self.db.close()
                break

            func = options.get(choice)
            if not func:
                print("Invalid choice.")
                continue

            try:
                self.logger.info(f"Executing routine {choice}...")

                if choice == '0':
                    print("Starting standard loop (Ctrl+C to stop)...")
                    while True:
                        try:
                            await func()
                            self.logger.info("Standard loop iteration complete. Sleeping 1 min...")
                            await asyncio.sleep(60)
                        except KeyboardInterrupt:
                            print("\nStandard loop interrupted by user.")
                            self.logger.info("Standard loop manually interrupted.")
                            break
                else:
                    await func()
                    self.logger.info(f"Routine {choice} completed successfully.")

            except Exception as e:
                self.logger.exception(f"Error during routine {choice}: {e}")
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(OsuDataFetcher().run())