from __future__ import annotations

from db_mcp.config import Config
from db_mcp.connection import Connection
from db_mcp.validation import validate_read_only_query


async def query_sqlite(conn: Connection, config: Config, sql: str) -> list[dict]:
    if config.is_read_only:
        validate_read_only_query(sql)

    async with conn.acquire_sqlite() as db:
        async with db.execute(sql) as cur:
            rows = await cur.fetchall()
            columns = [d[0] for d in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in rows]
