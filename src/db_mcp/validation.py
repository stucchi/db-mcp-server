from __future__ import annotations

import re

_READ_ONLY_PREFIXES = ("select", "show", "describe", "explain", "with")


def _split_statements(sql: str) -> list[str]:
    """Split SQL into individual statements by semicolons.

    Respects single-quoted, double-quoted, and backtick-quoted strings so that
    semicolons inside literals are **not** treated as statement separators.
    """
    statements: list[str] = []
    current: list[str] = []
    in_quote: str | None = None
    i = 0

    while i < len(sql):
        ch = sql[i]

        # Inside a quoted string, handle backslash escapes (e.g. \' or \")
        if in_quote is not None and ch == "\\":
            current.append(ch)
            i += 1
            if i < len(sql):
                current.append(sql[i])
                i += 1
            continue

        # Quote characters: toggle in/out of quoted context
        if ch in ("'", '"', "`"):
            if in_quote is None:
                in_quote = ch
            elif in_quote == ch:
                # Check for doubled-quote escape (e.g. '' inside a string)
                if i + 1 < len(sql) and sql[i + 1] == ch:
                    current.append(ch)
                    current.append(ch)
                    i += 2
                    continue
                in_quote = None
            current.append(ch)
            i += 1
            continue

        # Semicolons outside of any quoted context mark statement boundaries
        if ch == ";" and in_quote is None:
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    # Trailing statement (no terminating semicolon)
    stmt = "".join(current).strip()
    if stmt:
        statements.append(stmt)

    return statements


def validate_read_only_query(sql: str) -> None:
    statements = _split_statements(sql)
    if not statements:
        raise ValueError("Empty query.")
    for stmt in statements:
        trimmed = stmt.lower()
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
