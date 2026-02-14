from __future__ import annotations

from db_mcp.connection import Connection


async def list_collections(conn: Connection) -> list[str]:
    return await conn.db.list_collection_names()
