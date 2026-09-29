import re

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "case-converter-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


def _split(text: str) -> list[str]:
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\b)|\d+", text)
    if not parts:
        parts = re.split(r"[\s_-]+", text)
    return [p.lower() for p in parts if p]


@mcp.tool()
async def to_camel_case(text: str) -> str:
    """Convert text to camelCase."""
    parts = _split(text)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


@mcp.tool()
async def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    return "".join(p.capitalize() for p in _split(text))


@mcp.tool()
async def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    return "_".join(_split(text))


@mcp.tool()
async def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    return "-".join(_split(text))


@mcp.tool()
async def to_upper_case(text: str) -> str:
    """Convert text to UPPER_CASE."""
    return "_".join(_split(text)).upper()


@mcp.tool()
async def to_title_case(text: str) -> str:
    """Convert text to Title Case."""
    return " ".join(p.capitalize() for p in _split(text))


@mcp.tool()
async def to_all_cases(text: str) -> dict:
    """Convert text to all case formats at once."""
    return {
        "camelCase": await to_camel_case(text),
        "PascalCase": await to_pascal_case(text),
        "snake_case": await to_snake_case(text),
        "kebab-case": await to_kebab_case(text),
        "UPPER_CASE": await to_upper_case(text),
        "Title Case": await to_title_case(text),
        "lowercase": "".join(_split(text)),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
