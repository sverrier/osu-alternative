import psycopg

class util_api:
    def __init__(self, config):
        self.dbname = config["DBNAME"]
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
