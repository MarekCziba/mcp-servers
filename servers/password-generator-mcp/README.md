# 🔑 Password Generator MCP

[![PyPI](https://img.shields.io/pypi/v/password-generator-mcp?logo=pypi&logoColor=fff)](https://pypi.org/project/password-generator-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/password-generator-mcp?logo=python&logoColor=fff)](https://www.python.org/)
[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Generate secure passwords, memorable passphrases, numeric PINs and API keys from your agent.

No API key, no account, no telemetry. Everything is drawn with Python's `secrets`
module and generated locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `generate_password` | Secure random password from the full 94-character set | `length = 16`, `include_uppercase = True`, `include_digits = True`, `include_symbols = True` |
| `generate_passphrase` | Memorable passphrase from a 39-word list | `word_count = 4`, `separator = "-"` |
| `generate_pin` | Numeric PIN code | `length = 6` |
| `generate_api_key` | API key with an optional prefix | `prefix = "sk"`, `length = 32` |

`generate_password` always starts from lowercase letters and adds uppercase, digits and
`string.punctuation` as the flags allow — switch them all off for a lowercase-only secret.
`generate_api_key` joins prefix and body with `_` (`sk_…`); an empty prefix returns the bare
alphanumeric body.

## 🚀 Install

```bash
uvx password-generator-mcp          # recommended, no installation
pip install password-generator-mcp  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add password-generator -- uvx password-generator-mcp
```

```json
{
  "mcpServers": {
    "password-generator": {
      "command": "uvx",
      "args": ["password-generator-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "password-generator": {
      "type": "local",
      "command": ["uvx", "password-generator-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  A 20-character password with no symbols, please
Agent: [calls generate_password with length=20, include_symbols=false]
       kT9vQx2LmR7pWz4NbYsD

You:  A five-word passphrase separated by spaces
Agent: [calls generate_passphrase with word_count=5, separator=" "]
       alpha river moon gold stone

You:  A 4-digit PIN and an API key for a Stripe-style key starting with "pk"
Agent: [calls generate_pin, generate_api_key]
       7041
       pk_Gm2Xq8vRt1LzP0wE5nHs9jKf3dQy6Ub
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/password-generator-mcp
```

The tests assert length, character-set, word-list and format constraints plus randomness
sanity — nothing is compared against a second run of the same generator.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
