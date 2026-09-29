"""Live tests for base64-encoding-mcp — assertions use published RFC 4648 vectors."""

import binascii

import pytest
from base64_encoding_mcp.main import (
    decode_base64,
    decode_base64url,
    decode_html,
    decode_url,
    encode_base64,
    encode_base64url,
    encode_html,
    encode_url,
)


async def test_encode_base64_rfc4648_vectors() -> None:
    assert await encode_base64("") == ""
    assert await encode_base64("a") == "YQ=="
    assert await encode_base64("ab") == "YWI="
    assert await encode_base64("Man") == "TWFu"
    assert await encode_base64("hello") == "aGVsbG8="
    assert await encode_base64("~~>") == "fn4+"


async def test_encode_base64_utf8_is_encoded_as_bytes() -> None:
    assert await encode_base64("\u2713") == "4pyT"
    assert await encode_base64("\u017c\u00f3\u0142w") == "xbzDs8WCdw=="


async def test_decode_base64_vectors() -> None:
    assert await decode_base64("") == ""
    assert await decode_base64("TWFu") == "Man"
    assert await decode_base64("aGVsbG8=") == "hello"
    assert await decode_base64("fn4+") == "~~>"


async def test_base64_round_trip() -> None:
    for text in [
        "",
        "hello world",
        "MCP: \u00fcn\u00efc\u00f6d\u00e9 \u2713",
        "line one\nline two",
    ]:
        assert await decode_base64(await encode_base64(text)) == text


async def test_encode_base64url_uses_url_alphabet_without_padding() -> None:
    # RFC 4648 §5: '+' becomes '-', '/' becomes '_', and '=' padding is omitted.
    assert await encode_base64url("hello") == "aGVsbG8"
    assert await encode_base64url("~~>") == "fn4-"
    assert await encode_base64url("Man") == "TWFu"
    assert "=" not in await encode_base64url("a")
    assert "+" not in await encode_base64url("~~>")
    assert "/" not in await encode_base64url("~~>")


async def test_decode_base64url_accepts_padded_and_unpadded_input() -> None:
    assert await decode_base64url("") == ""
    assert await decode_base64url("TWFu") == "Man"
    assert await decode_base64url("aGVsbG8") == "hello"
    assert await decode_base64url("aGVsbG8=") == "hello"
    assert await decode_base64url("fn4-") == "~~>"


async def test_base64url_round_trip() -> None:
    for text in ["", "hello world", "session?=1&x=2", "\u00fcn\u00efc\u00f6d\u00e9 \u2713"]:
        assert await decode_base64url(await encode_base64url(text)) == text


async def test_url_encoding_known_vectors() -> None:
    assert await encode_url("") == ""
    assert await encode_url("hello world") == "hello%20world"
    assert await encode_url("MCP & you") == "MCP%20%26%20you"
    assert await encode_url("a/b") == "a/b"  # RFC 3986: '/' stays unescaped
    assert await encode_url("\u017c\u00f3\u0142w") == "%C5%BC%C3%B3%C5%82w"
    assert await decode_url("") == ""
    assert await decode_url("hello%20world") == "hello world"
    assert await decode_url("%C5%BC%C3%B3%C5%82w") == "\u017c\u00f3\u0142w"


async def test_url_round_trip() -> None:
    for text in ["a b", "key=value&other=1", "\u00fcn\u00efc\u00f6d\u00e9", "100% done"]:
        assert await decode_url(await encode_url(text)) == text


async def test_html_escaping_known_vectors() -> None:
    assert await encode_html("") == ""
    assert await encode_html("<b>") == "&lt;b&gt;"
    assert await encode_html("a & b") == "a &amp; b"
    assert await encode_html('<a href="x">Tom & Jerry\'s</a>') == (
        "&lt;a href=&quot;x&quot;&gt;Tom &amp; Jerry&#x27;s&lt;/a&gt;"
    )
    assert await decode_html("") == ""
    assert await decode_html("&lt;b&gt;") == "<b>"
    assert await decode_html("&amp;lt;") == "&lt;"


async def test_html_round_trip() -> None:
    for text in ['<p class="x">5 < 6 & 7 > 6</p>', "plain text", ""]:
        assert await decode_html(await encode_html(text)) == text


async def test_decode_base64_rejects_bad_padding() -> None:
    with pytest.raises(binascii.Error):
        await decode_base64("abc")


async def test_decode_base64_rejects_non_utf8_payload() -> None:
    # "/w==" is the Base64 of the single byte 0xFF, which is not valid UTF-8 text.
    with pytest.raises(UnicodeDecodeError):
        await decode_base64("/w==")
