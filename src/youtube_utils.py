"""Helpers voor het parsen van YouTube-URLs en video-ID's."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

# YouTube video-ID's zijn altijd 11 tekens uit [A-Za-z0-9_-].
_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")

_YOUTUBE_PATH_PREFIXES = {"shorts", "embed", "live", "v"}


def extract_video_id(input_value: str) -> str:
    """Geef de canonieke video-ID terug voor een URL of losse ID.

    Ondersteunde vormen:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/live/VIDEO_ID
        - VIDEO_ID (losse 11-tekens string)
    """
    if not input_value or not isinstance(input_value, str):
        raise ValueError("Lege of ongeldige invoer.")

    candidate = input_value.strip()

    if _VIDEO_ID_RE.match(candidate):
        return candidate

    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path or ""

    if host == "youtu.be":
        vid = path.lstrip("/").split("/")[0]
        if _VIDEO_ID_RE.match(vid):
            return vid

    if host.endswith("youtube.com"):
        # /watch?v=VIDEO_ID
        if path == "/watch":
            vid = parse_qs(parsed.query).get("v", [""])[0]
            if _VIDEO_ID_RE.match(vid):
                return vid

        # /shorts/<id>, /embed/<id>, /live/<id>, /v/<id>
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] in _YOUTUBE_PATH_PREFIXES:
            if _VIDEO_ID_RE.match(parts[1]):
                return parts[1]

    raise ValueError(f"Kan geen geldige video-ID afleiden uit: {input_value!r}")


def build_watch_url(video_id: str) -> str:
    """Bouw de canonieke watch-URL voor een video-ID."""
    return f"https://www.youtube.com/watch?v={video_id}"
