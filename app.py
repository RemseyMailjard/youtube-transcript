"""TranscriptBuddy — Minimal Streamlit app with full YouTube API features.

Start locally:
    uv run streamlit run app.py
"""

from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st

from src.export_service import build_filename, to_json, to_markdown, to_txt
from src.models import TranscriptResult
from src.rss_service import get_channel_latest
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
    render_success,
    render_transcript_block,
    render_transcript_stats,
    render_video_list,
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


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="YouTube to Transcript",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_css()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Transcript"


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
render_hero()


# ---------------------------------------------------------------------------
# Navigation tabs
# ---------------------------------------------------------------------------
tabs = st.tabs(["Transcript", "Search", "Channel", "Playlist"])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: TRANSCRIPT
# ═══════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("##### Get Transcript")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        video_url = st.text_input(
            "YouTube URL",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",
            key="transcript_url",
        )
    with col_btn:
        fetch_btn = st.button("Get Transcript", type="primary", use_container_width=True)

    # Language selector
    with st.expander("Language & format options"):
        lang_col, fmt_col = st.columns(2)
        with lang_col:
            languages = st.multiselect(
                "Preferred languages",
                options=list(SUPPORTED_LANGUAGES.keys()),
                default=DEFAULT_LANGUAGES,
                format_func=lambda c: f"{SUPPORTED_LANGUAGES[c]} ({c})",
            )
        with fmt_col:
            include_ts = st.checkbox("Include timestamps", value=False)
            merge_para = st.checkbox("Merge into paragraphs", value=False)

    if fetch_btn and video_url.strip():
        try:
            with st.spinner("Fetching transcript..."):
                result = get_transcript(video_url.strip(), languages or DEFAULT_LANGUAGES)

            render_success(f"Transcript fetched — {result.language} ({result.language_code.upper()})")
            render_transcript_stats(result)

            cleaned = clean_transcript(
                result.snippets,
                include_timestamps=include_ts,
                merge_paragraphs=merge_para,
            )

            render_copy_button(cleaned, key="transcript")
            render_transcript_block(cleaned)

            # Downloads
            st.markdown('<div class="tb-section">Download</div>', unsafe_allow_html=True)
            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button(
                    "Download .txt",
                    data=to_txt(result, body=cleaned),
                    file_name=build_filename(result.video_id, result.fetched_at, "txt"),
                    mime="text/plain",
                    use_container_width=True,
                )
            with d2:
                st.download_button(
                    "Download .md",
                    data=to_markdown(result, body=cleaned),
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

            # Table view
            with st.expander("Table view"):
                df = pd.DataFrame({
                    "Start": [fmt_hms(s.start) for s in result.snippets],
                    "Duration": [round(s.duration, 2) for s in result.snippets],
                    "Text": [s.text for s in result.snippets],
                })
                st.dataframe(df, use_container_width=True, hide_index=True)

        except ValueError:
            render_error("Invalid YouTube URL or video ID.", "Check your URL and try again.")
        except VideoUnavailable:
            render_error("Video unavailable.", "It may be private, deleted, or restricted.")
        except TranscriptsDisabled:
            render_error("Transcripts are disabled for this video.")
        except NoTranscriptFound:
            render_error("No transcript found.", f"Tried: {', '.join(languages or DEFAULT_LANGUAGES)}")
        except _BLOCK_EXCS:  # type: ignore[misc]
            render_error("YouTube is blocking this request.", "Try again later or run locally.")
        except CouldNotRetrieveTranscript as e:
            render_error(f"Could not retrieve transcript: {e}")
        except Exception as e:
            render_error(f"Something went wrong: {type(e).__name__}: {e}")

    elif fetch_btn:
        render_error("Please enter a YouTube URL or video ID.")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: SEARCH
# ═══════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("##### Search YouTube")

    s_col1, s_col2, s_col3 = st.columns([3, 1, 1])
    with s_col1:
        search_query = st.text_input(
            "Search query",
            placeholder="Search YouTube...",
            label_visibility="collapsed",
            key="search_query",
        )
    with s_col2:
        search_type = st.selectbox("Type", ["video", "channel"], label_visibility="collapsed")
    with s_col3:
        search_btn = st.button("Search", type="primary", use_container_width=True)

    if search_btn and search_query.strip():
        try:
            with st.spinner("Searching..."):
                data = search_youtube(search_query.strip(), search_type=search_type)

            results = data.get("results", [])
            st.caption(f"{len(results)} results found")

            if search_type == "video":
                render_video_list(results)
            else:
                for ch in results:
                    st.markdown(
                        f"""
                        <div class="tb-result-card">
                            <h4>{html.escape(ch.get('title', ''))}</h4>
                            <div class="meta">
                                <span>{html.escape(ch.get('handle', ''))}</span>
                                <span>{html.escape(ch.get('subscriberCount', '') or '')}</span>
                            </div>
                            <div class="meta" style="margin-top:4px;">{html.escape((ch.get('description', '') or '')[:200])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        except Exception as e:
            render_error(f"Search failed: {e}")

    elif search_btn:
        render_error("Please enter a search query.")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: CHANNEL
# ═══════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("##### Channel Explorer")

    channel_input = st.text_input(
        "Channel",
        placeholder="@handle, channel URL, or UC… ID",
        label_visibility="collapsed",
        key="channel_input",
    )

    ch_sub = st.tabs(["Latest (RSS)", "All Videos", "Search in Channel", "Resolve ID"])

    # -- Latest (RSS) --
    with ch_sub[0]:
        if st.button("Get Latest Videos", type="primary", key="ch_latest_btn"):
            if channel_input.strip():
                try:
                    with st.spinner("Fetching RSS feed..."):
                        data = get_channel_latest(channel_input.strip())
                    ch_info = data.get("channel", {})
                    render_success(f"Channel: {ch_info.get('title', '')} — {data.get('result_count', 0)} videos")

                    for v in data.get("results", []):
                        vid = v.get("videoId", "")
                        views = f"{int(v.get('viewCount', 0)):,} views" if v.get("viewCount") else ""
                        st.markdown(
                            f"""
                            <div class="tb-video-item">
                                <img src="{html.escape(v.get('thumbnail', {}).get('url', ''))}" alt="">
                                <div class="info">
                                    <h4>{html.escape(v.get('title', ''))}</h4>
                                    <div class="meta"><span>{html.escape(v.get('published', '')[:10])}</span> · <span>{html.escape(views)}</span></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                except Exception as e:
                    render_error(f"Failed: {e}")
            else:
                render_error("Enter a channel @handle, URL, or ID above.")

    # -- All Videos --
    with ch_sub[1]:
        if st.button("Get All Videos", type="primary", key="ch_videos_btn"):
            if channel_input.strip():
                try:
                    with st.spinner("Fetching channel videos..."):
                        data = get_channel_videos(channel_input.strip())
                    results = data.get("results", [])
                    info = data.get("playlist_info", {})
                    render_success(f"{info.get('ownerName', '')} — {info.get('numVideos', len(results))} videos")
                    render_video_list(results[:100])
                    if len(results) > 100:
                        st.caption(f"Showing first 100 of {len(results)} videos")
                except Exception as e:
                    render_error(f"Failed: {e}")
            else:
                render_error("Enter a channel @handle, URL, or ID above.")

    # -- Search in Channel --
    with ch_sub[2]:
        ch_search_q = st.text_input(
            "Search within channel",
            placeholder="Search query...",
            label_visibility="collapsed",
            key="ch_search_q",
        )
        if st.button("Search Channel", type="primary", key="ch_search_btn"):
            if channel_input.strip() and ch_search_q.strip():
                try:
                    with st.spinner("Searching channel..."):
                        data = search_channel(channel_input.strip(), ch_search_q.strip())
                    results = data.get("results", [])
                    st.caption(f"{len(results)} results found")
                    render_video_list(results)
                except Exception as e:
                    render_error(f"Failed: {e}")
            else:
                render_error("Enter both a channel and search query.")

    # -- Resolve ID --
    with ch_sub[3]:
        if st.button("Resolve Channel ID", type="primary", key="ch_resolve_btn"):
            if channel_input.strip():
                try:
                    with st.spinner("Resolving..."):
                        data = resolve_channel(channel_input.strip())
                    render_success(f"Channel ID: {data['channel_id']}")
                    st.code(data["channel_id"], language=None)
                    st.caption(f"Resolved from: {data['resolved_from']}")
                except Exception as e:
                    render_error(f"Failed: {e}")
            else:
                render_error("Enter a channel @handle, URL, or ID above.")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4: PLAYLIST
# ═══════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("##### Playlist Videos")

    pl_col1, pl_col2 = st.columns([4, 1])
    with pl_col1:
        playlist_input = st.text_input(
            "Playlist",
            placeholder="Playlist URL or ID (PL…, UU…, LL…)",
            label_visibility="collapsed",
            key="playlist_input",
        )
    with pl_col2:
        pl_btn = st.button("Get Videos", type="primary", use_container_width=True, key="pl_btn")

    if pl_btn and playlist_input.strip():
        try:
            with st.spinner("Fetching playlist..."):
                data = get_playlist_videos(playlist_input.strip())
            results = data.get("results", [])
            info = data.get("playlist_info", {})
            render_success(f"{info.get('title', 'Playlist')} — {info.get('numVideos', len(results))} videos")
            render_video_list(results)
        except Exception as e:
            render_error(f"Failed: {e}")
    elif pl_btn:
        render_error("Please enter a playlist URL or ID.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
render_footer()
