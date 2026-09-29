"""Live tests for hash-checksum-mcp — assertions use published NIST/RFC vectors."""

from hash_checksum_mcp.main import generate_all_hashes, generate_hash, verify_hash


async def test_sha256_nist_vector() -> None:
    assert await generate_hash("abc", "sha256") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


async def test_md5_rfc1321_vector() -> None:
    assert await generate_hash("abc", "md5") == "900150983cd24fb0d6963f7d28e17f72"


async def test_sha1_vector() -> None:
    assert await generate_hash("abc", "sha1") == "a9993e364706816aba3e25717850c26c9cd0d89d"


async def test_default_algorithm_is_sha256() -> None:
    assert await generate_hash("abc") == await generate_hash("abc", "sha256")


async def test_all_hashes_returns_every_algorithm() -> None:
    result = await generate_all_hashes("hello world")
    assert set(result) == {"md5", "sha1", "sha256", "sha512", "crc32", "blake2b", "sha3_256"}
    assert len(result["sha256"]) == 64
    assert all(isinstance(v, str) and v for v in result.values())


async def test_verify_hash_match_and_mismatch() -> None:
    digest = await generate_hash("abc", "sha256")
    ok = await verify_hash("abc", "sha256", digest)
    assert ok == {"match": True, "expected": digest, "actual": digest}

    bad = await verify_hash("abc", "sha256", "0" * 64)
    assert bad["match"] is False
    assert bad["actual"] == digest


async def test_unsupported_algorithm_reports_error() -> None:
    try:
        await generate_hash("abc", "sha999")
    except ValueError as exc:
        assert "Unsupported algorithm" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown algorithm")
