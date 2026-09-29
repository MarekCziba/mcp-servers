# 🕒 Datetime Utility MCP

[![PyPI](https://img.shields.io/pypi/v/datetime-utility-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/datetime-utility-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/datetime-utility-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Timestamps, strftime formatting, timezone conversion and human-readable relative time from your agent.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `unix_timestamp` | Current Unix timestamp in seconds, milliseconds and ISO-8601 | — |
| `format_date` | Format a date using a strftime format string | `year`, `month`, `day`, `format_str = "%Y-%m-%d"` |
| `convert_timezone` | Convert a datetime string between timezones | `dt_str`, `from_tz = "UTC"`, `to_tz = "US/Eastern"`, `fmt = "%Y-%m-%d %H:%M:%S"` |
| `relative_time` | Human-readable relative time from a Unix timestamp | `unix_seconds = None` (defaults to now) |
| `list_timezones` | List available IANA timezones, optionally filtered | `query = ""` (returns the first 50 zones when empty) |

Timezones use the IANA names from `zoneinfo` (`UTC`, `US/Eastern`, `Asia/Tokyo`, …) and honour DST.
`relative_time` buckets: seconds (`just now`), minutes, hours and days — past and future.

## 🚀 Install

```bash
uvx datetime-utility-mcp          # recommended, no installation
pip install datetime-utility-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add datetime-utility -- uvx datetime-utility-mcp
```

```json
{
  "mcpServers": {
    "datetime-utility": {
      "command": "uvx",
      "args": ["datetime-utility-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "datetime-utility": {
      "type": "local",
      "command": ["uvx", "datetime-utility-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  What is noon UTC in Tokyo on 15 June 2023?
Agent: [calls convert_timezone]
       {"input": "2023-06-15 12:00:00", "from": "UTC", "to": "Asia/Tokyo",
        "result": "2023-06-15 21:00:00"}

You:  Format 25 December 2023 as %d/%m/%Y
Agent: [calls format_date]
       25/12/2023
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/datetime-utility-mcp
```

The tests assert against fixed timestamps and known DST boundaries — 08:00 in summer, 07:00 in
winter for US/Eastern — not against whatever the implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
