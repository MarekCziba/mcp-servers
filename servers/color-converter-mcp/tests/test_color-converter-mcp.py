"""Live tests for color-converter-mcp — assertions use published CSS color values."""

import pytest
from color_converter_mcp.main import (
    NAMED_COLORS,
    hex_to_all,
    hex_to_rgb,
    name_to_hex,
    rgb_to_hex,
    rgb_to_hsl,
)


async def test_hex_to_rgb_known_pairs() -> None:
    assert await hex_to_rgb("#FF0000") == {"r": 255, "g": 0, "b": 0, "hex": "#FF0000"}
    assert await hex_to_rgb("#00FF00") == {"r": 0, "g": 255, "b": 0, "hex": "#00FF00"}
    assert await hex_to_rgb("#0000FF") == {"r": 0, "g": 0, "b": 255, "hex": "#0000FF"}
    assert await hex_to_rgb("#FFFFFF") == {"r": 255, "g": 255, "b": 255, "hex": "#FFFFFF"}
    assert await hex_to_rgb("#000000") == {"r": 0, "g": 0, "b": 0, "hex": "#000000"}


async def test_hex_shorthand_and_missing_hash() -> None:
    assert await hex_to_rgb("#f00") == {"r": 255, "g": 0, "b": 0, "hex": "#f00"}
    assert await hex_to_rgb("#fff") == {"r": 255, "g": 255, "b": 255, "hex": "#fff"}
    assert await hex_to_rgb("00FF00") == {"r": 0, "g": 255, "b": 0, "hex": "00FF00"}


async def test_rgb_to_hex_known_pairs() -> None:
    assert await rgb_to_hex(255, 0, 0) == "#FF0000"
    assert await rgb_to_hex(0, 0, 0) == "#000000"
    assert await rgb_to_hex(255, 255, 255) == "#FFFFFF"
    assert await rgb_to_hex(128, 128, 128) == "#808080"
    assert await rgb_to_hex(1, 2, 3) == "#010203"  # zero-padded to two digits


async def test_rgb_hex_round_trip() -> None:
    for r, g, b in [(12, 34, 56), (7, 8, 9), (250, 251, 252), (0, 0, 0)]:
        hex_color = await rgb_to_hex(r, g, b)
        result = await hex_to_rgb(hex_color)
        assert (result["r"], result["g"], result["b"]) == (r, g, b)
        assert result["hex"] == hex_color


async def test_rgb_to_hsl_published_css_values() -> None:
    assert await rgb_to_hsl(255, 0, 0) == {"h": 0, "s": 100, "l": 50}  # hsl(0 100% 50%)
    assert await rgb_to_hsl(0, 255, 0) == {"h": 120, "s": 100, "l": 50}  # hsl(120 100% 50%)
    assert await rgb_to_hsl(0, 0, 255) == {"h": 240, "s": 100, "l": 50}  # hsl(240 100% 50%)
    assert await rgb_to_hsl(255, 255, 255) == {"h": 0, "s": 0, "l": 100}
    assert await rgb_to_hsl(0, 0, 0) == {"h": 0, "s": 0, "l": 0}
    assert await rgb_to_hsl(128, 128, 128) == {"h": 0, "s": 0, "l": 50}  # hsl(0 0% 50%)
    assert await rgb_to_hsl(255, 192, 203) == {"h": 350, "s": 100, "l": 88}  # CSS "pink"


async def test_hex_to_all_red() -> None:
    assert await hex_to_all("#FF0000") == {
        "hex": "#FF0000",
        "rgb": {"r": 255, "g": 0, "b": 0},
        "hsl": {"h": 0, "s": 100, "l": 50},
        "hsv": {"h": 0, "s": 100, "v": 100},
        "cmyk": {"c": 0.0, "m": 1.0, "y": 1.0, "k": 0.0},
    }


async def test_hex_to_all_black_and_white() -> None:
    black = await hex_to_all("#000000")
    assert black["rgb"] == {"r": 0, "g": 0, "b": 0}
    assert black["hsl"] == {"h": 0, "s": 0, "l": 0}
    assert black["hsv"] == {"h": 0, "s": 0, "v": 0}
    assert black["cmyk"] == {"c": 1.0, "m": 1.0, "y": 1.0, "k": 1.0}

    white = await hex_to_all("#FFFFFF")
    assert white["rgb"] == {"r": 255, "g": 255, "b": 255}
    assert white["hsl"] == {"h": 0, "s": 0, "l": 100}
    assert white["cmyk"] == {"c": 0.0, "m": 0.0, "y": 0.0, "k": 0.0}


async def test_hex_to_all_mid_gray() -> None:
    gray = await hex_to_all("#808080")
    assert gray["hsl"] == {"h": 0, "s": 0, "l": 50}
    assert gray["hsv"] == {"h": 0, "s": 0, "v": 50}
    assert gray["cmyk"] == {"c": 0.5, "m": 0.5, "y": 0.5, "k": 0.5}


async def test_name_to_hex_known_colors() -> None:
    assert await name_to_hex("red") == {
        "name": "red",
        "hex": "#FF0000",
        "rgb": {"r": 255, "g": 0, "b": 0},
    }
    assert await name_to_hex("orange") == {
        "name": "orange",
        "hex": "#FFA500",
        "rgb": {"r": 255, "g": 165, "b": 0},
    }
    assert (await name_to_hex("gray"))["hex"] == "#808080"
    assert (await name_to_hex("teal"))["hex"] == "#008080"
    assert (await name_to_hex("navy"))["hex"] == "#000080"
    assert (await name_to_hex("magenta"))["hex"] == "#FF00FF"


async def test_name_lookup_is_case_insensitive_and_echoes_input() -> None:
    assert await name_to_hex("RED") == {
        "name": "RED",
        "hex": "#FF0000",
        "rgb": {"r": 255, "g": 0, "b": 0},
    }


async def test_published_named_color_table() -> None:
    assert len(NAMED_COLORS) == 16
    assert NAMED_COLORS["red"] == (255, 0, 0)
    assert NAMED_COLORS["orange"] == (255, 165, 0)
    assert NAMED_COLORS["black"] == (0, 0, 0)
    assert NAMED_COLORS["white"] == (255, 255, 255)


async def test_unknown_color_reports_error_instead_of_raising() -> None:
    assert await name_to_hex("chartreuse") == {"error": "Unknown color: chartreuse"}
    assert await name_to_hex("") == {"error": "Unknown color: "}


async def test_invalid_hex_raises_value_error() -> None:
    with pytest.raises(ValueError):
        await hex_to_rgb("#GG0000")
    with pytest.raises(ValueError):
        await hex_to_rgb("#FF00")  # four digits is not a supported length
    with pytest.raises(ValueError):
        await hex_to_rgb("red")  # not a hex color at all
