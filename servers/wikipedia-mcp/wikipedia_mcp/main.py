from urllib.parse import quote

import httpx
from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "wikipedia-mcp"
mcp = MCPServer(MCP_SERVER_NAME)
USER_AGENT = "MarekCziba-MCP/1.0 (https://github.com/MarekCziba/mcp-servers)"
MAX_LIMIT = 20
MIN_CHARS = 100


def _base_url(language: str) -> str:
    lang = "".join(ch for ch in language.strip().lower() if ch.isalnum() or ch == "-")
    return f"https://{lang or 'en'}.wikipedia.org"


def _wiki_url(language: str, title: str) -> str:
    return f"{_base_url(language)}/wiki/{quote(title.replace(' ', '_'), safe='')}"


def _strip_html(text: str) -> str:
    """Remove the HTML tags Wikipedia wraps around search-match highlights."""
    out: list[str] = []
    in_tag = False
    for ch in text:
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        elif not in_tag:
            out.append(ch)
    return "".join(out)


async def _get_json(url: str, params: dict) -> dict:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def search_articles(query: str, limit: int = 5, language: str = "en") -> list[dict]:
    """Search Wikipedia. Returns up to `limit` articles with title, snippet, word count and URL."""
    limit = max(1, min(int(limit), MAX_LIMIT))
    data = await _get_json(
        f"{_base_url(language)}/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet|wordcount",
            "format": "json",
        },
    )
    results = []
    for item in data.get("query", {}).get("search", []):
        title = item.get("title", "")
        results.append(
            {
                "title": title,
                "snippet": _strip_html(item.get("snippet", "")),
                "wordcount": item.get("wordcount", 0),
                "url": _wiki_url(language, title),
            }
        )
    return results


@mcp.tool()
async def get_summary(title: str, language: str = "en") -> dict:
    """Get the intro summary of a Wikipedia article (description, short extract, URL, thumbnail)."""
    url = (
        f"{_base_url(language)}/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}"
    )
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 404:
            return {"error": f"No Wikipedia article named '{title}' in {language}."}
        resp.raise_for_status()
        data = resp.json()
    return {
        "title": data.get("title", title),
        "description": data.get("description", ""),
        "extract": data.get("extract", ""),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        "thumbnail": (data.get("thumbnail") or {}).get("source", ""),
    }


@mcp.tool()
async def get_article_text(title: str, max_chars: int = 5000, language: str = "en") -> dict:
    """Get the plain text of a Wikipedia article, truncated to `max_chars` characters."""
    data = await _get_json(
        f"{_base_url(language)}/w/api.php",
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "titles": title,
            "redirects": 1,
            "format": "json",
        },
    )
    page = next(iter(data.get("query", {}).get("pages", {}).values()), {})
    extract = page.get("extract")
    if extract is None:
        return {"error": f"No Wikipedia article named '{title}' in {language}."}
    max_chars = max(MIN_CHARS, int(max_chars))
    return {
        "title": page.get("title", title),
        "text": extract[:max_chars],
        "chars": min(len(extract), max_chars),
        "truncated": len(extract) > max_chars,
    }


@mcp.tool()
async def get_related_articles(title: str, limit: int = 5, language: str = "en") -> list[dict]:
    """List articles linked from a Wikipedia article (outgoing links, main namespace only)."""
    limit = max(1, min(int(limit), MAX_LIMIT))
    data = await _get_json(
        f"{_base_url(language)}/w/api.php",
        {
            "action": "query",
            "prop": "links",
            "plnamespace": 0,
            "pllimit": limit,
            "titles": title,
            "redirects": 1,
            "format": "json",
        },
    )
    page = next(iter(data.get("query", {}).get("pages", {}).values()), {})
    return [
        {"title": link.get("title", ""), "url": _wiki_url(language, link.get("title", ""))}
        for link in page.get("links", [])
    ]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
