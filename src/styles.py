"""Global CSS for TranscriptBuddy — minimal design."""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --tb-yellow: #FCBF17;
    --tb-yellow-dark: #E5A800;
    --tb-dark: #2D2D2D;
    --tb-text: #333333;
    --tb-text-light: #666666;
    --tb-muted: #999999;
    --tb-border: #E8E8E8;
    --tb-bg: #FFFFFF;
    --tb-bg-light: #FAFAFA;
    --tb-radius: 12px;
    --tb-radius-sm: 8px;
    --tb-shadow: 0 2px 8px rgba(0,0,0,0.06);
    --tb-shadow-lg: 0 4px 16px rgba(0,0,0,0.1);
}

#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }
.stDeployButton { display: none !important; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 0;
    padding-bottom: 3rem;
    max-width: 900px;
}

[data-testid="stSidebar"] {
    background: #FAFAFA;
    border-right: 1px solid var(--tb-border);
}

/* Hero banner */
.tb-hero {
    background: var(--tb-yellow);
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    margin: -1rem -1rem 2rem -1rem;
}
.tb-hero h1 {
    color: var(--tb-dark);
    font-size: 2.8rem;
    font-weight: 900;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
}
.tb-hero p {
    color: var(--tb-dark);
    font-size: 1rem;
    margin: 0;
    opacity: 0.85;
    line-height: 1.5;
}

/* Nav tabs */
.tb-nav {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--tb-border);
    margin-bottom: 1.5rem;
}
.tb-nav-item {
    padding: 0.7rem 1.2rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--tb-muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.15s ease;
    text-decoration: none;
}
.tb-nav-item:hover {
    color: var(--tb-dark);
}
.tb-nav-item.active {
    color: var(--tb-dark);
    border-bottom-color: var(--tb-yellow);
}

/* Section titles */
.tb-section {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--tb-muted);
    margin: 1.5rem 0 0.8rem 0;
}

/* Result card */
.tb-result-card {
    background: var(--tb-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--tb-shadow);
}
.tb-result-card:hover {
    box-shadow: var(--tb-shadow-lg);
}
.tb-result-card h4 {
    margin: 0 0 0.3rem 0;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--tb-text);
}
.tb-result-card .meta {
    font-size: 0.8rem;
    color: var(--tb-text-light);
}
.tb-result-card .meta span {
    margin-right: 1rem;
}

/* Transcript area */
.tb-transcript {
    background: var(--tb-bg-light);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius-sm);
    padding: 1.5rem;
    line-height: 1.8;
    font-size: 0.92rem;
    color: var(--tb-text);
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 500px;
    overflow-y: auto;
}
.tb-transcript::-webkit-scrollbar { width: 5px; }
.tb-transcript::-webkit-scrollbar-thumb {
    background: var(--tb-border);
    border-radius: 3px;
}

/* Stats row */
.tb-stats-row {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin: 0.5rem 0 1rem 0;
}
.tb-stat {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
}
.tb-stat .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--tb-muted);
    font-weight: 600;
}
.tb-stat .value {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--tb-text);
}

/* Success / error bars */
.tb-success {
    background: #E8F5E9;
    border: 1px solid #C8E6C9;
    border-radius: var(--tb-radius-sm);
    padding: 0.7rem 1rem;
    color: #2E7D32;
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}
.tb-error {
    background: #FFEBEE;
    border: 1px solid #FFCDD2;
    border-radius: var(--tb-radius-sm);
    padding: 0.7rem 1rem;
    color: #C62828;
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

/* Video list item */
.tb-video-item {
    display: flex;
    gap: 1rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--tb-border);
    align-items: flex-start;
}
.tb-video-item:last-child { border-bottom: none; }
.tb-video-item img {
    width: 160px;
    height: 90px;
    object-fit: cover;
    border-radius: 6px;
    flex-shrink: 0;
}
.tb-video-item .info h4 {
    margin: 0 0 0.3rem 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--tb-text);
    line-height: 1.3;
}
.tb-video-item .info .meta {
    font-size: 0.78rem;
    color: var(--tb-text-light);
}

/* Primary button override */
button[kind="primary"] {
    background: var(--tb-yellow) !important;
    color: var(--tb-dark) !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    border-radius: var(--tb-radius-sm) !important;
}
button[kind="primary"]:hover {
    background: var(--tb-yellow-dark) !important;
    box-shadow: var(--tb-shadow) !important;
}

/* Input styling */
.stTextInput input {
    border-radius: var(--tb-radius-sm) !important;
    border: 1.5px solid var(--tb-border) !important;
    padding: 0.6rem 0.9rem !important;
    font-size: 0.92rem !important;
}
.stTextInput input:focus {
    border-color: var(--tb-yellow) !important;
    box-shadow: 0 0 0 3px rgba(252,191,23,0.15) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid var(--tb-border);
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
    color: var(--tb-muted);
}
.stTabs [aria-selected="true"] {
    color: var(--tb-dark) !important;
    border-bottom: 2px solid var(--tb-yellow) !important;
}

/* Footer */
.tb-footer {
    text-align: center;
    color: var(--tb-muted);
    font-size: 0.8rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--tb-border);
}
.tb-footer a {
    color: var(--tb-text);
    font-weight: 600;
    text-decoration: none;
}
.tb-footer a:hover { text-decoration: underline; }

/* Download buttons */
.stDownloadButton button {
    border-radius: var(--tb-radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
