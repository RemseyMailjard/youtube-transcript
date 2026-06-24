"""TranscriptBuddy — Premium Streamlit app.

Start locally:
    uv run streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.export_service import build_filename, save_transcript, to_json, to_markdown, to_txt
from src.models import TranscriptResult
from src.styles import inject_css
from src.transcript_service import (
    CouldNotRetrieveTranscript,
    DEFAULT_LANGUAGES,
    NoTranscriptFound,
    SUPPORTED_LANGUAGES,
    TranscriptsDisabled,
    VideoUnavailable,
    clean_transcript,
    get_transcript,
)
from src.ui_components import (
    fmt_hms,
    render_copy_button,
    render_error,
    render_footer,
    render_hero,
    render_history_sidebar,
    render_how_it_works,
    render_stat_cards,
    render_success_bar,
    render_transcript_block,
)
from src.youtube_utils import build_watch_url

try:
    from src.transcript_service import IpBlocked, RequestBlocked  # type: ignore[attr-defined]

    _BLOCK_EXCS: tuple[type[BaseException], ...] = (RequestBlocked, IpBlocked)
except ImportError:
    _BLOCK_EXCS = ()


APP_NAME = "TranscriptBuddy"
APP_TAGLINE = "Turn YouTube videos into clean, usable transcripts"
EXAMPLE_URL = "https://www.youtube.com/watch?v=9-zxCfKKxyU"

_ERROR_MESSAGES: dict[str, tuple[str, str | None]] = {
    "empty_input": (
        "Please enter a YouTube URL or video ID.",
        None,
    ),
    "no_languages": (
        "Please select at least one preferred language.",
        None,
    ),
    "invalid": (
        "Invalid input — we couldn't extract a video ID.",
        "Make sure you're using a valid YouTube URL or an 11-character video ID.",
    ),
    "unavailable": (
        "This video is unavailable.",
        "It may be private, deleted, or restricted in your region.",
    ),
    "disabled": (
        "Transcripts are disabled for this video.",
        "The video owner has turned off captions. Try a different video.",
    ),
    "not_found": (
        "No transcript found for your selected languages.",
        "Try adding more languages in the sidebar, or the video may not have captions.",
    ),
    "blocked": (
        "YouTube is blocking this request.",
        "This often happens on cloud-hosted servers. Try running locally or wait a few minutes.",
    ),
    "generic": (
        "Something went wrong while fetching the transcript.",
        None,
    ),
}


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def _init_state() -> None:
    defaults: dict = {
        "video_input": "",
        "result": None,
        "error_key": None,
        "error_detail": None,
        "cache_bust": 0,
        "auto_save": False,
        "saved_path": None,
        "history": [],
        "include_timestamps": False,
        "merge_paragraphs": False,
        "remove_extra_spaces": True,
        "lowercase": False,
        "remove_filler_words": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _reset_app() -> None:
    for key in ("video_input", "result", "error_key", "error_detail", "saved_path"):
        st.session_state[key] = None if key != "video_input" else ""
    st.session_state["cache_bust"] += 1


def _load_example() -> None:
    st.session_state["video_input"] = EXAMPLE_URL


# ---------------------------------------------------------------------------
# Cached fetch
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _cached_get_transcript(
    video_input: str,
    languages: tuple[str, ...],
    _cache_bust: int,
) -> TranscriptResult:
    return get_transcript(video_input, list(languages))


def _run_fetch(video_input: str, languages: list[str]) -> None:
    st.session_state["result"] = None
    st.session_state["error_key"] = None
    st.session_state["error_detail"] = None
    st.session_state["saved_path"] = None

    if not video_input.strip():
        st.session_state["error_key"] = "empty_input"
        return
    if not languages:
        st.session_state["error_key"] = "no_languages"
        return

    try:
        with st.spinner("Fetching transcript..."):
            result = _cached_get_transcript(
                video_input.strip(),
                tuple(languages),
                st.session_state["cache_bust"],
            )
    except ValueError as e:
        st.session_state["error_key"] = "invalid"
        st.session_state["error_detail"] = str(e)
    except VideoUnavailable as e:
        st.session_state["error_key"] = "unavailable"
        st.session_state["error_detail"] = str(e)
    except TranscriptsDisabled:
        st.session_state["error_key"] = "disabled"
    except NoTranscriptFound:
        st.session_state["error_key"] = "not_found"
        st.session_state["error_detail"] = f"Tried: {', '.join(languages)}"
    except _BLOCK_EXCS as e:  # type: ignore[misc]
        st.session_state["error_key"] = "blocked"
        st.session_state["error_detail"] = type(e).__name__
    except CouldNotRetrieveTranscript as e:
        st.session_state["error_key"] = "generic"
        st.session_state["error_detail"] = f"{type(e).__name__}: {e}"
    except Exception as e:
        st.session_state["error_key"] = "generic"
        st.session_state["error_detail"] = f"{type(e).__name__}: {e}"
    else:
        st.session_state["result"] = result
        _add_to_history(result)
        if st.session_state["auto_save"]:
            st.session_state["saved_path"] = str(save_transcript(result, fmt="txt"))


def _add_to_history(result: TranscriptResult) -> None:
    entry = {
        "video_id": result.video_id,
        "language": f"{result.language} ({result.language_code})",
        "time": result.fetched_at.strftime("%H:%M:%S"),
    }
    history: list[dict] = st.session_state["history"]
    if not history or history[-1]["video_id"] != result.video_id:
        history.append(entry)
    if len(history) > 10:
        history[:] = history[-10:]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def _render_sidebar() -> list[str]:
    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            '<span style="font-size:1.6rem;">🎬</span>'
            '<span style="font-size:1.15rem;font-weight:700;color:#0f172a;">TranscriptBuddy</span>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Settings & preferences")
        st.divider()

        # Language preferences
        st.markdown('<p class="sidebar-section">Language preferences</p>', unsafe_allow_html=True)
        language_codes = st.multiselect(
            "Preferred languages (order = priority)",
            options=list(SUPPORTED_LANGUAGES.keys()),
            default=DEFAULT_LANGUAGES,
            format_func=lambda code: f"{SUPPORTED_LANGUAGES[code]} ({code})",
            help="TranscriptBuddy tries languages in this order. Not all videos have captions in every language.",
            label_visibility="collapsed",
        )
        st.caption("⚡ Availability depends on YouTube captions")

        st.divider()

        # Transcript cleaning
        st.markdown('<p class="sidebar-section">Transcript cleaning</p>', unsafe_allow_html=True)
        st.session_state["include_timestamps"] = st.toggle(
            "Include timestamps",
            value=st.session_state["include_timestamps"],
            help="Prepend [HH:MM:SS] to each line.",
        )
        st.session_state["merge_paragraphs"] = st.toggle(
            "Merge lines into paragraphs",
            value=st.session_state["merge_paragraphs"],
            help="Group every 5 lines into a paragraph for easier reading.",
        )
        st.session_state["remove_extra_spaces"] = st.toggle(
            "Remove extra spaces",
            value=st.session_state["remove_extra_spaces"],
            help="Collapse multiple spaces and trim whitespace.",
        )
        st.session_state["lowercase"] = st.toggle(
            "Convert to lowercase",
            value=st.session_state["lowercase"],
        )
        st.session_state["remove_filler_words"] = st.toggle(
            "Remove filler words",
            value=st.session_state["remove_filler_words"],
            help="Removes common English filler words (um, uh, like, etc.). Use with caution.",
        )

        st.divider()

        # Export settings
        st.markdown('<p class="sidebar-section">Export settings</p>', unsafe_allow_html=True)
        st.session_state["auto_save"] = st.toggle(
            "Auto-save to output/",
            value=st.session_state["auto_save"],
            help="Automatically save as .txt to the output folder after fetching.",
        )

        st.divider()

        # History
        render_history_sidebar(st.session_state.get("history", []))

        st.divider()

        # About
        st.markdown('<p class="sidebar-section">About</p>', unsafe_allow_html=True)
        with st.expander("How it works"):
            st.markdown(
                "TranscriptBuddy uses the `youtube-transcript-api` library to fetch "
                "captions from YouTube videos. It works with auto-generated and manually "
                "added captions in 11+ languages."
            )
        with st.expander("Known limitations"):
            st.markdown(
                "- Not all videos have captions available\n"
                "- Some uploaders disable transcripts\n"
                "- YouTube may block requests from cloud/datacenter IPs\n"
                "- Auto-generated captions may contain errors\n"
                "- Running locally provides the most reliable experience"
            )
        with st.expander("Theme tip"):
            st.markdown(
                'TranscriptBuddy looks best in **light mode**. Go to\n'
                "*Settings → Theme → Light* in the Streamlit menu."
            )

        st.divider()
        st.caption("TranscriptBuddy v1.0 · Powered by youtube-transcript-api")

    return language_codes


# ---------------------------------------------------------------------------
# Input area
# ---------------------------------------------------------------------------
def _render_input(languages: list[str]) -> None:
    st.markdown(
        '<p class="tb-section-title">Enter a YouTube video</p>'
        '<p class="tb-section-sub">Paste any YouTube URL or video ID below</p>',
        unsafe_allow_html=True,
    )

    col_input, col_btns = st.columns([4, 1])
    with col_input:
        st.text_input(
            "YouTube URL or Video ID",
            key="video_input",
            placeholder="https://www.youtube.com/watch?v=... or paste a video ID",
            label_visibility="collapsed",
        )
    with col_btns:
        st.button(
            "Try example",
            on_click=_load_example,
            use_container_width=True,
        )

    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        fetch_clicked = st.button(
            "🎯 Get Transcript",
            type="primary",
            use_container_width=True,
        )
    with c2:
        refetch_clicked = st.button(
            "🔄 Refetch (clear cache)",
            use_container_width=True,
            disabled=not st.session_state.get("video_input"),
        )
    with c3:
        st.button("Reset", on_click=_reset_app, use_container_width=True)

    if refetch_clicked:
        st.session_state["cache_bust"] += 1
        _run_fetch(st.session_state["video_input"], languages)
    elif fetch_clicked:
        _run_fetch(st.session_state["video_input"], languages)


# ---------------------------------------------------------------------------
# Result rendering
# ---------------------------------------------------------------------------
def _get_cleaned_text(result: TranscriptResult) -> str:
    return clean_transcript(
        result.snippets,
        include_timestamps=st.session_state.get("include_timestamps", False),
        merge_paragraphs=st.session_state.get("merge_paragraphs", False),
        remove_extra_spaces=st.session_state.get("remove_extra_spaces", True),
        lowercase=st.session_state.get("lowercase", False),
        remove_filler_words=st.session_state.get("remove_filler_words", False),
    )


def _get_timestamped_text(result: TranscriptResult) -> str:
    return clean_transcript(
        result.snippets,
        include_timestamps=True,
        merge_paragraphs=False,
        remove_extra_spaces=st.session_state.get("remove_extra_spaces", True),
        lowercase=st.session_state.get("lowercase", False),
        remove_filler_words=st.session_state.get("remove_filler_words", False),
    )


def _snippets_dataframe(result: TranscriptResult) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Start": [fmt_hms(s.start) for s in result.snippets],
            "Duration (s)": [round(s.duration, 2) for s in result.snippets],
            "Text": [s.text for s in result.snippets],
        }
    )


def _render_downloads(result: TranscriptResult, cleaned_text: str) -> None:
    st.markdown(
        '<p class="tb-section-title">Download transcript</p>'
        '<p class="tb-section-sub">Export in your preferred format</p>',
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "📄 Download .txt",
            data=to_txt(result, body=cleaned_text),
            file_name=build_filename(result.video_id, result.fetched_at, "txt"),
            mime="text/plain",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "📝 Download .md",
            data=to_markdown(result, body=cleaned_text),
            file_name=build_filename(result.video_id, result.fetched_at, "md"),
            mime="text/markdown",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            "🔧 Download .json",
            data=to_json(result),
            file_name=build_filename(result.video_id, result.fetched_at, "json"),
            mime="application/json",
            use_container_width=True,
        )

    if st.session_state.get("saved_path"):
        st.success(f"Auto-saved to: `{st.session_state['saved_path']}`")


def _render_result(result: TranscriptResult) -> None:
    render_success_bar(result.video_id, f"{result.language} ({result.language_code.upper()})")

    # Link to video
    st.markdown(
        f"[▶️ Watch on YouTube]({build_watch_url(result.video_id)})",
    )

    # Stat cards
    render_stat_cards(result)

    # Prepare texts
    cleaned_text = _get_cleaned_text(result)
    timestamped_text = _get_timestamped_text(result)

    # Tabs
    tab_clean, tab_ts, tab_table, tab_raw = st.tabs(
        ["📄 Clean transcript", "⏱️ Timestamped", "📊 Table view", "🔧 Raw data"]
    )

    with tab_clean:
        render_copy_button(cleaned_text, key="clean")
        render_transcript_block(cleaned_text)

    with tab_ts:
        render_copy_button(timestamped_text, key="ts")
        render_transcript_block(timestamped_text)

    with tab_table:
        df = _snippets_dataframe(result)
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)

    with tab_raw:
        with st.expander("Metadata (JSON)", expanded=True):
            st.json(
                {
                    "video_id": result.video_id,
                    "language": result.language,
                    "language_code": result.language_code,
                    "is_generated": result.is_generated,
                    "fetched_at": result.fetched_at.isoformat(timespec="seconds"),
                    "line_count": result.line_count,
                    "word_count": result.word_count,
                    "char_count": result.char_count,
                    "reading_time_minutes": round(result.reading_time_minutes, 1),
                    "duration_seconds": round(result.duration_seconds, 1),
                }
            )
        with st.expander("First 5 snippets"):
            st.json(
                [
                    {"text": s.text, "start": s.start, "duration": s.duration}
                    for s in result.snippets[:5]
                ]
            )

    st.divider()
    _render_downloads(result, cleaned_text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    _init_state()
    languages = _render_sidebar()

    render_hero(APP_NAME, APP_TAGLINE)
    _render_input(languages)

    # Error display
    error_key = st.session_state.get("error_key")
    if error_key:
        msg, hint = _ERROR_MESSAGES.get(error_key, _ERROR_MESSAGES["generic"])
        detail = st.session_state.get("error_detail")
        render_error(msg, hint)
        if detail:
            with st.expander("Technical details"):
                st.code(detail, language=None)

    # Result display
    if st.session_state["result"] is not None:
        st.divider()
        _render_result(st.session_state["result"])
    elif not error_key:
        st.divider()
        render_how_it_works()

    render_footer()


if __name__ == "__main__":
    main()
