"""Export- en serialisatielogica voor `TranscriptResult`.

Pure functies: in -> out. Geen Streamlit. Geen globale state.
Ze produceren ofwel een string (voor downloads) of schrijven een bestand
(voor lokale CLI runs).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .models import TranscriptResult

DEFAULT_OUTPUT_DIR = Path("output")


# ---------------------------------------------------------------------------
# Bestandsnamen
# ---------------------------------------------------------------------------
def build_filename(video_id: str, fetched_at: datetime, extension: str) -> str:
    """`transcript_<id>_<YYYY-MM-DD_HH-MM-SS>.<ext>`."""
    timestamp = fetched_at.strftime("%Y-%m-%d_%H-%M-%S")
    ext = extension.lstrip(".")
    return f"transcript_{video_id}_{timestamp}.{ext}"


# ---------------------------------------------------------------------------
# Serializers per formaat
# ---------------------------------------------------------------------------
def to_txt(result: TranscriptResult, body: str | None = None) -> str:
    """Plain-text export met metadata-header.

    `body` overschrijft de standaard `result.text`, zodat de UI een
    bewerkte (cleaned) versie kan exporteren.
    """
    header = (
        "=== Transcript metadata ===\n"
        f"Video ID       : {result.video_id}\n"
        f"Taal           : {result.language} ({result.language_code})\n"
        f"Auto-generated : {result.is_generated}\n"
        f"Opgehaald op   : {result.fetched_at.isoformat(timespec='seconds')}\n"
        f"Aantal regels  : {result.line_count}\n"
        f"Aantal woorden : {result.word_count}\n"
        "===========================\n\n"
    )
    return header + (body if body is not None else result.text)


def to_markdown(result: TranscriptResult, body: str | None = None) -> str:
    """Markdown export met metadata-tabel. `body` is optioneel override."""
    lines = [
        f"# Transcript - {result.video_id}",
        "",
        "| Veld | Waarde |",
        "| --- | --- |",
        f"| Video ID | `{result.video_id}` |",
        f"| Taal | {result.language} ({result.language_code}) |",
        f"| Auto-generated | {result.is_generated} |",
        f"| Opgehaald op | {result.fetched_at.isoformat(timespec='seconds')} |",
        f"| Aantal regels | {result.line_count} |",
        f"| Aantal woorden | {result.word_count} |",
        "",
        "## Transcript",
        "",
        body if body is not None else result.text,
        "",
    ]
    return "\n".join(lines)


def to_json(result: TranscriptResult, indent: int = 2) -> str:
    """JSON export, snippets behouden voor herbruik door downstream apps."""
    payload = {
        "video_id": result.video_id,
        "language": result.language,
        "language_code": result.language_code,
        "is_generated": result.is_generated,
        "fetched_at": result.fetched_at.isoformat(timespec="seconds"),
        "line_count": result.line_count,
        "word_count": result.word_count,
        "duration_seconds": result.duration_seconds,
        "snippets": [asdict(s) for s in result.snippets],
    }
    return json.dumps(payload, ensure_ascii=False, indent=indent)


# ---------------------------------------------------------------------------
# Disk-IO (lokaal / CLI)
# ---------------------------------------------------------------------------
def save_transcript(
    result: TranscriptResult,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fmt: str = "txt",
) -> Path:
    """Schrijf het transcript naar `output/` als .txt, .md of .json.

    Geeft het pad naar het geschreven bestand terug.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = fmt.lower().lstrip(".")
    if fmt == "txt":
        content = to_txt(result)
    elif fmt == "md":
        content = to_markdown(result)
    elif fmt == "json":
        content = to_json(result)
    else:
        raise ValueError(f"Onbekend exportformaat: {fmt!r} (kies txt, md of json).")

    file_path = output_dir / build_filename(result.video_id, result.fetched_at, fmt)
    file_path.write_text(content, encoding="utf-8")
    return file_path
