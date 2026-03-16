from __future__ import annotations

from db_mcp.connection import Connection
from db_mcp.validation import sanitize_table_name


async def describe_sqlite(conn: Connection, table: str) -> list[dict]:
    safe_name = sanitize_table_name(table)
    async with conn.acquire_sqlite() as db:
        async with db.execute(f"PRAGMA table_info({safe_name})") as cur:
            rows = await cur.fetchall()
            columns = [d[0] for d in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in rows]
