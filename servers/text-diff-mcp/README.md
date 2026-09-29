# 🆚 Text Diff MCP

[![PyPI](https://img.shields.io/pypi/v/text-diff-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/text-diff-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/text-diff-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Compare two texts — unified diff, structured JSON opcodes, a similarity score or a side-by-side HTML table.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `unified_diff` | Compare two texts and return a unified diff | `text1`, `text2`, `context_lines = 3` |
| `diff_json` | Compare two texts and return differences as JSON | `text1`, `text2` |
| `similarity_ratio` | Character-level similarity ratio between two texts | `text1`, `text2` |
| `html_diff` | Side-by-side HTML table with changes highlighted | `text1`, `text2 = ""` |

`unified_diff` returns a standard unified diff string — empty when the texts are identical.
`diff_json` returns one object per changed hunk: `type` (`insert`, `replace` or `delete`) plus
`text1_start` / `text1_end` / `text2_start` / `text2_end` line offsets.
`similarity_ratio` returns `{"ratio": 0.8, "percentage": 80.0}`.

## 🚀 Install

```bash
uvx text-diff-mcp          # recommended, no installation
pip install text-diff-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add text-diff -- uvx text-diff-mcp
```

```json
{
  "mcpServers": {
    "text-diff": {
      "command": "uvx",
      "args": ["text-diff-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "text-diff": {
      "type": "local",
      "command": ["uvx", "text-diff-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  What changed between "Hello World\n" and "Hello MCP World\n"?
Agent: [calls unified_diff]
       --- 
       +++
       @@ -1 +1 @@
       -Hello World
       +Hello MCP World

You:  How similar are "hello" and "hallo"?
Agent: [calls similarity_ratio]
       {"ratio": 0.8, "percentage": 80.0}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/text-diff-mcp
```

The tests assert against hand-computed unified diffs, opcodes and similarity values — not against
whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
