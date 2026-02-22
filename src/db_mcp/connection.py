from __future__ import annotations

import struct
import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import aiomysql
import asyncpg
import motor.motor_asyncio
from pymysql.constants import COMMAND

from db_mcp.config import Config

# MySQL COM_SET_OPTION argument to turn off multi-statement support.
_MULTI_STATEMENTS_OFF = struct.pack("<H", 1)


class Connection:
    def __init__(self, config: Config) -> None:
        self.config = config
        self._pool: aiomysql.Pool | None = None
        self._pg_pool: asyncpg.Pool | None = None
        self._mongo_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        self._mongo_db: Any = None
        # Track connections where multi-statements have been disabled.
        self._safe_conns: set[int] = set()

    @property
    def pool(self) -> aiomysql.Pool:
        assert self._pool is not None, "MySQL pool not initialized"
        return self._pool

    @property
    def pg_pool(self) -> asyncpg.Pool:
        assert self._pg_pool is not None, "PostgreSQL pool not initialized"
        return self._pg_pool

    @property
    def db(self) -> Any:
        assert self._mongo_db is not None, "MongoDB database not initialized"
        return self._mongo_db

    async def connect(self) -> None:
        if self.config.is_mysql:
            await self._connect_mysql()
        elif self.config.is_postgresql:
            await self._connect_postgresql()
        else:
            await self._connect_mongodb()

    # ------------------------------------------------------------------
    # MySQL helpers
    # ------------------------------------------------------------------

    async def _disable_multi_statements(self, conn: aiomysql.Connection) -> None:
        """Disable multi-statement query support on *conn*.

        aiomysql unconditionally sets CLIENT_MULTI_STATEMENTS during the
        handshake.  We send COM_SET_OPTION(MYSQL_OPTION_MULTI_STATEMENTS_OFF)
        to instruct the server to reject any query containing multiple
        statements, closing the protocol-level loophole.
        """
        conn_id = id(conn)
        if conn_id in self._safe_conns:
            return
        await conn._execute_command(COMMAND.COM_SET_OPTION, _MULTI_STATEMENTS_OFF)
        pkt = await conn._read_packet()
        if not pkt.is_ok_packet() and not pkt.is_eof_packet():
            raise RuntimeError("Failed to disable multi-statement queries")
        self._safe_conns.add(conn_id)

    @asynccontextmanager
    async def acquire_mysql(self) -> AsyncIterator[aiomysql.Connection]:
        """Acquire a MySQL connection with multi-statements disabled."""
        async with self.pool.acquire() as conn:
            await self._disable_multi_statements(conn)
            yield conn

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
        # Verify connectivity and disable multi-statement support.
        async with self.acquire_mysql() as conn:
            await conn.ping()
        print("[db-mcp] MySQL connected.", file=sys.stderr)

    # ------------------------------------------------------------------
    # PostgreSQL helpers
    # ------------------------------------------------------------------

    @asynccontextmanager
    async def acquire_pg(self) -> AsyncIterator[asyncpg.Connection]:
        """Acquire a PostgreSQL connection from the pool."""
        async with self.pg_pool.acquire() as conn:
            yield conn

    async def _connect_postgresql(self) -> None:
        print(
            f"[db-mcp] Connecting to PostgreSQL {self.config.db_host}:{self.config.db_port}"
            f"/{self.config.db_database} ({self.config.db_mode})...",
            file=sys.stderr,
        )
        self._pg_pool = await asyncpg.create_pool(
            host=self.config.db_host,
            port=self.config.db_port,
            user=self.config.db_user,
            password=self.config.db_password,
            database=self.config.db_database,
        )
        # Verify connectivity
        async with self.acquire_pg() as conn:
            await conn.fetchval("SELECT 1")
        print("[db-mcp] PostgreSQL connected.", file=sys.stderr)

    # ------------------------------------------------------------------
    # MongoDB helpers
    # ------------------------------------------------------------------

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
        if self._pg_pool is not None:
            await self._pg_pool.close()
            print("[db-mcp] PostgreSQL disconnected.", file=sys.stderr)
        if self._mongo_client is not None:
            self._mongo_client.close()
            print("[db-mcp] MongoDB disconnected.", file=sys.stderr)
