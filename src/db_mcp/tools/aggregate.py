from __future__ import annotations

from typing import Any

from db_mcp.config import Config
from db_mcp.connection import Connection
from db_mcp.validation import sanitize_table_name, validate_aggregate_pipeline


async def aggregate_mongodb(
    conn: Connection,
    config: Config,
    collection: str,
    pipeline: list[dict[str, Any]],
) -> list[dict]:
    validate_aggregate_pipeline(pipeline, config.is_read_only)
    safe_name = sanitize_table_name(collection)
    cursor = conn.db[safe_name].aggregate(pipeline)
    return await cursor.to_list(1000)
