"""Smoke-test every server: start it over stdio, run initialize + tools/list."""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Users\marek\mcp-servers")
SERVERS = sorted(p for p in (ROOT / "servers").iterdir() if p.is_dir())
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")

INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "smoke", "version": "0"},
    },
}
NOTIF = {"jsonrpc": "2.0", "method": "notifications/initialized"}
LIST = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

failures = []
summary = []

for server in SERVERS:
    payload = "\n".join(json.dumps(m) for m in (INIT, NOTIF, LIST)) + "\n"
    if (server / "src" / "website_to_markdown_mcp" / "server.py").exists():
        cmd, cwd = [PY, "-m", "website_to_markdown_mcp.server"], server / "src"
    else:
        cmd, cwd = [PY, "-m", f"{server.name.replace('-', '_')}.main"], server
    try:
        proc = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=45,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        failures.append(f"{server.name}: TIMEOUT")
        continue

    lines = [ln for ln in proc.stdout.splitlines() if ln.strip().startswith("{")]
    init_ok = any('"serverInfo"' in ln for ln in lines)
    tools = []
    for ln in lines:
        try:
            msg = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2 and "result" in msg:
            tools = [t["name"] for t in msg["result"].get("tools", [])]

    if init_ok and tools:
        summary.append(f"{server.name}: OK, tools={tools}")
    else:
        err = proc.stderr.strip().splitlines()
        tail = err[-1] if err else "(brak stderr)"
        failures.append(f"{server.name}: init_ok={init_ok}, tools={tools}, err={tail}")

print("\n".join(summary))
if failures:
    print("\n=== FAILURES ===")
    print("\n".join(failures))
    sys.exit(1)
print(f"\nOK: {len(SERVERS)} serwerow odpowiada poprawnie")
