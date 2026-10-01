# 📰 RSS Feed Reader MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Fetch, parse and search any RSS or Atom feed from your agent — metadata plus up to 50 entries per call.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `get_feed` | Fetch and parse one RSS/Atom feed; returns feed metadata and up to 50 entries | `feed_url` |
| `get_multiple_feeds` | Fetch several feeds in one call — a failing URL comes back as `{url, error}` instead of breaking the batch | `feed_urls` |
| `search_feed` | Case-insensitive keyword search across entry titles + summaries, max 20 matches | `feed_url`, `keyword` |

Feed object: `title`, `link`, `description`, `language`, `entries`.
Every entry: `title`, `link`, `published`, `summary` (first 1000 characters), `authors`.

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/rss-feed-reader-mcp rss-feed-reader-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/rss-feed-reader-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add rss-feed-reader -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/rss-feed-reader-mcp rss-feed-reader-mcp
```

Cursor, Windsurf, or any JSON-config client:

```json
{
  "mcpServers": {
    "rss-feed-reader": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/rss-feed-reader-mcp", "rss-feed-reader-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "rss-feed-reader": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/rss-feed-reader-mcp", "rss-feed-reader-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  What's on the Hacker News front page right now?
Agent: [calls get_feed with https://hnrss.org/frontpage]
       {"title": "Hacker News: Front Page", "entries": [{...}, ...]}

You:  Which BBC headlines mention "climate"?
Agent: [calls search_feed with the BBC news feed and the keyword "climate"]
       [{"title": "...", "summary": "..."}]
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/rss-feed-reader-mcp
uv run ruff check servers/rss-feed-reader-mcp
uv run ruff format servers/rss-feed-reader-mcp
```

The tests hit **live feeds** (hnrss.org, BBC News) and assert real structure — feed titles,
entry counts, the exact entry keys, keyword matching and case-insensitivity — plus error
handling for a bogus URL and per-URL failure isolation in `get_multiple_feeds`. Reddit's
`/.rss` answers HTTP 429 after the first request from this network, so it is not asserted
against.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
