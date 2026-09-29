"""Live tests for seo-analyzer-mcp — real pages fetched from this machine."""

import httpx
import pytest
from seo_analyzer_mcp.main import analyze_multiple, analyze_page, analyze_seo, extract_links

EXAMPLE = "https://example.com"
DOCS = "https://docs.python.org/3/tutorial/"
BOGUS = "https://seo-analyzer-test-invalid-domain-987654.invalid/"


async def test_analyze_seo_example_com_live() -> None:
    result = await analyze_seo(EXAMPLE)
    assert result["url"] == EXAMPLE
    assert result["status_code"] == 200
    assert result["title"] == "Example Domain"
    assert result["title_length"] == 14
    assert result["title_ok"] is False
    assert result["meta_description"] == ""
    assert result["headings"]["h1"] == []
    assert result["has_h1"] is False
    assert result["images"] == {"total": 0, "missing_alt": 0, "alt_ok": True}
    assert result["canonical"] == ""
    assert result["og_tags"] == {}
    assert result["structured_data"] == 0
    assert 0 < result["word_count"] < 100
    assert result["links"]["external"] >= 1


async def test_analyze_seo_python_docs_live() -> None:
    result = await analyze_seo(DOCS)
    assert result["title"].startswith("The Python Tutorial")
    assert result["title_ok"] is True
    assert result["meta_description"].startswith("Python is an easy to learn")
    assert result["meta_description_length"] > 160
    assert result["meta_description_ok"] is False
    assert result["has_h1"] is True
    assert len(result["headings"]["h1"]) == 1
    assert result["headings"]["h3"]
    assert result["images"]["total"] >= 1
    assert result["images"]["alt_ok"] is True
    assert result["canonical"].startswith("https://docs.python.org/3/tutorial/")
    assert "og:title" in result["og_tags"]
    assert result["structured_data"] >= 0
    assert result["word_count"] > 500


async def test_extract_links_live() -> None:
    example_links = await extract_links(EXAMPLE)
    assert example_links["url"] == EXAMPLE
    assert example_links["internal_links"] == []
    assert example_links["external_links"]
    assert all(link.startswith("http") for link in example_links["external_links"])

    docs_links = await extract_links(DOCS)
    all_links = docs_links["internal_links"] + docs_links["external_links"]
    assert all_links
    assert all(link.startswith("http") for link in all_links)
    assert len(all_links) == len(set(all_links))


async def test_analyze_multiple_error_isolation_live() -> None:
    results = await analyze_multiple([EXAMPLE, BOGUS, DOCS])
    assert [r["url"] for r in results] == [EXAMPLE, BOGUS, DOCS]
    assert "error" not in results[0]
    assert results[0]["title"] == "Example Domain"
    assert results[1]["error"]
    assert "error" not in results[2]
    assert results[2]["title"].startswith("The Python Tutorial")


async def test_invalid_url_raises_http_error() -> None:
    with pytest.raises(httpx.HTTPError):
        await analyze_seo(BOGUS)
    with pytest.raises(httpx.HTTPError):
        await extract_links(BOGUS)


def test_analyze_page_offline_synthetic_html() -> None:
    title = "A perfectly tuned SEO title for search engines"
    description = "Meta description for the synthetic test page. " * 3
    html = (
        "<html><head>"
        f"<title>{title}</title>"
        f'<meta name="description" content="{description}">'
        '<link rel="canonical" href="https://site.test/page">'
        '<meta property="og:title" content="OG Title">'
        '<script type="application/ld+json">{"@type": "WebPage"}</script>'
        "</head><body>"
        "<h1>Solo heading</h1><h2>Sub heading</h2>"
        '<img src="a.png" alt="a"><img src="b.png">'
        '<a href="https://site.test/x">x</a><a href="https://other.test/y">y</a>'
        "</body></html>"
    )
    result = analyze_page("https://site.test/page", html)
    assert result["title"] == title
    assert 30 <= result["title_length"] <= 60
    assert result["title_ok"] is True
    assert 120 <= result["meta_description_length"] <= 160
    assert result["meta_description_ok"] is True
    assert result["has_h1"] is True
    assert result["headings"]["h2"] == ["Sub heading"]
    assert result["images"] == {"total": 2, "missing_alt": 1, "alt_ok": False}
    assert result["canonical"] == "https://site.test/page"
    assert result["robots"] == ""
    assert result["og_tags"] == {"og:title": "OG Title"}
    assert result["structured_data"] == 1
    assert result["links"] == {"internal": 1, "external": 1}
    assert result["word_count"] > 5
