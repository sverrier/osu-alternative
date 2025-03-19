import csv
import asyncpg
import asyncio
import os


class Database:
    def __init__(self, port, database, user, password):
        self.pool = None
        self.port = port
        self.database = database
        self.user = user 
        self.password = password

    async def get_pool(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                min_size=1,
                max_size=10,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=120,
            )

        return self.pool

    async def execute_query(self, query, *params):
        pool = await self.get_pool()

        try:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetch(query, *params)
                    return result
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Query timed out")

    async def export_to_csv(self, query, filename, *params):
        pool = await self.get_pool()

        try:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetch(query, *params)
                    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.writer(csvfile)
                        # Write headers
                        writer.writerow([desc for desc in result[0].keys()])
                        # Write rows
                        for row in result:
                            writer.writerow(row)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError("Query timed out")

    async def close(self):
        if self.pool is not None:
            await self.pool.close()
