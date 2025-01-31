import user
import api

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

apiv2 = api.util_api(config_values)
apiv2.refresh_token()

print("Go")

u = apiv2.get_user(6245906)

with open('user.txt', 'w') as f:
    print(u, file=f)

s = apiv2.get_beatmap_scores(714001)

with open('beatmap_scores.txt', 'w') as f:
    print(s, file=f)

b = apiv2.get_beatmap(714001)

with open('beatmap.txt', 'w') as f:
    print(b, file=f)

with open('score_sql.txt', 'w') as f:
    print(s.generate_insert_query(), file=f)

with open('user_sql.txt', 'w') as f:
    print(u.generate_insert_query(), file=f)

with open('beatmap_sql.txt', 'w') as f:
    print(b.generate_insert_query(), file=f)