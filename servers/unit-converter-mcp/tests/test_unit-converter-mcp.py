"""Live tests for unit-converter-mcp — assertions use published unit definitions."""

from unit_converter_mcp.main import (
    CONVERSIONS,
    convert,
    convert_length,
    convert_temperature,
    convert_weight,
    list_units,
)


async def test_convert_temperature_known_points() -> None:
    assert (await convert_temperature(0, "C", "F"))["result"] == 32.0
    assert (await convert_temperature(100, "C", "F"))["result"] == 212.0
    assert (await convert_temperature(0, "C", "K"))["result"] == 273.15
    assert (await convert_temperature(-40, "C", "F"))["result"] == -40.0
    assert (await convert_temperature(98.6, "F", "C"))["result"] == 37.0
    assert (await convert_temperature(300, "K", "C"))["result"] == 26.85
    assert (await convert_temperature(32, "F", "C"))["result"] == 0.0


async def test_convert_temperature_round_trip() -> None:
    fahrenheit = await convert_temperature(25, "C", "F")
    assert fahrenheit["result"] == 77.0
    back = await convert_temperature(fahrenheit["result"], "F", "C")
    assert back["result"] == 25.0

    kelvin = await convert_temperature(0, "C", "K")
    assert (await convert_temperature(kelvin["result"], "K", "C"))["result"] == 0.0


async def test_convert_temperature_same_unit_is_identity() -> None:
    result = await convert_temperature(21.5, "C", "C")
    assert result == {
        "value": 21.5,
        "from": "C",
        "to": "C",
        "result": 21.5,
        "category": "temperature",
    }


async def test_convert_length_definitions() -> None:
    assert (await convert_length(1, "in", "cm"))["result"] == 2.54
    assert (await convert_length(1, "km", "m"))["result"] == 1000.0
    assert (await convert_length(1609.344, "m", "mi"))["result"] == 1.0
    assert (await convert_length(2.5, "m", "ft"))["result"] == 8.2020997375


async def test_convert_weight_definitions() -> None:
    assert (await convert_weight(1000, "g", "kg"))["result"] == 1.0
    assert (await convert_weight(1, "kg", "mg"))["result"] == 1000000.0
    assert (await convert_weight(1, "kg", "lb"))["result"] == 2.2046244202


async def test_convert_pressure_and_digital_definitions() -> None:
    bar = await convert(1, "bar", "psi")
    assert bar["result"] == 14.5037680789
    assert bar["category"] == "pressure"

    kib = await convert(1, "KiB", "B")
    assert kib["result"] == 1024.0
    assert kib["category"] == "digital"

    assert (await convert(8, "b", "B"))["result"] == 1.0
    assert (await convert(1, "KB", "B"))["result"] == 1000.0


async def test_convert_auto_detects_category() -> None:
    result = await convert(1, "m", "ft")
    assert result == {
        "value": 1,
        "from": "m",
        "to": "ft",
        "result": 3.280839895,
        "category": "length",
    }


async def test_convert_identity_returns_original_value() -> None:
    result = await convert(5, "m", "m")
    assert result["result"] == 5.0
    assert result["category"] == "length"


async def test_convert_unknown_units_return_error() -> None:
    assert await convert(1, "USD", "EUR") == {"error": "Unknown units: USD, EUR"}
    assert await convert(1, "m", "lb") == {"error": "Unknown units: m, lb"}


async def test_convert_wrong_category_returns_error() -> None:
    assert await convert(1, "m", "ft", category="weight") == {"error": "Units not in weight"}
    assert await convert(1, "m", "ft", category="bogus") == {"error": "Unknown category: bogus"}


async def test_list_units_returns_all_categories() -> None:
    units = await list_units()
    assert set(units) == {
        "length",
        "weight",
        "volume",
        "speed",
        "area",
        "pressure",
        "energy",
        "digital",
    }
    assert units["length"] == ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"]
    assert "temperature" not in units


async def test_list_units_filtered_and_unknown() -> None:
    assert await list_units("length") == {"length": ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"]}
    assert await list_units("bogus") == {"bogus": []}


async def test_conversion_table_is_complete() -> None:
    for units in CONVERSIONS.values():
        assert units
        for factor in units.values():
            assert isinstance(factor, (int, float))
            assert factor > 0
