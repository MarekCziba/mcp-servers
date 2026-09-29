import re
import secrets
import string
import uuid

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "uuid-generator-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


@mcp.tool()
async def generate_uuid(version: int = 4) -> str:
    """Generate a UUID. Version 4 (random) or 7 (time-ordered)."""
    if version == 7:
        return str(uuid.uuid7())
    return str(uuid.uuid4())


@mcp.tool()
async def generate_nanoid(size: int = 21) -> str:
    """Generate a nano-style ID. Size defaults to 21 characters."""
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(secrets.choice(alphabet) for _ in range(size))


@mcp.tool()
async def generate_slug(text: str, max_length: int = 80) -> str:
    """Convert text to a URL-friendly slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug[:max_length].rstrip("-")


@mcp.tool()
async def generate_random_string(
    length: int = 16, include_digits: bool = True, include_symbols: bool = False
) -> str:
    """Generate a random string with configurable character sets."""
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_symbols:
        chars += string.punctuation
    return "".join(secrets.choice(chars) for _ in range(length))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
