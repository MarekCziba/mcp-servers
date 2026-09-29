"""MCP server that turns web pages into clean, LLM-ready Markdown."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from mcp.server.mcpserver import MCPServer

SERVER_NAME = "website-to-markdown"
USER_AGENT = (
    "Mozilla/5.0 (compatible; website-to-markdown-mcp/0.1; "
    "+https://github.com/MarekCziba/website-to-markdown-mcp)"
)
DEFAULT_MAX_LENGTH = 50_000
DEFAULT_TIMEOUT = 30.0
MAX_CONCURRENCY = 5
MIN_EXTRACTED_LENGTH = 50
STRIP_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "aside", "form")

mcp = MCPServer(
    SERVER_NAME,
    instructions=(
        "Converts web pages into clean Markdown for LLM context. "
        "Use fetch_url for a single page, fetch_urls for batches, "
        "extract_metadata for title/description/Open Graph tags."
    ),
)


def _validate_url(url: str) -> None:
    """Reject anything that is not an absolute http(s) URL."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported URL scheme in {url!r}: only http and https are allowed")
    if not parsed.netloc:
        raise ValueError(f"Invalid URL (missing host): {url!r}")


def _page_title(html: str) -> str | None:
    """Return the <title> text of a page, if any."""
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("title")
    return title.get_text(strip=True) if title else None


def _ensure_h1(markdown: str, html: str) -> str:
    """Prepend the document title as an H1 when extraction dropped it."""
    first_line = markdown.lstrip().splitlines()[0].lstrip() if markdown.strip() else ""
    if first_line.startswith("#"):
        return markdown
    title = _page_title(html)
    if not title:
        return markdown
    return f"# {title}\n\n{markdown}"


async def fetch_page(url: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Fetch one URL and return clean Markdown text."""
    _validate_url(url)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en"}
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=DEFAULT_TIMEOUT, headers=headers
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    extracted = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=True,
        include_images=True,
        url=url,
    )
    if extracted and len(extracted) >= MIN_EXTRACTED_LENGTH:
        markdown = _ensure_h1(extracted, html)
        return markdown[:max_length]

    soup = BeautifulSoup(html, "lxml")
    for tag in soup(STRIP_TAGS):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    if len(text) < MIN_EXTRACTED_LENGTH:
        text = md(html, heading_style="ATX")
    return text[:max_length]


async def fetch_pages(
    urls: list[str],
    max_length: int = DEFAULT_MAX_LENGTH,
) -> list[dict[str, str | None]]:
    """Fetch several URLs concurrently, returning ``{url, markdown, error}`` dicts."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def _one(url: str) -> dict[str, str | None]:
        async with semaphore:
            try:
                return {"url": url, "markdown": await fetch_page(url, max_length), "error": None}
            except Exception as exc:
                return {"url": url, "markdown": None, "error": f"{type(exc).__name__}: {exc}"}

    return list(await asyncio.gather(*(_one(url) for url in urls)))


async def page_metadata(url: str) -> dict[str, str]:
    """Extract title, description, author and Open Graph fields from a page."""
    _validate_url(url)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en"}
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=DEFAULT_TIMEOUT, headers=headers
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "lxml")
    meta: dict[str, str] = {}

    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        meta["title"] = title_tag.get_text(strip=True)

    for name in ("description", "author", "keywords"):
        tag = soup.find("meta", attrs={"name": name}) or soup.find(
            "meta", attrs={"property": f"og:{name}"}
        )
        if tag and tag.get("content"):
            meta[name] = tag["content"]

    for prop in ("og:title", "og:description", "og:image", "og:url", "og:type"):
        tag = soup.find("meta", attrs={"property": prop})
        if tag and tag.get("content"):
            meta[prop.replace("og:", "og_")] = tag["content"]

    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href"):
        meta["canonical"] = canonical["href"]

    return meta


@mcp.tool()
async def fetch_url(url: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Fetch a single web page and convert it to clean Markdown.

    Args:
        url: Absolute http(s) URL of the page to convert.
        max_length: Maximum number of characters of Markdown to return.
    """
    return await fetch_page(url, max_length)


@mcp.tool()
async def fetch_urls(
    urls: list[str],
    max_length: int = DEFAULT_MAX_LENGTH,
) -> list[dict[str, str | None]]:
    """Fetch several web pages concurrently and convert each to Markdown.

    Args:
        urls: List of absolute http(s) URLs.
        max_length: Maximum number of characters of Markdown per page.
    """
    return await fetch_pages(urls, max_length)


@mcp.tool()
async def extract_metadata(url: str) -> dict[str, str]:
    """Extract page metadata (title, description, author, Open Graph tags).

    Args:
        url: Absolute http(s) URL of the page to inspect.
    """
    return await page_metadata(url)


def main() -> None:
    """Run the server over stdio (the default MCP transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
