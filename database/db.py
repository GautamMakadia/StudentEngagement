from http.client import HTTPException

import asyncpg


from config import get_setting, Settings

setting: Settings = get_setting()

tables = {
    "users": "users",
    "session": "session",
    "venue": "venue",
}

class Postgres:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=setting.DB_USER,
            password=setting.DB_PASS,
            host="127.0.0.1",
            database=setting.DB_NAME,
            min_size=1,
            max_size=100
        )

    async def disconnect(self):
        await self.pool.close()


database = Postgres()