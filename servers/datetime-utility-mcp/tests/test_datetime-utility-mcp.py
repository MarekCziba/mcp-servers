"""Live tests for datetime-utility-mcp — assertions use fixed timestamps and DST boundaries."""

import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfoNotFoundError

import pytest
from datetime_utility_mcp.main import (
    convert_timezone,
    format_date,
    list_timezones,
    relative_time,
    unix_timestamp,
)


async def test_unix_timestamp_shape_and_clock() -> None:
    result = await unix_timestamp()
    assert set(result) == {"unix_seconds", "unix_ms", "iso"}
    assert isinstance(result["unix_seconds"], int)
    assert isinstance(result["unix_ms"], int)
    assert result["unix_ms"] // 1000 == result["unix_seconds"]
    assert 1_700_000_000 <= result["unix_seconds"] <= 4_000_000_000

    iso = datetime.fromisoformat(result["iso"])
    assert iso.utcoffset() == timedelta(0)
    assert abs(iso.timestamp() - result["unix_seconds"]) < 5


async def test_format_date_default_format() -> None:
    assert await format_date(2000, 2, 29) == "2000-02-29"
    assert await format_date(1970, 1, 1) == "1970-01-01"


async def test_format_date_custom_format() -> None:
    assert await format_date(2023, 12, 25, "%d/%m/%Y") == "25/12/2023"
    assert await format_date(1999, 1, 2, "%A") == "Saturday"


async def test_format_date_invalid_date_raises() -> None:
    with pytest.raises(ValueError):
        await format_date(2023, 2, 29)
    with pytest.raises(ValueError):
        await format_date(2023, 13, 1)


async def test_convert_timezone_dst_boundary() -> None:
    summer = await convert_timezone("2023-06-15 12:00:00", "UTC", "US/Eastern")
    assert summer == {
        "input": "2023-06-15 12:00:00",
        "from": "UTC",
        "to": "US/Eastern",
        "result": "2023-06-15 08:00:00",
    }

    winter = await convert_timezone("2023-01-15 12:00:00", "UTC", "US/Eastern")
    assert winter["result"] == "2023-01-15 07:00:00"


async def test_convert_timezone_tokyo_crosses_midnight() -> None:
    result = await convert_timezone("2023-06-15 23:30:00", "UTC", "Asia/Tokyo")
    assert result["result"] == "2023-06-16 08:30:00"


async def test_convert_timezone_round_trip() -> None:
    noon_utc = "2023-06-15 12:00:00"
    eastern = await convert_timezone(noon_utc, "UTC", "US/Eastern")
    back = await convert_timezone(eastern["result"], "US/Eastern", "UTC")
    assert back["result"] == noon_utc


async def test_convert_timezone_unknown_zone_raises() -> None:
    with pytest.raises(ZoneInfoNotFoundError):
        await convert_timezone("2023-06-15 12:00:00", "UTC", "Not/AZone")


async def test_convert_timezone_malformed_input_raises() -> None:
    with pytest.raises(ValueError):
        await convert_timezone("15/06/2023 12:00:00")


async def test_relative_time_past_buckets() -> None:
    now = int(time.time())

    moment = await relative_time(now - 10)
    assert moment["relative"] == "just now"
    assert 10 <= moment["seconds_ago"] <= 20

    assert await relative_time(now - 61) == {"relative": "1 minute ago", "minutes_ago": 1}
    assert await relative_time(now - 300) == {"relative": "5 minutes ago", "minutes_ago": 5}
    assert await relative_time(now - 3600) == {"relative": "1 hour ago", "hours_ago": 1}
    assert await relative_time(now - 3 * 3600) == {"relative": "3 hours ago", "hours_ago": 3}
    assert await relative_time(now - 2 * 86400 - 3600) == {
        "relative": "2 days ago",
        "days_ago": 2,
    }


async def test_relative_time_future_buckets() -> None:
    now = int(time.time())
    result = await relative_time(now + 300)
    assert result["relative"] == "in 5 minutes"
    assert result["minutes_ago"] < 0

    moment = await relative_time(now + 10)
    assert moment["relative"] == "in a moment"
    assert moment["seconds_ago"] < 0


async def test_relative_time_defaults_to_now() -> None:
    result = await relative_time()
    assert set(result) == {"relative", "seconds_ago"}
    assert result["relative"] == "just now"
    assert 0 <= result["seconds_ago"] <= 5


async def test_list_timezones_default_is_sorted_first_fifty() -> None:
    zones = await list_timezones()
    assert len(zones) == 50
    assert zones == sorted(zones)
    assert zones[0] == "Africa/Abidjan"


async def test_list_timezones_filtered_by_query() -> None:
    assert await list_timezones("Europe/War") == ["Europe/Warsaw"]
    assert "UTC" in await list_timezones("utc")
    assert "Pacific/Auckland" in await list_timezones("pacific")
    assert await list_timezones("qqq_nothing_matches") == []
