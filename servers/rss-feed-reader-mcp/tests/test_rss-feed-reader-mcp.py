"""Live tests for rss-feed-reader-mcp — real feeds fetched from this machine."""

import asyncio

import httpx
import pytest
from rss_feed_reader_mcp.main import get_feed, get_multiple_feeds, search_feed

HNRSS = "https://hnrss.org/frontpage"
BBC = "https://feeds.bbci.co.uk/news/rss.xml"
BOGUS = "https://feed-reader-test-invalid-domain-987654.invalid/rss.xml"

ENTRY_KEYS = {"title", "link", "published", "summary", "authors"}
ATTEMPTS = 3


async def _get_feed(url: str) -> dict:
    """Fetch with a small retry budget — hnrss.org occasionally drops connections."""
    for attempt in range(ATTEMPTS):
        try:
            return await get_feed(url)
        except httpx.HTTPError:
            if attempt == ATTEMPTS - 1:
                raise
            await asyncio.sleep(1.5)


async def _search_feed(url: str, keyword: str) -> list[dict]:
    for attempt in range(ATTEMPTS):
        try:
            return await search_feed(url, keyword)
        except httpx.HTTPError:
            if attempt == ATTEMPTS - 1:
                raise
            await asyncio.sleep(1.5)


async def _get_multiple_feeds(urls: list[str], good_indexes: set[int]) -> list[dict]:
    results: list[dict] = []
    for attempt in range(ATTEMPTS):
        results = await get_multiple_feeds(urls)
        if all("error" not in results[i] for i in good_indexes):
            return results
        await asyncio.sleep(1.5)
    return results


async def test_get_feed_hnrss_live() -> None:
    feed = await _get_feed(HNRSS)
    assert "Hacker News" in feed["title"]
    assert feed["link"].startswith("http")
    assert len(feed["entries"]) >= 10
    for entry in feed["entries"]:
        assert set(entry) == ENTRY_KEYS
        assert entry["title"]
        assert entry["link"].startswith("http")
        assert entry["published"]
        assert isinstance(entry["authors"], list)
        assert len(entry["summary"]) <= 1000


async def test_get_feed_bbc_live() -> None:
    feed = await _get_feed(BBC)
    assert feed["title"] == "BBC News"
    assert 10 <= len(feed["entries"]) <= 50
    first = feed["entries"][0]
    assert first["title"] and first["link"].startswith("http") and first["published"]


async def test_search_feed_keyword_live() -> None:
    matches = await _search_feed(BBC, "the")
    assert matches, "BBC front page must contain entries mentioning 'the'"
    assert len(matches) <= 20
    for entry in matches:
        assert set(entry) == ENTRY_KEYS
        assert "the" in (entry["title"] + entry["summary"]).lower()


async def test_search_feed_is_case_insensitive_and_handles_no_match() -> None:
    lower = await _search_feed(BBC, "the")
    upper = await _search_feed(BBC, "THE")
    assert len(lower) == len(upper)
    assert lower
    empty = await _search_feed(HNRSS, "zzzqqqxyzzy-not-a-real-token")
    assert empty == []


async def test_get_multiple_feeds_isolates_failures() -> None:
    results = await _get_multiple_feeds([HNRSS, BOGUS, BBC], good_indexes={0, 2})
    assert len(results) == 3
    assert "error" not in results[0]
    assert "entries" in results[0] and results[0]["entries"]
    assert results[1]["url"] == BOGUS
    assert results[1]["error"]
    assert "error" not in results[2]
    assert "entries" in results[2] and results[2]["entries"]


async def test_bogus_feed_url_raises_http_error() -> None:
    with pytest.raises(httpx.HTTPError):
        await _get_feed(BOGUS)
    with pytest.raises(httpx.HTTPError):
        await _search_feed(BOGUS, "anything")
