"""CLI-shim over `src/` - bewaart de eerdere lokale workflow.

Uitvoeren:
    uv run python main.py "<YouTube URL of video-ID>" [--languages nl en]
"""

from __future__ import annotations

import argparse
import sys

from src.export_service import save_transcript
from src.transcript_service import (
    CouldNotRetrieveTranscript,
    DEFAULT_LANGUAGES,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    get_transcript,
)

try:
    from src.transcript_service import IpBlocked, RequestBlocked  # type: ignore
    _BLOCK_EXCS: tuple[type[BaseException], ...] = (RequestBlocked, IpBlocked)
except ImportError:  # pragma: no cover
    _BLOCK_EXCS = ()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Download een YouTube-transcriptie als .txt/.md/.json bestand."
    )
    p.add_argument("video", help="YouTube URL of 11-karakter video-ID")
    p.add_argument(
        "--languages",
        nargs="+",
        default=DEFAULT_LANGUAGES,
        help=f"Voorkeurstalen in volgorde (default: {' '.join(DEFAULT_LANGUAGES)})",
    )
    p.add_argument(
        "--format",
        choices=["txt", "md", "json"],
        default="txt",
        help="Output formaat (default: txt)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        result = get_transcript(args.video, languages=args.languages)
    except ValueError as e:
        print(f"[invoerfout] {e}", file=sys.stderr)
        return 2
    except VideoUnavailable as e:
        print(f"[video niet beschikbaar] {e}", file=sys.stderr)
        return 3
    except TranscriptsDisabled as e:
        print(f"[transcripties uitgeschakeld] {e}", file=sys.stderr)
        return 4
    except NoTranscriptFound as e:
        print(
            f"[geen transcript in talen {args.languages}] {e}",
            file=sys.stderr,
        )
        return 5
    except _BLOCK_EXCS as e:  # type: ignore[misc]
        print(
            f"[geblokkeerd door YouTube - {type(e).__name__}] "
            "Overweeg een (residential) proxy.",
            file=sys.stderr,
        )
        return 6
    except CouldNotRetrieveTranscript as e:
        print(f"[{type(e).__name__}] {e}", file=sys.stderr)
        return 7
    except Exception as e:  # pragma: no cover
        print(f"[onverwachte fout] {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    path = save_transcript(result, fmt=args.format)
    print(f"Opgeslagen: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
