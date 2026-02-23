from __future__ import annotations

import getpass
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    db_type: str  # "mysql", "postgresql", or "mongodb"
    db_mode: str  # "read-only" or "read-write"
    db_database: str

    # MySQL / PostgreSQL
    db_host: str
    db_port: int
    db_user: str
    db_password: str

    # MongoDB
    db_url: str

    # SSH tunnel (MySQL / PostgreSQL only)
    ssh_host: str
    ssh_port: int
    ssh_user: str
    ssh_key: str
    ssh_password: str

    @property
    def is_mysql(self) -> bool:
        return self.db_type == "mysql"

    @property
    def is_postgresql(self) -> bool:
        return self.db_type == "postgresql"

    @property
    def is_mongodb(self) -> bool:
        return self.db_type == "mongodb"

    @property
    def is_read_only(self) -> bool:
        return self.db_mode == "read-only"

    @property
    def has_ssh_tunnel(self) -> bool:
        return bool(self.ssh_host)

    @staticmethod
    def from_env() -> Config:
        db_type = os.environ.get("DB_TYPE", "").lower()
        db_mode = os.environ.get("DB_MODE", "read-only").lower()
        db_database = os.environ.get("DB_DATABASE", "")

        missing: list[str] = []

        if db_type not in ("mysql", "postgresql", "mongodb"):
            raise RuntimeError(
                "DB_TYPE must be 'mysql', 'postgresql', or 'mongodb'.\n"
                "Set DB_TYPE in your environment variables."
            )

        if not db_database:
            missing.append("DB_DATABASE")

        if db_mode not in ("read-only", "read-write"):
            raise RuntimeError(
                "DB_MODE must be 'read-only' or 'read-write'.\n"
                f"Got: '{db_mode}'"
            )

        # MySQL / PostgreSQL connection vars
        db_host = os.environ.get("DB_HOST", "localhost")
        default_port = "5432" if db_type == "postgresql" else "3306"
        db_port = int(os.environ.get("DB_PORT", default_port))
        default_user = "postgres" if db_type == "postgresql" else "root"
        db_user = os.environ.get("DB_USER", default_user)
        db_password = os.environ.get("DB_PASSWORD", "")
        db_url = os.environ.get("DB_URL", "")

        if db_type in ("mysql", "postgresql") and not db_password:
            missing.append("DB_PASSWORD")

        if db_type == "mongodb" and not db_url:
            missing.append("DB_URL")

        # SSH tunnel vars
        ssh_host = os.environ.get("SSH_HOST", "")
        ssh_port = int(os.environ.get("SSH_PORT", "22"))
        ssh_user = os.environ.get("SSH_USER", getpass.getuser())
        ssh_key = os.environ.get("SSH_KEY", "")
        ssh_password = os.environ.get("SSH_PASSWORD", "")

        if ssh_host:
            if db_type == "mongodb":
                raise RuntimeError(
                    "SSH tunneling is not supported for MongoDB.\n"
                    "MongoDB uses DB_URL which may contain replica set routing or SRV records.\n"
                    "Please manage the SSH tunnel externally for MongoDB connections."
                )
            if not ssh_key and not ssh_password:
                raise RuntimeError(
                    "SSH_HOST is set but no authentication provided.\n"
                    "Set SSH_KEY (path to private key) or SSH_PASSWORD."
                )

        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}.\n"
                "MySQL requires: DB_TYPE, DB_DATABASE, DB_PASSWORD\n"
                "PostgreSQL requires: DB_TYPE, DB_DATABASE, DB_PASSWORD\n"
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
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_user=ssh_user,
            ssh_key=ssh_key,
            ssh_password=ssh_password,
        )


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
