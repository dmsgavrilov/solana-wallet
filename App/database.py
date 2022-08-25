import asyncpg

import config


class DB:

    def __init__(self):
        self.__pool = None
        self.__closed = True

    async def create_pool(self):
        if self.__closed:
            self.__pool = await asyncpg.create_pool(config.DATABASE_URI)
            self.__closed = False

    async def execute(self, query, *args):
        await self.create_pool()

        async with self.__pool.acquire() as connection:
            await connection.execute(query, *args)

    async def fetch_many(self, query, *args):
        await self.create_pool()

        async with self.__pool.acquire(timeout=20) as connection:
            result = await connection.fetch(query, *args)
            result = [dict(row) for row in result]
            return result

    async def fetch_row(self, query, *args):
        await self.create_pool()

        async with self.__pool.acquire(timeout=20) as connection:
            result = await connection.fetchrow(query, *args)
            return dict(result)

    async def fetch_value(self, query, *args):
        await self.create_pool()

        async with self.__pool.acquire(timeout=20) as connection:
            result = await connection.fetchval(query, *args)
            return result


db = DB()
