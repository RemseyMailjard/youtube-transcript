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
# Session state defaults
# ---------------------------------------------------------------------------
_DEFAULTS: dict[str, Any] = {
    "transcript_result": None,
    "transcript_error": None,
    "search_results": None,
    "search_error": None,
    "channel_latest_data": None,
    "channel_videos_data": None,
    "channel_search_data": None,
    "channel_resolve_data": None,
    "channel_error": None,
    "playlist_data": None,
    "playlist_error": None,
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
import streamlit.components.v1 as _components
_components.html(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap" rel="stylesheet">
    <div style="background:linear-gradient(135deg,#FF0000 0%,#CC0000 100%);padding:2.5rem 2rem 2rem;text-align:center;font-family:Inter,sans-serif;">
        <div style="color:#FFFFFF;font-size:2.8rem;font-weight:900;margin:0 0 0.5rem 0;letter-spacing:-0.03em;">YouTube to Transcript</div>
        <div style="color:rgba(255,255,255,0.9);font-size:1.05rem;line-height:1.6;">Generate YouTube Transcript for FREE.<br>
        Access all Transcript Languages, Easy Copy and Edit!</div>
    </div>
    """,
    height=190,
)


# ---------------------------------------------------------------------------
# Callback functions
# ---------------------------------------------------------------------------
def _fetch_transcript() -> None:
    st.session_state["transcript_result"] = None
    st.session_state["transcript_error"] = None
    url = st.session_state.get("transcript_url", "").strip()
    if not url:
        st.session_state["transcript_error"] = "Please enter a YouTube URL or video ID."
        return
    _do_fetch_for_url(url)


def _fetch_from_search(video_id: str) -> None:
    st.session_state["transcript_url"] = video_id
    _do_fetch_for_url(video_id)


def _do_fetch_for_url(url: str) -> None:
    st.session_state["transcript_result"] = None
    st.session_state["transcript_error"] = None
    langs = st.session_state.get("lang_selection", DEFAULT_LANGUAGES)
    try:
        result = get_transcript(url, langs or DEFAULT_LANGUAGES)
        st.session_state["transcript_result"] = result
    except ValueError:
        st.session_state["transcript_error"] = "Invalid YouTube URL or video ID."
    except VideoUnavailable:
        st.session_state["transcript_error"] = "Video unavailable — may be private or deleted."
    except TranscriptsDisabled:
        st.session_state["transcript_error"] = "Transcripts are disabled for this video."
    except NoTranscriptFound:
        st.session_state["transcript_error"] = f"No transcript found. Tried: {', '.join(langs or DEFAULT_LANGUAGES)}"
    except _BLOCK_EXCS:  # type: ignore[misc]
        st.session_state["transcript_error"] = "YouTube is blocking this request. Try later or run locally."
    except CouldNotRetrieveTranscript as e:
        st.session_state["transcript_error"] = f"Could not retrieve transcript: {e}"
    except Exception as e:
        st.session_state["transcript_error"] = f"{type(e).__name__}: {e}"


def _do_search() -> None:
    st.session_state["search_results"] = None
    st.session_state["search_error"] = None
    q = st.session_state.get("search_query", "").strip()
    if not q:
        st.session_state["search_error"] = "Please enter a search query."
        return
    stype = st.session_state.get("search_type", "video")
    try:
        st.session_state["search_results"] = search_youtube(q, search_type=stype)
    except Exception as e:
        st.session_state["search_error"] = f"Search failed: {e}"


def _do_channel_latest() -> None:
    st.session_state["channel_latest_data"] = None
    st.session_state["channel_error"] = None
    ch = st.session_state.get("channel_input", "").strip()
    if not ch:
        st.session_state["channel_error"] = "Enter a channel @handle, URL, or ID."
        return
    try:
        st.session_state["channel_latest_data"] = get_channel_latest(ch)
    except Exception as e:
        st.session_state["channel_error"] = f"Failed: {e}"


def _do_channel_videos() -> None:
    st.session_state["channel_videos_data"] = None
    st.session_state["channel_error"] = None
    ch = st.session_state.get("channel_input", "").strip()
    if not ch:
        st.session_state["channel_error"] = "Enter a channel @handle, URL, or ID."
        return
    try:
        st.session_state["channel_videos_data"] = get_channel_videos(ch)
    except Exception as e:
        st.session_state["channel_error"] = f"Failed: {e}"


def _do_channel_search() -> None:
    st.session_state["channel_search_data"] = None
    st.session_state["channel_error"] = None
    ch = st.session_state.get("channel_input", "").strip()
    q = st.session_state.get("ch_search_q", "").strip()
    if not ch or not q:
        st.session_state["channel_error"] = "Enter both a channel and search query."
        return
    try:
        st.session_state["channel_search_data"] = search_channel(ch, q)
    except Exception as e:
        st.session_state["channel_error"] = f"Failed: {e}"


def _do_channel_resolve() -> None:
    st.session_state["channel_resolve_data"] = None
    st.session_state["channel_error"] = None
    ch = st.session_state.get("channel_input", "").strip()
    if not ch:
        st.session_state["channel_error"] = "Enter a channel @handle, URL, or ID."
        return
    try:
        st.session_state["channel_resolve_data"] = resolve_channel(ch)
    except Exception as e:
        st.session_state["channel_error"] = f"Failed: {e}"


def _do_playlist() -> None:
    st.session_state["playlist_data"] = None
    st.session_state["playlist_error"] = None
    pl = st.session_state.get("playlist_input", "").strip()
    if not pl:
        st.session_state["playlist_error"] = "Please enter a playlist URL or ID."
        return
    try:
        st.session_state["playlist_data"] = get_playlist_videos(pl)
    except Exception as e:
        st.session_state["playlist_error"] = f"Failed: {e}"


# ---------------------------------------------------------------------------
# Navigation tabs
# ---------------------------------------------------------------------------
tabs = st.tabs(["Transcript", "Search", "Channel", "Playlist", "API Docs"])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: TRANSCRIPT
# ═══════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("##### Get Transcript")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        st.text_input(
            "YouTube URL",
            placeholder="Paste YouTube URL here...",
            label_visibility="collapsed",
            key="transcript_url",
        )
    with col_btn:
        st.button(
            "Get Transcript",
            type="primary",
            use_container_width=True,
            on_click=_fetch_transcript,
        )

    with st.expander("Language & format options"):
        lang_col, fmt_col = st.columns(2)
        with lang_col:
            st.multiselect(
                "Preferred languages",
                options=list(SUPPORTED_LANGUAGES.keys()),
                default=DEFAULT_LANGUAGES,
                format_func=lambda c: f"{SUPPORTED_LANGUAGES[c]} ({c})",
                key="lang_selection",
            )
        with fmt_col:
            include_ts = st.checkbox("Include timestamps", value=False, key="include_ts")
            merge_para = st.checkbox("Merge into paragraphs", value=False, key="merge_para")

    # Show error
    if st.session_state["transcript_error"]:
        render_error(st.session_state["transcript_error"])

    # Show result
    result: TranscriptResult | None = st.session_state["transcript_result"]
    if result is not None:
        render_success(f"Transcript fetched — {result.language} ({result.language_code.upper()})")
        render_transcript_stats(result)

        cleaned = clean_transcript(
            result.snippets,
            include_timestamps=include_ts,
            merge_paragraphs=merge_para,
        )

        render_copy_button(cleaned, key="transcript")
        render_transcript_block(cleaned)

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

        with st.expander("Table view"):
            df = pd.DataFrame({
                "Start": [fmt_hms(s.start) for s in result.snippets],
                "Duration": [round(s.duration, 2) for s in result.snippets],
                "Text": [s.text for s in result.snippets],
            })
            st.dataframe(df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: SEARCH
# ═══════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("##### Search YouTube")

    s_col1, s_col2, s_col3 = st.columns([3, 1, 1])
    with s_col1:
        st.text_input(
            "Search query",
            placeholder="Search YouTube...",
            label_visibility="collapsed",
            key="search_query",
        )
    with s_col2:
        st.selectbox("Type", ["video", "channel"], label_visibility="collapsed", key="search_type")
    with s_col3:
        st.button("Search", type="primary", use_container_width=True, on_click=_do_search)

    if st.session_state["search_error"]:
        render_error(st.session_state["search_error"])

    # Show transcript result fetched from search (above search results)
    search_tr: TranscriptResult | None = st.session_state["transcript_result"]
    if search_tr is not None:
        render_success(f"Transcript — {search_tr.video_id} — {search_tr.language} ({search_tr.language_code.upper()})")
        render_transcript_stats(search_tr)

        s_cleaned = clean_transcript(
            search_tr.snippets,
            include_timestamps=st.session_state.get("include_ts", False),
            merge_paragraphs=st.session_state.get("merge_para", False),
        )

        render_copy_button(s_cleaned, key="search_transcript")
        render_transcript_block(s_cleaned)

        sd1, sd2, sd3 = st.columns(3)
        with sd1:
            st.download_button(
                "Download .txt",
                data=to_txt(search_tr, body=s_cleaned),
                file_name=build_filename(search_tr.video_id, search_tr.fetched_at, "txt"),
                mime="text/plain", use_container_width=True, key="s_dl_txt",
            )
        with sd2:
            st.download_button(
                "Download .md",
                data=to_markdown(search_tr, body=s_cleaned),
                file_name=build_filename(search_tr.video_id, search_tr.fetched_at, "md"),
                mime="text/markdown", use_container_width=True, key="s_dl_md",
            )
        with sd3:
            st.download_button(
                "Download .json",
                data=to_json(search_tr),
                file_name=build_filename(search_tr.video_id, search_tr.fetched_at, "json"),
                mime="application/json", use_container_width=True, key="s_dl_json",
            )
        st.divider()

    search_data = st.session_state["search_results"]
    if search_data:
        results = search_data.get("results", [])
        st.caption(f"{len(results)} results found")

        stype = st.session_state.get("search_type", "video")
        if stype == "video":
            for i, v in enumerate(results):
                video_id = v.get("videoId", "")
                title = v.get("title", "Untitled")
                channel = v.get("channelTitle", "")
                length = v.get("lengthText", "")
                views = v.get("viewCountText", "")
                thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
                meta = " · ".join(p for p in [channel, length, views] if p)

                col_thumb, col_info, col_action = st.columns([1.5, 3, 1])
                with col_thumb:
                    if thumb:
                        st.image(thumb, use_container_width=True)
                with col_info:
                    st.markdown(f"**{html.escape(title)}**", unsafe_allow_html=True)
                    st.caption(meta)
                with col_action:
                    st.button(
                        "Get Transcript",
                        key=f"sr_{i}",
                        type="primary",
                        use_container_width=True,
                        on_click=_fetch_from_search,
                        args=(video_id,),
                    )
                st.divider()
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



# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: CHANNEL
# ═══════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("##### Channel Explorer")

    st.text_input(
        "Channel",
        placeholder="@handle, channel URL, or UC… ID",
        label_visibility="collapsed",
        key="channel_input",
    )

    ch_sub = st.tabs(["Latest (RSS)", "All Videos", "Search in Channel", "Resolve ID"])

    if st.session_state["channel_error"]:
        render_error(st.session_state["channel_error"])

    # -- Latest (RSS) --
    with ch_sub[0]:
        st.button("Get Latest Videos", type="primary", key="ch_latest_btn", on_click=_do_channel_latest)

        data = st.session_state["channel_latest_data"]
        if data:
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

    # -- All Videos --
    with ch_sub[1]:
        st.button("Get All Videos", type="primary", key="ch_videos_btn", on_click=_do_channel_videos)

        data = st.session_state["channel_videos_data"]
        if data:
            results = data.get("results", [])
            info = data.get("playlist_info", {})
            render_success(f"{info.get('ownerName', '')} — {info.get('numVideos', len(results))} videos")
            render_video_list(results[:100])
            if len(results) > 100:
                st.caption(f"Showing first 100 of {len(results)} videos")

    # -- Search in Channel --
    with ch_sub[2]:
        st.text_input(
            "Search within channel",
            placeholder="Search query...",
            label_visibility="collapsed",
            key="ch_search_q",
        )
        st.button("Search Channel", type="primary", key="ch_search_btn", on_click=_do_channel_search)

        data = st.session_state["channel_search_data"]
        if data:
            results = data.get("results", [])
            st.caption(f"{len(results)} results found")
            render_video_list(results)

    # -- Resolve ID --
    with ch_sub[3]:
        st.button("Resolve Channel ID", type="primary", key="ch_resolve_btn", on_click=_do_channel_resolve)

        data = st.session_state["channel_resolve_data"]
        if data:
            render_success(f"Channel ID: {data['channel_id']}")
            st.code(data["channel_id"], language=None)
            st.caption(f"Resolved from: {data['resolved_from']}")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4: PLAYLIST
# ═══════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("##### Playlist Videos")

    pl_col1, pl_col2 = st.columns([4, 1])
    with pl_col1:
        st.text_input(
            "Playlist",
            placeholder="Playlist URL or ID (PL…, UU…, LL…)",
            label_visibility="collapsed",
            key="playlist_input",
        )
    with pl_col2:
        st.button("Get Videos", type="primary", use_container_width=True, key="pl_btn", on_click=_do_playlist)

    if st.session_state["playlist_error"]:
        render_error(st.session_state["playlist_error"])

    pl_data = st.session_state["playlist_data"]
    if pl_data:
        results = pl_data.get("results", [])
        info = pl_data.get("playlist_info", {})
        render_success(f"{info.get('title', 'Playlist')} — {info.get('numVideos', len(results))} videos")
        render_video_list(results)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5: API DOCS
# ═══════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("##### REST API Documentation")
    st.markdown("Base URL: `https://youtube-transcript-remsey.streamlit.app/api/v2`")
    st.code('uv run uvicorn api:app --port 8000', language="bash")

    st.divider()

    # ── Endpoints table ──
    st.markdown("##### Endpoints")
    st.markdown("""
| Endpoint | Description | Method |
|----------|-------------|--------|
| `/api/v2/youtube/transcript` | Extract video transcript | GET |
| `/api/v2/youtube/search` | Search videos or channels | GET |
| `/api/v2/youtube/channel/resolve` | Resolve @handle to channel ID | GET |
| `/api/v2/youtube/channel/search` | Search within a channel | GET |
| `/api/v2/youtube/channel/videos` | List channel uploads | GET |
| `/api/v2/youtube/channel/latest` | Latest 15 videos (RSS) | GET |
| `/api/v2/youtube/playlist/videos` | List playlist videos | GET |
""")

    st.divider()

    # ── Transcript ──
    st.markdown("##### Transcript")
    st.code("GET /api/v2/youtube/transcript", language=None)
    st.markdown("""
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | string | Yes | — | YouTube URL or video ID |
| `format` | string | No | `json` | `json` or `text` |
| `include_timestamp` | bool | No | `true` | Include timestamps |
| `send_metadata` | bool | No | `false` | Include video metadata |
""")
    with st.expander("Example response"):
        st.code("""{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [
    { "text": "Never gonna give you up", "start": 0.0, "duration": 4.12 },
    { "text": "Never gonna let you down", "start": 4.12, "duration": 3.85 }
  ]
}""", language="json")

    st.divider()

    # ── Search ──
    st.markdown("##### Search")
    st.code("GET /api/v2/youtube/search", language=None)
    st.markdown("""
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | — | Search query (1-200 chars) |
| `type` | string | No | `video` | `video` or `channel` |
""")

    st.divider()

    # ── Channel ──
    st.markdown("##### Channel Endpoints")
    st.markdown("""
**Resolve** — `GET /api/v2/youtube/channel/resolve?input=@TED`

**Search** — `GET /api/v2/youtube/channel/search?channel=@TED&q=innovation`

**Videos** — `GET /api/v2/youtube/channel/videos?channel=@TED`

**Latest (RSS)** — `GET /api/v2/youtube/channel/latest?channel=@TED`

All accept `@handle`, channel URL, or `UC…` ID.
""")

    st.divider()

    # ── Playlist ──
    st.markdown("##### Playlist")
    st.code("GET /api/v2/youtube/playlist/videos?playlist=PLrAXtmErZgOe...", language=None)
    st.markdown("Accepts playlist URL or ID (PL…, UU…, LL…).")

    st.divider()

    # ── Code examples ──
    st.markdown("##### Code Examples")
    ex_py, ex_js, ex_curl = st.tabs(["Python", "JavaScript", "cURL"])

    with ex_py:
        st.code("""import requests

BASE = "https://youtube-transcript-remsey.streamlit.app/api/v2"

# Get transcript
resp = requests.get(f"{BASE}/youtube/transcript", params={
    "video_url": "dQw4w9WgXcQ",
    "format": "json",
    "include_timestamp": True,
})
for segment in resp.json()["transcript"]:
    print(f"[{segment['start']}s] {segment['text']}")

# Search
resp = requests.get(f"{BASE}/youtube/search", params={"q": "python", "type": "video"})
for v in resp.json()["results"]:
    print(f"{v['title']} ({v['videoId']})")
""", language="python")

    with ex_js:
        st.code("""const BASE = "https://youtube-transcript-remsey.streamlit.app/api/v2";

const resp = await fetch(`${BASE}/youtube/transcript?video_url=dQw4w9WgXcQ`);
const data = await resp.json();
data.transcript.forEach(s => console.log(`[${s.start}s] ${s.text}`));
""", language="javascript")

    with ex_curl:
        st.code("""# Transcript
curl "https://youtube-transcript-remsey.streamlit.app/api/v2/youtube/transcript?video_url=dQw4w9WgXcQ"

# Search
curl "https://youtube-transcript-remsey.streamlit.app/api/v2/youtube/search?q=python&type=video"

# Channel latest
curl "https://youtube-transcript-remsey.streamlit.app/api/v2/youtube/channel/latest?channel=@TED"
""", language="bash")

    st.divider()

    # ── Error handling ──
    st.markdown("##### Error Handling")
    st.markdown("""
| Status | Code | Description |
|--------|------|-------------|
| `200` | — | Success |
| `400` | `INVALID_INPUT` | Bad request |
| `404` | `VIDEO_NOT_FOUND` | Video not found |
| `404` | `NO_TRANSCRIPT` | No transcript available |
| `408` | `REQUEST_BLOCKED` | Blocked by YouTube |
| `422` | `INVALID_URL` | Invalid URL format |
| `500` | `INTERNAL_ERROR` | Server error |
""")

    st.info("Interactive Swagger UI available at [localhost:8000/docs](https://youtube-transcript-remsey.streamlit.app/docs) when the API server is running.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
render_footer()
