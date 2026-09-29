from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "unit-converter-mcp"
mcp = MCPServer(MCP_SERVER_NAME)

CONVERSIONS = {
    "length": {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1.0,
        "km": 1000.0,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1609.344,
    },
    "weight": {
        "mg": 0.000001,
        "g": 0.001,
        "kg": 1.0,
        "t": 1000.0,
        "oz": 0.0283495,
        "lb": 0.453592,
        "st": 6.35029,
    },
    "volume": {
        "ml": 0.000001,
        "l": 0.001,
        "m3": 1.0,
        "gal": 0.00378541,
        "qt": 0.000946353,
        "pt": 0.000473176,
        "cup": 0.000236588,
        "fl_oz": 0.0000295735,
    },
    "speed": {"m/s": 1.0, "km/h": 0.277778, "mph": 0.44704, "kn": 0.514444, "ft/s": 0.3048},
    "area": {
        "mm2": 0.000001,
        "cm2": 0.0001,
        "m2": 1.0,
        "ha": 10000.0,
        "km2": 1000000.0,
        "in2": 0.00064516,
        "ft2": 0.092903,
        "ac": 4046.86,
    },
    "pressure": {
        "Pa": 1.0,
        "kPa": 1000.0,
        "bar": 100000.0,
        "psi": 6894.76,
        "atm": 101325.0,
        "mmHg": 133.322,
    },
    "energy": {
        "J": 1.0,
        "kJ": 1000.0,
        "cal": 4.184,
        "kcal": 4184.0,
        "Wh": 3600.0,
        "kWh": 3600000.0,
        "BTU": 1055.06,
    },
    "digital": {
        "b": 1,
        "B": 8,
        "KB": 8000,
        "MB": 8000000,
        "GB": 8000000000,
        "TB": 8000000000000,
        "KiB": 8192,
        "MiB": 8388608,
        "GiB": 8589934592,
    },
}


@mcp.tool()
async def convert(value: float, from_unit: str, to_unit: str, category: str = "") -> dict:
    """Convert a value between units. Categories: length, weight, volume, speed, area, pressure, energy, digital."""
    if not category:
        for cat, units in CONVERSIONS.items():
            if from_unit in units and to_unit in units:
                category = cat
                break
        if not category:
            return {"error": f"Unknown units: {from_unit}, {to_unit}"}
    units = CONVERSIONS.get(category)
    if not units:
        return {"error": f"Unknown category: {category}"}
    if from_unit not in units or to_unit not in units:
        return {"error": f"Units not in {category}"}
    base = value * units[from_unit]
    result = base / units[to_unit]
    return {
        "value": value,
        "from": from_unit,
        "to": to_unit,
        "result": round(result, 10),
        "category": category,
    }


@mcp.tool()
async def convert_length(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert length: mm, cm, m, km, in, ft, yd, mi."""
    return await convert(value, from_unit, to_unit, "length")


@mcp.tool()
async def convert_weight(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert weight: mg, g, kg, t, oz, lb, st."""
    return await convert(value, from_unit, to_unit, "weight")


@mcp.tool()
async def convert_temperature(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert temperature: C, F, K."""
    if from_unit == "C":
        if to_unit == "F":
            result = value * 9 / 5 + 32
        elif to_unit == "K":
            result = value + 273.15
        else:
            result = value
    elif from_unit == "F":
        if to_unit == "C":
            result = (value - 32) * 5 / 9
        elif to_unit == "K":
            result = (value - 32) * 5 / 9 + 273.15
        else:
            result = value
    elif from_unit == "K":
        if to_unit == "C":
            result = value - 273.15
        elif to_unit == "F":
            result = (value - 273.15) * 9 / 5 + 32
        else:
            result = value
    else:
        result = value
    return {
        "value": value,
        "from": from_unit,
        "to": to_unit,
        "result": round(result, 4),
        "category": "temperature",
    }


@mcp.tool()
async def list_units(category: str = "") -> dict:
    """List all available units, optionally filtered by category."""
    if category:
        return {category: list(CONVERSIONS.get(category, {}).keys())}
    return {cat: list(units.keys()) for cat, units in CONVERSIONS.items()}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
