import os
import logging
import json
import time
from datetime import datetime
from cryptography.fernet import Fernet

from util.jsonDataObject import jsonDataObject
from util.userExtended import UserExtended
from util.userMaster import UserMaster
from util.beatmap import Beatmap
from util.scoreOsu import ScoreOsu
from util.scoreFruits import ScoreFruits
from util.scoreMania import ScoreMania
from util.scoreTaiko import ScoreTaiko
from util.api import util_api
from util.db import db


class OsuDataFetcher:
    def __init__(self, config_file="config.txt"):
        self._setup_logging()
        self.logger.info("Initializing OsuDataFetcher...")
        self.config_file = config_file
        self.config_values = self._load_or_create_config()
        self.db = db(self.config_values)
        self.db.execSetupFiles()
        self.apiv2 = util_api(self.config_values)
        self.apiv2.refresh_token()

    def _setup_logging(self):
        os.makedirs('logs', exist_ok=True)
        log_filename = f"logs/osu_fetcher_{datetime.now().strftime('%Y%m%d')}.log"

        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

        # Root logger setup
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

    def _generate_id_batches_from_query(self, query, batch_size=50):
        rs = self.db.executeQuery(query)
        ids = sorted(row[0] for row in rs)
        for i in range(0, len(ids), batch_size):
            yield ids[i:i + batch_size]

    def _execute_sql_file(self, filename: str, subdir: str = "sql/inserts"):
        """Executes a .sql script file and logs the result."""
        file_path = os.path.join(subdir, filename)
        self.logger.info(f"Executing SQL file: {file_path}")

        if not os.path.exists(file_path):
            self.logger.error(f"SQL file not found: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as sql_file:
                sql_script = sql_file.read()
            self.db.executeSQL(sql_script)
            self.db.commit()
            self.logger.info(f"Successfully executed: {filename}")
        except Exception as e:
            self.logger.exception(f"Error executing {filename}: {e}")


    # ---------------- ROUTINES ----------------
    def fetch_beatmaps(self):
        self.logger.info("Fetching beatmaps...")
        maxid = self.db.executeQuery("select coalesce(max(id), 1) from beatmap;")[0][0]
        for batch in self._generate_id_batches(maxid, maxid + 100000, 50):
            beatmaps = self.apiv2.get_beatmaps(batch).get("beatmaps", [])
            queries = ''.join(Beatmap(l).generate_insert_query() for l in beatmaps)
            if queries:
                self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(beatmaps)} beatmaps.")
            if len(beatmaps) == 0:
                break
        self.db.commit()

    def fetch_users(self):
        self.logger.info("Fetching users...")
        maxid = self.db.executeQuery("select coalesce(max(id), 1) from userMaster;")[0][0]
        for batch in self._generate_id_batches(maxid, maxid + 100000, 50):
            users = self.apiv2.get_users(batch).get("users", [])
            queries = ''.join(UserMaster(u.copy()).generate_insert_query() for u in users)
            self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(users)} users.")
            if len(users) < 25:
                break
        self.db.commit()

    def fetch_leaderboard_scores(self):
        self.logger.info("Fetching leaderboard scores...")
        rs = self.db.executeQuery("select beatmap_id from beatmaplive where beatmap_id > 3550000 order by beatmap_id;")
        for row in rs:
            beatmap_id = row[0]
            scores = self.apiv2.get_beatmap_scores(beatmap_id)
            queries = ''
            for l in scores:
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][l['ruleset_id']]
                queries += score_cls(l).generate_insert_query()
            self.db.executeSQL(queries)
            self.logger.info(f"Processed {len(scores)} scores for beatmap {beatmap_id}.")
        self.db.commit()

    def sync_registered_user_scores(self):
        query = "SELECT user_id FROM registrations WHERE is_synced = false ORDER BY registrationdate LIMIT 1"
        rs = self.db.executeQuery(query)
        user_id = rs[0][0]

        if user_id is None:
            self.logger.info(f"All registered users are synced")
            return

        all_beatmaps = []
        limit = 50
        offset = 0

        self.logger.info(f"Fetching all beatmaps for user {user_id}...")

        # Fetch all pages until empty
        while True:
            page = self.apiv2.get_user_beatmaps_most_played(user_id, limit, offset)
            if not page:
                break
            all_beatmaps.extend(page)
            offset += limit
            self.logger.info(f"Fetched beatmaps up to {offset} for user {user_id}...")

        beatmap_ids = [b["beatmap_id"] for b in all_beatmaps]
        self.logger.info(f"Fetched {len(beatmap_ids)} total beatmaps for user {user_id}")

        # Query DB for beatmaps to sync
        query = f"""
            SELECT beatmap_id
            FROM beatmapLive
            WHERE beatmap_id > (
                SELECT COALESCE(MAX(beatmap_id), 0)
                FROM logger
                WHERE logType = 'FETCHER' AND user_id = {user_id}
            )
        """
        rs = self.db.executeQuery(query)
        existing_ids = {row[0] for row in rs}

        # Cross-match and sort
        target_ids = sorted([bid for bid in beatmap_ids if bid in existing_ids])
        total = len(target_ids)
        self.logger.info(f"{total} beatmaps pending sync for user {user_id}")

        # Sync scores for matching beatmaps in ascending order
        for idx, beatmap_id in enumerate(target_ids, start=1):
            self.logger.info(f"[{idx}/{total}] Processing beatmap {beatmap_id}...")

            scores = self.apiv2.get_beatmap_user_scores(beatmap_id, user_id)
            queries = ""
            for s in scores:
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][s["ruleset_id"]]
                queries += score_cls(s).generate_insert_query()

            self.db.executeSQL(queries)
            log_query = (
                f"INSERT INTO logger VALUES ('FETCHER', {user_id}, {beatmap_id}) "
                "ON CONFLICT (logtype, user_id) DO UPDATE SET beatmap_id = EXCLUDED.beatmap_id"
            )
            self.db.executeSQL(log_query)

            self.logger.info(f"[{idx}/{total}] - Processed {len(scores)} scores for beatmap {beatmap_id}")

        query = (f"UPDATE registrations SET is_synced = true where user_id = {user_id}")

        self.db.commit()
        self.logger.info(f"✅ Sync complete for user {user_id} ({total} beatmaps processed).")


    def fetch_recent_scores(self):
        self.logger.info("Fetching recent scores...")
        counter = 0
        while True:
            result = self.db.executeQuery("SELECT cursor_string FROM cursorString ORDER BY dateInserted DESC LIMIT 1")
            cursor_string = result[0][0] if result else None
            json_response = self.apiv2.get_scores(cursor_string)
            scores = json_response["scores"]
            cursor_string = json_response["cursor_string"]
            queries = ''
            for l in scores:
                score_cls = [ScoreOsu, ScoreTaiko, ScoreFruits, ScoreMania][l['ruleset_id']]
                queries += score_cls(l).generate_insert_query()
            self.db.executeSQL(queries)
            self.db.executeSQL(f"INSERT INTO cursorString values ('{cursor_string}', '{datetime.now()}')")
            counter += 1
            self.logger.info(f"Processed {len(scores)} scores in batch {counter}.")
            if len(scores) < 25:
                break

    def sync_newly_ranked_maps(self):
        self.logger.info("Syncing newly ranked maps...")
        query = "SELECT DISTINCT beatmap_id FROM scoreosu s WHERE ended_at >= (NOW() - INTERVAL '1 day') EXCEPT SELECT beatmap_id FROM beatmaplive b"
        for batch in self._generate_id_batches_from_query(query, 50):
            beatmaps = self.apiv2.get_beatmaps(batch).get("beatmaps", [])
            queries = ''.join(Beatmap(l).generate_insert_query() for l in beatmaps)
            self.db.executeSQL(queries)
        self.db.commit()

        self._execute_sql_file("update_beatmapLive.sql")
        self._execute_sql_file("insert_beatmapHistory.sql")

    def update_registered_users(self):
        self.logger.info("Updating registered users...")
        query = "SELECT user_id FROM userLive"
        for batch in self._generate_id_batches_from_query(query, 50):
            users = self.apiv2.get_users(batch).get("users", [])
            queries = ''.join(UserMaster(u.copy()).generate_insert_query() for u in users)
            if queries:
                self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(users)} users.")
        self.db.commit()

        self._execute_sql_file("update_userLive.sql")
        self._execute_sql_file("insert_userHistory.sql")

    def update_ranked_maps(self):
        self.logger.info("Updating ranked beatmaps...")
        query = "SELECT beatmap_id FROM beatmapLive"
        for batch in self._generate_id_batches_from_query(query, 50):
            beatmaps = self.apiv2.get_beatmaps(batch).get("beatmaps", [])
            queries = ''.join(Beatmap(l).generate_insert_query() for l in beatmaps)
            if queries:
                self.db.executeSQL(queries)
            self.logger.info(f"Processed batch {batch[0]}-{batch[-1]} with {len(beatmaps)} beatmaps.")
        self.db.commit()

    def standard_loop(self):
        self.fetch_beatmaps()
        self.fetch_users()
        self.fetch_recent_scores()
        self.sync_newly_ranked_maps()
        self.update_registered_users()
        self.sync_registered_user_scores()
    # ---------------- ENTRYPOINT ----------------
    def run(self):
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
        }

        while True:
            print(
                "\n0: Standard Loop\n1: Fetch beatmaps\n2: Fetch users\n3: Fetch leaderboard scores"
                "\n4: Fetch user beatmap scores\n5: Fetch recent scores\n6: Sync newly ranked maps"
                "\n7: Update registered users\n8: Update ranked maps\nQ: Quit"
            )
            choice = input("Choose an option: ").strip().lower()

            if choice == 'q':
                self.logger.info("Exiting application.")
                print("Exiting application.")
                break

            func = options.get(choice)
            if not func:
                print("Invalid choice.")
                continue

            try:
                self.logger.info(f"Executing routine {choice}...")

                if choice == '0':
                    print("🚀 Starting standard loop (Ctrl+C to stop)...")
                    while True:
                        try:
                            func()  # run standard_loop()
                            self.logger.info("Standard loop iteration complete. Sleeping 5 min...")
                            time.sleep(60)  # adjust interval as needed
                        except KeyboardInterrupt:
                            print("\n⏹️  Standard loop interrupted by user.")
                            self.logger.info("Standard loop manually interrupted.")
                            break

                else:
                    func()
                    self.logger.info(f"Routine {choice} completed successfully.")

            except Exception as e:
                self.logger.exception(f"Error during routine {choice}: {e}")
                print(f"Error: {e}")



if __name__ == "__main__":
    OsuDataFetcher().run()
