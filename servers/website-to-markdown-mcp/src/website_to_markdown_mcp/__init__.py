"""Website to Markdown MCP server."""

from website_to_markdown_mcp.server import (
    fetch_page,
    fetch_pages,
    main,
    page_metadata,
)

__version__ = "0.1.0"
__all__ = ["__version__", "fetch_page", "fetch_pages", "main", "page_metadata"]
