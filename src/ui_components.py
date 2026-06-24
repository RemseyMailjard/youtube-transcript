"""Reusable Streamlit UI components for TranscriptBuddy.

Each function renders a self-contained visual block using custom HTML/CSS
from styles.py and native Streamlit widgets.
"""

from __future__ import annotations

import html
import math
from datetime import timedelta

import streamlit as st
import streamlit.components.v1 as components

from .models import TranscriptResult


def render_hero(title: str, tagline: str) -> None:
    st.markdown(
        f"""
        <div class="tb-hero">
            <div class="pill">Free &amp; Open Source</div>
            <h1>{html.escape(title)}</h1>
            <p class="tagline">{html.escape(tagline)}</p>
            <div class="features">
                <div class="feature-item">
                    <span class="feature-icon">🌍</span> 11 languages
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📋</span> One-click copy
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📥</span> TXT, MD, JSON export
                </div>
                <div class="feature-item">
                    <span class="feature-icon">⚡</span> Instant results
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_how_it_works() -> None:
    st.markdown('<p class="tb-section-title">How it works</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="tb-steps">
            <div class="tb-step">
                <div class="step-num">1</div>
                <h4>Paste a URL</h4>
                <p>Enter any YouTube video link or video ID. We support all standard URL formats including shorts and embeds.</p>
            </div>
            <div class="tb-step">
                <div class="step-num">2</div>
                <h4>Get transcript</h4>
                <p>Click the button and we'll fetch the available captions. Choose your preferred language in the sidebar.</p>
            </div>
            <div class="tb-step">
                <div class="step-num">3</div>
                <h4>Copy or download</h4>
                <p>Copy the clean transcript to your clipboard, or download it as TXT, Markdown, or JSON.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(result: TranscriptResult) -> None:
    reading_min = result.reading_time_minutes
    if reading_min < 1:
        reading_str = "< 1 min"
    else:
        reading_str = f"{math.ceil(reading_min)} min"

    lang_display = f"{result.language} ({result.language_code.upper()})"
    caption_type = "Auto-generated" if result.is_generated else "Manual"

    st.markdown(
        f"""
        <div class="tb-stats">
            <div class="tb-card">
                <div class="icon">🎬</div>
                <div class="label">Video ID</div>
                <div class="value" style="font-size:1rem;word-break:break-all;">{html.escape(result.video_id)}</div>
            </div>
            <div class="tb-card">
                <div class="icon">🌐</div>
                <div class="label">Language</div>
                <div class="value" style="font-size:1.1rem;">{html.escape(lang_display)}</div>
                <div class="hint">{html.escape(caption_type)}</div>
            </div>
            <div class="tb-card">
                <div class="icon">📝</div>
                <div class="label">Words</div>
                <div class="value">{result.word_count:,}</div>
            </div>
            <div class="tb-card">
                <div class="icon">🔤</div>
                <div class="label">Characters</div>
                <div class="value">{result.char_count:,}</div>
            </div>
            <div class="tb-card">
                <div class="icon">📖</div>
                <div class="label">Reading time</div>
                <div class="value" style="font-size:1.2rem;">{reading_str}</div>
                <div class="hint">~200 words/min</div>
            </div>
            <div class="tb-card">
                <div class="icon">📋</div>
                <div class="label">Lines</div>
                <div class="value">{result.line_count:,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_success_bar(video_id: str, language: str) -> None:
    st.markdown(
        f"""
        <div class="tb-success-bar">
            <span>✅</span>
            Transcript fetched successfully
            <span class="tb-badge success">{html.escape(language)}</span>
            <span class="tb-badge muted">{html.escape(video_id)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error(message: str, hint: str | None = None) -> None:
    hint_html = ""
    if hint:
        hint_html = f'<div class="error-hint">{html.escape(hint)}</div>'
    st.markdown(
        f"""
        <div class="tb-error-bar">
            <span class="error-icon">⚠️</span>
            <div>
                <div class="error-text">{html.escape(message)}</div>
                {hint_html}
            </div>
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
    escaped = html.escape(text).replace("\\", "\\\\").replace("`", "\\`").replace("'", "\\'")
    js_safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    components.html(
        f"""
        <div style="display:flex;justify-content:flex-end;margin-bottom:4px;font-family:Inter,-apple-system,sans-serif;">
            <button id="copyBtn_{key}" class="tb-copy-btn" onclick="copyTranscript_{key}()" style="
                display:inline-flex;align-items:center;gap:6px;
                background:#fff;border:1.5px solid #e2e8f0;border-radius:6px;
                padding:7px 14px;font-size:13px;font-weight:600;
                color:#475569;cursor:pointer;transition:all .15s ease;
                font-family:inherit;
            ">
                <span id="copyIcon_{key}">📋</span>
                <span id="copyText_{key}">Copy transcript</span>
            </button>
        </div>
        <script>
        function copyTranscript_{key}() {{
            const text = `{js_safe}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copyBtn_{key}');
                const icon = document.getElementById('copyIcon_{key}');
                const txt = document.getElementById('copyText_{key}');
                btn.style.borderColor = '#10b981';
                btn.style.color = '#047857';
                btn.style.background = 'rgba(16,185,129,0.08)';
                icon.textContent = '✅';
                txt.textContent = 'Copied!';
                setTimeout(() => {{
                    btn.style.borderColor = '#e2e8f0';
                    btn.style.color = '#475569';
                    btn.style.background = '#fff';
                    icon.textContent = '📋';
                    txt.textContent = 'Copy transcript';
                }}, 2000);
            }}).catch(() => {{
                const txt = document.getElementById('copyText_{key}');
                txt.textContent = 'Use Ctrl+C to copy';
                setTimeout(() => {{ txt.textContent = 'Copy transcript'; }}, 3000);
            }});
        }}
        </script>
        """,
        height=45,
    )


def render_history_sidebar(history: list[dict]) -> None:
    if not history:
        return

    st.markdown('<p class="sidebar-section">Recent transcripts</p>', unsafe_allow_html=True)
    for i, entry in enumerate(reversed(history[-5:])):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"**{entry['video_id']}** · {entry['language']}<br>"
                f"<span style='color:#94a3b8;font-size:.78rem'>{entry['time']}</span>",
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("Load", key=f"hist_{i}", use_container_width=True):
                st.session_state["video_input"] = f"https://www.youtube.com/watch?v={entry['video_id']}"
                st.rerun()


def render_footer() -> None:
    st.markdown(
        """
        <div class="tb-footer">
            <div style="margin-bottom:.3rem;">
                <strong style="color:#0f172a;font-size:.95rem;">TranscriptBuddy</strong>
            </div>
            Turn YouTube videos into clean, usable transcripts<br>
            Built with Streamlit &amp; youtube-transcript-api · Free &amp; open source<br>
            <span style="font-size:.76rem;color:#94a3b8;">
                Transcript availability depends on YouTube captions provided by video creators.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="tb-footer-brand">
            <span>Built by</span>
            <span class="author-name">Remsey Mailjard</span>
            <a href="https://www.linkedin.com/in/remseymailjard/" target="_blank" rel="noopener" class="tb-linkedin-btn">
                🔗 LinkedIn
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fmt_hms(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))
