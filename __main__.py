from osualt.userHistory import UserHistory
from osualt.userExtended import UserExtended
from osualt.userOsu import UserOsu
from osualt.userTaiko import UserTaiko
from osualt.userFruits import UserFruits
from osualt.userMania import UserMania
from osualt.beatmap import Beatmap
from osualt.beatmapHistory import BeatmapHistory
from osualt.scoreOsu import ScoreOsu
from osualt.api import util_api
from osualt.db import db

import os



# File name
config_file = "config.txt"

# Function to create the configuration file
def create_config_file(file_name):
    print("Config file not found. Let's create one.")
    config = {}
    config["KEY"] = input("Enter the KEY value (This is your client_secret for the osu api): ").strip()
    config["CLIENT"] = input("Enter the CLIENT ID value (This is your client_public for the osu api): ").strip()
    config["DELAY"] = input("Enter the DELAY value (Values in milliseconds e.g 1000): ").strip()
    config["DBNAME"] = input("Enter the DBNAME value (Postgres DB name): ").strip()
    config["USERNAME"] = input("Enter the USERNAME value (Postgres username): ").strip()
    config["PASSWORD"] = input("Enter the PASSWORD value (Postgres password): ").strip()
    config["PORT"] = input("Enter the PORT value: ").strip()

    
    # Write to file
    with open(file_name, "w") as file:
        for key, value in config.items():
            file.write(f"[{key}]={value}\n")
    print(f"Configuration file '{file_name}' created successfully.")
    return config

# Function to read the configuration file
def read_config_file(file_name):
    config = {}
    with open(file_name, "r") as file:
        for line in file:
            # Parse lines of the format [KEY]=value
            if "=" in line:
                key, value = line.strip().split("=", 1)
                key = key.strip("[]")  # Remove square brackets
                config[key] = value
    return config

def generate_id_batches(start_id, end_id, batch_size=50):
    """Generate batches of IDs in ascending order."""
    for i in range(start_id, end_id, batch_size):
        yield list(range(i, min(i + batch_size, end_id)))

# Main logic
if os.path.exists(config_file):
    print(f"Found '{config_file}'. Reading configuration...")
    config_values = read_config_file(config_file)
else:
    config_values = create_config_file(config_file)

# Print the stored configuration
print("\nConfiguration values:")
for key, value in config_values.items():
    print(f"{key} = {value}")

db = db(config_values)

db.execSetupFiles()

apiv2 = util_api(config_values)
apiv2.refresh_token()

print("1: Fetch beatmaps")
print("2: Fetch users")

routine = input("Choose an option: ")

if routine == "1":
    for batch in generate_id_batches(4887842, 4888892, batch_size=50):

        beatmaps = apiv2.get_beatmaps(batch)

        li = beatmaps.get("beatmaps", [])
        for l in li:
            b = Beatmap(l)
            with open(r'out\beatmap.txt', 'w', encoding='utf-8') as f:
                print(b, file=f)

            bd = BeatmapHistory(l)

            with open(r'out\beatmapHistory.txt', 'w', encoding='utf-8') as f:
                print(bd, file=f)

            db.executeSQL(b.generate_insert_query())

            db.executeSQL(bd.generate_insert_query())

elif routine == "2":
    for batch in generate_id_batches(6245906, 6245956, batch_size=50):

        users = apiv2.get_users(batch)

        li = users.get("users", [])
        for l in li:
            u = UserOsu(l.copy())
            with open(r'out\userOsu.txt', 'w', encoding='utf-8') as f:
                print(u, file=f)

            with open(r'out\userOsuSQL.txt', 'w', encoding='utf-8') as f:
                print(u.generate_insert_query(), file=f)
            
            db.executeSQL(u.generate_insert_query())

            u = UserTaiko(l.copy())
            with open(r'out\userTaiko.txt', 'w', encoding='utf-8') as f:
                print(u, file=f)

            with open(r'out\userTaikoSQL.txt', 'w', encoding='utf-8') as f:
                print(u.generate_insert_query(), file=f)
 
            db.executeSQL(u.generate_insert_query())

            u = UserFruits(l.copy())
            with open(r'out\userFruits.txt', 'w', encoding='utf-8') as f:
                print(u, file=f)

            with open(r'out\userFruitsSQL.txt', 'w', encoding='utf-8') as f:
                print(u.generate_insert_query(), file=f)
 
            db.executeSQL(u.generate_insert_query())

            u = UserMania(l.copy())
            with open(r'out\userMania.txt', 'w', encoding='utf-8') as f:
                print(u, file=f)

            with open(r'out\userManiaSQL.txt', 'w', encoding='utf-8') as f:
                print(u.generate_insert_query(), file=f)
 
            db.executeSQL(u.generate_insert_query())

else:

    u = apiv2.get_user(6245906)

    with open(r'out\user.txt', 'w') as f:
        print(u, file=f)

    with open(r'out\user_sql.txt', 'w') as f:
        print(u.generate_insert_query(), file=f)

    daily_u = UserHistory(u.jsonObject)
    with open(r'out\user.txt', 'w') as f:
        print(daily_u, file=f)

    with open(r'out\user_sql.txt', 'w') as f:
        print(daily_u.generate_insert_query(), file=f)


    s = apiv2.get_beatmap_scores(4796487)

    with open(r'out\std_score.txt', 'w') as f:
        print(s, file=f)

    with open(r'out\std_score_sql.txt', 'w') as f:
        print(s.generate_insert_query(), file=f)

    db.executeSQL(s.generate_insert_query())
    db.executeSQL(u.generate_insert_query())

    s = apiv2.get_beatmap_scores(4254301)

    with open(r'out\ctb_score.txt', 'w') as f:
        print(s, file=f)

    with open(r'out\ctb_score_sql.txt', 'w') as f:
        print(s.generate_insert_query(), file=f)

    db.executeSQL(s.generate_insert_query())

    s = apiv2.get_beatmap_scores(4097226)

    with open(r'out\mania_score.txt', 'w') as f:
        print(s, file=f)

    with open(r'out\mania_score_sql.txt', 'w') as f:
        print(s.generate_insert_query(), file=f)

    db.executeSQL(s.generate_insert_query())

    s = apiv2.get_beatmap_scores(4941880)

    with open(r'out\taiko_score.txt', 'w') as f:
        print(s, file=f)

    with open(r'out\taiko_score_sql.txt', 'w') as f:
        print(s.generate_insert_query(), file=f)

    db.executeSQL(s.generate_insert_query())