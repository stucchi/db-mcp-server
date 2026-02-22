from __future__ import annotations

import aiomysql

from db_mcp.connection import Connection


async def list_tables(conn: Connection) -> list[dict]:
    async with conn.acquire_mysql() as c:
        async with c.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SHOW TABLES")
            return await cur.fetchall()


async def list_tables_pg(conn: Connection) -> list[dict]:
    async with conn.acquire_pg() as c:
        rows = await c.fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        return [dict(r) for r in rows]
