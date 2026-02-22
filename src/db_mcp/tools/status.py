from __future__ import annotations

from db_mcp.config import Config


def get_status(config: Config) -> dict:
    info: dict = {
        "type": config.db_type,
        "database": config.db_database,
        "mode": config.db_mode,
        "status": "connected",
    }
    if config.is_mysql or config.is_postgresql:
        info["host"] = f"{config.db_host}:{config.db_port}"
        info["user"] = config.db_user
    else:
        info["url"] = config.db_url
    return info
