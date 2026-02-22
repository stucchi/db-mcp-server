from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from db_mcp.config import get_config
from db_mcp.connection import Connection
from db_mcp.tools.aggregate import aggregate_mongodb
from db_mcp.tools.describe import describe_mongodb, describe_mysql, describe_pg
from db_mcp.tools.execute import execute_mysql, execute_pg
from db_mcp.tools.list_collections import list_collections as _list_collections
from db_mcp.tools.list_tables import list_tables as _list_tables, list_tables_pg as _list_tables_pg
from db_mcp.tools.query import query_mongodb, query_mysql, query_pg
from db_mcp.tools.status import get_status

config = get_config()
_conn = Connection(config)


def _format(result: Any) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, default=str)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    await _conn.connect()
    try:
        yield
    finally:
        await _conn.close()


mcp = FastMCP(
    f"db-mcp-server ({config.db_type}:{config.db_database})",
    lifespan=app_lifespan,
)


# --- Tool: query ---

if config.is_mysql:

    @mcp.tool()
    async def query(
        query: Annotated[str, "SQL SELECT query to execute"],
    ) -> str:
        """Execute a read-only query on the MySQL database. Only SELECT, SHOW, DESCRIBE, EXPLAIN, WITH are allowed on read-only databases."""
        rows = await query_mysql(_conn, config, query)
        return _format(rows)

elif config.is_postgresql:

    @mcp.tool()
    async def query(
        query: Annotated[str, "SQL SELECT query to execute"],
    ) -> str:
        """Execute a read-only query on the PostgreSQL database. Only SELECT, SHOW, DESCRIBE, EXPLAIN, WITH are allowed on read-only databases."""
        rows = await query_pg(_conn, config, query)
        return _format(rows)

else:

    @mcp.tool()
    async def query(
        collection: Annotated[str, "Collection name to query"],
        filter: Annotated[dict | None, "MongoDB filter object (default: {})"] = None,
        limit: Annotated[int, "Maximum number of results (default: 100, max: 1000)"] = 100,
    ) -> str:
        """Execute a find query on a MongoDB collection."""
        rows = await query_mongodb(_conn, collection, filter, limit)
        return _format(rows)


# --- Tool: execute (MySQL / PostgreSQL only) ---

if config.is_mysql:

    @mcp.tool()
    async def execute(
        query: Annotated[str, "SQL query to execute (INSERT, UPDATE, DELETE, etc.)"],
    ) -> str:
        """Execute a write query on the MySQL database. Only works if the database is configured with mode='read-write'."""
        result = await execute_mysql(_conn, config, query)
        return _format(result)

elif config.is_postgresql:

    @mcp.tool()
    async def execute(
        query: Annotated[str, "SQL query to execute (INSERT, UPDATE, DELETE, etc.)"],
    ) -> str:
        """Execute a write query on the PostgreSQL database. Only works if the database is configured with mode='read-write'."""
        result = await execute_pg(_conn, config, query)
        return _format(result)


# --- Tool: describe ---

if config.is_mysql:

    @mcp.tool()
    async def describe(
        table: Annotated[str, "Table name to describe"],
    ) -> str:
        """Describe the structure of a MySQL table (DESCRIBE)."""
        rows = await describe_mysql(_conn, table)
        return _format(rows)

elif config.is_postgresql:

    @mcp.tool()
    async def describe(
        table: Annotated[str, "Table name to describe"],
    ) -> str:
        """Describe the structure of a PostgreSQL table (column info from information_schema)."""
        rows = await describe_pg(_conn, table)
        return _format(rows)

else:

    @mcp.tool()
    async def describe(
        collection: Annotated[str, "Collection name to describe"],
    ) -> str:
        """Describe the structure of a MongoDB collection ($collStats)."""
        rows = await describe_mongodb(_conn, collection)
        return _format(rows)


# --- Tool: list_tables (MySQL / PostgreSQL) ---

if config.is_mysql:

    @mcp.tool()
    async def list_tables() -> str:
        """List all tables in the MySQL database."""
        rows = await _list_tables(_conn)
        return _format(rows)

elif config.is_postgresql:

    @mcp.tool()
    async def list_tables() -> str:
        """List all tables in the PostgreSQL database (public schema)."""
        rows = await _list_tables_pg(_conn)
        return _format(rows)


# --- Tool: list_collections (MongoDB only) ---

if config.is_mongodb:

    @mcp.tool()
    async def list_collections() -> str:
        """List all collections in the MongoDB database."""
        names = await _list_collections(_conn)
        return _format(names)


# --- Tool: aggregate (MongoDB only) ---

if config.is_mongodb:

    @mcp.tool()
    async def aggregate(
        collection: Annotated[str, "Collection name to aggregate"],
        pipeline: Annotated[list[dict[str, Any]], "MongoDB aggregation pipeline array"],
    ) -> str:
        """Execute an aggregation pipeline on a MongoDB collection. Pipelines with $out/$merge are blocked on read-only databases."""
        rows = await aggregate_mongodb(_conn, config, collection, pipeline)
        return _format(rows)


# --- Tool: status ---


@mcp.tool()
async def status() -> str:
    """Show connection info: type, host, database, mode, status."""
    return _format(get_status(config))


def main() -> None:
    mcp.run(transport="stdio")
