"""Live tests for uuid-generator-mcp — assertions use RFC 9562 structure and invariants."""

import re
import string
import time

from uuid_generator_mcp.main import (
    generate_nanoid,
    generate_random_string,
    generate_slug,
    generate_uuid,
)

UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
UUID7_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
NANOID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


async def test_generate_uuid_defaults_to_random_v4() -> None:
    value = await generate_uuid()
    assert UUID4_RE.fullmatch(value)
    assert await generate_uuid(version=4) != value


async def test_uuid4_values_are_unique() -> None:
    values = {await generate_uuid() for _ in range(100)}
    assert len(values) == 100


async def test_uuid7_is_version_7_with_rfc9562_variant() -> None:
    value = await generate_uuid(version=7)
    assert UUID7_RE.fullmatch(value)


async def test_uuid7_embeds_a_current_millisecond_timestamp() -> None:
    value = await generate_uuid(version=7)
    timestamp_ms = int(value.replace("-", "")[:12], 16)
    now_ms = int(time.time() * 1000)
    assert abs(timestamp_ms - now_ms) <= 60_000


async def test_uuid7_timestamps_never_go_backwards() -> None:
    stamps = []
    for _ in range(25):
        value = await generate_uuid(version=7)
        stamps.append(int(value.replace("-", "")[:12], 16))
    assert stamps == sorted(stamps)


async def test_unsupported_version_falls_back_to_v4() -> None:
    # Only 4 and 7 are implemented; anything else returns a random v4 UUID.
    assert UUID4_RE.fullmatch(await generate_uuid(version=3))
    assert UUID4_RE.fullmatch(await generate_uuid(version=99))


async def test_nanoid_default_size_and_alphabet() -> None:
    value = await generate_nanoid()
    assert len(value) == 21
    assert NANOID_RE.fullmatch(value)
    assert set(value) <= set(string.ascii_letters + string.digits + "_-")


async def test_nanoid_custom_sizes() -> None:
    assert len(await generate_nanoid(size=10)) == 10
    assert NANOID_RE.fullmatch(await generate_nanoid(size=1))
    assert await generate_nanoid(size=0) == ""


async def test_nanoid_values_are_unique() -> None:
    values = {await generate_nanoid() for _ in range(200)}
    assert len(values) == 200


async def test_slug_known_vectors() -> None:
    assert await generate_slug("Hello World!") == "hello-world"
    assert await generate_slug("  Multiple   spaces  ") == "multiple-spaces"
    assert await generate_slug("Already-a-Slug") == "already-a-slug"
    assert await generate_slug("C++ rocks") == "c-rocks"
    assert await generate_slug("Version 2 Update") == "version-2-update"


async def test_slug_drops_non_ascii_characters() -> None:
    assert await generate_slug("Über Straße!") == "ber-strae"


async def test_slug_empty_and_punctuation_only() -> None:
    assert await generate_slug("") == ""
    assert await generate_slug("   ") == ""
    assert await generate_slug("!!!") == ""
    assert await generate_slug("._-") == ""


async def test_slug_respects_max_length_and_trailing_hyphen() -> None:
    slug = await generate_slug("aaaa bbbb cccc dddd eeee ffff gggg hhhh", max_length=10)
    assert slug == "aaaa-bbbb"
    assert len(slug) <= 10

    long_slug = await generate_slug("word " * 40, max_length=20)
    assert len(long_slug) <= 20
    assert not long_slug.endswith("-")

    assert await generate_slug("a" * 200, max_length=80) == "a" * 80


async def test_random_string_default_shape() -> None:
    value = await generate_random_string()
    assert re.fullmatch(r"[A-Za-z0-9]{16}", value)


async def test_random_string_flag_combinations() -> None:
    letters = await generate_random_string(length=20, include_digits=False)
    assert re.fullmatch(r"[A-Za-z]{20}", letters)

    alphanumeric = await generate_random_string(length=20, include_symbols=True)
    assert set(alphanumeric) <= set(string.ascii_letters + string.digits + string.punctuation)


async def test_random_string_length_boundaries() -> None:
    assert await generate_random_string(length=0) == ""
    assert await generate_random_string(length=-5) == ""
    assert len(await generate_random_string(length=1)) == 1


async def test_random_string_covers_its_alphabet() -> None:
    seen: set[str] = set()
    for _ in range(100):
        seen |= set(await generate_random_string(length=100))
    assert seen == set(string.ascii_letters + string.digits)


async def test_random_string_symbols_actually_appear() -> None:
    seen: set[str] = set()
    for _ in range(50):
        seen |= set(await generate_random_string(length=100, include_symbols=True))
    assert seen & set(string.punctuation)


async def test_random_strings_are_unique() -> None:
    values = {await generate_random_string(length=32) for _ in range(50)}
    assert len(values) == 50
