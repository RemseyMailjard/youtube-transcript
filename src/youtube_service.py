"""YouTube data service via yt-dlp.

Biedt search, channel en playlist functionaliteit zonder YouTube Data API key.
"""

from __future__ import annotations

import re
from typing import Any

import yt_dlp

_UC_RE = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
_HANDLE_RE = re.compile(r"^@[\w.-]+$")


def _base_opts() -> dict[str, Any]:
    return {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
    }


def _extract(url: str, opts: dict[str, Any] | None = None) -> dict[str, Any]:
    ydl_opts = _base_opts()
    if opts:
        ydl_opts.update(opts)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if info is None:
        raise ValueError(f"Could not extract info from: {url}")
    return info


def _normalize_channel_input(input_value: str) -> str:
    """Accepteert @handle, channel URL, of UC… ID en geeft een bruikbare URL terug."""
    v = input_value.strip()
    if _UC_RE.match(v):
        return f"https://www.youtube.com/channel/{v}"
    if _HANDLE_RE.match(v):
        return f"https://www.youtube.com/{v}"
    if "youtube.com" in v or "youtu.be" in v:
        return v
    raise ValueError(f"Invalid channel input: {input_value!r}")


def _format_video_entry(entry: dict[str, Any]) -> dict[str, Any]:
    video_id = entry.get("id", "")
    channel_id = entry.get("channel_id", "")
    return {
        "type": "video",
        "videoId": video_id,
        "title": entry.get("title", ""),
        "channelId": channel_id,
        "channelTitle": entry.get("channel", entry.get("uploader", "")),
        "channelHandle": entry.get("uploader_id", ""),
        "lengthText": _format_duration(entry.get("duration")),
        "viewCountText": _format_view_count(entry.get("view_count")),
        "publishedTimeText": entry.get("upload_date", ""),
        "thumbnails": _build_thumbnails(video_id),
    }


def _format_channel_entry(entry: dict[str, Any]) -> dict[str, Any]:
    channel_id = entry.get("channel_id", entry.get("id", ""))
    handle = entry.get("uploader_id", entry.get("channel_url", ""))
    return {
        "type": "channel",
        "channelId": channel_id,
        "title": entry.get("title", entry.get("channel", "")),
        "handle": handle,
        "url": entry.get("url", f"https://www.youtube.com/channel/{channel_id}"),
        "description": entry.get("description", ""),
        "subscriberCount": None,
        "thumbnails": [],
    }


def _format_duration(seconds: float | int | None) -> str:
    if seconds is None:
        return ""
    s = int(seconds)
    if s >= 3600:
        return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"
    return f"{s // 60}:{s % 60:02d}"


def _format_view_count(count: int | None) -> str:
    if count is None:
        return ""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M views"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K views"
    return f"{count} views"


def _build_thumbnails(video_id: str) -> list[dict[str, Any]]:
    if not video_id:
        return []
    return [
        {
            "url": f"https://i.ytimg.com/vi/{video_id}/default.jpg",
            "width": 120,
            "height": 90,
        },
        {
            "url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "width": 480,
            "height": 360,
        },
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_youtube(
    query: str,
    search_type: str = "video",
    max_results: int = 20,
) -> dict[str, Any]:
    """Zoek YouTube videos of channels."""
    if search_type == "channel":
        url = f"ytsearch{max_results}:{query} channel"
    else:
        url = f"ytsearch{max_results}:{query}"

    info = _extract(url)
    entries = info.get("entries", []) or []

    if search_type == "channel":
        results = [_format_channel_entry(e) for e in entries if e]
    else:
        results = [_format_video_entry(e) for e in entries if e]

    return {
        "results": results,
        "result_count": len(results),
        "continuation_token": None,
        "has_more": False,
    }


def resolve_channel(input_value: str) -> dict[str, str]:
    """Resolve @handle/URL naar channel ID."""
    v = input_value.strip()
    if _UC_RE.match(v):
        return {"channel_id": v, "resolved_from": v}

    url = _normalize_channel_input(v)
    info = _extract(url, {"playlist_items": "0"})
    channel_id = info.get("channel_id", info.get("id", ""))
    if not channel_id:
        raise ValueError(f"Could not resolve channel ID from: {input_value!r}")
    return {"channel_id": channel_id, "resolved_from": v}


def search_channel(channel: str, query: str) -> dict[str, Any]:
    """Zoek videos binnen een specifiek kanaal."""
    url = _normalize_channel_input(channel)
    # yt-dlp doesn't natively support channel search, so we fetch all and filter
    info = _extract(url + "/videos")
    entries = info.get("entries", []) or []

    q_lower = query.lower()
    filtered = [
        e for e in entries
        if e and q_lower in (e.get("title", "") or "").lower()
    ]

    results = [_format_video_entry(e) for e in filtered]
    return {
        "results": results,
        "result_count": len(results),
        "continuation_token": None,
        "has_more": False,
    }


def get_channel_videos(channel: str) -> dict[str, Any]:
    """Haal alle videos op van een kanaal (gepagineerd via yt-dlp)."""
    url = _normalize_channel_input(channel) + "/videos"
    info = _extract(url)
    entries = info.get("entries", []) or []

    results = [_format_video_entry(e) for e in entries if e]

    playlist_info = {
        "title": f"Uploads from {info.get('channel', info.get('title', 'Unknown'))}",
        "numVideos": str(len(results)),
        "description": info.get("description", ""),
        "ownerName": info.get("channel", info.get("uploader", "")),
        "viewCount": None,
    }

    return {
        "results": results,
        "playlist_info": playlist_info,
        "continuation_token": None,
        "has_more": False,
    }


def get_playlist_videos(playlist: str) -> dict[str, Any]:
    """Haal alle videos op uit een playlist."""
    v = playlist.strip()
    if "youtube.com" in v or "youtu.be" in v:
        url = v
    else:
        url = f"https://www.youtube.com/playlist?list={v}"

    info = _extract(url)
    entries = info.get("entries", []) or []

    results = [_format_video_entry(e) for e in entries if e]

    playlist_info = {
        "title": info.get("title", ""),
        "numVideos": str(len(results)),
        "description": info.get("description", ""),
        "ownerName": info.get("channel", info.get("uploader", "")),
        "viewCount": None,
    }

    return {
        "results": results,
        "playlist_info": playlist_info,
        "continuation_token": None,
        "has_more": False,
    }
