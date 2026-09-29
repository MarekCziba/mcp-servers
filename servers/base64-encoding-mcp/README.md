# 📦 Base64 Encoding MCP

[![PyPI](https://img.shields.io/pypi/v/base64-encoding-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/base64-encoding-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/base64-encoding-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Encode and decode Base64, Base64URL, URL percent-encoding and HTML entities from your agent.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `encode_base64` | Encode text to standard Base64 (RFC 4648 §4) | `text` |
| `decode_base64` | Decode standard Base64 back to text | `encoded` |
| `encode_base64url` | Encode text to URL-safe Base64, padding stripped | `text` |
| `decode_base64url` | Decode URL-safe Base64 (padding is optional) | `encoded` |
| `encode_url` | Percent-encode text for use inside a URL | `text` |
| `decode_url` | Decode a percent-encoded string back to text | `encoded` |
| `encode_html` | Escape HTML special characters (`<`, `>`, `&`, quotes) | `text` |
| `decode_html` | Unescape HTML entities back to text | `encoded` |

`encode_base64url` maps `+` → `-` and `/` → `_` and drops the `=` padding (RFC 4648 §5);
`decode_base64url` re-adds the padding for you, so both padded and unpadded input work.
All eight tools are pure functions of their argument — no state, no network access.

## 🚀 Install

```bash
uvx base64-encoding-mcp          # recommended, no installation
pip install base64-encoding-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add base64-encoding -- uvx base64-encoding-mcp
```

```json
{
  "mcpServers": {
    "base64-encoding": {
      "command": "uvx",
      "args": ["base64-encoding-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "base64-encoding": {
      "type": "local",
      "command": ["uvx", "base64-encoding-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Base64-encode "hello" — is that the RFC 4648 test vector?
Agent: [calls encode_base64]
       aGVsbG8=

You:  I need "~~>" as a URL-safe query parameter, both ways
Agent: [calls encode_base64, encode_base64url]
       fn4+   (standard, "=" padding implied)
       fn4-   (URL-safe, padding stripped)

You:  Decode "aGVsbG8" — a JWT segment with no padding
Agent: [calls decode_base64url]
       hello
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/base64-encoding-mcp
```

The tests assert against published RFC 4648 vectors and percent-/HTML-encoding rules —
not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
