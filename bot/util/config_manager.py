# bot/utils/config_manager.py
import os

def create_config_file(file_name):
    print("Config file not found. Let's create one.")
    config = {}
    config["DBNAME"] = input("Enter the DBNAME (Postgres DB name): ").strip()
    config["USERNAME"] = input("Enter the USERNAME (Postgres username): ").strip()
    config["PASSWORD"] = input("Enter the PASSWORD (Postgres password): ").strip()
    config["PORT"] = input("Enter the PORT: ").strip()
    config["DISCORD_TOKEN"] = input("Enter the DISCORD_TOKEN: ").strip()

    with open(file_name, "w") as f:
        for k, v in config.items():
            f.write(f"[{k}]={v}\n")
    print(f"Configuration file '{file_name}' created successfully.")
    return config

def read_config_file(file_name):
    config = {}
    with open(file_name, "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                config[key.strip("[]")] = val
    return config

def load_config(file_name):
    if os.path.exists(file_name):
        return read_config_file(file_name)
    return create_config_file(file_name)