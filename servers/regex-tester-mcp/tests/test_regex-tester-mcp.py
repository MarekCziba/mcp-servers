"""Live tests for regex-tester-mcp — assertions use fixed patterns with known matches."""

import re

import pytest
from regex_tester_mcp.main import (
    replace_regex,
    split_regex,
    validate_regex,
)
from regex_tester_mcp.main import (
    test_regex as match_regex,
)


async def test_regex_matches_with_positions() -> None:
    result = await match_regex(r"\d+", "abc 123 def 456")
    assert result == {
        "valid": True,
        "pattern": r"\d+",
        "matches": [
            {"match": "123", "start": 4, "end": 7, "groups": None},
            {"match": "456", "start": 12, "end": 15, "groups": None},
        ],
        "count": 2,
        "error": None,
    }


async def test_regex_reports_capture_groups() -> None:
    result = await match_regex(r"(\d+)-(\d+)", "12-34 and 56-78")
    assert result["valid"] is True
    assert result["count"] == 2
    assert result["matches"][0] == {
        "match": "12-34",
        "start": 0,
        "end": 5,
        "groups": ["12", "34"],
    }
    assert result["matches"][1]["groups"] == ["56", "78"]


async def test_regex_ignore_case_flag() -> None:
    result = await match_regex("hello", "Hello HELLO", flags="i")
    assert result["count"] == 2
    assert [m["match"] for m in result["matches"]] == ["Hello", "HELLO"]


async def test_regex_no_match_returns_empty_list() -> None:
    result = await match_regex(r"\d+", "no digits here")
    assert result == {
        "valid": True,
        "pattern": r"\d+",
        "matches": [],
        "count": 0,
        "error": None,
    }


async def test_regex_invalid_pattern_returns_error() -> None:
    result = await match_regex("[", "abc")
    assert result["valid"] is False
    assert result["matches"] == []
    assert result["count"] == 0
    assert isinstance(result["error"], str)
    assert "unterminated character set" in result["error"]


async def test_regex_dotall_flag() -> None:
    result = await match_regex(r"a.b", "a\nb", flags="s")
    assert result["count"] == 1
    assert result["matches"][0]["match"] == "a\nb"

    without_flag = await match_regex(r"a.b", "a\nb")
    assert without_flag["count"] == 0


async def test_replace_regex_all_occurrences() -> None:
    assert await replace_regex(r"\d+", "#", "a1 b22") == "a# b#"


async def test_replace_regex_group_backreference() -> None:
    assert await replace_regex(r"(\w+)@(\w+)", r"\2@\1", "user@host") == "host@user"


async def test_replace_regex_with_flags() -> None:
    assert await replace_regex("cat", "dog", "Cat cat CAT", flags="i") == "dog dog dog"


async def test_replace_regex_invalid_pattern_raises() -> None:
    with pytest.raises(re.error):
        await replace_regex("[", "x", "abc")


async def test_split_regex_by_comma_and_space() -> None:
    assert await split_regex(r",\s*", "a, b , c") == ["a", "b ", "c"]


async def test_split_regex_by_whitespace_keeps_empty_edges() -> None:
    assert await split_regex(r"\s+", "  hello   world ") == ["", "hello", "world", ""]


async def test_validate_regex_accepts_valid_patterns() -> None:
    assert await validate_regex(r"^\d{4}$") == {
        "valid": True,
        "pattern": r"^\d{4}$",
        "error": None,
    }


async def test_validate_regex_rejects_invalid_patterns() -> None:
    result = await validate_regex("(")
    assert result["valid"] is False
    assert result["pattern"] == "("
    assert "missing )" in result["error"]

    star = await validate_regex("*")
    assert star["valid"] is False
    assert "nothing to repeat" in star["error"]


async def test_validate_regex_accepts_empty_pattern() -> None:
    assert await validate_regex("") == {"valid": True, "pattern": "", "error": None}
