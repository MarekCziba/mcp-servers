# 🎨 Color Converter MCP

[![PyPI](https://img.shields.io/pypi/v/color-converter-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/color-converter-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/color-converter-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Convert colors between HEX, RGB, HSL, HSV and CMYK — plus 16 named CSS colors.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `hex_to_rgb` | Convert HEX (`#FF0000` or `#F00`) to RGB | `hex_color` |
| `rgb_to_hex` | Convert RGB (0–255) to uppercase HEX | `r`, `g`, `b` |
| `rgb_to_hsl` | Convert RGB to HSL (degrees + percents) | `r`, `g`, `b` |
| `hex_to_all` | Convert HEX to HEX, RGB, HSL, HSV and CMYK at once | `hex_color` |
| `name_to_hex` | Convert a named color to HEX and RGB | `color_name` |

The leading `#` is optional, `#RGB` shorthand is expanded, and `name_to_hex` matches
names case-insensitively. An unknown name returns `{"error": "Unknown color: ..."}` rather
than raising. Named colors: red, green, blue, white, black, yellow, cyan, magenta, gray,
orange, purple, pink, brown, navy, teal and maroon.

## 🚀 Install

```bash
uvx color-converter-mcp          # recommended, no installation
pip install color-converter-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add color-converter -- uvx color-converter-mcp
```

```json
{
  "mcpServers": {
    "color-converter": {
      "command": "uvx",
      "args": ["color-converter-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "color-converter": {
      "type": "local",
      "command": ["uvx", "color-converter-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  What is #FF0000 in every format you support?
Agent: [calls hex_to_all]
       {"hex": "#FF0000", "rgb": {"r": 255, "g": 0, "b": 0},
        "hsl": {"h": 0, "s": 100, "l": 50}, "hsv": {"h": 0, "s": 100, "v": 100},
        "cmyk": {"c": 0.0, "m": 1.0, "y": 1.0, "k": 0.0}}

You:  Which HEX value is "orange", and what is #f00 in RGB?
Agent: [calls name_to_hex, hex_to_rgb]
       {"name": "orange", "hex": "#FFA500", "rgb": {"r": 255, "g": 165, "b": 0}}
       {"r": 255, "g": 0, "b": 0, "hex": "#f00"}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/color-converter-mcp
```

The tests assert against published CSS color values — `#FF0000` = RGB(255, 0, 0) =
`hsl(0 100% 50%)`, `#808080` = CMYK(0.5, 0.5, 0.5, 0.5) — and HEX↔RGB round-trips,
not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
