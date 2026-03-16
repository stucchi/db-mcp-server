from __future__ import annotations

from db_mcp.connection import Connection


async def list_tables_sqlite(conn: Connection) -> list[dict]:
    async with conn.acquire_sqlite() as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ) as cur:
            rows = await cur.fetchall()
            return [{"table_name": row[0]} for row in rows]
