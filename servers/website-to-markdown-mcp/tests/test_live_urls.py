"""Live tests: fetch real pages and assert on the actual converted output."""

from __future__ import annotations

import pytest

from website_to_markdown_mcp.server import (
    _validate_url,
    fetch_page,
    fetch_pages,
    page_metadata,
)

EXAMPLE_URL = "https://example.com"
PYTHON_URL = "https://docs.python.org/3/tutorial/"
WIKI_URL = "https://en.wikipedia.org/wiki/Model_Context_Protocol"

HTML_MARKERS = ("<html", "<div", "<p>", "<script", "<h1")


def _assert_markdown(text: str) -> None:
    assert text.strip(), "converter returned empty output"
    lowered = text.lower()
    for marker in HTML_MARKERS:
        assert marker not in lowered, f"raw HTML leaked into Markdown: {marker!r}"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (EXAMPLE_URL, "Example Domain"),
        (PYTHON_URL, "Python Tutorial"),
        (WIKI_URL, "Model Context Protocol"),
    ],
    ids=["example.com", "docs.python.org", "wikipedia"],
)
async def test_fetch_url_live(url: str, expected: str) -> None:
    markdown = await fetch_page(url)
    _assert_markdown(markdown)
    assert expected in markdown, f"expected {expected!r} in Markdown for {url}"
    assert len(markdown) > 100, f"suspiciously short output for {url}: {len(markdown)} chars"


async def test_output_is_markdown_not_html() -> None:
    markdown = await fetch_page(EXAMPLE_URL)
    assert markdown.lstrip().startswith("#"), "output must open with a Markdown heading"
    assert "Example Domain" in markdown.splitlines()[0]


async def test_max_length_is_respected() -> None:
    markdown = await fetch_page(PYTHON_URL, max_length=500)
    assert len(markdown) <= 500


async def test_metadata_live() -> None:
    meta = await page_metadata(PYTHON_URL)
    assert "Python Tutorial" in meta["title"]
    assert "description" in meta, "python.org ships a meta description, it must be extracted"

    example_meta = await page_metadata(EXAMPLE_URL)
    assert example_meta["title"] == "Example Domain"


async def test_batch_live_mixed_results() -> None:
    results = await fetch_pages([EXAMPLE_URL, "not-a-url", WIKI_URL])
    assert [r["url"] for r in results] == [EXAMPLE_URL, "not-a-url", WIKI_URL]
    assert results[0]["error"] is None
    assert "Example Domain" in results[0]["markdown"]
    assert results[1]["error"], "invalid URL must be reported as an error"
    assert results[1]["markdown"] is None
    assert results[2]["error"] is None
    assert "Model Context Protocol" in results[2]["markdown"]


def test_url_validation_rejects_bad_input() -> None:
    for bad in ("ftp://example.com", "javascript:alert(1)", "example.com", ""):
        with pytest.raises(ValueError):
            _validate_url(bad)
    _validate_url("https://example.com/path?q=1")
