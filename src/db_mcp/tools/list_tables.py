from __future__ import annotations

import aiomysql

from db_mcp.connection import Connection


async def list_tables(conn: Connection) -> list[dict]:
    async with conn.pool.acquire() as c:
        async with c.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SHOW TABLES")
            return await cur.fetchall()
