"""Live tests for wikipedia-mcp — real Wikipedia API requests from this machine."""

import asyncio

import httpx
from wikipedia_mcp.main import (
    get_article_text,
    get_related_articles,
    get_summary,
    search_articles,
)

ATTEMPTS = 3
BOGUS_LANG = "zz-bogus-domain-987654"


async def _retry(factory):
    """Call the wrapped coroutine with a small retry budget — the API occasionally throttles."""
    for attempt in range(ATTEMPTS):
        try:
            return await factory()
        except httpx.HTTPError:
            if attempt == ATTEMPTS - 1:
                raise
            await asyncio.sleep(1.5)


async def test_search_articles_returns_ranked_matches() -> None:
    results = await _retry(lambda: search_articles("Python programming language", limit=5))
    assert results
    assert len(results) <= 5
    assert results[0]["title"]
    assert results[0]["url"].startswith("https://en.wikipedia.org/wiki/")
    assert "Python" in results[0]["snippet"]
    assert results[0]["wordcount"] > 1000


async def test_search_articles_respects_limit() -> None:
    results = await _retry(lambda: search_articles("artificial intelligence", limit=3))
    assert 1 <= len(results) <= 3


async def test_search_articles_no_results_returns_empty_list() -> None:
    results = await _retry(lambda: search_articles("zzqqxyzzy-not-a-real-token-827461", limit=5))
    assert results == []


async def test_search_articles_non_english_wikipedia() -> None:
    results = await _retry(lambda: search_articles("Python", limit=3, language="de"))
    assert results
    assert all(r["url"].startswith("https://de.wikipedia.org/") for r in results)


async def test_search_snippets_have_no_html_tags() -> None:
    results = await _retry(lambda: search_articles("Albert Einstein", limit=5))
    assert results
    for item in results:
        assert "<" not in item["snippet"] and ">" not in item["snippet"]


async def test_get_summary_known_article() -> None:
    summary = await _retry(lambda: get_summary("Albert Einstein"))
    assert summary["title"] == "Albert Einstein"
    assert "Einstein" in summary["extract"]
    assert summary["description"]
    assert summary["url"].startswith("https://en.wikipedia.org/wiki/Albert_Einstein")
    assert summary["thumbnail"].startswith("http")


async def test_get_summary_redirects_to_canonical_title() -> None:
    summary = await _retry(lambda: get_summary("Alan Turing"))
    assert summary["title"] in {"Alan Turing", "Turing, Alan"} or "Turing" in summary["title"]
    assert "Turing" in summary["extract"]


async def test_get_summary_missing_article_returns_error() -> None:
    summary = await _retry(lambda: get_summary("Zzqxyzzy not a real article 918273"))
    assert "error" in summary


async def test_get_article_text_truncates_to_max_chars() -> None:
    article = await _retry(lambda: get_article_text("Python (programming language)", max_chars=500))
    assert article["title"] == "Python (programming language)"
    assert len(article["text"]) == 500
    assert article["chars"] == 500
    assert article["truncated"] is True
    assert "Python" in article["text"]


async def test_get_article_text_returns_full_text_when_short_enough() -> None:
    article = await _retry(lambda: get_article_text("Dog", max_chars=500_000))
    assert article["truncated"] is False
    assert article["chars"] == len(article["text"])
    assert len(article["text"]) > 1000


async def test_get_article_text_resolves_redirects() -> None:
    article = await _retry(lambda: get_article_text("Gaiman", max_chars=500))
    assert "Gaiman" in article["title"]
    assert article["text"]


async def test_get_article_text_missing_returns_error() -> None:
    article = await _retry(lambda: get_article_text("Zzqxyzzy not a real article 918273"))
    assert "error" in article


async def test_get_related_articles_lists_outgoing_links() -> None:
    links = await _retry(lambda: get_related_articles("Albert Einstein", limit=8))
    assert links
    assert len(links) <= 8
    for link in links:
        assert link["title"]
        assert link["url"].startswith("https://en.wikipedia.org/wiki/")


async def test_get_related_articles_missing_returns_empty_list() -> None:
    links = await _retry(lambda: get_related_articles("Zzqxyzzy not a real article 918273"))
    assert links == []


async def test_bogus_language_domain_raises_http_error() -> None:
    try:
        await _retry(lambda: get_summary("Einstein", language=BOGUS_LANG))
    except httpx.HTTPError:
        return
    raise AssertionError("expected httpx.HTTPError for a non-resolving Wikipedia domain")
