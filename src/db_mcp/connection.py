from __future__ import annotations

import sys
from typing import Any

import aiomysql
import motor.motor_asyncio

from db_mcp.config import Config


class Connection:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._pool: aiomysql.Pool | None = None
        self._mongo_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        self._mongo_db: Any = None

    @property
    def pool(self) -> aiomysql.Pool:
        assert self._pool is not None, "MySQL pool not initialized"
        return self._pool

    @property
    def db(self) -> Any:
        assert self._mongo_db is not None, "MongoDB database not initialized"
        return self._mongo_db

    async def connect(self) -> None:
        if self.config.is_mysql:
            await self._connect_mysql()
        else:
            await self._connect_mongodb()

    async def _connect_mysql(self) -> None:
        print(
            f"[db-mcp] Connecting to MySQL {self.config.db_host}:{self.config.db_port}"
            f"/{self.config.db_database} ({self.config.db_mode})...",
            file=sys.stderr,
        )
        self._pool = await aiomysql.create_pool(
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_user,
            password=self.config.db_password,
            db=self.config.db_database,
            autocommit=True,
        )
        # Verify connectivity
        async with self._pool.acquire() as conn:
            await conn.ping()
        print("[db-mcp] MySQL connected.", file=sys.stderr)

    async def _connect_mongodb(self) -> None:
        print(
            f"[db-mcp] Connecting to MongoDB {self.config.db_database} "
            f"({self.config.db_mode})...",
            file=sys.stderr,
        )
        self._mongo_client = motor.motor_asyncio.AsyncIOMotorClient(self.config.db_url)
        self._mongo_db = self._mongo_client[self.config.db_database]
        # Verify connectivity
        await self._mongo_db.command("ping")
        print("[db-mcp] MongoDB connected.", file=sys.stderr)

    async def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
            print("[db-mcp] MySQL disconnected.", file=sys.stderr)
        if self._mongo_client is not None:
            self._mongo_client.close()
            print("[db-mcp] MongoDB disconnected.", file=sys.stderr)
