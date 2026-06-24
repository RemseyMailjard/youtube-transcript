"""Service-laag rond `youtube_transcript_api`.

Bevat zowel low-level helpers als een high-level orchestrator
(`get_transcript`) die door CLI, Streamlit én een latere Azure Function
hergebruikt kan worden.
"""

from __future__ import annotations

from datetime import datetime

from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)

from .models import TranscriptResult, TranscriptSnippet
from .youtube_utils import extract_video_id

# Re-export zodat callers één importpad hebben voor exception-handling.
__all__ = [
    "CouldNotRetrieveTranscript",
    "DEFAULT_LANGUAGES",
    "NoTranscriptFound",
    "SUPPORTED_LANGUAGES",
    "TranscriptsDisabled",
    "VideoUnavailable",
    "fetch_transcript",
    "format_transcript",
    "get_transcript",
]

# Defensief: RequestBlocked / IpBlocked bestaan pas in recentere lib-versies.
try:
    from youtube_transcript_api import IpBlocked, RequestBlocked  # noqa: F401

    __all__ += ["IpBlocked", "RequestBlocked"]
except ImportError:  # pragma: no cover
    pass


DEFAULT_LANGUAGES: list[str] = ["en", "nl"]

# Talen die in de Streamlit UI te kiezen zijn (ISO 639-1 code -> Engelse label).
# Volgorde = volgorde in de UI-dropdown.
SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "nl": "Dutch",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
}

# Voorzichtige Engelse filler-words lijst. Alleen actief als de gebruiker
# de toggle expliciet aanzet. Bewust kort gehouden om transcripts niet
# inhoudelijk te veranderen.
_FILLER_WORDS_EN: tuple[str, ...] = (
    "um", "uh", "erm", "hmm", "like", "you know",
    "i mean", "sort of", "kind of", "basically", "literally",
)


def fetch_transcript(video_id: str, languages: list[str] | None = None):
    """Dunne wrapper rond `YouTubeTranscriptApi().fetch()`.

    Geeft een `FetchedTranscript` terug (itereerbaar over snippets).
    """
    api = YouTubeTranscriptApi()
    return api.fetch(video_id, languages=languages or DEFAULT_LANGUAGES)


def format_transcript(snippets: list[TranscriptSnippet]) -> str:
    """Zet snippets om naar leesbare platte tekst, één snippet per regel."""
    lines: list[str] = []
    for snippet in snippets:
        clean = " ".join(snippet.text.split())  # collapse whitespace/newlines
        if clean:
            lines.append(clean)
    return "\n".join(lines)


def get_transcript(
    input_value: str,
    languages: list[str] | None = None,
) -> TranscriptResult:
    """End-to-end: invoer -> video-id -> fetch -> domain object.

    Schrijft NIET naar disk; alle I/O zit in `export_service`. Daarmee
    is deze functie direct herbruikbaar in een Azure Function.
    """
    video_id = extract_video_id(input_value)
    fetched = fetch_transcript(video_id, languages=languages)

    snippets = [
        TranscriptSnippet(
            text=" ".join(s.text.split()),
            start=float(s.start),
            duration=float(s.duration),
        )
        for s in fetched
    ]

    return TranscriptResult(
        video_id=fetched.video_id,
        language=fetched.language,
        language_code=fetched.language_code,
        is_generated=fetched.is_generated,
        fetched_at=datetime.now(),
        snippets=snippets,
    )


# ---------------------------------------------------------------------------
# Tekst-cleaning (puur presentatie - draait NA fetch)
# ---------------------------------------------------------------------------
def _strip_filler_words(text: str) -> str:
    """Verwijdert een voorzichtige set Engelse filler-woorden uit `text`."""
    import re

    for phrase in sorted(_FILLER_WORDS_EN, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(phrase)}\b[,]?\s*", flags=re.IGNORECASE)
        text = pattern.sub("", text)
    # collapse double spaces die kunnen ontstaan na verwijderen
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def _format_hms(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def clean_transcript(
    snippets: list[TranscriptSnippet],
    *,
    include_timestamps: bool = False,
    merge_paragraphs: bool = False,
    remove_extra_spaces: bool = True,
    lowercase: bool = False,
    remove_filler_words: bool = False,
    paragraph_size: int = 5,
) -> str:
    """Pure functie: snippets -> bewerkte tekst volgens de gekozen opties.

    `paragraph_size` = aantal snippets per paragraaf wanneer `merge_paragraphs`
    actief is.
    """
    if not snippets:
        return ""

    lines: list[str] = []
    for s in snippets:
        text = s.text
        if remove_extra_spaces:
            text = " ".join(text.split())
        if not text:
            continue
        if include_timestamps:
            text = f"[{_format_hms(s.start)}] {text}"
        lines.append(text)

    if merge_paragraphs and not include_timestamps:
        # groepeer N snippets per alinea, gescheiden door blank line
        paragraphs: list[str] = []
        for i in range(0, len(lines), max(paragraph_size, 1)):
            paragraphs.append(" ".join(lines[i : i + paragraph_size]))
        body = "\n\n".join(paragraphs)
    else:
        body = "\n".join(lines)

    if remove_filler_words:
        body = _strip_filler_words(body)
    if lowercase:
        body = body.lower()

    return body


__all__ += ["clean_transcript"]
