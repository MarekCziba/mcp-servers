import feedparser
import httpx
from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "rss-feed-reader-mcp"
mcp = MCPServer(MCP_SERVER_NAME)
USER_AGENT = "Mozilla/5.0 (compatible; MarekCziba-MCP/1.0)"


async def fetch_feed(url: str) -> dict:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        raw = resp.text

    parsed = feedparser.parse(raw)
    feed_info = {
        "title": parsed.feed.get("title", ""),
        "link": parsed.feed.get("link", ""),
        "description": parsed.feed.get("subtitle", parsed.feed.get("description", "")),
        "language": parsed.feed.get("language", ""),
        "entries": [
            {
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "published": e.get("published", ""),
                "summary": e.get("summary", "")[:1000],
                "authors": [a.get("name", "") for a in e.get("authors", [])],
            }
            for e in parsed.entries[:50]
        ],
    }
    return feed_info


async def search_feeds(url: str, keyword: str) -> list[dict]:
    feed = await fetch_feed(url)
    keyword_lower = keyword.lower()
    matches = [e for e in feed["entries"] if keyword_lower in (e["title"] + e["summary"]).lower()]
    return matches[:20]


@mcp.tool()
async def get_feed(feed_url: str) -> dict:
    """Fetch and parse an RSS/Atom feed. Returns feed metadata and up to 50 entries."""
    return await fetch_feed(feed_url)


@mcp.tool()
async def get_multiple_feeds(feed_urls: list[str]) -> list[dict]:
    """Fetch multiple RSS/Atom feeds at once. Returns list of feed objects."""
    results = []
    for url in feed_urls:
        try:
            results.append(await fetch_feed(url))
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results


@mcp.tool()
async def search_feed(feed_url: str, keyword: str) -> list[dict]:
    """Search entries in a feed by keyword. Returns matching entries."""
    return await search_feeds(feed_url, keyword)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
