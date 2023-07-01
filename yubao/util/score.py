import sqlite3

from aiotg import Chat

from yubao import extendChat
from yubao.util.sqlite import Sqlite
from yubao.config import Config
config = Config().read_config()

dbfile = dbfile = config['score_db']

class Score():
    def __init__(self, chat:Chat) -> None:
        with Sqlite(dbfile) as sqliter:
            if not sqliter.check_table_exists("score"):
                sqliter.create_table("score","user_id TEXT PRIMARY KEY, first_name TEXT, username TEXT, score INTEGER")
        chat.__class__ = extendChat
        self.uid = chat.get_uid()
        self.first_name = chat.get_first_name()
        self.username = chat.get_username()
        pass

    async def total_score(self):
        with Sqlite(dbfile) as sqliter:
            cursor = await sqliter.execute_sql(f"SELECT * FROM score WHERE user_id='{self.uid}'")
            row = cursor.fetchone()
            if row is None:
                return 0
            else:
                return row[3]
            
    async def _exist(self):
        with Sqlite(dbfile) as sqliter:
            cursor = await sqliter.execute_sql(f"SELECT * FROM score WHERE user_id='{self.uid}'")
            row = cursor.fetchone()
            return False if row is None else True


    async def add_score(self, score:int):

        async with Sqlite(dbfile) as sqliter:
            if await self._exist():  # 存在这个人的记录，更新分数
                with Sqlite(dbfile) as sqliter:
                    cursor = await sqliter.execute_sql(f"SELECT * FROM score WHERE user_id='{self.uid}'")
                    old_score = cursor.fetchone()[3]
                    new_score = old_score + score
                    cursor1 = await sqliter.execute_sql(f"UPDATE score SET score={new_score}, first_name='{self.first_name}', username='{self.username}' WHERE user_id='{self.uid}'")
            else:  # 不存在记录，插入分数
                await sqliter.execute_sql(f"INSERT INTO score (user_id, first_name, username, score) VALUES ('{self.uid}','{self.first_name}','{self.username}','{score}')")
        return await self.total_score()