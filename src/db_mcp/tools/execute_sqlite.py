from __future__ import annotations

from db_mcp.config import Config
from db_mcp.connection import Connection


async def execute_sqlite(conn: Connection, config: Config, sql: str) -> dict:
    if config.is_read_only:
        raise ValueError(
            "This database is in READ-ONLY mode. "
            "Write operations are not allowed."
        )

    async with conn.acquire_sqlite() as db:
        async with db.execute(sql) as cur:
            await db.commit()
            return {
                "affectedRows": cur.rowcount,
                "lastRowId": cur.lastrowid or 0,
            }
