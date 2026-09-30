"""Unit tests for pure helpers — no network required."""

from __future__ import annotations

import pytest

from website_to_markdown_mcp.server import _ensure_h1, _page_title, _validate_url


def test_validate_url_accepts_http_and_https() -> None:
    _validate_url("https://example.com/path?q=1")
    _validate_url("http://example.com")


@pytest.mark.parametrize(
    "bad",
    ["ftp://example.com", "javascript:alert(1)", "example.com", "", "https://"],
    ids=["ftp", "javascript", "no-scheme", "empty", "no-host"],
)
def test_validate_url_rejects_bad_input(bad: str) -> None:
    with pytest.raises(ValueError):
        _validate_url(bad)


def test_page_title_extracts_title_text() -> None:
    html = "<html><head><title>  Hello World  </title></head><body></body></html>"
    assert _page_title(html) == "Hello World"


def test_page_title_returns_none_without_title() -> None:
    assert _page_title("<html><body><p>no title</p></body></html>") is None


def test_ensure_h1_prepends_title_when_heading_missing() -> None:
    markdown = "Some content without a heading."
    html = "<html><head><title>My Title</title></head><body></body></html>"
    out = _ensure_h1(markdown, html)
    assert out.startswith("# My Title\n\n")
    assert "Some content without a heading." in out


def test_ensure_h1_keeps_existing_heading() -> None:
    markdown = "# Already a heading\n\nBody."
    html = "<html><head><title>Other</title></head></html>"
    assert _ensure_h1(markdown, html) == markdown


def test_ensure_h1_without_title_returns_markdown_unchanged() -> None:
    markdown = "plain text content"
    assert _ensure_h1(markdown, "<html></html>") == markdown


def test_ensure_h1_handles_empty_markdown() -> None:
    assert _ensure_h1("", "<html></html>") == ""
