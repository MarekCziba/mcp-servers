# 🌐 Wikipedia MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Search Wikipedia and pull article summaries, plain text and outgoing links into your agent.

No API key, no account, no telemetry. Runs locally over stdio. Works in 300+ languages —
every tool takes an optional `language` code (`en`, `de`, `pl`, `ja`, …).

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `search_articles` | Search Wikipedia; returns title, HTML-free snippet, word count and URL | `query`, `limit = 5`, `language = "en"` |
| `get_summary` | Intro summary of an article — description, short extract, URL, thumbnail | `title`, `language = "en"` |
| `get_article_text` | Full plain text of an article, truncated to a character budget | `title`, `max_chars = 5000`, `language = "en"` |
| `get_related_articles` | Outgoing article links from a page (main namespace only) | `title`, `limit = 5`, `language = "en"` |

`limit` is clamped to 1–20 and `max_chars` to a minimum of 100. Redirects and
disambiguation links resolve automatically; a missing article returns an `error` field
instead of throwing. Endpoints used: the MediaWiki Action API (`/w/api.php`) and the
official REST API (`/api/rest_v1/page/summary`).

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/wikipedia-mcp wikipedia-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/wikipedia-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add wikipedia -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/wikipedia-mcp wikipedia-mcp
```

```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/wikipedia-mcp", "wikipedia-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "wikipedia": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/wikipedia-mcp", "wikipedia-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Who was Alan Turing and what did he work on?
Agent: [calls get_summary("Alan Turing")]
       Alan Mathison Turing was an English mathematician, computer scientist, logician …

You:  Pull the first 800 characters of that article and 5 pages it links to
Agent: [calls get_article_text("Alan Turing", max_chars=800), get_related_articles("Alan Turing", limit=5)]

You:  Sprawdź po polsku czym jest Sztuczna inteligencja
Agent: [calls get_summary("Sztuczna inteligencja", language="pl")]
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/wikipedia-mcp
```

The tests hit the real Wikipedia API and assert on known facts — the Einstein article's
title and URL, 500-character truncation, snippets with no HTML tags, redirects resolving
to canonical titles — not on whatever the implementation happens to return. Wikipedia
content is CC BY-SA; attribute the article URL when you republish its text.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
