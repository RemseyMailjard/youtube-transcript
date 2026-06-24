"""Global CSS for TranscriptBuddy.

Injected once per session via `inject_css()`. Kept in a single string so the
visual identity is easy to tweak without touching app logic.
"""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
:root {
    --tb-primary: #6366f1;
    --tb-primary-dark: #4f46e5;
    --tb-primary-soft: rgba(99, 102, 241, 0.10);
    --tb-text: #0f172a;
    --tb-muted: #64748b;
    --tb-border: #e2e8f0;
    --tb-card-bg: #ffffff;
    --tb-card-shadow: 0 1px 2px rgba(15, 23, 42, 0.04),
                      0 8px 24px rgba(15, 23, 42, 0.06);
    --tb-radius: 14px;
}

/* Hide Streamlit chrome that doesn't belong on a SaaS-style app */
#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }
.stDeployButton { display: none !important; }

/* Tighten top padding so the hero sits closer to the top */
[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 2.2rem;
    padding-bottom: 4rem;
    max-width: 1180px;
}

/* === Hero ============================================================== */
.tb-hero {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 55%, #ec4899 100%);
    color: #fff;
    border-radius: var(--tb-radius);
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.6rem;
    box-shadow: var(--tb-card-shadow);
    position: relative;
    overflow: hidden;
}
.tb-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 85% 15%,
                rgba(255,255,255,0.20) 0%, transparent 55%);
    pointer-events: none;
}
.tb-hero h1 {
    color: #fff;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0 0 .5rem 0;
}
.tb-hero p.tagline {
    color: rgba(255,255,255,0.92);
    font-size: 1.05rem;
    margin: 0 0 .25rem 0;
    max-width: 640px;
}
.tb-hero p.subtle {
    color: rgba(255,255,255,0.75);
    font-size: .92rem;
    margin: .75rem 0 0 0;
    max-width: 680px;
}
.tb-hero .pill {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.30);
    color: #fff;
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
    padding: .25rem .65rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}

/* === Section heading =================================================== */
.tb-section-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--tb-text);
    margin: 1.4rem 0 .6rem 0;
}
.tb-section-sub {
    color: var(--tb-muted);
    font-size: .9rem;
    margin: -.4rem 0 .8rem 0;
}

/* === Stat cards ======================================================== */
.tb-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: .9rem;
    margin: .5rem 0 1.2rem 0;
}
.tb-card {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius);
    padding: 1rem 1.1rem;
    box-shadow: var(--tb-card-shadow);
}
.tb-card .label {
    text-transform: uppercase;
    font-size: .72rem;
    letter-spacing: .07em;
    color: var(--tb-muted);
    font-weight: 600;
    margin-bottom: .35rem;
}
.tb-card .value {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--tb-text);
    line-height: 1.1;
}
.tb-card .hint {
    color: var(--tb-muted);
    font-size: .78rem;
    margin-top: .25rem;
}

/* === Badges / pills ==================================================== */
.tb-badge {
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    background: var(--tb-primary-soft);
    color: var(--tb-primary-dark);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 999px;
    padding: .2rem .65rem;
    font-size: .78rem;
    font-weight: 600;
    margin-right: .35rem;
}
.tb-badge.success { background: rgba(16,185,129,.10); color: #047857; border-color: rgba(16,185,129,.30); }
.tb-badge.muted   { background: rgba(100,116,139,.10); color: #475569; border-color: rgba(100,116,139,.25); }

/* === Empty state / how-it-works ======================================== */
.tb-step {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius);
    padding: 1.1rem 1.2rem;
    height: 100%;
    box-shadow: var(--tb-card-shadow);
}
.tb-step .step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    border-radius: 999px;
    background: var(--tb-primary);
    color: #fff;
    font-weight: 700;
    font-size: .85rem;
    margin-bottom: .65rem;
}
.tb-step h4 { margin: 0 0 .25rem 0; font-size: 1rem; font-weight: 600; }
.tb-step p  { margin: 0; color: var(--tb-muted); font-size: .9rem; }

/* === Transcript reading area =========================================== */
.tb-transcript {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius);
    padding: 1.4rem 1.6rem;
    line-height: 1.7;
    font-size: 1rem;
    color: var(--tb-text);
    box-shadow: var(--tb-card-shadow);
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 560px;
    overflow-y: auto;
}

/* === History rows ====================================================== */
.tb-history-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid var(--tb-border);
    border-radius: 10px;
    padding: .55rem .85rem;
    margin-bottom: .45rem;
    background: var(--tb-card-bg);
}
.tb-history-row .meta {
    color: var(--tb-muted);
    font-size: .82rem;
}

/* === Footer ============================================================ */
.tb-footer {
    text-align: center;
    color: var(--tb-muted);
    font-size: .82rem;
    margin-top: 3rem;
    padding-top: 1.4rem;
    border-top: 1px solid var(--tb-border);
}

/* === Streamlit native widget polish ==================================== */
button[kind="primary"] {
    background: var(--tb-primary) !important;
    border: 1px solid var(--tb-primary) !important;
    box-shadow: 0 1px 2px rgba(79,70,229,.20);
}
button[kind="primary"]:hover {
    background: var(--tb-primary-dark) !important;
    border-color: var(--tb-primary-dark) !important;
}
.stTextInput input, .stTextArea textarea {
    border-radius: 10px !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: .4rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
}
</style>
"""


def inject_css() -> None:
    """Inject TranscriptBuddy's global CSS. Safe to call once per rerun."""
    st.markdown(_CSS, unsafe_allow_html=True)
