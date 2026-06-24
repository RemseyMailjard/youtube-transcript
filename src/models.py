"""Domain models voor TranscriptBuddy.

Pure dataclasses, geen Streamlit- of HTTP-afhankelijkheden, zodat ze
hergebruikt kunnen worden in:
- de CLI (main.py)
- de Streamlit-app (app.py)
- een latere Azure Function HTTP-trigger
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class TranscriptSnippet:
    """Eén regel uit een transcript."""

    text: str
    start: float       # seconden vanaf videostart
    duration: float    # seconden


@dataclass
class TranscriptResult:
    """Volledig opgehaalde transcriptie met metadata."""

    video_id: str
    language: str
    language_code: str
    is_generated: bool
    fetched_at: datetime
    snippets: List[TranscriptSnippet]

    # -- afgeleide eigenschappen ------------------------------------------------
    @property
    def text(self) -> str:
        """Snippets samengevoegd tot leesbare platte tekst (één regel per snippet)."""
        return "\n".join(s.text for s in self.snippets if s.text)

    @property
    def line_count(self) -> int:
        return len(self.snippets)

    @property
    def word_count(self) -> int:
        return sum(len(s.text.split()) for s in self.snippets)

    @property
    def char_count(self) -> int:
        return sum(len(s.text) for s in self.snippets)

    @property
    def reading_time_minutes(self) -> float:
        return self.word_count / 200

    @property
    def duration_seconds(self) -> float:
        if not self.snippets:
            return 0.0
        last = self.snippets[-1]
        return last.start + last.duration
