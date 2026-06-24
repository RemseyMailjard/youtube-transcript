"""TranscriptBuddy REST API — FastAPI applicatie.

Start:
    uv run uvicorn api:app --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.models import TranscriptResult
from src.rss_service import get_channel_latest
from src.transcript_service import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    get_transcript,
)
from src.youtube_service import (
    get_channel_videos,
    get_playlist_videos,
    resolve_channel,
    search_channel,
    search_youtube,
)

try:
    from src.transcript_service import IpBlocked, RequestBlocked  # type: ignore[attr-defined]
    _BLOCK_EXCS: tuple[type[BaseException], ...] = (RequestBlocked, IpBlocked)
except ImportError:
    _BLOCK_EXCS = ()

app = FastAPI(
    title="TranscriptBuddy API",
    description=(
        "YouTube Transcript & Data API — haal transcripts op, zoek videos, "
        "blader door kanalen en playlists. Geen API key nodig."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _error(status: int, message: str, code: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"detail": message, "code": code})


def _transcript_to_json(
    result: TranscriptResult,
    fmt: str,
    include_timestamp: bool,
    send_metadata: bool,
) -> dict[str, Any]:
    """Bouw de API response voor het transcript endpoint."""
    response: dict[str, Any] = {
        "video_id": result.video_id,
        "language": result.language_code,
    }

    if fmt == "text":
        if include_timestamp:
            lines = [f"[{s.start}s] {s.text}" for s in result.snippets]
            response["transcript"] = "\n".join(lines)
        else:
            response["transcript"] = " ".join(s.text for s in result.snippets)
    else:
        if include_timestamp:
            response["transcript"] = [
                {"text": s.text, "start": s.start, "duration": s.duration}
                for s in result.snippets
            ]
        else:
            response["transcript"] = [{"text": s.text} for s in result.snippets]

    if send_metadata:
        response["metadata"] = {
            "title": None,
            "author_name": None,
            "author_url": None,
            "thumbnail_url": f"https://i.ytimg.com/vi/{result.video_id}/hqdefault.jpg",
        }

    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/api/v2/youtube/transcript",
    summary="Extract video transcript",
    tags=["Transcript"],
)
async def youtube_transcript(
    video_url: str = Query(..., description="YouTube video URL or video ID"),
    format: str = Query("json", description="Output format: json or text", regex="^(json|text)$"),
    include_timestamp: bool = Query(True, description="Include timestamps in output"),
    send_metadata: bool = Query(False, description="Include video metadata"),
) -> dict[str, Any]:
    """Haal het transcript op van een YouTube video.

    Accepteert volledige YouTube URLs, korte URLs (youtu.be), of losse video IDs.
    """
    try:
        result = get_transcript(video_url)
    except ValueError:
        raise _error(422, "Invalid YouTube URL or video ID.", "INVALID_URL")
    except VideoUnavailable:
        raise _error(404, "Video not found or unavailable.", "VIDEO_NOT_FOUND")
    except TranscriptsDisabled:
        raise _error(404, "Transcripts are disabled for this video.", "TRANSCRIPTS_DISABLED")
    except NoTranscriptFound:
        raise _error(404, "No transcript found for this video.", "NO_TRANSCRIPT")
    except _BLOCK_EXCS:  # type: ignore[misc]
        raise _error(408, "YouTube is blocking this request. Retry later.", "REQUEST_BLOCKED")
    except CouldNotRetrieveTranscript as e:
        raise _error(500, f"Could not retrieve transcript: {e}", "RETRIEVAL_ERROR")
    except Exception as e:
        raise _error(500, f"Unexpected error: {type(e).__name__}: {e}", "INTERNAL_ERROR")

    return _transcript_to_json(result, format, include_timestamp, send_metadata)


@app.get(
    "/api/v2/youtube/search",
    summary="Search YouTube videos or channels",
    tags=["Search"],
)
async def youtube_search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    type: str = Query("video", description="Result type: video or channel", regex="^(video|channel)$"),
) -> dict[str, Any]:
    """Zoek YouTube voor videos of channels."""
    try:
        return search_youtube(q, search_type=type)
    except Exception as e:
        raise _error(500, f"Search failed: {type}: {e}", "SEARCH_ERROR")


@app.get(
    "/api/v2/youtube/channel/resolve",
    summary="Resolve @handle/URL to channel ID",
    tags=["Channel"],
)
async def youtube_channel_resolve(
    input: str = Query(..., min_length=1, max_length=200, description="@handle, channel URL, or UC… ID"),
) -> dict[str, str]:
    """Resolve een @handle, URL of UC… ID naar een canoniek channel ID."""
    try:
        return resolve_channel(input)
    except ValueError as e:
        raise _error(400, str(e), "INVALID_INPUT")
    except Exception as e:
        raise _error(500, f"Could not resolve channel: {e}", "RESOLVE_ERROR")


@app.get(
    "/api/v2/youtube/channel/search",
    summary="Search within a channel",
    tags=["Channel"],
)
async def youtube_channel_search(
    channel: str = Query(..., description="@handle, channel URL, or UC… channel ID"),
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
) -> dict[str, Any]:
    """Zoek videos binnen een specifiek kanaal."""
    try:
        return search_channel(channel, q)
    except ValueError as e:
        raise _error(400, str(e), "INVALID_INPUT")
    except Exception as e:
        raise _error(500, f"Channel search failed: {e}", "CHANNEL_SEARCH_ERROR")


@app.get(
    "/api/v2/youtube/channel/videos",
    summary="List channel uploads (paginated)",
    tags=["Channel"],
)
async def youtube_channel_videos(
    channel: str = Query(..., description="@handle, channel URL, or UC… channel ID"),
) -> dict[str, Any]:
    """Haal alle geüploade videos op van een kanaal."""
    try:
        return get_channel_videos(channel)
    except ValueError as e:
        raise _error(400, str(e), "INVALID_INPUT")
    except Exception as e:
        raise _error(500, f"Could not fetch channel videos: {e}", "CHANNEL_VIDEOS_ERROR")


@app.get(
    "/api/v2/youtube/channel/latest",
    summary="Latest 15 videos via RSS",
    tags=["Channel"],
)
async def youtube_channel_latest(
    channel: str = Query(..., description="@handle, channel URL, or UC… channel ID"),
) -> dict[str, Any]:
    """Haal de laatste ~15 videos op via YouTube RSS feed."""
    try:
        return get_channel_latest(channel)
    except ValueError as e:
        raise _error(400, str(e), "INVALID_INPUT")
    except Exception as e:
        raise _error(500, f"Could not fetch latest videos: {e}", "RSS_ERROR")


@app.get(
    "/api/v2/youtube/playlist/videos",
    summary="List playlist videos (paginated)",
    tags=["Playlist"],
)
async def youtube_playlist_videos(
    playlist: str = Query(..., description="YouTube playlist URL or playlist ID"),
) -> dict[str, Any]:
    """Haal alle videos op uit een YouTube playlist."""
    try:
        return get_playlist_videos(playlist)
    except ValueError as e:
        raise _error(400, str(e), "INVALID_INPUT")
    except Exception as e:
        raise _error(500, f"Could not fetch playlist videos: {e}", "PLAYLIST_ERROR")


@app.get("/", summary="API info", tags=["Info"])
async def root() -> dict[str, str]:
    return {
        "name": "TranscriptBuddy API",
        "version": "2.0.0",
        "docs": "/docs",
        "base_url": "/api/v2",
    }
