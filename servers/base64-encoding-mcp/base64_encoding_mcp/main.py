import base64
import html as htmlmod
import urllib.parse

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "base64-encoding-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


@mcp.tool()
async def encode_base64(text: str) -> str:
    """Encode text to Base64."""
    return base64.b64encode(text.encode()).decode()


@mcp.tool()
async def decode_base64(encoded: str) -> str:
    """Decode Base64 to text."""
    return base64.b64decode(encoded).decode()


@mcp.tool()
async def encode_base64url(text: str) -> str:
    """Encode text to Base64URL (safe for URLs)."""
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


@mcp.tool()
async def decode_base64url(encoded: str) -> str:
    """Decode Base64URL to text."""
    padding = 4 - len(encoded) % 4
    if padding != 4:
        encoded += "=" * padding
    return base64.urlsafe_b64decode(encoded).decode()


@mcp.tool()
async def encode_url(text: str) -> str:
    """URL-encode a string."""
    return urllib.parse.quote(text)


@mcp.tool()
async def decode_url(encoded: str) -> str:
    """URL-decode a string."""
    return urllib.parse.unquote(encoded)


@mcp.tool()
async def encode_html(text: str) -> str:
    """Escape HTML entities."""
    return htmlmod.escape(text)


@mcp.tool()
async def decode_html(encoded: str) -> str:
    """Unescape HTML entities."""
    return htmlmod.unescape(encoded)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
