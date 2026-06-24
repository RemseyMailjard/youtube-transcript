"""TranscriptBuddy - Streamlit app.

Lokaal starten:
    uv run streamlit run app.py

De zware logica leeft in `src/`, deze module bevat enkel UI + glue.
"""

from __future__ import annotations

from datetime import timedelta

import pandas as pd
import streamlit as st

from src.export_service import (
    build_filename,
    save_transcript,
    to_json,
    to_markdown,
    to_txt,
)
from src.models import TranscriptResult
from src.transcript_service import (
    CouldNotRetrieveTranscript,
    DEFAULT_LANGUAGES,
    NoTranscriptFound,
    SUPPORTED_LANGUAGES,
    TranscriptsDisabled,
    VideoUnavailable,
    get_transcript,
)
from src.youtube_utils import build_watch_url

try:
    from src.transcript_service import IpBlocked, RequestBlocked  # type: ignore
    _BLOCK_EXCS: tuple[type[BaseException], ...] = (RequestBlocked, IpBlocked)
except ImportError:  # pragma: no cover
    _BLOCK_EXCS = ()


APP_NAME = "TranscriptBuddy"
APP_TAGLINE = "Turn YouTube videos into clean transcripts"
EXAMPLE_URL = "https://www.youtube.com/watch?v=9-zxCfKKxyU"


# ---------------------------------------------------------------------------
# Page config + styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def _init_state() -> None:
    defaults = {
        "video_input": "",
        "result": None,         # TranscriptResult | None
        "error": None,          # str | None
        "cache_bust": 0,        # int, gebruikt om st.cache_data te omzeilen
        "auto_save": False,
        "saved_path": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _reset_app() -> None:
    """Reset alle invoer en resultaten."""
    for key in ("video_input", "result", "error", "saved_path"):
        st.session_state[key] = None if key != "video_input" else ""
    st.session_state["cache_bust"] += 1


def _load_example() -> None:
    st.session_state["video_input"] = EXAMPLE_URL


# ---------------------------------------------------------------------------
# Cached fetch (busted via session counter)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _cached_get_transcript(
    video_input: str,
    languages: tuple[str, ...],
    _cache_bust: int,
) -> TranscriptResult:
    return get_transcript(video_input, list(languages))


def _run_fetch(video_input: str, languages: list[str]) -> None:
    """Roep de service-laag aan, vang exceptions in een nette string."""
    st.session_state["result"] = None
    st.session_state["error"] = None
    st.session_state["saved_path"] = None

    if not video_input.strip():
        st.session_state["error"] = "Voer eerst een YouTube URL of video-ID in."
        return
    if not languages:
        st.session_state["error"] = "Kies minstens één voorkeurstaal."
        return

    try:
        with st.spinner("Transcript ophalen..."):
            result = _cached_get_transcript(
                video_input.strip(),
                tuple(languages),
                st.session_state["cache_bust"],
            )
    except ValueError as e:
        st.session_state["error"] = f"Ongeldige invoer: {e}"
    except VideoUnavailable as e:
        st.session_state["error"] = f"Video niet beschikbaar: {e}"
    except TranscriptsDisabled:
        st.session_state["error"] = (
            "Voor deze video staan transcripties uitgeschakeld door de uploader."
        )
    except NoTranscriptFound:
        st.session_state["error"] = (
            f"Geen transcript gevonden voor talen {languages}. "
            "Probeer een andere taalvolgorde."
        )
    except _BLOCK_EXCS as e:  # type: ignore[misc]
        st.session_state["error"] = (
            f"YouTube blokkeert dit verzoek ({type(e).__name__}). "
            "Dit gebeurt vaak vanaf cloud-IP's. Probeer het later opnieuw "
            "of stel een (residential) proxy in."
        )
    except CouldNotRetrieveTranscript as e:
        st.session_state["error"] = f"{type(e).__name__}: {e}"
    except Exception as e:  # pragma: no cover
        st.session_state["error"] = f"Onverwachte fout: {type(e).__name__}: {e}"
    else:
        st.session_state["result"] = result
        if st.session_state["auto_save"]:
            st.session_state["saved_path"] = str(save_transcript(result, fmt="txt"))


# ---------------------------------------------------------------------------
# Render-helpers
# ---------------------------------------------------------------------------
def _fmt_hms(seconds: float) -> str:
    """`123.4` -> `00:02:03`."""
    return str(timedelta(seconds=int(seconds)))


def _snippets_dataframe(result: TranscriptResult) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Start": [_fmt_hms(s.start) for s in result.snippets],
            "Duur (s)": [round(s.duration, 2) for s in result.snippets],
            "Tekst": [s.text for s in result.snippets],
        }
    )


def _render_header() -> None:
    st.title(f"🎬 {APP_NAME}")
    st.caption(APP_TAGLINE)
    st.write(
        "Plak een YouTube-link of video-ID, kies je voorkeurstalen in de "
        "zijbalk en haal direct een schoon transcript op. Bekijk, kopieer of "
        "download het als `.txt`, `.md` of `.json`."
    )


def _render_sidebar() -> tuple[list[str], bool, bool]:
    with st.sidebar:
        st.header("⚙️ Instellingen")

        language_codes = st.multiselect(
            "Voorkeurstalen (volgorde = prioriteit)",
            options=list(SUPPORTED_LANGUAGES.keys()),
            default=DEFAULT_LANGUAGES,
            format_func=lambda code: f"{SUPPORTED_LANGUAGES[code]} ({code})",
            help=(
                "TranscriptBuddy probeert de talen in deze volgorde. "
                "Standaard eerst Nederlands, dan Engels."
            ),
        )

        st.divider()
        show_table = st.toggle(
            "Toon tabelweergave",
            value=True,
            help="Laat snippets zien met starttijd en duur.",
        )
        st.session_state["auto_save"] = st.toggle(
            "Sla automatisch op in `output/`",
            value=st.session_state["auto_save"],
            help="Schrijft het transcript als .txt naar de output-map.",
        )

        st.divider()
        st.subheader("ℹ️ Goed om te weten")
        st.info(
            "Niet elke YouTube-video heeft een transcript. Sommige uploaders "
            "schakelen ondertitels uit.",
            icon="ℹ️",
        )
        st.warning(
            "YouTube blokkeert soms verzoeken vanaf cloud- of datacenter-IP's. "
            "Lokaal werkt meestal probleemloos.",
            icon="⚠️",
        )

        st.divider()
        st.caption(f"{APP_NAME} · v0.1 · Powered by `youtube-transcript-api`")

    return language_codes, show_table, st.session_state["auto_save"]


def _render_input(languages: list[str]) -> None:
    col_input, col_example = st.columns([5, 1])
    with col_input:
        st.text_input(
            "YouTube URL of video-ID",
            key="video_input",
            placeholder="https://www.youtube.com/watch?v=...",
        )
    with col_example:
        st.write("")  # spacer voor uitlijning
        st.write("")
        st.button("Voorbeeld", on_click=_load_example, use_container_width=True)

    col_fetch, col_refetch, col_reset = st.columns([2, 2, 1])
    with col_fetch:
        fetch_clicked = st.button(
            "🎯 Haal transcript op",
            type="primary",
            use_container_width=True,
        )
    with col_refetch:
        refetch_clicked = st.button(
            "🔄 Opnieuw ophalen (cache leeg)",
            use_container_width=True,
            disabled=not st.session_state["video_input"],
        )
    with col_reset:
        st.button("✖ Reset", on_click=_reset_app, use_container_width=True)

    if refetch_clicked:
        st.session_state["cache_bust"] += 1
        _run_fetch(st.session_state["video_input"], languages)
    elif fetch_clicked:
        _run_fetch(st.session_state["video_input"], languages)


def _render_metadata(result: TranscriptResult) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Video ID", result.video_id)
    col2.metric("Taal", f"{result.language_code.upper()}")
    col3.metric("Regels", result.line_count)
    col4.metric("Woorden", result.word_count)

    sub1, sub2, sub3 = st.columns(3)
    sub1.markdown(f"**Taalnaam:** {result.language}")
    sub2.markdown(
        f"**Type:** {'Auto-generated' if result.is_generated else 'Handmatig'}"
    )
    sub3.markdown(
        f"**Opgehaald:** {result.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    st.markdown(f"[▶️ Open video op YouTube]({build_watch_url(result.video_id)})")


def _render_downloads(result: TranscriptResult) -> None:
    st.subheader("⬇️ Downloads")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "Download .txt",
            data=to_txt(result),
            file_name=build_filename(result.video_id, result.fetched_at, "txt"),
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Download .md",
            data=to_markdown(result),
            file_name=build_filename(result.video_id, result.fetched_at, "md"),
            mime="text/markdown",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            "Download .json",
            data=to_json(result),
            file_name=build_filename(result.video_id, result.fetched_at, "json"),
            mime="application/json",
            use_container_width=True,
        )

    if st.session_state.get("saved_path"):
        st.success(
            f"📁 Lokaal opgeslagen: `{st.session_state['saved_path']}`",
            icon="💾",
        )


def _render_result(result: TranscriptResult, show_table: bool) -> None:
    st.success("Transcript succesvol opgehaald.", icon="✅")
    _render_metadata(result)

    tabs = st.tabs(["📄 Transcript", "📊 Tabel", "🔧 Technisch"])

    with tabs[0]:
        st.text_area(
            "Transcript (alleen-lezen)",
            value=result.text,
            height=500,
            label_visibility="collapsed",
        )

    with tabs[1]:
        if show_table:
            df = _snippets_dataframe(result)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Tabelweergave staat uit in de zijbalk.")

    with tabs[2]:
        with st.expander("Ruwe metadata"):
            st.json(
                {
                    "video_id": result.video_id,
                    "language": result.language,
                    "language_code": result.language_code,
                    "is_generated": result.is_generated,
                    "fetched_at": result.fetched_at.isoformat(timespec="seconds"),
                    "line_count": result.line_count,
                    "word_count": result.word_count,
                    "duration_seconds": result.duration_seconds,
                }
            )
        with st.expander("Eerste 3 snippets (JSON)"):
            st.json(
                [
                    {"text": s.text, "start": s.start, "duration": s.duration}
                    for s in result.snippets[:3]
                ]
            )

    st.divider()
    _render_downloads(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    _init_state()
    languages, show_table, _ = _render_sidebar()
    _render_header()

    st.divider()
    _render_input(languages)

    if st.session_state["error"]:
        st.error(st.session_state["error"], icon="🚫")

    if st.session_state["result"] is not None:
        st.divider()
        _render_result(st.session_state["result"], show_table=show_table)


if __name__ == "__main__":
    main()

