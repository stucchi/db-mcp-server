from __future__ import annotations

import aiomysql

from db_mcp.connection import Connection
from db_mcp.validation import sanitize_table_name


async def describe_mysql(conn: Connection, table: str) -> list[dict]:
    safe_name = sanitize_table_name(table)
    async with conn.acquire_mysql() as c:
        async with c.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(f"DESCRIBE {safe_name}")
            return await cur.fetchall()


async def describe_pg(conn: Connection, table: str) -> list[dict]:
    safe_name = sanitize_table_name(table)
    async with conn.acquire_pg() as c:
        rows = await c.fetch(
            "SELECT column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = $1 "
            "ORDER BY ordinal_position",
            safe_name,
        )
        return [dict(r) for r in rows]


async def describe_mongodb(conn: Connection, collection: str) -> list[dict]:
    safe_name = sanitize_table_name(collection)
    cursor = conn.db[safe_name].aggregate([{"$collStats": {"storageStats": {}}}])
    return await cursor.to_list(10)
