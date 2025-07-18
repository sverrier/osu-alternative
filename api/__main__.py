from util.jsonDataObject import jsonDataObject
from util.userExtendedHistory import UserExtendedHistory
from util.userExtended import UserExtended
from util.userMaster import UserMaster
from util.userHistory import UserHistory
from util.beatmap import Beatmap
from util.beatmapHistory import BeatmapHistory
from util.scoreOsu import ScoreOsu
from util.scoreFruits import ScoreFruits
from util.scoreMania import ScoreMania
from util.scoreTaiko import ScoreTaiko
from util.api import util_api
from util.db import db

import os
from datetime import datetime



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

def generate_id_batches_from_query(db, query, batch_size=50):
    """Fetch distinct beatmap_ids and generate batches."""
    
    rs = db.executeQuery(query)  # Fetch query result
    beatmap_ids = sorted(row[0] for row in rs)  # Extract and sort IDs

    # Generate batches
    for i in range(0, len(beatmap_ids), batch_size):
        yield beatmap_ids[i:i + batch_size]

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
print("3: Fetch leaderboard scores")
print("4: Fetch user beatmap scores")
print("5: Fetch recent scores")
print("6: Sync newly ranked maps")
print("7: Update registered users")


routine = input("Choose an option: ")

if routine == "1":
    maxid = db.executeQuery("select coalesce(max(id), 1) from beatmap;")[0][0]
    for batch in generate_id_batches(maxid, maxid + 2000000, batch_size=50):

        print(batch)
        finalquery = ""
        beatmaps = apiv2.get_beatmaps(batch)

        li = beatmaps.get("beatmaps", [])
        for l in li:
            b = Beatmap(l)

            bd = BeatmapHistory(l)

            finalquery = finalquery + b.generate_insert_query()
            finalquery = finalquery + bd.generate_insert_query()


        db.executeSQL(finalquery)

elif routine == "2":
    maxid = db.executeQuery("select coalesce(max(id), 1) from userMaster;")[0][0]
    for batch in generate_id_batches(maxid, maxid + 5000000, batch_size=50):

        print(batch)
        users = apiv2.get_users(batch)
        finalquery = ""

        li = users.get("users", [])
        for l in li:
            u = UserMaster(l.copy())
            
            finalquery = finalquery + u.generate_insert_query()

        db.executeSQL(finalquery)

elif routine == "3":

    maxid = db.executeQuery("""
        select
            coalesce(min(beatmap_id), 0 )
        from
            (
            select
                beatmap_id,
                count(*) as countscores
            from
                scoreOsu
            group by
                beatmap_id
            order by
                countscores) t
        where
            countscores < 25""")[0][0]

    rs = db.executeQuery("select id from beatmap where status = 'ranked' and id > " + str(maxid) + " order by id;")
    for row in rs:
        finalquery = ""
        beatmap_id = row[0]
        print(beatmap_id)
        scores = apiv2.get_beatmap_scores(beatmap_id)
        for l in scores:
            if l["ruleset_id"] == 0:
                s = ScoreOsu(l)
            elif l["ruleset_id"] == 1:
                s = ScoreTaiko(l)
            elif l["ruleset_id"] == 2:
                s = ScoreFruits(l)
            elif l["ruleset_id"] == 3:
                s = ScoreMania(l)

            finalquery = finalquery + s.generate_insert_query()

        db.executeSQL(finalquery)


elif routine == "4":

    user_id = input("Enter a user_id:")

    rs = db.executeQuery("select id from beatmap where beatmap.status = 'ranked'" + 
        " and beatmap.id > (select coalesce(max(beatmap_id), 0) from logger where logType = 'FETCHER' and user_id = " + user_id + ")"
        " except (select beatmap_id from scoreosu where user_id = " + user_id +
        " UNION " +
        "select beatmap_id from scoretaiko where user_id = " + user_id +
        " UNION " +
        " select beatmap_id from scorefruits where user_id = " + user_id +
        " UNION " +
        " select beatmap_id from scoremania where user_id = " + user_id + ")" +
        " order by ID;")

    for row in rs:
        finalquery = ""
        beatmap_id = row[0]
        print(beatmap_id)
        scores = apiv2.get_beatmap_user_scores(beatmap_id, user_id)
        for l in scores:
            if l["ruleset_id"] == 0:
                s = ScoreOsu(l)
            elif l["ruleset_id"] == 1:
                s = ScoreTaiko(l)
            elif l["ruleset_id"] == 2:
                s = ScoreFruits(l)
            elif l["ruleset_id"] == 3:
                s = ScoreMania(l)

            finalquery = finalquery + s.generate_insert_query()

        db.executeSQL(finalquery)

elif routine == "5": 

    counter = 0

    while True:

        result = db.executeQuery("SELECT cursor_string FROM cursorString ORDER BY dateInserted DESC LIMIT 1")
        cursor_string = result[0][0] if result else None        
        print(cursor_string)
        finalquery = ""

        json_response = apiv2.get_scores(cursor_string)
        scores = json_response["scores"]
        cursor_string = json_response["cursor_string"]
        for l in scores:
            if l["ruleset_id"] == 0:
                s = ScoreOsu(l)
            elif l["ruleset_id"] == 1:
                s = ScoreTaiko(l)
            elif l["ruleset_id"] == 2:
                s = ScoreFruits(l)
            elif l["ruleset_id"] == 3:
                s = ScoreMania(l)

            finalquery = finalquery + s.generate_insert_query()

        db.executeSQL(finalquery)

        counter = counter + 1

        sql = "INSERT INTO cursorString values ('" + cursor_string + "', '" + str(datetime.now()) +  "')"

        db.executeSQL(sql)

        print(counter)

elif routine == "6":

    query = """
        SELECT DISTINCT beatmap_id 
        FROM scoreosu s 
        EXCEPT 
        SELECT beatmap_id FROM beatmaplive b
    """
    
    for batch in generate_id_batches_from_query(db, query, batch_size=50):
        print(batch)
        finalquery = ""
        beatmaps = apiv2.get_beatmaps(batch)

        li = beatmaps.get("beatmaps", [])
        for l in li:
            b = Beatmap(l)

            bd = BeatmapHistory(l)

            finalquery = finalquery + b.generate_insert_query()
            finalquery = finalquery + bd.generate_insert_query()


        db.executeSQL(finalquery)

elif routine == "7":

    query = """
        SELECT user_id 
        FROM userLive
    """
    
    for batch in generate_id_batches_from_query(db, query, batch_size=50):
        print(batch)
        finalquery = ""
        users = apiv2.get_users(batch)

        li = users.get("users", [])
        for l in li:
            u = UserMaster(l.copy())
            
            finalquery = finalquery + u.generate_insert_query()
            
            u = UserHistory(l.copy())    
            
            finalquery = finalquery + u.generate_insert_query()
            
        json_response = apiv2.get_user(6245906)
        u = UserExtended(json_response.copy())
        with open(r'out\userExtended.txt', 'w', encoding="utf-8") as f:
            print(u, file=f)
        finalquery = finalquery + u.generate_insert_query()
        
        u = UserExtendedHistory(json_response.copy())
        finalquery = finalquery + u.generate_insert_query()



        db.executeSQL(finalquery)

else:

    b = apiv2.get_beatmaps(['4645011']).get("beatmaps", [])[0]

    print(b)

    with open(r'out\beatmap.txt', 'w', encoding="utf-8") as f:
        print(b, file=f)

    json_response = apiv2.get_user(6245906)
    u = UserExtended(json_response)

    with open(r'out\user.txt', 'w', encoding="utf-8") as f:
        print(u, file=f)

    with open(r'out\user_sql.txt', 'w', encoding="utf-8") as f:
        print(u.generate_insert_query(), file=f)

    daily_u = UserHistory(json_response)
    with open(r'out\userHistory.txt', 'w') as f:
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