# 🔐 Hash & Checksum MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Generate and verify cryptographic hashes from your agent — MD5, SHA-1, SHA-256, SHA-512, CRC32, BLAKE2b and SHA3-256.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `generate_hash` | Hash a piece of text with one algorithm | `text`, `algorithm = "sha256"` |
| `generate_all_hashes` | Every supported algorithm at once, keyed by name | `text` |
| `verify_hash` | Compare text against an expected digest | `text`, `algorithm`, `expected_hash` |

Supported algorithms: `md5`, `sha1`, `sha256`, `sha512`, `crc32`, `blake2b`, `sha3_256`.

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/hash-checksum-mcp hash-checksum-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/hash-checksum-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add hash-checksum -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/hash-checksum-mcp hash-checksum-mcp
```

```json
{
  "mcpServers": {
    "hash-checksum": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/hash-checksum-mcp", "hash-checksum-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "hash-checksum": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/hash-checksum-mcp", "hash-checksum-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Hash "abc" with sha256 and tell me if it matches the NIST vector
Agent: [calls generate_hash]
       ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad

You:  Did the build artefact really come from release 4.2.1?
Agent: [calls verify_hash with the expected digest]
       {"match": true, ...}
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/hash-checksum-mcp
```

The tests assert against published NIST/RFC digest vectors — not against whatever the
implementation happens to return.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
