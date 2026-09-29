# ✉️ Brevo MCP

[![PyPI](https://img.shields.io/pypi/v/brevo-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/brevo-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/brevo-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Send transactional and bulk emails through the [Brevo](https://www.brevo.com/) API from your agent.

Needs a free `BREVO_API_KEY` (Settings → SMTP & API). Without it every tool answers
`ERROR: BREVO_API_KEY not set` and nothing is sent. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `send_email` | Send one transactional email; returns `OK: <messageId>` or `FAIL <status>` | `to`, `to_name`, `subject`, `html_content`, `sender_email = "marekcziba@gmail.com"`, `sender_name = "Marek Cziba"` |
| `send_bulk_emails` | Send a personalised message to many recipients, one line per result | `recipients`, `sender_email = "marekcziba@gmail.com"`, `sender_name = "Marek Cziba"` |
| `account_info` | Account email, company and plan as JSON | — |

Each item of `recipients` is `{"email": str, "name": str, "subject": str, "html": str}`.

## 🚀 Install

```bash
uvx brevo-mcp          # recommended, no installation
pip install brevo-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add brevo -- uvx brevo-mcp
```

Cursor, Windsurf, or any JSON-config client:

```json
{
  "mcpServers": {
    "brevo": {
      "command": "uvx",
      "args": ["brevo-mcp"],
      "env": {
        "BREVO_API_KEY": "your-api-key"
      }
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "brevo": {
      "type": "local",
      "command": ["uvx", "brevo-mcp"],
      "enabled": true,
      "environment": {
        "BREVO_API_KEY": "your-api-key"
      }
    }
  }
}
```

## 💡 Example session

```
You:  Send "Your quote is ready" to ada@example.com
Agent: [calls send_email]
       OK: <messageId>

You:  Check what plan this Brevo account is on
Agent: [calls account_info]
       {"email": "you@example.com", "company": "...", "plan": "..."}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/brevo-mcp
uv run ruff check servers/brevo-mcp
uv run ruff format servers/brevo-mcp
```

The suite needs **no API key and never sends an email**: it verifies the import, the three
tools registered on the server, their exact signatures, and that calls with
`BREVO_API_KEY` absent return the documented `ERROR: BREVO_API_KEY not set` within a
timeout — with `httpx.AsyncClient` stubbed out so any attempt to open a connection fails
the test.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
