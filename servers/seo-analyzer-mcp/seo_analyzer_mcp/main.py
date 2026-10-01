from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "seo-analyzer-mcp"
mcp = MCPServer(MCP_SERVER_NAME)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def fetch_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text


def analyze_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    result = {"url": url, "status_code": 200}

    title_tag = soup.find("title")
    result["title"] = title_tag.get_text(strip=True) if title_tag else ""
    result["title_length"] = len(result["title"])
    result["title_ok"] = 30 <= result["title_length"] <= 60

    meta_desc = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = meta_desc.get("content", "").strip() if meta_desc else ""
    result["meta_description_length"] = len(result["meta_description"])
    result["meta_description_ok"] = 120 <= result["meta_description_length"] <= 160

    result["headings"] = {}
    for level in ["h1", "h2", "h3"]:
        tags = soup.find_all(level)
        result["headings"][level] = [h.get_text(strip=True) for h in tags if h.get_text(strip=True)]
    result["has_h1"] = len(result["headings"].get("h1", [])) == 1

    img_tags = soup.find_all("img")
    total_imgs = len(img_tags)
    missing_alt = sum(1 for img in img_tags if not img.get("alt"))
    result["images"] = {
        "total": total_imgs,
        "missing_alt": missing_alt,
        "alt_ok": total_imgs == 0 or missing_alt == 0,
    }

    canonical = soup.find("link", attrs={"rel": "canonical"})
    result["canonical"] = canonical.get("href") if canonical else ""

    robots = soup.find("meta", attrs={"name": "robots"})
    result["robots"] = robots.get("content", "") if robots else ""

    og_tags = {}
    for tag in soup.find_all("meta", attrs={"property": True}):
        prop = tag.get("property", "")
        if prop.startswith("og:"):
            og_tags[prop] = tag.get("content", "")
    result["og_tags"] = og_tags

    schema_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    result["structured_data"] = len(schema_scripts)

    text = soup.get_text(separator=" ", strip=True)
    words = text.split()
    result["word_count"] = len(words)

    links = soup.find_all("a", href=True)
    internal = []
    external = []
    domain = urlparse(url).netloc
    for a in links:
        href = a["href"]
        if href.startswith("http") and domain in href:
            internal.append(href)
        elif href.startswith("http"):
            external.append(href)
    result["links"] = {"internal": len(set(internal)), "external": len(set(external))}

    return result


@mcp.tool()
async def analyze_seo(url: str) -> dict:
    """Analyze a webpage for SEO best practices. Returns meta tags, headings, images, links, and more."""
    html = await fetch_html(url)
    return analyze_page(url, html)


@mcp.tool()
async def analyze_multiple(urls: list[str]) -> list[dict]:
    """Analyze SEO for multiple webpages. Returns list of analysis results."""
    results = []
    for url in urls:
        try:
            html = await fetch_html(url)
            results.append(analyze_page(url, html))
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results


@mcp.tool()
async def extract_links(url: str) -> dict:
    """Extract all internal and external links from a webpage."""
    html = await fetch_html(url)
    soup = BeautifulSoup(html, "lxml")
    domain = urlparse(url).netloc
    internal, external = [], []
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h.startswith("http") and domain in h:
            internal.append(h)
        elif h.startswith("http"):
            external.append(h)
    return {
        "url": url,
        "internal_links": list(set(internal)),
        "external_links": list(set(external)),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
