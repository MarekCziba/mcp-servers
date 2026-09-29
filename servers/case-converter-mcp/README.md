# 🔡 Case Converter MCP

[![PyPI](https://img.shields.io/pypi/v/case-converter-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/case-converter-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/case-converter-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Convert identifiers between camelCase, PascalCase, snake_case, kebab-case, UPPER_CASE and Title Case.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `to_camel_case` | Convert text to camelCase | `text` |
| `to_pascal_case` | Convert text to PascalCase | `text` |
| `to_snake_case` | Convert text to snake_case | `text` |
| `to_kebab_case` | Convert text to kebab-case | `text` |
| `to_upper_case` | Convert text to UPPER_CASE | `text` |
| `to_title_case` | Convert text to Title Case | `text` |
| `to_all_cases` | All seven formats at once, keyed by format name | `text` |

Words are split on capitalisation boundaries, digit runs and separators (space, `_`, `-`),
so `HTTPServer` → `http_server`, `XMLHttpRequest` → `xml_http_request` and
`hello world2024` → `hello_world_2024`. Input in any style converges to the same result.

## 🚀 Install

```bash
uvx case-converter-mcp          # recommended, no installation
pip install case-converter-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add case-converter -- uvx case-converter-mcp
```

```json
{
  "mcpServers": {
    "case-converter": {
      "command": "uvx",
      "args": ["case-converter-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "case-converter": {
      "type": "local",
      "command": ["uvx", "case-converter-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Rename HTTPServer to snake_case and camelCase
Agent: [calls to_snake_case, to_camel_case]
       http_server
       httpServer

You:  Give me every case style for "hello world" in one go
Agent: [calls to_all_cases]
       {"camelCase": "helloWorld", "PascalCase": "HelloWorld",
        "snake_case": "hello_world", "kebab-case": "hello-world",
        "UPPER_CASE": "HELLO_WORLD", "Title Case": "Hello World",
        "lowercase": "helloworld"}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/case-converter-mcp
```

The tests assert known word conversions in every style plus cross-format invariants —
not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
