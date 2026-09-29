import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from mcp.server.mcpserver import MCPServer

MCP_SERVER_NAME = "datetime-utility-mcp"
mcp = MCPServer(MCP_SERVER_NAME)


@mcp.tool()
async def unix_timestamp() -> dict:
    """Get the current Unix timestamp."""
    now = time.time()
    return {
        "unix_seconds": int(now),
        "unix_ms": int(now * 1000),
        "iso": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
async def format_date(year: int, month: int, day: int, format_str: str = "%Y-%m-%d") -> str:
    """Format a date using a strftime format string."""
    dt = datetime(year, month, day)
    return dt.strftime(format_str)


@mcp.tool()
async def convert_timezone(
    dt_str: str, from_tz: str = "UTC", to_tz: str = "US/Eastern", fmt: str = "%Y-%m-%d %H:%M:%S"
) -> dict:
    """Convert a datetime string between timezones."""
    dt = datetime.strptime(dt_str, fmt).replace(tzinfo=ZoneInfo(from_tz))
    converted = dt.astimezone(ZoneInfo(to_tz))
    return {"input": dt_str, "from": from_tz, "to": to_tz, "result": converted.strftime(fmt)}


@mcp.tool()
async def relative_time(unix_seconds: int | None = None) -> dict:
    """Get human-readable relative time from a Unix timestamp."""
    if unix_seconds is None:
        unix_seconds = int(time.time())
    now = int(time.time())
    diff = now - unix_seconds
    abs_diff = abs(diff)
    if abs_diff < 60:
        return {"relative": "just now" if diff >= 0 else "in a moment", "seconds_ago": diff}
    mins = abs_diff // 60
    if mins < 60:
        return {
            "relative": f"{mins} minute{'s' if mins > 1 else ''} ago"
            if diff >= 0
            else f"in {mins} minutes",
            "minutes_ago": diff // 60,
        }
    hrs = mins // 60
    if hrs < 24:
        return {
            "relative": f"{hrs} hour{'s' if hrs > 1 else ''} ago"
            if diff >= 0
            else f"in {hrs} hours",
            "hours_ago": diff // 3600,
        }
    days = hrs // 24
    return {
        "relative": f"{days} day{'s' if days > 1 else ''} ago" if diff >= 0 else f"in {days} days",
        "days_ago": diff // 86400,
    }


@mcp.tool()
async def list_timezones(query: str = "") -> list[str]:
    """List available timezones, optionally filtered by a search string."""
    import zoneinfo

    all_zones = zoneinfo.available_timezones()
    if query:
        return sorted([z for z in all_zones if query.lower() in z.lower()])
    return sorted(list(all_zones))[:50]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
