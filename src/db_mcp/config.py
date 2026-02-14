from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    db_type: str  # "mysql" or "mongodb"
    db_mode: str  # "read-only" or "read-write"
    db_database: str

    # MySQL
    db_host: str
    db_port: int
    db_user: str
    db_password: str

    # MongoDB
    db_url: str

    @property
    def is_mysql(self) -> bool:
        return self.db_type == "mysql"

    @property
    def is_mongodb(self) -> bool:
        return self.db_type == "mongodb"

    @property
    def is_read_only(self) -> bool:
        return self.db_mode == "read-only"

    @staticmethod
    def from_env() -> Config:
        db_type = os.environ.get("DB_TYPE", "").lower()
        db_mode = os.environ.get("DB_MODE", "read-only").lower()
        db_database = os.environ.get("DB_DATABASE", "")

        missing: list[str] = []

        if db_type not in ("mysql", "mongodb"):
            raise RuntimeError(
                "DB_TYPE must be 'mysql' or 'mongodb'.\n"
                "Set DB_TYPE in your environment variables."
            )

        if not db_database:
            missing.append("DB_DATABASE")

        if db_mode not in ("read-only", "read-write"):
            raise RuntimeError(
                "DB_MODE must be 'read-only' or 'read-write'.\n"
                f"Got: '{db_mode}'"
            )

        # MySQL-specific
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = int(os.environ.get("DB_PORT", "3306"))
        db_user = os.environ.get("DB_USER", "root")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_url = os.environ.get("DB_URL", "")

        if db_type == "mysql" and not db_password:
            missing.append("DB_PASSWORD")

        if db_type == "mongodb" and not db_url:
            missing.append("DB_URL")

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}.\n"
                "MySQL requires: DB_TYPE, DB_DATABASE, DB_PASSWORD\n"
                "MongoDB requires: DB_TYPE, DB_DATABASE, DB_URL"
            )

        return Config(
            db_type=db_type,
            db_mode=db_mode,
            db_database=db_database,
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_url=db_url,
        )


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
