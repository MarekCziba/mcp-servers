"""Live tests for password-generator-mcp — assertions check published constraints."""

import re
import string

from password_generator_mcp.main import (
    generate_api_key,
    generate_passphrase,
    generate_password,
    generate_pin,
)

# The published word list the passphrase tool draws from (NATO alphabet + nature words).
WORD_LIST = [
    "alpha",
    "bravo",
    "charlie",
    "delta",
    "echo",
    "foxtrot",
    "golf",
    "hotel",
    "india",
    "juliet",
    "kilo",
    "lima",
    "mike",
    "november",
    "oscar",
    "papa",
    "quebec",
    "romeo",
    "sierra",
    "tango",
    "uniform",
    "victor",
    "whiskey",
    "xray",
    "yankee",
    "zulu",
    "cloud",
    "star",
    "moon",
    "sun",
    "river",
    "lake",
    "mountain",
    "forest",
    "stone",
    "iron",
    "copper",
    "silver",
    "gold",
]

FULL_SET = set(string.ascii_letters + string.digits + string.punctuation)


async def test_generate_password_default_shape() -> None:
    password = await generate_password()
    assert len(password) == 16
    assert set(password) <= FULL_SET


async def test_generate_password_respects_flags() -> None:
    lower_only = await generate_password(
        length=10, include_uppercase=False, include_digits=False, include_symbols=False
    )
    assert len(lower_only) == 10
    assert set(lower_only) <= set(string.ascii_lowercase)

    letters_only = await generate_password(length=10, include_digits=False, include_symbols=False)
    assert set(letters_only) <= set(string.ascii_letters)


async def test_generate_password_length_boundaries() -> None:
    assert await generate_password(length=0) == ""
    assert await generate_password(length=-5) == ""
    assert len(await generate_password(length=1)) == 1
    assert len(await generate_password(length=64)) == 64


async def test_generate_password_covers_the_full_character_set() -> None:
    seen: set[str] = set()
    for _ in range(100):
        seen |= set(await generate_password(length=100))
    assert seen == FULL_SET


async def test_generate_password_is_random() -> None:
    samples = {await generate_password() for _ in range(50)}
    assert len(samples) == 50


async def test_generate_passphrase_default_is_four_hyphen_words() -> None:
    passphrase = await generate_passphrase()
    words = passphrase.split("-")
    assert len(words) == 4
    assert set(words) <= set(WORD_LIST)


async def test_generate_passphrase_custom_count_and_separator() -> None:
    spaced = await generate_passphrase(word_count=5, separator=" ")
    assert len(spaced.split(" ")) == 5
    assert set(spaced.split(" ")) <= set(WORD_LIST)

    single = await generate_passphrase(word_count=1)
    assert single in WORD_LIST

    assert await generate_passphrase(word_count=0) == ""


async def test_generate_passphrase_only_uses_published_words() -> None:
    seen: set[str] = set()
    for _ in range(400):
        for word in (await generate_passphrase(word_count=6)).split("-"):
            assert word in WORD_LIST
            seen.add(word)
    # Every word of the published list really is drawn by the generator.
    assert seen == set(WORD_LIST)


async def test_generate_pin_is_all_digits() -> None:
    assert re.fullmatch(r"\d{6}", await generate_pin())
    assert re.fullmatch(r"\d{4}", await generate_pin(length=4))
    assert re.fullmatch(r"\d{16}", await generate_pin(length=16))


async def test_generate_pin_length_boundaries() -> None:
    assert await generate_pin(length=0) == ""
    assert re.fullmatch(r"\d{1}", await generate_pin(length=1))


async def test_generate_pin_uses_every_digit() -> None:
    digits = {d for _ in range(200) for d in await generate_pin(length=10)}
    assert digits == set(string.digits)


async def test_generate_api_key_default_shape() -> None:
    key = await generate_api_key()
    assert re.fullmatch(r"sk_[A-Za-z0-9]{32}", key)
    assert len(key) == len("sk_") + 32


async def test_generate_api_key_custom_prefix_and_length() -> None:
    assert re.fullmatch(r"tok_[A-Za-z0-9]{8}", await generate_api_key(prefix="tok", length=8))
    assert re.fullmatch(r"[A-Za-z0-9]{32}", await generate_api_key(prefix="", length=32))
    assert "_" not in await generate_api_key(prefix="", length=8)


async def test_generate_api_key_bodies_are_random() -> None:
    keys = {await generate_api_key() for _ in range(50)}
    assert len(keys) == 50


async def test_negative_length_returns_empty_string() -> None:
    assert await generate_password(length=-1) == ""
    assert await generate_pin(length=-1) == ""
    assert await generate_api_key(prefix="sk", length=-1) == "sk_"


async def test_word_list_has_the_published_39_entries() -> None:
    assert len(WORD_LIST) == 39
    assert len(set(WORD_LIST)) == 39
