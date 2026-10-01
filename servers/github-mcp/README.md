# github-mcp

Search GitHub and read repositories, issues, files and READMEs over the Model
Context Protocol (MCP) — with **zero API keys** for everything public.

Anonymous GitHub REST API access is enough for all five tools (60 requests/hour);
set an optional `GITHUB_TOKEN` if you want authenticated access (5,000/hour) or
private repositories.

## Tools (5)

| Tool | What it does |
| --- | --- |
| `search_repositories` | Search public repos by stars — full name, stats, language, topics |
| `get_repository` | Metadata for one repo: stars, forks, license, topics, default branch, last push |
| `list_issues` | Issues and pull requests of a repo (open/closed/all, flags PRs) |
| `get_file_contents` | Read a text file from a repo (base64-decoded, size, truncation flag) |
| `get_readme` | Fetch a repo's README as plain Markdown |

## Quick start

```bash
uvx --from "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/github-mcp" github-mcp
```

### Claude Desktop / Claude Code config

```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/MarekCziba/mcp-servers#subdirectory=servers/github-mcp",
        "github-mcp"
      ],
      "env": { "GITHUB_TOKEN": "ghp_optional_for_private_repos" }
    }
  }
}
```

`GITHUB_TOKEN` is optional — omit it for public-repo use.

## Development

Live tests against the real GitHub API from your machine:

```bash
uv run pytest servers/github-mcp -v   # 11 tests
uv run ruff check servers/github-mcp
```

MIT license.
