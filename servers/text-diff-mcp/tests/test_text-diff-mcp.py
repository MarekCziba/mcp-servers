"""Live tests for text-diff-mcp — assertions use hand-computed diff vectors."""

import json

from text_diff_mcp.main import diff_json, html_diff, similarity_ratio, unified_diff


async def test_unified_diff_known_hunk() -> None:
    result = await unified_diff("a\nb\nc", "a\nx\nc")
    assert result == "--- \n+++ \n@@ -1,3 +1,3 @@\n a\n-b\n+x\n c"


async def test_unified_diff_identical_texts_is_empty() -> None:
    assert await unified_diff("same line\n", "same line\n") == ""


async def test_unified_diff_insertion_hunk() -> None:
    result = await unified_diff("a\n", "a\nb\n")
    assert result == "--- \n+++ \n@@ -1 +1,2 @@\n a\n+b\n"


async def test_unified_diff_zero_context_lines() -> None:
    result = await unified_diff("a\nb\nc\nd\n", "a\nb\nX\n", context_lines=0)
    assert result == "--- \n+++ \n@@ -3,2 +3 @@\n-c\n-d\n+X\n"


async def test_diff_json_known_replace_opcode() -> None:
    changes = json.loads(await diff_json("a\nb\nc", "a\nx\nc"))
    assert changes == [
        {
            "type": "replace",
            "text1_start": 1,
            "text1_end": 2,
            "text2_start": 1,
            "text2_end": 2,
        }
    ]


async def test_diff_json_insert_opcode() -> None:
    changes = json.loads(await diff_json("a\nb", "a\nb\nc"))
    assert changes == [
        {
            "type": "insert",
            "text1_start": 2,
            "text1_end": 2,
            "text2_start": 2,
            "text2_end": 3,
        }
    ]


async def test_diff_json_identical_texts_is_empty_list() -> None:
    assert await diff_json("x", "x") == "[]"


async def test_diff_json_delete_opcode() -> None:
    changes = json.loads(await diff_json("keep\ngone\n", "keep\n"))
    assert changes == [
        {
            "type": "delete",
            "text1_start": 1,
            "text1_end": 2,
            "text2_start": 1,
            "text2_end": 1,
        }
    ]


async def test_similarity_ratio_known_values() -> None:
    assert await similarity_ratio("hello", "hallo") == {"ratio": 0.8, "percentage": 80.0}
    assert await similarity_ratio("abc", "abc") == {"ratio": 1.0, "percentage": 100.0}
    assert await similarity_ratio("abc", "") == {"ratio": 0.0, "percentage": 0.0}


async def test_similarity_ratio_is_symmetric() -> None:
    forward = await similarity_ratio("the quick brown fox", "the quick brown cat")
    backward = await similarity_ratio("the quick brown cat", "the quick brown fox")
    assert forward == backward


async def test_html_diff_is_a_table_with_change_classes() -> None:
    html = await html_diff("a\nb\nc", "a\nx\nc")
    assert html.strip().startswith("<table")
    assert html.rstrip().endswith("</table>")
    assert '<span class="diff_sub">b</span>' in html
    assert '<span class="diff_add">x</span>' in html
    assert 'class="diff_header"' in html


async def test_html_diff_defaults_to_empty_second_text() -> None:
    html = await html_diff("only line")
    assert isinstance(html, str)
    assert '<span class="diff_sub">only&nbsp;line</span>' in html
    assert "</table>" in html


async def test_unified_diff_returns_string_for_unicode_text() -> None:
    result = await unified_diff("zażółć\n", "zażółć gęślą\n")
    assert isinstance(result, str)
    assert "-zażółć" in result
    assert "+zażółć gęślą" in result
    assert result.startswith("--- \n+++ \n@@ ")


async def test_empty_inputs() -> None:
    assert await diff_json("", "") == "[]"
    assert await unified_diff("", "") == ""
    assert await similarity_ratio("", "") == {"ratio": 1.0, "percentage": 100.0}
