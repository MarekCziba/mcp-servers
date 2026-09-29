"""Live tests for data-converter-mcp — assertions use exact known serializations and round-trips."""

import json

import pytest
from data_converter_mcp.main import (
    convert,
    convert_data,
    flatten_json,
    format_json,
    validate_json,
)

PEOPLE_JSON = '[{"name": "Alice", "city": "Paris"}, {"name": "Bob", "city": "Tokyo"}]'


async def test_json_to_csv_known_output() -> None:
    out = await convert_data(PEOPLE_JSON, "json", "csv")
    assert out == "name,city\r\nAlice,Paris\r\nBob,Tokyo"
    assert out.splitlines() == ["name,city", "Alice,Paris", "Bob,Tokyo"]


async def test_json_csv_json_round_trip_preserves_data() -> None:
    csv_text = await convert_data(PEOPLE_JSON, "json", "csv")
    back = await convert_data(csv_text, "csv", "json")
    assert json.loads(back) == json.loads(PEOPLE_JSON)


async def test_json_to_yaml_sorts_keys() -> None:
    out = await convert_data('{"b": 2, "a": 1}', "json", "yaml")
    assert out == "a: 1\nb: 2\n"


async def test_yaml_to_json_known_output() -> None:
    out = await convert_data("a: 1\nb: 2\n", "yaml", "json")
    assert out == '{\n  "a": 1,\n  "b": 2\n}'


async def test_json_yaml_json_round_trip() -> None:
    source = '{"name": "Alice", "age": 30}'
    yaml_text = await convert_data(source, "json", "yaml")
    back = await convert_data(yaml_text, "yaml", "json")
    assert json.loads(back) == json.loads(source)


async def test_json_to_markdown_table_shape() -> None:
    out = await convert_data(PEOPLE_JSON, "json", "markdown")
    assert out == ("| name | city |\n| --- | --- |\n| Alice | Paris |\n| Bob | Tokyo |")
    lines = out.splitlines()
    assert lines[0] == "| name | city |"
    assert lines[1] == "| --- | --- |"
    assert len(lines) == 4


async def test_markdown_table_escapes_pipes() -> None:
    out = await convert_data('[{"x": "a|b"}]', "json", "markdown")
    assert out == "| x |\n| --- |\n| a\\|b |"


async def test_json_to_xml_known_output() -> None:
    out = await convert_data('[{"name": "Alice"}]', "json", "xml")
    assert out == (
        '<?xml version="1.0" ?>\n<root>\n  <item>\n    <name>Alice</name>\n  </item>\n</root>\n'
    )


async def test_json_xml_json_round_trip() -> None:
    xml_text = await convert_data(PEOPLE_JSON, "json", "xml")
    back = await convert_data(xml_text, "xml", "json")
    assert json.loads(back) == json.loads(PEOPLE_JSON)


async def test_empty_inputs() -> None:
    assert await convert_data("[]", "json", "csv") == ""
    assert await convert_data("[]", "json", "markdown") == ""
    assert await convert_data("", "csv", "json") == "[]"


async def test_single_dict_becomes_one_csv_row() -> None:
    out = await convert_data('{"a": 1}', "json", "csv")
    assert out.splitlines() == ["a", "1"]


async def test_convert_reports_unsupported_formats() -> None:
    assert await convert_data("{}", "ini", "json") == (
        "Conversion error: Unsupported source format: ini"
    )
    assert await convert_data("{}", "json", "ini") == (
        "Conversion error: Unsupported target format: ini"
    )
    with pytest.raises(ValueError, match="Unsupported source format"):
        convert("{}", "ini", "json")
    with pytest.raises(ValueError, match="Unsupported target format"):
        convert("{}", "json", "ini")


async def test_convert_data_reports_malformed_input() -> None:
    out = await convert_data("not json", "json", "csv")
    assert out == "Conversion error: Expecting value: line 1 column 1 (char 0)"


async def test_format_json_custom_indent() -> None:
    assert await format_json('{"b":1,"a":2}', 4) == '{\n    "b": 1,\n    "a": 2\n}'


async def test_format_json_default_indent() -> None:
    assert await format_json('{"b":1,"a":2}') == '{\n  "b": 1,\n  "a": 2\n}'


async def test_format_json_invalid_input_returns_error_string() -> None:
    out = await format_json("{bad")
    assert out.startswith("Error: ")


async def test_validate_json_valid_and_invalid() -> None:
    assert await validate_json('{"a":1}') == {"valid": True, "error": None}
    assert await validate_json("123") == {"valid": True, "error": None}

    bad = await validate_json('{"a":')
    assert bad["valid"] is False
    assert bad["error"] == "Expecting value: line 1 column 6 (char 5)"

    empty = await validate_json("")
    assert empty["valid"] is False
    assert empty["error"] == "Expecting value: line 1 column 1 (char 0)"


async def test_flatten_json_known_shape() -> None:
    out = await flatten_json('{"a": {"b": 1}, "c": [10, 20]}')
    assert json.loads(out) == {"a.b": 1, "c.0": 10, "c.1": 20}
    assert json.loads(await flatten_json('{"x": 5}')) == {"x": 5}


async def test_flatten_json_invalid_input_raises() -> None:
    with pytest.raises(json.JSONDecodeError):
        await flatten_json("{bad")
