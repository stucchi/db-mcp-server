from __future__ import annotations

from typing import Any

import aiomysql

from db_mcp.config import Config
from db_mcp.connection import Connection
from db_mcp.validation import validate_read_only_query


async def query_mysql(conn: Connection, config: Config, sql: str) -> list[dict]:
    if config.is_read_only:
        validate_read_only_query(sql)

    async with conn.acquire_mysql() as c:
        async with c.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql)
            rows = await cur.fetchall()
    return rows


async def query_pg(conn: Connection, config: Config, sql: str) -> list[dict]:
    if config.is_read_only:
        validate_read_only_query(sql)

    async with conn.acquire_pg() as c:
        rows = await c.fetch(sql)
        return [dict(r) for r in rows]


async def query_mongodb(
    conn: Connection,
    collection: str,
    filter_obj: dict[str, Any] | None = None,
    limit: int = 100,
) -> list[dict]:
    if filter_obj is None:
        filter_obj = {}
    capped = min(limit, 1000)
    results = await conn.db[collection].find(filter_obj).limit(capped).to_list(capped)
    return results
