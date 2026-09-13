# osualternative/util/db.py
import asyncpg
import os
import time
import logging
import asyncio

class db:
    def __init__(self, config, logger):
        self.dbname = config["DBNAME"]
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.port = config["PORT"]
        self.host = config.get("HOST", "localhost")
        self.pool = None
        self.logger = logger

    async def get_pool(self, timeout=300):
        """Ensure asyncpg pool exists."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                database=self.dbname,
                user=self.username,
                password=self.password,
                min_size=1,
                max_size=10,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=timeout,
            )
            self.logger.info("Database pool created")
        return self.pool

    async def runMigrations(self, migrations_dir="sql/migrations"):
        """Apply pending dated migration files from sql/migrations.

        Each migration is recorded in a `schema_migrations` table after it
        succeeds, so a file runs exactly once against the database instead of
        re-executing every SQL file on every launch. Only files whose name is
        not yet recorded in schema_migrations are applied (in sorted filename
        order, so the YYYYMMDD prefix controls run order).

        To add a schema change, drop a new dated file in sql/migrations, e.g.
        "20251125 - add column", and it will be applied on the next launch.
        Do not edit a migration that has already been applied; add a new one.
        """
        pool = await self.get_pool()

        # Ensure the tracking table exists before checking what has run.
        await self.executeSQL(
            "CREATE TABLE IF NOT EXISTS public.schema_migrations ("
            "  filename   TEXT PRIMARY KEY,"
            "  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            ")"
        )

        applied = set()
        for row in await pool.fetch("SELECT filename FROM public.schema_migrations"):
            applied.add(row["filename"])

        applied_count = 0
        for filename in sorted(os.listdir(migrations_dir)):
            if not filename.endswith(".sql"):
                continue
            if filename in applied:
                continue

            path = os.path.join(migrations_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()

            self.logger.info(f"Applying migration {filename}...")
            await self.executeSQL(sql)
            await pool.execute(
                "INSERT INTO public.schema_migrations (filename) VALUES ($1)"
                " ON CONFLICT (filename) DO NOTHING",
                filename,
            )
            applied_count += 1
            self.logger.info(f"Applied migration {filename}")

        if applied_count:
            self.logger.info(f"Applied {applied_count} new migration(s).")
        else:
            self.logger.info("No new migrations to apply.")

    async def executeSQL(self, query):
        """Execute SQL statements (INSERT, UPDATE, DELETE, CREATE)."""
        pool = await self.get_pool()
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    result = await conn.execute(query)
            return result
        except Exception as e:
            self.logger.error(f"Error executing sql: {query} — {e}")
            raise

    async def executeBatch(self, queries):
        """Execute multiple SQL statements in a single transaction."""
        pool = await self.get_pool()
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    for q in queries:
                        await conn.execute(q)
            self.logger.info(f"Batch executed {len(queries)} queries")
        except Exception as e:
            self.logger.error(f"Error executing batch: {e}")
            raise

    async def executeQuery(self, query):
        """Execute SELECT query and return (result, elapsed_time_seconds)."""
        pool = await self.get_pool()
        start_time = time.perf_counter()
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    result = await conn.fetch(query)
            elapsed = time.perf_counter() - start_time
            return result, elapsed
        except Exception as e:
            self.logger.error(f"Error executing query: {query} — {e}")
            raise

    async def executeParametrized(self, query, *params):
        """Execute parameterized INSERT/UPDATE/DELETE."""
        pool = await self.get_pool(timeout=240)
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(query, *params)
            self.logger.debug(f"Executed parameterized query")
        except Exception as e:
            self.logger.error(f"Error executing query: {query} — {e}")
            raise

    async def fetchParametrized(self, query, *params):
        """Execute parameterized SELECT and return results."""
        pool = await self.get_pool()
        try:
            async with pool.acquire() as conn:
                result = await conn.fetch(query, *params)
            return result
        except Exception as e:
            self.logger.error(f"Error executing query: {query} — {e}")
            raise
    
    async def executemany(self, query, params_list):
        """Execute parameterized query multiple times efficiently."""
        if not params_list:
            self.logger.debug("No parameters to insert")
            return
        pool = await self.get_pool()
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.executemany(query, params_list)
            self.logger.info(f"Batch inserted {len(params_list)} records")
        except Exception as e:
            self.logger.error(f"Error in executemany: {e}")
            raise

    async def close(self):
        """Gracefully close the database pool."""
        if self.pool:
            await self.pool.close()
            self.logger.info("Database pool closed")
            self.pool = None
