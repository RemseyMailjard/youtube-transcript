"""Reusable Streamlit UI components — minimal design."""

from __future__ import annotations

import html
import math
from datetime import timedelta
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from .models import TranscriptResult


def render_hero() -> None:
    st.markdown(
        """
        <div class="tb-hero">
            <h1>YouTube to Transcript</h1>
            <p>Generate YouTube Transcript for FREE.<br>
            Access all Transcript Languages, Easy Copy and Edit!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_transcript_stats(result: TranscriptResult) -> None:
    reading_min = result.reading_time_minutes
    reading_str = "< 1 min" if reading_min < 1 else f"{math.ceil(reading_min)} min"
    caption_type = "Auto" if result.is_generated else "Manual"

    st.markdown(
        f"""
        <div class="tb-stats-row">
            <div class="tb-stat"><div class="label">Language</div><div class="value">{html.escape(result.language)} ({result.language_code.upper()})</div></div>
            <div class="tb-stat"><div class="label">Type</div><div class="value">{caption_type}</div></div>
            <div class="tb-stat"><div class="label">Words</div><div class="value">{result.word_count:,}</div></div>
            <div class="tb-stat"><div class="label">Lines</div><div class="value">{result.line_count:,}</div></div>
            <div class="tb-stat"><div class="label">Reading</div><div class="value">{reading_str}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_transcript_block(text: str) -> None:
    st.markdown(
        f'<div class="tb-transcript">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def render_copy_button(text: str, key: str = "copy") -> None:
    js_safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    components.html(
        f"""
        <div style="display:flex;justify-content:flex-end;margin-bottom:4px;font-family:Inter,sans-serif;">
            <button id="copyBtn_{key}" onclick="doCopy_{key}()" style="
                display:inline-flex;align-items:center;gap:6px;
                background:#fff;border:1.5px solid #E8E8E8;border-radius:8px;
                padding:7px 14px;font-size:13px;font-weight:600;
                color:#666;cursor:pointer;transition:all .15s ease;font-family:inherit;
            ">
                <span id="copyIcon_{key}">📋</span>
                <span id="copyText_{key}">Copy</span>
            </button>
        </div>
        <script>
        function doCopy_{key}() {{
            navigator.clipboard.writeText(`{js_safe}`).then(() => {{
                document.getElementById('copyIcon_{key}').textContent = '✅';
                document.getElementById('copyText_{key}').textContent = 'Copied!';
                document.getElementById('copyBtn_{key}').style.borderColor = '#4CAF50';
                document.getElementById('copyBtn_{key}').style.color = '#2E7D32';
                setTimeout(() => {{
                    document.getElementById('copyIcon_{key}').textContent = '📋';
                    document.getElementById('copyText_{key}').textContent = 'Copy';
                    document.getElementById('copyBtn_{key}').style.borderColor = '#E8E8E8';
                    document.getElementById('copyBtn_{key}').style.color = '#666';
                }}, 2000);
            }});
        }}
        </script>
        """,
        height=45,
    )


def render_success(message: str) -> None:
    st.markdown(f'<div class="tb-success">{html.escape(message)}</div>', unsafe_allow_html=True)


def render_error(message: str, hint: str | None = None) -> None:
    full = message
    if hint:
        full += f" — {hint}"
    st.markdown(f'<div class="tb-error">{html.escape(full)}</div>', unsafe_allow_html=True)


def render_video_list(videos: list[dict[str, Any]]) -> None:
    for v in videos:
        video_id = v.get("videoId", "")
        title = v.get("title", "Untitled")
        channel = v.get("channelTitle", "")
        length = v.get("lengthText", "")
        views = v.get("viewCountText", "")
        thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""

        meta_parts = []
        if channel:
            meta_parts.append(channel)
        if length:
            meta_parts.append(length)
        if views:
            meta_parts.append(views)
        meta_str = " · ".join(meta_parts)

        st.markdown(
            f"""
            <div class="tb-video-item">
                <img src="{html.escape(thumb)}" alt="">
                <div class="info">
                    <h4>{html.escape(title)}</h4>
                    <div class="meta">{html.escape(meta_str)}</div>
                    <div class="meta" style="margin-top:2px;color:#999;">ID: {html.escape(video_id)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_footer() -> None:
    st.markdown(
        """
        <div class="tb-footer">
            <p>Built by <a href="https://www.linkedin.com/in/remseymailjard/" target="_blank">Remsey Mailjard</a>
            · Powered by youtube-transcript-api &amp; yt-dlp</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fmt_hms(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))
