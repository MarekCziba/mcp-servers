import colorsys

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "color-converter-mcp"
mcp = MCPServer(MCP_SERVER_NAME)

NAMED_COLORS = {
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "gray": (128, 128, 128),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
    "maroon": (128, 0, 0),
}


def parse_hex(h: str) -> tuple:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


@mcp.tool()
async def hex_to_rgb(hex_color: str) -> dict:
    """Convert HEX color (#FF0000) to RGB (255, 0, 0)."""
    r, g, b = parse_hex(hex_color)
    return {"r": r, "g": g, "b": b, "hex": hex_color}


@mcp.tool()
async def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to HEX color."""
    return to_hex((r, g, b))


@mcp.tool()
async def rgb_to_hsl(r: int, g: int, b: int) -> dict:
    """Convert RGB to HSL."""
    h, lightness, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return {"h": round(h * 360), "s": round(s * 100), "l": round(lightness * 100)}


@mcp.tool()
async def hex_to_all(hex_color: str) -> dict:
    """Convert HEX to all supported color formats."""
    r, g, b = parse_hex(hex_color)
    h, lightness, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hsv_h, hsv_s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    cmyk_c = 1 - r / 255
    cmyk_m = 1 - g / 255
    cmyk_y = 1 - b / 255
    cmyk_k = min(cmyk_c, cmyk_m, cmyk_y)
    return {
        "hex": hex_color,
        "rgb": {"r": r, "g": g, "b": b},
        "hsl": {"h": round(h * 360), "s": round(s * 100), "l": round(lightness * 100)},
        "hsv": {"h": round(hsv_h * 360), "s": round(hsv_s * 100), "v": round(v * 100)},
        "cmyk": {
            "c": round(cmyk_c, 2),
            "m": round(cmyk_m, 2),
            "y": round(cmyk_y, 2),
            "k": round(cmyk_k, 2),
        },
    }


@mcp.tool()
async def name_to_hex(color_name: str) -> dict:
    """Convert a named color to HEX."""
    name = color_name.lower()
    if name not in NAMED_COLORS:
        return {"error": f"Unknown color: {color_name}"}
    rgb = NAMED_COLORS[name]
    return {"name": color_name, "hex": to_hex(rgb), "rgb": {"r": rgb[0], "g": rgb[1], "b": rgb[2]}}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
