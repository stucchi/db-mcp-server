# db-mcp-server

MCP server for MySQL and MongoDB databases. One instance per database, no Docker required.

## Installation

```bash
uvx db-mcp-server
```

## Configuration

Configure via environment variables. Each instance connects to a single database.

### MySQL

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | Yes | — | `mysql` |
| `DB_DATABASE` | Yes | — | Database name |
| `DB_PASSWORD` | Yes | — | Password |
| `DB_HOST` | No | `localhost` | Host |
| `DB_PORT` | No | `3306` | Port |
| `DB_USER` | No | `root` | User |
| `DB_MODE` | No | `read-only` | `read-only` or `read-write` |

### MongoDB

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | Yes | — | `mongodb` |
| `DB_DATABASE` | Yes | — | Database name |
| `DB_URL` | Yes | — | Connection URL (`mongodb://...`) |
| `DB_MODE` | No | `read-only` | `read-only` or `read-write` |

## Usage in .mcp.json

```json
{
  "mcpServers": {
    "db-prod": {
      "command": "uvx",
      "args": ["db-mcp-server"],
      "env": {
        "DB_TYPE": "mysql",
        "DB_MODE": "read-only",
        "DB_HOST": "db.example.com",
        "DB_PORT": "3306",
        "DB_USER": "root",
        "DB_PASSWORD": "secret",
        "DB_DATABASE": "myapp"
      }
    }
  }
}
```

For multiple databases, add multiple instances:

```json
{
  "mcpServers": {
    "db-prod": {
      "command": "uvx",
      "args": ["db-mcp-server"],
      "env": { "DB_TYPE": "mysql", "DB_DATABASE": "prod", "..." : "..." }
    },
    "db-staging": {
      "command": "uvx",
      "args": ["db-mcp-server"],
      "env": { "DB_TYPE": "mongodb", "DB_DATABASE": "staging", "..." : "..." }
    }
  }
}
```

## Tools

### MySQL

- **query** — Execute read-only SQL (SELECT, SHOW, DESCRIBE, EXPLAIN, WITH)
- **execute** — Execute write SQL (INSERT, UPDATE, DELETE) — requires `DB_MODE=read-write`
- **describe** — Describe table structure
- **list_tables** — List all tables
- **status** — Show connection info

### MongoDB

- **query** — Find documents in a collection
- **describe** — Collection stats ($collStats)
- **list_collections** — List all collections
- **aggregate** — Execute aggregation pipelines ($out/$merge blocked on read-only)
- **status** — Show connection info

## License

MIT
