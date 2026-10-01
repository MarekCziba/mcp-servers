import base64
import os
from urllib.parse import quote

import httpx
from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "github-mcp"
mcp = MCPServer(MCP_SERVER_NAME)
API_BASE = "https://api.github.com"
USER_AGENT = "MarekCziba-MCP/1.0 (https://github.com/MarekCziba/mcp-servers)"
MAX_LIMIT = 20


def _headers() -> dict:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(f"{API_BASE}{path}", params=params, headers=_headers())
        if resp.status_code == 404:
            return {"error": resp.status_code}
        resp.raise_for_status()
        return resp.json()


def _repo_summary(repo: dict) -> dict:
    license_info = repo.get("license") or {}
    return {
        "full_name": repo.get("full_name", ""),
        "description": repo.get("description") or "",
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "language": repo.get("language") or "",
        "license": license_info.get("spdx_id", ""),
        "topics": repo.get("topics", []),
        "url": repo.get("html_url", ""),
        "default_branch": repo.get("default_branch", ""),
        "pushed_at": repo.get("pushed_at", ""),
    }


@mcp.tool()
async def search_repositories(query: str, limit: int = 5) -> list[dict]:
    """Search public GitHub repositories by stars. Returns full name, stats, language and topics."""
    limit = max(1, min(int(limit), MAX_LIMIT))
    data = await _get("/search/repositories", {"q": query, "per_page": limit, "sort": "stars"})
    if "error" in data:
        return []
    return [_repo_summary(item) for item in data.get("items", [])]


@mcp.tool()
async def get_repository(owner: str, repo: str) -> dict:
    """Get metadata for one repository: stars, forks, language, license, topics, default branch."""
    data = await _get(f"/repos/{quote(owner)}/{quote(repo)}")
    if "error" in data:
        return {"error": f"No GitHub repository '{owner}/{repo}'."}
    return _repo_summary(data)


@mcp.tool()
async def list_issues(owner: str, repo: str, state: str = "open", limit: int = 10) -> list[dict]:
    """List a repository's issues and pull requests. state: open, closed or all."""
    if state not in {"open", "closed", "all"}:
        state = "open"
    limit = max(1, min(int(limit), MAX_LIMIT))
    data = await _get(
        f"/repos/{quote(owner)}/{quote(repo)}/issues", {"state": state, "per_page": limit}
    )
    if not isinstance(data, list):
        return []
    return [
        {
            "number": item.get("number", 0),
            "title": item.get("title", ""),
            "state": item.get("state", ""),
            "is_pull_request": "pull_request" in item,
            "author": (item.get("user") or {}).get("login", ""),
            "comments": item.get("comments", 0),
            "created_at": item.get("created_at", ""),
            "url": item.get("html_url", ""),
        }
        for item in data
    ]


@mcp.tool()
async def get_file_contents(owner: str, repo: str, path: str, ref: str = "") -> dict:
    """Read a text file from a repository. Returns base64-decoded content plus size and URL."""
    params = {"ref": ref} if ref else None
    data = await _get(
        f"/repos/{quote(owner)}/{quote(repo)}/contents/{quote(path, safe='/')}", params
    )
    if "error" in data:
        return {"error": f"No file '{path}' in {owner}/{repo}."}
    if isinstance(data, list):
        return {"error": f"'{path}' is a directory in {owner}/{repo}, not a file."}
    if data.get("encoding") != "base64":
        return {"error": f"File '{path}' is not text (encoding={data.get('encoding')})."}
    text = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
    return {
        "path": data.get("path", path),
        "size": data.get("size", 0),
        "text": text,
        "truncated": bool(data.get("truncated")),
        "url": data.get("html_url", ""),
    }


@mcp.tool()
async def get_readme(owner: str, repo: str, ref: str = "") -> dict:
    """Fetch a repository's README as plain Markdown text."""
    params = {"ref": ref} if ref else None
    data = await _get(f"/repos/{quote(owner)}/{quote(repo)}/readme", params)
    if "error" in data:
        return {"error": f"No README found in {owner}/{repo}."}
    text = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
    return {
        "name": data.get("name", "README"),
        "text": text,
        "url": data.get("html_url", ""),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
