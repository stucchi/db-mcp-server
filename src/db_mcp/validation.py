from __future__ import annotations

import re

_READ_ONLY_PREFIXES = ("select", "show", "describe", "explain", "with")


def validate_read_only_query(sql: str) -> None:
    trimmed = sql.strip().lower()
    if not any(trimmed.startswith(p) for p in _READ_ONLY_PREFIXES):
        raise ValueError(
            "Only SELECT, SHOW, DESCRIBE, EXPLAIN, WITH queries are allowed "
            "on read-only databases."
        )


def sanitize_table_name(name: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "", name)
    if not sanitized:
        raise ValueError(f"Invalid table/collection name: {name!r}")
    return sanitized


def validate_aggregate_pipeline(pipeline: list, read_only: bool) -> None:
    if not read_only:
        return
    for stage in pipeline:
        if not isinstance(stage, dict):
            continue
        for key in stage:
            if key in ("$out", "$merge"):
                raise ValueError(
                    f"Aggregation pipelines with {key} are not allowed "
                    "on read-only databases."
                )
