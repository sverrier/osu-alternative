import psycopg
import os

class db:
    def __init__(self, config):
        self.dbname = config["DBNAME"]
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.port = config["PORT"]

    def execSetupFiles(self):
         for filename in sorted(os.listdir("sql")):
            if filename.endswith(".sql"):
                file_path = os.path.join("sql", filename)
                print(f"Executing {file_path}...")
                
                with open(file_path, 'r', encoding='utf-8') as sql_file:
                    sql_script = sql_file.read()
                    try:
                        self.executeSQL(sql_script)
                        print(f"Successfully executed {filename}")
                    except Exception as e:
                        print(f"Error executing {filename}: {e}")

    def executeSQL(self, query):
        with psycopg.connect(dbname = self.dbname, port=self.port, user = self.username, password = self.password, client_encoding="UTF8") as conn:
            with conn.cursor() as cur:
                with open(r'out\debug.txt', 'w', encoding='utf-8') as f:
                    print(query, file=f)
                cur.execute(query)
                conn.commit()   

    def executeQuery(self, query):
        with psycopg.connect(dbname = self.dbname, port=self.port, user = self.username, password = self.password, client_encoding="UTF8") as conn:
            with conn.cursor() as cur:
                with open(r'out\debug.txt', 'w', encoding='utf-8') as f:
                    print(query, file=f)
                cur.execute(query)
                rs = cur.fetchall()
                print(rs)
                return rs