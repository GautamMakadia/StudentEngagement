import asyncpg
from config import env

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
            user=env.DB_USER,
            password=env.DB_PASS,
            host="127.0.0.1",
            database=env.DB_NAME,
            min_size=1,
            max_size=100
        )

    async def disconnect(self):
        await self.pool.close()


database = Postgres()