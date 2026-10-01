# 🔍 Regex Tester MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Test, validate, replace and split text with regular expressions from your agent — Python `re` syntax.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `test_regex` | Test a pattern against text, returns matches with positions | `pattern`, `text`, `flags = ""` |
| `replace_regex` | Replace all regex matches in text | `pattern`, `replacement`, `text`, `flags = ""` |
| `split_regex` | Split text by a regex pattern | `pattern`, `text` |
| `validate_regex` | Check whether a pattern is syntactically correct | `pattern` |

`flags` accepts any combination of `i` (ignore case), `m` (multiline) and `s` (dot matches newline).
`test_regex` and `validate_regex` never raise on a bad pattern — they return
`{"valid": false, "error": "..."}` instead.

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/regex-tester-mcp regex-tester-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/regex-tester-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add regex-tester -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/regex-tester-mcp regex-tester-mcp
```

```json
{
  "mcpServers": {
    "regex-tester": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/regex-tester-mcp", "regex-tester-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "regex-tester": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/regex-tester-mcp", "regex-tester-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Find the numbers in "abc 123 def 456"
Agent: [calls test_regex with pattern \d+]
       {"valid": true, "count": 2, "error": null,
        "matches": [{"match": "123", "start": 4, "end": 7, "groups": null},
                    {"match": "456", "start": 12, "end": 15, "groups": null}]}

You:  Is "[" a usable pattern?
Agent: [calls validate_regex]
       {"valid": false, "error": "unterminated character set at position 0"}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/regex-tester-mcp
```

The tests assert against fixed patterns with known match positions, captures and error messages —
not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
