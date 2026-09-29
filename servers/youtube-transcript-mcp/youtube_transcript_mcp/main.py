import json
import re

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("youtube-transcript-mcp")


def _extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    parsed = re.match(r"^([a-zA-Z0-9_-]{11})$", url.strip())
    if parsed:
        return parsed.group(1)

    return None


def _format_timestamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"[{h}:{m:02d}:{s:02d}]"
    return f"[{m:02d}:{s:02d}]"


@mcp.tool(description="Get the transcript of a YouTube video as formatted text with timestamps")
async def get_transcript(video_url: str, language: str = "en") -> str:
    from youtube_transcript_api import YouTubeTranscriptApi

    video_id = _extract_video_id(video_url)
    if not video_id:
        return '{"error": "Invalid YouTube URL or video ID"}'

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=[language])
        lines = [f"{_format_timestamp(entry.start)} {entry.text}" for entry in transcript]
        result = "\n".join(lines)

        return result

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(description="Get basic metadata about a YouTube video (title, author, thumbnail)")
async def get_video_info(video_url: str) -> str:
    video_id = _extract_video_id(video_url)
    if not video_id:
        return json.dumps({"error": "Invalid YouTube URL"})

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.youtube.com/oembed",
                params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            )
            if resp.status_code == 200:
                return json.dumps(resp.json(), indent=2, ensure_ascii=False)
            return json.dumps({"error": f"HTTP {resp.status_code}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(description="List all available transcript languages for a YouTube video")
async def list_languages(video_url: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi

    video_id = _extract_video_id(video_url)
    if not video_id:
        return json.dumps({"error": "Invalid YouTube URL"})

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
        languages = [
            {"language": t.language, "code": t.language_code, "generated": t.is_generated}
            for t in transcript_list
        ]
        return json.dumps(languages, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
