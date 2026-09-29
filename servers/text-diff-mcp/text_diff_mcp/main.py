import difflib
import json

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "text-diff-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


@mcp.tool()
async def unified_diff(text1: str, text2: str, context_lines: int = 3) -> str:
    """Compare two texts and return a unified diff."""
    lines1, lines2 = text1.splitlines(keepends=True), text2.splitlines(keepends=True)
    return "".join(difflib.unified_diff(lines1, lines2, n=context_lines))


@mcp.tool()
async def diff_json(text1: str, text2: str) -> str:
    """Compare two texts and return differences as JSON."""
    lines1, lines2 = text1.splitlines(), text2.splitlines()
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    changes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            changes.append(
                {
                    "type": tag,
                    "text1_start": i1,
                    "text1_end": i2,
                    "text2_start": j1,
                    "text2_end": j2,
                }
            )
    return json.dumps(changes, indent=2)


@mcp.tool()
async def similarity_ratio(text1: str, text2: str) -> dict:
    """Calculate the similarity ratio between two texts."""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    ratio = matcher.ratio()
    return {"ratio": round(ratio, 4), "percentage": round(ratio * 100, 2)}


@mcp.tool()
async def html_diff(text1: str, text2: str = "") -> str:
    """Compare two texts and return HTML with highlighted changes."""
    lines1, lines2 = text1.splitlines(), text2.splitlines()
    return difflib.HtmlDiff().make_table(lines1, lines2, context=True, numlines=2)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
