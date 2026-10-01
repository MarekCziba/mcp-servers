# 📊 Data Converter MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Convert data between JSON, CSV, YAML, XML and Markdown tables — plus JSON formatting, validation and flattening.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `convert_data` | Convert data between JSON, CSV, YAML, XML and Markdown table formats | `input_text`, `from_format = "json"`, `to_format = "csv"` |
| `format_json` | Pretty-format a JSON string with specified indentation | `input_text`, `indent = 2` |
| `validate_json` | Validate a JSON string, returns valid and error message | `input_text` |
| `flatten_json` | Flatten nested JSON into dot-notation key-value pairs | `input_text` |

Source formats: `json`, `csv`, `yaml`, `xml`. Target formats: those four plus `markdown`
(a pipe-separated table). Unsupported formats and malformed input come back as a
`"Conversion error: ..."` string — the tool never raises.

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/data-converter-mcp data-converter-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/data-converter-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add data-converter -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/data-converter-mcp data-converter-mcp
```

```json
{
  "mcpServers": {
    "data-converter": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/data-converter-mcp", "data-converter-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "data-converter": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/data-converter-mcp", "data-converter-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Turn this JSON into a CSV table
      [{"name": "Alice", "city": "Paris"}, {"name": "Bob", "city": "Tokyo"}]
Agent: [calls convert_data]
       name,city
       Alice,Paris
       Bob,Tokyo

You:  Is this config valid JSON?
      {"name": 
Agent: [calls validate_json]
       {"valid": false, "error": "Expecting value: line 1 column 10 (char 9)"}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/data-converter-mcp
```

The tests assert against exact known serializations and JSON→CSV→JSON / JSON→XML→JSON
round-trips — not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
