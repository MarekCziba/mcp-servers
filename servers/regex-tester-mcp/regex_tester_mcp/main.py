import re

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "regex-tester-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


@mcp.tool()
async def test_regex(pattern: str, text: str, flags: str = "") -> dict:
    """Test a regex pattern against text. Returns matches with positions."""
    f = 0
    if "i" in flags:
        f |= re.IGNORECASE
    if "m" in flags:
        f |= re.MULTILINE
    if "s" in flags:
        f |= re.DOTALL
    try:
        compiled = re.compile(pattern, f)
        matches = []
        for m in compiled.finditer(text):
            matches.append(
                {
                    "match": m.group(),
                    "start": m.start(),
                    "end": m.end(),
                    "groups": list(m.groups()) if m.groups() else None,
                }
            )
        return {
            "valid": True,
            "pattern": pattern,
            "matches": matches,
            "count": len(matches),
            "error": None,
        }
    except re.error as e:
        return {"valid": False, "pattern": pattern, "matches": [], "count": 0, "error": str(e)}


@mcp.tool()
async def replace_regex(pattern: str, replacement: str, text: str, flags: str = "") -> str:
    """Replace all regex matches in text with replacement string."""
    f = 0
    if "i" in flags:
        f |= re.IGNORECASE
    if "m" in flags:
        f |= re.MULTILINE
    if "s" in flags:
        f |= re.DOTALL
    return re.sub(pattern, replacement, text, flags=f)


@mcp.tool()
async def split_regex(pattern: str, text: str) -> list[str]:
    """Split text by regex pattern."""
    return re.split(pattern, text)


@mcp.tool()
async def validate_regex(pattern: str) -> dict:
    """Validate whether a regex pattern is syntactically correct."""
    try:
        re.compile(pattern)
        return {"valid": True, "pattern": pattern, "error": None}
    except re.error as e:
        return {"valid": False, "pattern": pattern, "error": str(e)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
