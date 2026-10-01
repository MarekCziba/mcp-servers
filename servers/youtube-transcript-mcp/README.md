# 🎬 YouTube Transcript MCP

[![CI](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml/badge.svg)](https://github.com/MarekCziba/mcp-servers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE)

> Turn any YouTube video into a timestamped transcript — plus oEmbed metadata and the list of available languages.

No API key, no account, no telemetry. Runs locally over stdio.

## 🧰 Tools

| Tool | Description | Arguments |
|------|-------------|-----------|
| `get_transcript` | Transcript as `[MM:SS] text` lines, one per cue | `video_url`, `language = "en"` |
| `get_video_info` | Video metadata (title, author, thumbnail, embed HTML) as JSON | `video_url` |
| `list_languages` | Available transcript languages as JSON: `language`, `code`, `generated` | `video_url` |

`video_url` accepts a full `watch?v=` URL, a `youtu.be` short link, an `embed`/`shorts` URL
or a bare 11-character video ID. Failures never raise — the tools return a
`{"error": "..."}` JSON string instead.

## 🚀 Install

```bash
uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/youtube-transcript-mcp youtube-transcript-mcp          # recommended, no installation
pip install "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/youtube-transcript-mcp"  # or with pip
```

## 🔌 Connect your MCP client

```bash
claude mcp add youtube-transcript -- uvx --from git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/youtube-transcript-mcp youtube-transcript-mcp
```

Cursor, Windsurf, or any JSON-config client:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/youtube-transcript-mcp", "youtube-transcript-mcp"]
    }
  }
}
```

opencode (`opencode.json`):

```json
{
  "mcp": {
    "youtube-transcript": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/youtube-transcript-mcp", "youtube-transcript-mcp"],
      "enabled": true
    }
  }
}
```

## 💡 Example session

```
You:  Give me the transcript of https://youtu.be/dQw4w9WgXcQ
Agent: [calls get_transcript]
       [00:01] [♪♪♪]
       [00:18] ♪ We're no strangers to love ♪
       [00:22] ♪ You know the rules ...

You:  Who uploaded it and what languages can you read it in?
Agent: [calls get_video_info, then list_languages]
       {"title": "Rick Astley - Never Gonna Give You Up ...", "author_name": "Rick Astley"}
       [{"language": "English", "code": "en", "generated": false}, ...]
```

## 🧪 Development

Part of the [MarekCziba/mcp-servers](https://github.com/MarekCziba/mcp-servers) monorepo.

```bash
uv sync
uv run pytest servers/youtube-transcript-mcp
uv run ruff check servers/youtube-transcript-mcp
uv run ruff format servers/youtube-transcript-mcp
```

The suite uses the real video `dQw4w9WgXcQ` and asserts **actual content**: timestamped
transcript lines, the known lyric line, oEmbed title/author/thumbnail and the real list of
transcript languages. If YouTube is unreachable or blocks your IP, the tools do not raise —
they return a `{"error": "..."}` JSON string, so the live assertions fail instead of the
process hanging; re-run from a network that can reach YouTube. Invalid URLs and a
well-formed but non-existent video ID are always tested and must come back as that error
JSON.

## 📄 License

MIT — see [LICENSE](https://github.com/MarekCziba/mcp-servers/blob/main/LICENSE).

---

Built by **Marek Cziba** · [GitHub](https://github.com/MarekCziba) · [marekcziba@gmail.com](mailto:marekcziba@gmail.com)
