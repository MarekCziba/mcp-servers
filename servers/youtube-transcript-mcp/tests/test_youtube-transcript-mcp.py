"""Live tests for youtube-transcript-mcp — real video dQw4w9WgXcQ (Rick Astley).

If YouTube is unreachable from the machine running the suite, the tools return
``{"error": ...}`` JSON strings instead of raising; the live assertions below
then fail instead of hanging.
"""

import json
import re

from youtube_transcript_mcp.main import (
    _extract_video_id,
    _format_timestamp,
    get_transcript,
    get_video_info,
    list_languages,
)

VIDEO_ID = "dQw4w9WgXcQ"
WATCH_URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"
SHORT_URL = f"https://youtu.be/{VIDEO_ID}"
TIMESTAMPED_LINE = re.compile(r"^\[\d{1,2}:\d{2}(:\d{2})?\] ")


async def test_get_transcript_live() -> None:
    transcript = await get_transcript(WATCH_URL, "en")
    lines = transcript.splitlines()
    assert len(lines) > 50
    timestamped = [line for line in lines if TIMESTAMPED_LINE.match(line)]
    assert len(timestamped) > 50
    assert "no strangers to love" in transcript.lower()


async def test_get_transcript_accepts_short_and_bare_ids() -> None:
    from_short = await get_transcript(SHORT_URL)
    from_id = await get_transcript(VIDEO_ID)
    assert from_short == from_id
    assert TIMESTAMPED_LINE.match(from_short.splitlines()[0])


async def test_get_video_info_live() -> None:
    payload = json.loads(await get_video_info(WATCH_URL))
    assert "error" not in payload
    assert payload["title"].startswith("Rick Astley - Never Gonna Give You Up")
    assert payload["author_name"] == "Rick Astley"
    assert VIDEO_ID in payload["thumbnail_url"]
    assert payload["provider_name"] == "YouTube"


async def test_list_languages_live() -> None:
    languages = json.loads(await list_languages(WATCH_URL))
    assert isinstance(languages, list)
    assert languages
    assert {"language", "code", "generated"} <= set(languages[0])
    assert "en" in {entry["code"] for entry in languages}
    assert {entry["generated"] for entry in languages} == {True, False}


async def test_invalid_urls_return_error_json() -> None:
    transcript = json.loads(await get_transcript("https://example.com"))
    assert transcript["error"] == "Invalid YouTube URL or video ID"

    info = json.loads(await get_video_info("https://example.com"))
    assert info["error"] == "Invalid YouTube URL"

    languages = json.loads(await list_languages("not a video id"))
    assert languages["error"] == "Invalid YouTube URL"


async def test_missing_video_returns_error_json_not_exception() -> None:
    missing = "aaaaaaaaaaa"
    transcript = json.loads(await get_transcript(missing))
    assert "error" in transcript

    info = json.loads(await get_video_info(missing))
    assert info["error"].startswith("HTTP")

    languages = json.loads(await list_languages(missing))
    assert "error" in languages


def test_extract_video_id_url_variants() -> None:
    assert _extract_video_id(WATCH_URL) == VIDEO_ID
    assert _extract_video_id(SHORT_URL) == VIDEO_ID
    assert _extract_video_id(f"https://www.youtube.com/embed/{VIDEO_ID}") == VIDEO_ID
    assert _extract_video_id(f"https://www.youtube.com/shorts/{VIDEO_ID}") == VIDEO_ID
    assert _extract_video_id(VIDEO_ID) == VIDEO_ID
    assert _extract_video_id("https://example.com") is None
    assert _extract_video_id("dQw4w9WgXcQtoolong") is None


def test_format_timestamp_layouts() -> None:
    assert _format_timestamp(0) == "[00:00]"
    assert _format_timestamp(65.7) == "[01:05]"
    assert _format_timestamp(3725) == "[1:02:05]"
