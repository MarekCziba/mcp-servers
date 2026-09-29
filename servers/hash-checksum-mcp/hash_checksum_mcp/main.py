import hashlib
import zlib

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "hash-checksum-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


def _hash(text: str, algo: str) -> str:
    data = text.encode()
    if algo == "md5":
        return hashlib.md5(data).hexdigest()
    if algo == "sha1":
        return hashlib.sha1(data).hexdigest()
    if algo == "sha256":
        return hashlib.sha256(data).hexdigest()
    if algo == "sha512":
        return hashlib.sha512(data).hexdigest()
    if algo == "crc32":
        return format(zlib.crc32(data) & 0xFFFFFFFF, "08x")
    if algo == "blake2b":
        return hashlib.blake2b(data).hexdigest()
    if algo == "sha3_256":
        return hashlib.sha3_256(data).hexdigest()
    raise ValueError(f"Unsupported algorithm: {algo}")


@mcp.tool()
async def generate_hash(text: str, algorithm: str = "sha256") -> str:
    """Generate a hash of the input text. Supports: md5, sha1, sha256, sha512, crc32, blake2b, sha3_256."""
    return _hash(text, algorithm)


@mcp.tool()
async def generate_all_hashes(text: str) -> dict:
    """Generate all supported hashes for the input text at once."""
    return {
        a: _hash(text, a)
        for a in ("md5", "sha1", "sha256", "sha512", "crc32", "blake2b", "sha3_256")
    }


@mcp.tool()
async def verify_hash(text: str, algorithm: str, expected_hash: str) -> dict:
    """Verify that a text matches an expected hash."""
    actual = _hash(text, algorithm)
    return {"match": actual == expected_hash, "expected": expected_hash, "actual": actual}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
