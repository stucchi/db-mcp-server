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
    if config.has_ssh_tunnel:
        info["ssh_tunnel"] = f"{config.ssh_user}@{config.ssh_host}:{config.ssh_port}"
    return info
