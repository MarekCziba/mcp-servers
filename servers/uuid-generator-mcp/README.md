# 🆔 UUID Generator MCP

[![PyPI](https://img.shields.io/pypi/v/uuid-generator-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/uuid-generator-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/uuid-generator-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Generate UUIDs (v4 random and v7 time-ordered), nano-style IDs, URL slugs and random strings.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `generate_uuid` | Generate a UUID — v4 (random) or v7 (time-ordered) | `version = 4` |
| `generate_nanoid` | Generate a nano-style ID from a 64-character alphabet | `size = 21` |
| `generate_slug` | Convert text to a URL-friendly slug | `text`, `max_length = 80` |
| `generate_random_string` | Random string with configurable character sets | `length = 16`, `include_digits = True`, `include_symbols = False` |

Only versions 4 and 7 are implemented; any other `version` value falls back to a random
v4 UUID. `generate_slug` lowercases, drops everything outside `a-z 0-9 space hyphen`,
collapses runs of spaces/hyphens into one `-`, strips leading/trailing `-` and truncates to
`max_length`. `generate_nanoid` draws from `A-Za-z0-9_-`.

## 🚀 Install

```bash
uvx uuid-generator-mcp          # recommended, no installation
pip install uuid-generator-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add uuid-generator -- uvx uuid-generator-mcp
```

```json
{
  "mcpServers": {
    "uuid-generator": {
      "command": "uvx",
      "args": ["uuid-generator-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "uuid-generator": {
      "type": "local",
      "command": ["uvx", "uuid-generator-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Give me a time-ordered UUID for this database row
Agent: [calls generate_uuid with version=7]
       01a0ec57-6e31-73a7-a357-e7a2609bf0dc

You:  Slugify "Hello World!" for the URL and make a 12-char nano ID
Agent: [calls generate_slug, generate_nanoid with size=12]
       hello-world
       3-VLmJywnjoDG
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/uuid-generator-mcp
```

The tests assert the RFC 9562 UUID structure (version and variant nibbles, the 48-bit
millisecond timestamp, monotonicity), slug vectors and uniqueness — not against whatever
the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
