from __future__ import annotations

from db_mcp.config import Config
from db_mcp.connection import Connection


async def execute_mysql(conn: Connection, config: Config, sql: str) -> dict:
    if config.is_read_only:
        raise ValueError(
            "This database is in READ-ONLY mode. "
            "Write operations are not allowed."
        )

    async with conn.acquire_mysql() as c:
        async with c.cursor() as cur:
            await cur.execute(sql)
            return {
                "affectedRows": cur.rowcount,
                "insertId": cur.lastrowid or 0,
            }
