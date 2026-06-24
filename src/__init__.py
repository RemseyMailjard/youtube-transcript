"""TranscriptBuddy - reusable transcript core (CLI + Streamlit + future Azure)."""

from .models import TranscriptResult, TranscriptSnippet
from .transcript_service import (
    DEFAULT_LANGUAGES,
    SUPPORTED_LANGUAGES,
    clean_transcript,
    fetch_transcript,
    format_transcript,
    get_transcript,
)
from .youtube_utils import extract_video_id

__all__ = [
    "DEFAULT_LANGUAGES",
    "SUPPORTED_LANGUAGES",
    "TranscriptResult",
    "TranscriptSnippet",
    "clean_transcript",
    "extract_video_id",
    "fetch_transcript",
    "format_transcript",
    "get_transcript",
]
