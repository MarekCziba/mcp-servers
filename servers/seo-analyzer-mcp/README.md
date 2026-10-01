# 🔍 SEO Analyzer MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Audit any web page for on-page SEO — title, meta description, headings, image alt text, canonical, Open Graph, JSON-LD and links.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `analyze_seo` | Full on-page audit of one URL: title, meta description, h1–h3, image alt coverage, canonical, robots, OG tags, structured data, word count, internal/external links | `url` |
| `analyze_multiple` | Audit several URLs in one call — a failing URL comes back as `{url, error}` instead of breaking the batch | `urls` |
| `extract_links` | All internal and external links of a page, deduplicated | `url` |

Analysis object: `url`, `status_code`, `title`, `title_length`, `title_ok` (30–60 chars),
`meta_description`, `meta_description_length`, `meta_description_ok` (120–160 chars),
`headings` (`h1`/`h2`/`h3`), `has_h1` (exactly one H1), `images` (`total`, `missing_alt`,
`alt_ok`), `canonical`, `robots`, `og_tags`, `structured_data`, `word_count`,
`links` (`internal`, `external`).

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/seo-analyzer-mcp seo-analyzer-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/seo-analyzer-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add seo-analyzer -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/seo-analyzer-mcp seo-analyzer-mcp
```

Cursor, Windsurf, or any JSON-config client:

```json
{
  "mcpServers": {
    "seo-analyzer": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/seo-analyzer-mcp", "seo-analyzer-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "seo-analyzer": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/seo-analyzer-mcp", "seo-analyzer-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Is https://example.com missing anything important SEO-wise?
Agent: [calls analyze_seo]
       {"title": "Example Domain", "title_ok": false, "meta_description": "",
        "headings": {"h1": []}, "has_h1": false, "word_count": 29, ...}

You:  Compare the Python tutorial with its front page in one go
Agent: [calls analyze_multiple with both URLs]
       [{...}, {...}]
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/seo-analyzer-mcp
uv run ruff check servers/seo-analyzer-mcp
uv run ruff format servers/seo-analyzer-mcp
```

The tests fetch **live pages** (example.com, docs.python.org) and assert what is actually
true of them — exact title, heading counts, alt-text coverage, canonical URL, Open Graph
tags — plus `extract_links` output, batch error isolation with one invalid URL, and an
offline parse of synthetic HTML that pins down every branch of the analyzer.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
