"""Rename src/ layout to unique importable packages + emit pyproject per server."""

import re
from pathlib import Path

ROOT = Path(r"C:\Users\marek\mcp-servers\servers")
FLAGSHIP = "website-to-markdown-mcp"

DESC = {
    "base64-encoding-mcp": "Encode and decode Base64, Base64URL, URL and HTML entities over MCP.",
    "brevo-mcp": "Send transactional and bulk emails through the Brevo API over MCP.",
    "case-converter-mcp": "Convert text between camelCase, snake_case, kebab-case and more over MCP.",
    "color-converter-mcp": "Convert colors between HEX, RGB, HSL and CMYK over MCP.",
    "data-converter-mcp": "Convert data between JSON, CSV, YAML, XML and Markdown tables over MCP.",
    "datetime-utility-mcp": "Work with timestamps, timezones and human-readable dates over MCP.",
    "hash-checksum-mcp": "Generate and verify MD5, SHA, CRC32 and BLAKE2 hashes over MCP.",
    "password-generator-mcp": "Generate secure passwords, passphrases, PINs and API keys over MCP.",
    "regex-tester-mcp": "Test, replace and split text with regular expressions over MCP.",
    "rss-feed-reader-mcp": "Fetch, parse and search RSS/Atom feeds over MCP.",
    "seo-analyzer-mcp": "Analyze web pages for SEO signals: titles, meta, headings and links over MCP.",
    "text-diff-mcp": "Compute unified, JSON and HTML diffs plus similarity scores over MCP.",
    "unit-converter-mcp": "Convert length, weight, temperature and more between units over MCP.",
    "uuid-generator-mcp": "Generate UUIDs, nanoids, slugs and random strings over MCP.",
    "youtube-transcript-mcp": "Fetch YouTube transcripts, video info and available languages over MCP.",
}

rows = []
for server_dir in sorted(ROOT.iterdir()):
    if not server_dir.is_dir() or server_dir.name == FLAGSHIP:
        continue

    name = server_dir.name
    pkg = name.replace("-", "_")
    src = server_dir / "src"
    if not (src / "main.py").exists():
        rows.append(f"{name}: SKIPPED (no src/main.py)")
        continue

    pkg_dir = server_dir / pkg
    pkg_dir.mkdir(exist_ok=True)
    (pkg_dir / "main.py").write_text((src / "main.py").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    init_src = src / "__init__.py"
    init_text = init_src.read_text(encoding="utf-8") if init_src.exists() else ""
    (pkg_dir / "__init__.py").write_text(init_text or '"""' + DESC[name] + '"""\n', encoding="utf-8", newline="\n")

    for leftover in src.rglob("*"):
        if leftover.is_file():
            leftover.unlink()
    for leftover in sorted(src.rglob("*"), reverse=True):
        if leftover.is_dir():
            leftover.rmdir()
    src.rmdir()

    dockerfile = server_dir / "Dockerfile"
    if dockerfile.exists():
        text = dockerfile.read_text(encoding="utf-8")
        text = text.replace('"-m", "src.main"', f'"-m", "{pkg}.main"').replace(
            "python -m src.main", f"python -m {pkg}.main"
        )
        dockerfile.write_text(text, encoding="utf-8", newline="\n")

    deps = [
        ln.strip().rstrip(",")
        for ln in (server_dir / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    dep_list = ",\n".join(f'    "{d}"' for d in deps)

    pyproject = f"""[project]
name = "{name}"
version = "0.1.0"
description = "{DESC[name]}"
readme = "README.md"
requires-python = ">=3.10"
license = {{ text = "MIT" }}
keywords = ["mcp", "model-context-protocol", "llm", "ai"]
dependencies = [
{dep_list}
]

[project.scripts]
{name} = "{pkg}.main:main"

[project.urls]
Homepage = "https://github.com/MarekCziba/mcp-servers"
Repository = "https://github.com/MarekCziba/mcp-servers/tree/main/servers/{name}"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["{pkg}"]

[tool.ruff]
target-version = "py310"
line-length = 100
"""
    (server_dir / "pyproject.toml").write_text(pyproject, encoding="utf-8", newline="\n")
    rows.append(f"{name}: package={pkg}")

print("\n".join(rows))
