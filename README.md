# db-mcp-server

MCP server for MySQL, PostgreSQL, and MongoDB databases. One instance per database, no Docker required.

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

### PostgreSQL

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | Yes | — | `postgresql` |
| `DB_DATABASE` | Yes | — | Database name |
| `DB_PASSWORD` | Yes | — | Password |
| `DB_HOST` | No | `localhost` | Host |
| `DB_PORT` | No | `5432` | Port |
| `DB_USER` | No | `postgres` | User |
| `DB_MODE` | No | `read-only` | `read-only` or `read-write` |

### MongoDB

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | Yes | — | `mongodb` |
| `DB_DATABASE` | Yes | — | Database name |
| `DB_URL` | Yes | — | Connection URL (`mongodb://...`) |
| `DB_MODE` | No | `read-only` | `read-only` or `read-write` |

### SSH Tunnel (MySQL / PostgreSQL)

Optionally connect through an SSH bastion host. Set `SSH_HOST` to activate.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SSH_HOST` | No | — | SSH bastion host (activates tunneling) |
| `SSH_PORT` | No | `22` | SSH port |
| `SSH_USER` | No | Current OS user | SSH username |
| `SSH_KEY` | No | — | Path to private key (`~/.ssh/id_rsa`) |
| `SSH_PASSWORD` | No | — | SSH password (if no key) |

At least one of `SSH_KEY` or `SSH_PASSWORD` is required when `SSH_HOST` is set. SSH tunneling is not supported for MongoDB.

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

### With SSH tunnel

```json
{
  "mcpServers": {
    "db-behind-bastion": {
      "command": "uvx",
      "args": ["db-mcp-server"],
      "env": {
        "DB_TYPE": "postgresql",
        "DB_HOST": "10.0.0.5",
        "DB_PORT": "5432",
        "DB_USER": "postgres",
        "DB_PASSWORD": "secret",
        "DB_DATABASE": "myapp",
        "SSH_HOST": "bastion.example.com",
        "SSH_USER": "deploy",
        "SSH_KEY": "~/.ssh/id_rsa"
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
    "db-analytics": {
      "command": "uvx",
      "args": ["db-mcp-server"],
      "env": { "DB_TYPE": "postgresql", "DB_DATABASE": "analytics", "..." : "..." }
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

### PostgreSQL

- **query** — Execute read-only SQL (SELECT, SHOW, DESCRIBE, EXPLAIN, WITH)
- **execute** — Execute write SQL (INSERT, UPDATE, DELETE) — requires `DB_MODE=read-write`
- **describe** — Describe table structure (column info from information_schema)
- **list_tables** — List all tables in the public schema
- **status** — Show connection info

### MongoDB

- **query** — Find documents in a collection
- **describe** — Collection stats ($collStats)
- **list_collections** — List all collections
- **aggregate** — Execute aggregation pipelines ($out/$merge blocked on read-only)
- **status** — Show connection info

## License

MIT

<!-- mcp-name: io.github.stucchi/db -->
