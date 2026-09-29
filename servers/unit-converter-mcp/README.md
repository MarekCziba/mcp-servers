# ⚖️ Unit Converter MCP

[![PyPI](https://img.shields.io/pypi/v/unit-converter-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/unit-converter-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/unit-converter-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Convert length, weight, volume, speed, area, pressure, energy, digital and temperature units from your agent.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `convert` | Convert a value between any supported units | `value`, `from_unit`, `to_unit`, `category = ""` |
| `convert_length` | Convert length: mm, cm, m, km, in, ft, yd, mi | `value`, `from_unit`, `to_unit` |
| `convert_weight` | Convert weight: mg, g, kg, t, oz, lb, st | `value`, `from_unit`, `to_unit` |
| `convert_temperature` | Convert temperature: C, F, K | `value`, `from_unit`, `to_unit` |
| `list_units` | List all available units, optionally filtered by category | `category = ""` |

`convert` auto-detects the category when both units belong to the same one; categories are
`length`, `weight`, `volume`, `speed`, `area`, `pressure`, `energy` and `digital`
(temperature has its own tool). Unknown units or categories return an `{"error": "..."}` dict.
Results are rounded: 10 decimals for `convert`, 4 for `convert_temperature`.

## 🚀 Install

```bash
uvx unit-converter-mcp          # recommended, no installation
pip install unit-converter-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add unit-converter -- uvx unit-converter-mcp
```

```json
{
  "mcpServers": {
    "unit-converter": {
      "command": "uvx",
      "args": ["unit-converter-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "unit-converter": {
      "type": "local",
      "command": ["uvx", "unit-converter-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  How many centimetres is 1 inch?
Agent: [calls convert_length]
       {"value": 1, "from": "in", "to": "cm", "result": 2.54, "category": "length"}

You:  Is 100 °C hot in Fahrenheit, and what is 0 °C in Kelvin?
Agent: [calls convert_temperature twice]
       {"result": 212.0, ...}    {"result": 273.15, ...}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/unit-converter-mcp
```

The tests assert against published unit definitions — 0 °C = 32 °F = 273.15 K, 1 in = 2.54 cm,
1 KiB = 1024 B — not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
