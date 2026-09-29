"""Live tests for case-converter-mcp — assertions use known word conversions."""

import pytest
from case_converter_mcp.main import (
    to_all_cases,
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
    to_title_case,
    to_upper_case,
)


async def test_snake_case_known_words() -> None:
    assert await to_snake_case("hello world") == "hello_world"
    assert await to_snake_case("Hello World") == "hello_world"
    assert await to_snake_case("foo_bar") == "foo_bar"
    assert await to_snake_case("already-kebab-case") == "already_kebab_case"
    assert await to_snake_case("HTTPServer") == "http_server"
    assert await to_snake_case("XMLHttpRequest") == "xml_http_request"


async def test_camel_case_known_words() -> None:
    assert await to_camel_case("hello world") == "helloWorld"
    assert await to_camel_case("Hello World") == "helloWorld"
    assert await to_camel_case("foo_bar") == "fooBar"
    assert await to_camel_case("HTTPServer") == "httpServer"
    assert await to_camel_case("XMLHttpRequest") == "xmlHttpRequest"
    assert await to_camel_case("Version 2 Update") == "version2Update"


async def test_pascal_case_known_words() -> None:
    assert await to_pascal_case("hello world") == "HelloWorld"
    assert await to_pascal_case("foo_bar") == "FooBar"
    assert await to_pascal_case("XMLHttpRequest") == "XmlHttpRequest"
    assert await to_pascal_case("Version 2 Update") == "Version2Update"


async def test_kebab_case_known_words() -> None:
    assert await to_kebab_case("hello world") == "hello-world"
    assert await to_kebab_case("foo_bar") == "foo-bar"
    assert await to_kebab_case("XMLHttpRequest") == "xml-http-request"
    assert await to_kebab_case("Version 2 Update") == "version-2-update"


async def test_upper_case_known_words() -> None:
    assert await to_upper_case("hello world") == "HELLO_WORLD"
    assert await to_upper_case("XMLHttpRequest") == "XML_HTTP_REQUEST"
    assert await to_upper_case("Version 2 Update") == "VERSION_2_UPDATE"


async def test_title_case_known_words() -> None:
    assert await to_title_case("hello world") == "Hello World"
    assert await to_title_case("XMLHttpRequest") == "Xml Http Request"
    assert await to_title_case("Version 2 Update") == "Version 2 Update"


async def test_digit_runs_become_their_own_words() -> None:
    assert await to_snake_case("hello world2024") == "hello_world_2024"
    assert await to_camel_case("hello world2024") == "helloWorld2024"
    assert await to_snake_case("Version 2 Update") == "version_2_update"


async def test_input_in_any_style_converges() -> None:
    for text in ["hello world", "Hello World", "HELLO WORLD", "hello_world", "hello-world"]:
        assert await to_snake_case(text) == "hello_world"


async def test_all_cases_returns_all_seven_formats() -> None:
    result = await to_all_cases("hello world")
    assert set(result) == {
        "camelCase",
        "PascalCase",
        "snake_case",
        "kebab-case",
        "UPPER_CASE",
        "Title Case",
        "lowercase",
    }
    assert result == {
        "camelCase": "helloWorld",
        "PascalCase": "HelloWorld",
        "snake_case": "hello_world",
        "kebab-case": "hello-world",
        "UPPER_CASE": "HELLO_WORLD",
        "Title Case": "Hello World",
        "lowercase": "helloworld",
    }


async def test_all_cases_values_are_plain_strings() -> None:
    result = await to_all_cases("XMLHttpRequest")
    assert result == {
        "camelCase": "xmlHttpRequest",
        "PascalCase": "XmlHttpRequest",
        "snake_case": "xml_http_request",
        "kebab-case": "xml-http-request",
        "UPPER_CASE": "XML_HTTP_REQUEST",
        "Title Case": "Xml Http Request",
        "lowercase": "xmlhttprequest",
    }


async def test_formats_are_consistent_with_each_other() -> None:
    text = "Hello World Example 2024"
    snake = await to_snake_case(text)
    camel = await to_camel_case(text)
    assert await to_kebab_case(text) == snake.replace("_", "-")
    assert await to_upper_case(text) == snake.upper()
    assert await to_title_case(text) == " ".join(w.capitalize() for w in snake.split("_"))
    assert await to_pascal_case(text) == camel[:1].upper() + camel[1:]


async def test_empty_input_returns_empty_string() -> None:
    assert await to_pascal_case("") == ""
    assert await to_snake_case("") == ""
    assert await to_kebab_case("") == ""
    assert await to_upper_case("") == ""
    assert await to_title_case("") == ""


async def test_camel_case_empty_input_has_no_guard() -> None:
    # to_camel_case indexes the first word unconditionally.
    with pytest.raises(IndexError):
        await to_camel_case("")


async def test_punctuation_only_input_passes_through() -> None:
    assert await to_snake_case("!!!") == "!!!"
    assert await to_camel_case("!!!") == "!!!"
    assert await to_pascal_case("!!!") == "!!!"
    assert await to_upper_case("!!!") == "!!!"
