import psycopg
import os

class db:
    def __init__(self, config):
        self.dbname = config["DBNAME"]
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.port = config["PORT"]
        self.conn = psycopg.connect(
            dbname=self.dbname, 
            port=self.port, 
            user=self.username, 
            password=self.password, 
            client_encoding="UTF8"
        )
        self.conn.autocommit = False  # ✅ Manually commit for batching
        self.cur = self.conn.cursor()
        self.counter = 0

    def execSetupFiles(self):
         for filename in sorted(os.listdir("sql\creates")):
            if filename.endswith(".sql"):
                file_path = os.path.join("sql\creates", filename)
                print(f"Executing {file_path}...")
                
                with open(file_path, 'r', encoding='utf-8') as sql_file:
                    sql_script = sql_file.read()
                    try:
                        self.executeSQL(sql_script)
                        print(f"Successfully executed {filename}")
                    except Exception as e:
                        print(f"Error executing {filename}: {e}")

    def executeSQL(self, query):
        try:
            with open(r'out\debug.txt', 'w', encoding='utf-8') as f:
                print(query, file=f)

            self.cur.execute(query)
            self.counter = self.counter + 1
            if self.counter % 10 == 0:
                self.conn.commit()  # ✅ Commit if successful

        except Exception as e:
            self.conn.rollback()  # ✅ Rollback transaction to recover
            print(f"Error executing query: {e}")

    def executeQuery(self, query):
        with open(r'out\debug.txt', 'w', encoding='utf-8') as f:
            print(query, file=f)
        
        self.cur.execute(query)
        return self.cur.fetchall()  # ✅ Returns query result

    def close(self):
        """ Gracefully close the database connection """
        self.cur.close()
        self.conn.close()