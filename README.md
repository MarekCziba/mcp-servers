# mcp-servers

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=fff)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-2.x-2b6cb0)](https://modelcontextprotocol.io)

> **19 free, open-source [MCP](https://modelcontextprotocol.io) servers. No API key, no account, no pay-per-event.**

Every server speaks the Model Context Protocol over stdio, runs locally next to your
agent, and does one job well. Install any of them in a single command with
[`uv`](https://docs.astral.sh/uv/):

```bash
uvx website-to-markdown-mcp
```

## Servers

| Server | What it does | Tools |
|--------|--------------|:-----:|
| [`website-to-markdown-mcp`](servers/website-to-markdown-mcp) | Turn any web page into clean, LLM-ready Markdown | 3 |
| [`wikipedia-mcp`](servers/wikipedia-mcp) | Search Wikipedia — summaries, plain text, outgoing links | 4 |
| [`github-mcp`](servers/github-mcp) | Search GitHub — repos, issues, files, READMEs (zero API key) | 5 |
| [`job-tracker-mcp`](servers/job-tracker-mcp) | Local job application tracker — stages, stats, follow-ups, CSV | 8 |
| [`rss-feed-reader-mcp`](servers/rss-feed-reader-mcp) | Fetch, parse and search RSS/Atom feeds | 3 |
| [`seo-analyzer-mcp`](servers/seo-analyzer-mcp) | Audit pages for titles, meta, headings, images, links | 3 |
| [`youtube-transcript-mcp`](servers/youtube-transcript-mcp) | Transcripts, video info and languages for YouTube | 3 |
| [`data-converter-mcp`](servers/data-converter-mcp) | JSON ⇄ CSV ⇄ YAML ⇄ XML ⇄ Markdown tables | 4 |
| [`hash-checksum-mcp`](servers/hash-checksum-mcp) | MD5, SHA-1/2, CRC32, BLAKE2b, SHA3 — generate and verify | 3 |
| [`regex-tester-mcp`](servers/regex-tester-mcp) | Test, replace and split text with regular expressions | 4 |
| [`text-diff-mcp`](servers/text-diff-mcp) | Unified, JSON and HTML diffs plus similarity scoring | 4 |
| [`unit-converter-mcp`](servers/unit-converter-mcp) | Length, weight, temperature, area, volume, speed… | 5 |
| [`color-converter-mcp`](servers/color-converter-mcp) | HEX, RGB, HSL, CMYK and named colors | 5 |
| [`datetime-utility-mcp`](servers/datetime-utility-mcp) | Timestamps, timezone conversion, relative time | 5 |
| [`base64-encoding-mcp`](servers/base64-encoding-mcp) | Base64, Base64URL, URL and HTML entity codecs | 8 |
| [`uuid-generator-mcp`](servers/uuid-generator-mcp) | UUIDv4, nanoid, slug and random string generation | 4 |
| [`password-generator-mcp`](servers/password-generator-mcp) | Passwords, passphrases, PINs and API keys | 4 |
| [`case-converter-mcp`](servers/case-converter-mcp) | camelCase, snake_case, kebab-case, PascalCase… | 7 |
| [`brevo-mcp`](servers/brevo-mcp) | Send transactional and bulk email via the Brevo API * | 3 |

\* `brevo-mcp` is the only server that needs a key — set `BREVO_API_KEY`. Everything else works out of the box.

**85 tools total, MIT licensed, no telemetry.**

## Quick start

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (it ships `uvx`).
2. Add a server to your MCP client:

```bash
claude mcp add web-to-md -- uvx website-to-markdown-mcp
```

or in JSON config (Claude Desktop, Cursor, Windsurf, …):

```json
{
  "mcpServers": {
    "rss-feed-reader": {
      "command": "uvx",
      "args": ["rss-feed-reader-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "hash-checksum": {
      "type": "local",
      "command": ["uvx", "hash-checksum-mcp"],
      "enabled": true
    }
  }
}
```

Each server directory contains its own README with the exact tool signatures and
copy-paste client snippets.

## Repository layout

```
mcp-servers/
├── servers/
│   ├── website-to-markdown-mcp/     # each server: package/, tests/, README.md, pyproject.toml
│   ├── rss-feed-reader-mcp/
│   └── …                            # 19 total
├── .github/workflows/ci.yml         # ruff + pytest + build, per-server matrix
├── pyproject.toml                   # workspace config (lint, pytest, shared dev deps)
└── README.md
```

[`website-to-markdown-mcp`](https://github.com/MarekCziba/website-to-markdown-mcp) —
the flagship server — also lives in its own showcase repository.

## Development

```bash
uv sync                          # one venv for the whole workspace
uv run ruff check servers        # lint
uv run ruff format servers       # format
uv run pytest                    # every test suite
uv run pytest servers/rss-feed-reader-mcp   # one server
uv build servers/hash-checksum-mcp          # packaging check
```

Tests assert against **real known vectors and live URLs** — published NIST/RFC digests,
real RSS feeds, real GitHub API responses, pages that actually exist — not against
whatever the code happens to return.

## License

MIT — see [LICENSE](LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [LinkedIn](https://www.linkedin.com/in/marekcziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)

**Articles:** [MCP vs Apify vs Custom Agents: When to Use Each](https://www.linkedin.com/pulse/mcp-vs-apify-custom-agents-when-use-each-marek-cziba-rltzf/) · [dev.to mirror](https://dev.to/marekcziba/mcp-vs-apify-vs-custom-agents-when-to-use-each-4pl0)
