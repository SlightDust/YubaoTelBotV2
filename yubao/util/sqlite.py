import sqlite3
import os
os.makedirs('./db', exist_ok=True)

class Sqlite:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    async def __aenter__(self):
        self.conn = sqlite3.connect(self.db_file)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def check_table_exists(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None

    def create_table(self, table_name, columns):
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    async def execute_sql(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        return cursor

    # def execute_sql(self, sql):
    #     cursor = self.conn.cursor()
    #     cursor.execute(sql)
    #     self.conn.commit()


# with Sqlite('db/example.db') as sqliter:
#     if not sqliter.check_table_exists("users"):
#         print("create")
#         sqliter.create_table("users","id INTEGER PRIMARY KEY, name TEXT")
#     sqliter.execute_sql('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)')
#     sqliter.execute_sql("INSERT INTO users (name) VALUES ('Alice')")
#     sqliter.execute_sql("INSERT INTO users (name) VALUES ('Bob')")
#     sqliter.execute_sql("INSERT INTO users (name) VALUES ('Charlie')")
#     cursor = sqliter.conn.cursor()
#     cursor.execute("SELECT * FROM users")
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)
#     cursor.close()

# with Sqlite('db/login_bonus.db') as sqliter:
#     if not sqliter.check_table_exists("login_bonus"):
#         sqliter.create_table("login_bonus","id INTEGER PRIMARY KEY, first_name TEXT, user_id TEXT, username TEXT, chat_id TEXT, chat_title TEXT, chat_type TEXT, date DATE")
#     sqliter.execute_sql(r"INSERT INTO login_bonus(first_name, user_id, username, chat_id, chat_title, chat_type, date) VALUES ('轻尘喵','123','pipichen_nya','132','测试1','supergroup','2023-06-11')")
    
