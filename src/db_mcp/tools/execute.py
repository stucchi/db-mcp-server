from __future__ import annotations

import re

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


async def execute_pg(conn: Connection, config: Config, sql: str) -> dict:
    if config.is_read_only:
        raise ValueError(
            "This database is in READ-ONLY mode. "
            "Write operations are not allowed."
        )

    async with conn.acquire_pg() as c:
        status = await c.execute(sql)
        # asyncpg returns status strings like "INSERT 0 1", "DELETE 3", "UPDATE 5"
        match = re.search(r"(\d+)$", status or "")
        affected = int(match.group(1)) if match else 0
        return {"affectedRows": affected}
