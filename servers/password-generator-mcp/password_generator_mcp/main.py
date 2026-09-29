import secrets
import string

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "password-generator-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


@mcp.tool()
async def generate_password(
    length: int = 16,
    include_uppercase: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
) -> str:
    """Generate a secure random password."""
    chars = string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_symbols:
        chars += string.punctuation
    return "".join(secrets.choice(chars) for _ in range(length))


@mcp.tool()
async def generate_passphrase(word_count: int = 4, separator: str = "-") -> str:
    """Generate a memorable passphrase from random words."""
    words = [
        "alpha",
        "bravo",
        "charlie",
        "delta",
        "echo",
        "foxtrot",
        "golf",
        "hotel",
        "india",
        "juliet",
        "kilo",
        "lima",
        "mike",
        "november",
        "oscar",
        "papa",
        "quebec",
        "romeo",
        "sierra",
        "tango",
        "uniform",
        "victor",
        "whiskey",
        "xray",
        "yankee",
        "zulu",
        "cloud",
        "star",
        "moon",
        "sun",
        "river",
        "lake",
        "mountain",
        "forest",
        "stone",
        "iron",
        "copper",
        "silver",
        "gold",
    ]
    picked = [secrets.choice(words) for _ in range(word_count)]
    return separator.join(picked)


@mcp.tool()
async def generate_pin(length: int = 6) -> str:
    """Generate a numeric PIN code."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


@mcp.tool()
async def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
    """Generate an API key with optional prefix."""
    chars = string.ascii_letters + string.digits
    key = "".join(secrets.choice(chars) for _ in range(length))
    return f"{prefix}_{key}" if prefix else key


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
