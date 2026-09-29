import csv
import io
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "data-converter-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


def parse_json(text: str) -> list | dict:
    return json.loads(text)


def parse_csv(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def parse_yaml(text: str) -> list | dict:
    import yaml

    return yaml.safe_load(text)


def parse_xml(text: str) -> list[dict]:
    root = ET.fromstring(text)
    items = []
    for child in root:
        item = {}
        for sub in child:
            item[sub.tag] = sub.text or ""
        items.append(item)
    return items


def to_json(data: list | dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def to_csv(data: list | dict) -> str:
    if isinstance(data, dict):
        data = [data]
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue().strip()


def to_yaml(data: list | dict) -> str:
    import yaml

    return yaml.dump(data, allow_unicode=True, default_flow_style=False)


def to_xml(data: list | dict, root_name: str = "root", item_name: str = "item") -> str:
    root = ET.Element(root_name)
    if isinstance(data, dict):
        data = [data]
    for item_data in data:
        item = ET.SubElement(root, item_name)
        for key, val in item_data.items():
            child = ET.SubElement(item, key)
            child.text = str(val) if val is not None else ""
    rough = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(rough.encode())
    return dom.toprettyxml(indent="  ")


def to_markdown_table(data: list | dict) -> str:
    if isinstance(data, dict):
        data = [data]
    if not data:
        return ""
    headers = list(data[0].keys())
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in data:
        vals = [str(row.get(h, "")).replace("|", "\\|") for h in headers]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


PARSERS = {"json": parse_json, "csv": parse_csv, "yaml": parse_yaml, "xml": parse_xml}
SERIALIZERS = {
    "json": to_json,
    "csv": to_csv,
    "yaml": to_yaml,
    "xml": lambda d: to_xml(d),
    "markdown": to_markdown_table,
}


def convert(input_text: str, from_format: str, to_format: str) -> str:
    parser = PARSERS.get(from_format)
    if not parser:
        raise ValueError(f"Unsupported source format: {from_format}")
    data = parser(input_text)
    serializer = SERIALIZERS.get(to_format)
    if not serializer:
        raise ValueError(f"Unsupported target format: {to_format}")
    return serializer(data)


@mcp.tool()
async def convert_data(input_text: str, from_format: str = "json", to_format: str = "csv") -> str:
    """Convert data between JSON, CSV, YAML, XML, and Markdown table formats."""
    try:
        return convert(input_text, from_format, to_format)
    except Exception as e:
        return f"Conversion error: {str(e)}"


@mcp.tool()
async def format_json(input_text: str, indent: int = 2) -> str:
    """Pretty-format a JSON string with specified indentation."""
    try:
        data = json.loads(input_text)
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def validate_json(input_text: str) -> dict:
    """Validate a JSON string. Returns valid and error message."""
    try:
        json.loads(input_text)
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@mcp.tool()
async def flatten_json(input_text: str) -> str:
    """Flatten a nested JSON object into dot-notation key-value pairs as JSON."""
    data = json.loads(input_text)
    result = {}

    def _flatten(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _flatten(v, f"{prefix}{k}.")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _flatten(v, f"{prefix}{i}.")
        else:
            result[prefix.rstrip(".")] = obj

    _flatten(data)
    return json.dumps(result, indent=2, ensure_ascii=False)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
