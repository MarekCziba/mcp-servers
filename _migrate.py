"""Migrate Apify/FastMCP servers to standalone MCPServer (mcp 2.x) stdio servers."""

import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\marek\mcp-servers\servers")

STANDARD_TAIL = '''
def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
'''

report = []
errors = []

for main_py in sorted(ROOT.glob("*/src/main.py")):
    server = main_py.parent.parent.name
    if server == "website-to-markdown-mcp":
        report.append(f"{server}: SKIP (already migrated)")
        continue

    text = main_py.read_text(encoding="utf-8")

    # 1. imports
    text = text.replace("from mcp.server.fastmcp import FastMCP", "from mcp.server.mcpserver import MCPServer")
    text = re.sub(r"^from apify import Actor\n", "", text, flags=re.M)
    text = re.sub(r"^import asyncio\n", "", text, flags=re.M)
    text = re.sub(r"^import os, ", "import ", text, flags=re.M)

    # 2. constructor: keep only the server name argument
    def ctor(m: re.Match) -> str:
        args = m.group(1)
        first = args.split(",")[0].strip()
        return f"mcp = MCPServer({first})"

    text, n_ctor = re.subn(r"mcp = FastMCP\((.*?)\)\n", lambda m: ctor(m) + "\n", text, flags=re.S)

    # 3. cut everything from the Apify/entry function to EOF, append stdio main
    lines = text.splitlines(keepends=True)
    cut = None
    seen_tool = False
    for i, line in enumerate(lines):
        if line.startswith("@mcp.tool"):
            seen_tool = True
        if seen_tool and re.match(r"^(async )?def (run_standby|main)\s*\(", line):
            cut = i
            break

    if cut is None:
        errors.append(f"{server}: no entry function found after tools")
        continue

    text = "".join(lines[:cut]).rstrip() + "\n" + STANDARD_TAIL

    # 4. leftover apify references?
    leftovers = [ln.strip() for ln in text.splitlines() if "Actor" in ln or "apify" in ln or "FastMCP" in ln or "run_stdio_async" in ln]

    main_py.write_text(text, encoding="utf-8", newline="\n")
    status = f"{server}: migrated (ctor x{n_ctor})"
    if leftovers:
        status += f" | LEFTOVERS: {leftovers}"
        errors.append(status)
    report.append(status)

print("\n".join(report))
if errors:
    print("\n=== PROBLEMY ===")
    print("\n".join(errors))
    sys.exit(1)
print("\nOK: wszystkie zmigrowane")
