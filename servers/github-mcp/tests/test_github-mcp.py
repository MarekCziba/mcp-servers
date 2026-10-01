"""Live tests for github-mcp — real GitHub REST API requests from this machine."""

import asyncio

import httpx
from github_mcp.main import (
    get_file_contents,
    get_readme,
    get_repository,
    list_issues,
    search_repositories,
)

OWNER = "MarekCziba"
REPO = "mcp-servers"
ATTEMPTS = 3
BOGUS_REPO = "definitely-not-a-repo-918273"


async def _retry(factory):
    """Retry transient network failures; a real API error re-raises on the last attempt."""
    for attempt in range(ATTEMPTS):
        try:
            return await factory()
        except httpx.HTTPError:
            if attempt == ATTEMPTS - 1:
                raise
            await asyncio.sleep(2.0)


async def test_search_repositories_returns_ranked_matches() -> None:
    results = await _retry(lambda: search_repositories("model context protocol python", limit=3))
    assert results
    assert len(results) <= 3
    first = results[0]
    assert "/" in first["full_name"]
    assert first["stars"] >= 1
    assert first["url"].startswith("https://github.com/")
    assert isinstance(first["topics"], list)


async def test_search_repositories_respects_limit() -> None:
    results = await _retry(lambda: search_repositories("python", limit=2))
    assert 1 <= len(results) <= 2


async def test_get_repository_known_repo() -> None:
    repo = await _retry(lambda: get_repository(OWNER, REPO))
    assert repo["full_name"] == f"{OWNER}/{REPO}"
    assert repo["language"] == "Python"
    assert repo["stars"] >= 0
    assert repo["url"] == f"https://github.com/{OWNER}/{REPO}"
    assert isinstance(repo["forks"], int)
    assert repo["pushed_at"].startswith("20")


async def test_get_repository_missing_returns_error() -> None:
    repo = await _retry(lambda: get_repository(OWNER, BOGUS_REPO))
    assert "error" in repo


async def test_list_issues_returns_open_issues_with_urls() -> None:
    issues = await _retry(lambda: list_issues("python", "cpython", state="open", limit=5))
    assert issues
    assert len(issues) <= 5
    first = issues[0]
    assert first["number"] > 0
    assert first["title"]
    assert first["state"] in {"open", "closed"}
    assert isinstance(first["is_pull_request"], bool)
    expected_prefix = (
        "https://github.com/python/cpython/pull/"
        if first["is_pull_request"]
        else "https://github.com/python/cpython/issues/"
    )
    assert first["url"].startswith(expected_prefix)


async def test_list_issues_on_repo_without_issues_is_empty() -> None:
    issues = await _retry(lambda: list_issues(OWNER, BOGUS_REPO))
    assert issues == []


async def test_list_issues_rejects_unknown_state_and_falls_back() -> None:
    issues = await _retry(lambda: list_issues("python", "cpython", state="bogus", limit=2))
    assert issues
    assert all(i["state"] == "open" for i in issues)


async def test_get_file_contents_reads_real_readme() -> None:
    result = await _retry(lambda: get_file_contents(OWNER, REPO, "README.md"))
    assert result["path"] == "README.md"
    assert "# mcp-servers" in result["text"]
    assert result["size"] > 1000
    assert result["truncated"] is False
    assert result["url"].endswith("/README.md")


async def test_get_file_contents_missing_file_returns_error() -> None:
    result = await _retry(lambda: get_file_contents(OWNER, REPO, "no-such-file-918273.txt"))
    assert "error" in result


async def test_get_file_contents_directory_returns_error() -> None:
    result = await _retry(lambda: get_file_contents(OWNER, REPO, "servers"))
    assert "error" in result


async def test_get_readme_returns_markdown_text() -> None:
    result = await _retry(lambda: get_readme(OWNER, REPO))
    assert "# mcp-servers" in result["text"]
    assert result["url"].startswith("https://github.com/")
    assert len(result["text"]) > 1000
