# 🌐 Website to Markdown MCP

[![PyPI](https://img.shields.io/pypi/v/website-to-markdown-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/website-to-markdown-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/website-to-markdown-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/website-to-markdown-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/website-to-markdown-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Turn any web page into clean, structured Markdown — purpose-built for AI agents, LLM context and RAG pipelines.

No API key. No account. No pay-per-event. Runs locally over stdio.

---

## ✨ Why

LLMs read text, not DOM trees. This server fetches a page, strips the navigation,
ads and boilerplate, and hands your agent semantic Markdown it can reason over
immediately — a browser that speaks the model's language.

- **One command, no config** — `uvx website-to-markdown-mcp` and it is running
- **Real extraction** — [trafilatura](https://trafilatura.readthedocs.io/) for article text, BeautifulSoup fallback for everything else
- **Batch + concurrency** — up to 5 pages in flight at once, one bad URL never kills the batch
- **Honest output** — guarantees an H1 heading, never leaks raw HTML tags
- **Metadata too** — title, description, author, Open Graph tags, canonical URL

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `fetch_url` | Fetch one page and return clean Markdown | `url`, `max_length = 50000` |
| `fetch_urls` | Fetch several pages concurrently; returns `{url, markdown, error}` per item | `urls`, `max_length = 50000` |
| `extract_metadata` | Extract title, description, author, OG tags, canonical | `url` |

## 🚀 Install

```bash
# one-off, no installation (recommended)
uvx website-to-markdown-mcp

# or with pip
pip install website-to-markdown-mcp

# or from source
git clone https://github.com/MarekCziba/website-to-markdown-mcp
cd website-to-markdown-mcp
uv sync
```

## 🔌 Connect your MCP client

**Claude Desktop / Claude Code** — `claude mcp add`:

```bash
claude mcp add website-to-markdown -- uvx website-to-markdown-mcp
```

**Cursor, Windsurf, or any JSON-config client:**

```json
{
  "mcpServers": {
    "website-to-markdown": {
      "command": "uvx",
      "args": ["website-to-markdown-mcp"]
    }
  }
}
```

**opencode** (`opencode.json`):

```json
{
  "mcp": {
    "website-to-markdown": {
      "type": "local",
      "command": ["uvx", "website-to-markdown-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Summarise https://example.com
Agent: [calls fetch_url]
       # Example Domain

       This domain is for use in documentation examples without needing
       permission. ...

You:  Pull the title and description from three pages at once
Agent: [calls fetch_urls with 3 URLs]
```

## 🏗️ How it works

1. Your MCP client starts the server over stdio
2. `httpx` fetches the page (redirects followed, 30 s timeout, honest User-Agent)
3. `trafilatura` extracts the article body as Markdown
4. If extraction is too thin, boilerplate tags are stripped and `markdownify` takes over
5. The document title is re-attached as an `# H1` when the extractor dropped it

## 🧪 Development

```bash
uv sync                 # install runtime + dev dependencies
uv run pytest           # runs against LIVE urls (example.com, docs.python.org, wikipedia.org)
uv run ruff check src tests
uv run ruff format src tests
```

The test suite asserts on **actual output** — expected phrases, no leaked HTML tags,
`max_length` enforcement, batch error isolation and URL validation — not on “it looks fine”.

## 📄 License

MIT — see [LICENSE](LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [LinkedIn](https://www.linkedin.com/in/marekcziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
