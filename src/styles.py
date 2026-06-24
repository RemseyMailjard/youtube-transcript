"""Global CSS for TranscriptBuddy.

Injected once per session via `inject_css()`. Kept in a single string so the
visual identity is easy to tweak without touching app logic.
"""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --tb-primary: #6366f1;
    --tb-primary-dark: #4f46e5;
    --tb-primary-light: #818cf8;
    --tb-primary-soft: rgba(99, 102, 241, 0.08);
    --tb-accent: #ec4899;
    --tb-text: #0f172a;
    --tb-text-secondary: #475569;
    --tb-muted: #94a3b8;
    --tb-border: #e2e8f0;
    --tb-border-light: #f1f5f9;
    --tb-card-bg: #ffffff;
    --tb-bg-subtle: #f8fafc;
    --tb-card-shadow: 0 1px 3px rgba(15, 23, 42, 0.04),
                      0 4px 16px rgba(15, 23, 42, 0.06);
    --tb-card-shadow-lg: 0 4px 6px rgba(15, 23, 42, 0.04),
                         0 12px 32px rgba(15, 23, 42, 0.08);
    --tb-radius: 16px;
    --tb-radius-sm: 10px;
    --tb-radius-xs: 6px;
    --tb-success: #10b981;
    --tb-success-bg: rgba(16, 185, 129, 0.08);
    --tb-error: #ef4444;
    --tb-error-bg: rgba(239, 68, 68, 0.08);
    --tb-warning: #f59e0b;
    --tb-warning-bg: rgba(245, 158, 11, 0.08);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }
.stDeployButton { display: none !important; }

/* Global font */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Main container */
[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    max-width: 1120px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--tb-bg-subtle);
    border-right: 1px solid var(--tb-border);
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

/* === Hero ============================================================== */
.tb-hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 40%, #a855f7 70%, #ec4899 100%);
    color: #fff;
    border-radius: var(--tb-radius);
    padding: 2.8rem 3rem 2.4rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 24px rgba(99, 102, 241, 0.25);
    position: relative;
    overflow: hidden;
}
.tb-hero::before {
    content: "";
    position: absolute;
    top: -60%;
    right: -20%;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.tb-hero::after {
    content: "";
    position: absolute;
    bottom: -40%;
    left: -10%;
    width: 350px;
    height: 350px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.tb-hero .pill {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.25);
    color: #fff;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    padding: .3rem .75rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
}
.tb-hero h1 {
    color: #fff;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 .7rem 0;
    letter-spacing: -0.02em;
}
.tb-hero p.tagline {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    font-weight: 400;
    margin: 0;
    max-width: 560px;
    line-height: 1.5;
}
.tb-hero .features {
    display: flex;
    gap: 1.5rem;
    margin-top: 1.6rem;
    flex-wrap: wrap;
}
.tb-hero .feature-item {
    display: flex;
    align-items: center;
    gap: .4rem;
    color: rgba(255,255,255,0.85);
    font-size: .85rem;
    font-weight: 500;
}
.tb-hero .feature-icon {
    font-size: 1rem;
}

/* === Section headings ================================================== */
.tb-section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--tb-text);
    margin: 1.6rem 0 .5rem 0;
    letter-spacing: -0.01em;
}
.tb-section-sub {
    color: var(--tb-text-secondary);
    font-size: .88rem;
    margin: -.3rem 0 1rem 0;
    line-height: 1.5;
}

/* === Stat cards ======================================================== */
.tb-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: .75rem;
    margin: .5rem 0 1.5rem 0;
}
.tb-card {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius-sm);
    padding: 1rem 1.15rem;
    box-shadow: var(--tb-card-shadow);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.tb-card:hover {
    box-shadow: var(--tb-card-shadow-lg);
    transform: translateY(-1px);
}
.tb-card .icon {
    font-size: 1.2rem;
    margin-bottom: .4rem;
}
.tb-card .label {
    text-transform: uppercase;
    font-size: .68rem;
    letter-spacing: .08em;
    color: var(--tb-muted);
    font-weight: 600;
    margin-bottom: .35rem;
}
.tb-card .value {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--tb-text);
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.tb-card .hint {
    color: var(--tb-muted);
    font-size: .75rem;
    margin-top: .3rem;
}

/* === Badges / pills ==================================================== */
.tb-badge {
    display: inline-flex;
    align-items: center;
    gap: .3rem;
    background: var(--tb-primary-soft);
    color: var(--tb-primary-dark);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 999px;
    padding: .22rem .7rem;
    font-size: .76rem;
    font-weight: 600;
    white-space: nowrap;
}
.tb-badge.success {
    background: var(--tb-success-bg);
    color: #047857;
    border-color: rgba(16,185,129,.25);
}
.tb-badge.muted {
    background: rgba(148,163,184,.1);
    color: #64748b;
    border-color: rgba(148,163,184,.2);
}
.tb-badge.warning {
    background: var(--tb-warning-bg);
    color: #92400e;
    border-color: rgba(245,158,11,.25);
}

/* === How-it-works steps ================================================ */
.tb-steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1rem 0 1.5rem 0;
}
@media (max-width: 768px) {
    .tb-steps { grid-template-columns: 1fr; }
}
.tb-step {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius-sm);
    padding: 1.3rem 1.4rem;
    box-shadow: var(--tb-card-shadow);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.tb-step:hover {
    box-shadow: var(--tb-card-shadow-lg);
    transform: translateY(-2px);
}
.tb-step .step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--tb-primary) 0%, #8b5cf6 100%);
    color: #fff;
    font-weight: 700;
    font-size: .85rem;
    margin-bottom: .75rem;
}
.tb-step h4 {
    margin: 0 0 .35rem 0;
    font-size: .95rem;
    font-weight: 700;
    color: var(--tb-text);
}
.tb-step p {
    margin: 0;
    color: var(--tb-text-secondary);
    font-size: .85rem;
    line-height: 1.5;
}

/* === Transcript reading area =========================================== */
.tb-transcript {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius-sm);
    padding: 1.5rem 1.8rem;
    line-height: 1.8;
    font-size: .95rem;
    color: var(--tb-text);
    box-shadow: var(--tb-card-shadow);
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 520px;
    overflow-y: auto;
}
.tb-transcript::-webkit-scrollbar {
    width: 6px;
}
.tb-transcript::-webkit-scrollbar-track {
    background: transparent;
}
.tb-transcript::-webkit-scrollbar-thumb {
    background: var(--tb-border);
    border-radius: 3px;
}

/* === Copy button (JS clipboard) ======================================= */
.tb-copy-container {
    display: flex;
    justify-content: flex-end;
    margin-bottom: .5rem;
}
.tb-copy-btn {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius-xs);
    padding: .45rem .9rem;
    font-size: .82rem;
    font-weight: 600;
    color: var(--tb-text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: inherit;
}
.tb-copy-btn:hover {
    border-color: var(--tb-primary);
    color: var(--tb-primary);
    background: var(--tb-primary-soft);
}
.tb-copy-btn.copied {
    border-color: var(--tb-success);
    color: #047857;
    background: var(--tb-success-bg);
}

/* === Result header bar ================================================= */
.tb-result-header {
    display: flex;
    align-items: center;
    gap: .6rem;
    margin-bottom: .6rem;
    flex-wrap: wrap;
}
.tb-result-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--tb-text);
    margin: 0;
}

/* === History rows ====================================================== */
.tb-history-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius-xs);
    padding: .6rem 1rem;
    margin-bottom: .4rem;
    background: var(--tb-card-bg);
    transition: border-color 0.15s ease;
}
.tb-history-row:hover {
    border-color: var(--tb-primary-light);
}
.tb-history-row .meta {
    color: var(--tb-muted);
    font-size: .78rem;
}
.tb-history-row .id {
    font-weight: 600;
    font-size: .88rem;
    color: var(--tb-text);
}

/* === Download button group ============================================= */
.tb-downloads {
    display: flex;
    gap: .5rem;
    flex-wrap: wrap;
}

/* === Success banner ==================================================== */
.tb-success-bar {
    display: flex;
    align-items: center;
    gap: .6rem;
    background: var(--tb-success-bg);
    border: 1px solid rgba(16,185,129,.2);
    border-radius: var(--tb-radius-sm);
    padding: .7rem 1.1rem;
    margin-bottom: 1rem;
    color: #047857;
    font-weight: 600;
    font-size: .9rem;
}

/* === Error banner ====================================================== */
.tb-error-bar {
    display: flex;
    align-items: center;
    gap: .6rem;
    background: var(--tb-error-bg);
    border: 1px solid rgba(239,68,68,.15);
    border-radius: var(--tb-radius-sm);
    padding: .85rem 1.2rem;
    margin-bottom: 1rem;
}
.tb-error-bar .error-icon {
    font-size: 1.3rem;
    flex-shrink: 0;
}
.tb-error-bar .error-text {
    color: #991b1b;
    font-weight: 600;
    font-size: .9rem;
}
.tb-error-bar .error-hint {
    color: #b91c1c;
    font-size: .82rem;
    margin-top: .2rem;
}

/* === Footer ============================================================ */
.tb-footer {
    text-align: center;
    color: var(--tb-muted);
    font-size: .82rem;
    margin-top: 3.5rem;
    padding: 2rem 1.5rem 1.2rem;
    border-top: 1px solid var(--tb-border);
    background: linear-gradient(180deg, transparent 0%, var(--tb-bg-subtle) 100%);
}
.tb-footer a {
    color: var(--tb-primary);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.15s ease;
}
.tb-footer a:hover {
    color: var(--tb-primary-dark);
    text-decoration: underline;
}
.tb-footer-brand {
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--tb-border-light);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .5rem;
    font-size: .85rem;
    color: var(--tb-text-secondary);
}
.tb-footer-brand .author-name {
    font-weight: 700;
    color: var(--tb-text);
}
.tb-linkedin-btn {
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    background: #0A66C2;
    color: #fff !important;
    font-size: .75rem;
    font-weight: 600;
    padding: .3rem .7rem;
    border-radius: 999px;
    text-decoration: none !important;
    transition: all 0.2s ease;
    box-shadow: 0 1px 4px rgba(10,102,194,.25);
}
.tb-linkedin-btn:hover {
    background: #004182;
    box-shadow: 0 2px 8px rgba(10,102,194,.35);
    transform: translateY(-1px);
    color: #fff !important;
    text-decoration: none !important;
}
.tb-linkedin-btn svg {
    width: 14px;
    height: 14px;
    fill: #fff;
}

/* === Streamlit widget polish =========================================== */
button[kind="primary"] {
    background: linear-gradient(135deg, var(--tb-primary) 0%, #7c3aed 100%) !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(99,102,241,.25) !important;
    font-weight: 600 !important;
    letter-spacing: .01em;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(99,102,241,.35) !important;
    transform: translateY(-1px);
}
.stTextInput input {
    border-radius: var(--tb-radius-sm) !important;
    border: 1.5px solid var(--tb-border) !important;
    padding: .6rem .9rem !important;
    font-size: .92rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput input:focus {
    border-color: var(--tb-primary) !important;
    box-shadow: 0 0 0 3px var(--tb-primary-soft) !important;
}
.stTextArea textarea {
    border-radius: var(--tb-radius-sm) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: .25rem;
    background: var(--tb-bg-subtle);
    border-radius: var(--tb-radius-sm);
    padding: .25rem;
    border: 1px solid var(--tb-border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--tb-radius-xs);
    font-weight: 600;
    font-size: .85rem;
    padding: .5rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: var(--tb-card-bg) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
}
.stDownloadButton button {
    border-radius: var(--tb-radius-xs) !important;
    font-weight: 600 !important;
    font-size: .82rem !important;
}

/* === Sidebar section headings ========================================== */
.sidebar-section {
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--tb-muted);
    margin: 1.2rem 0 .5rem 0;
}

/* === Input area styling ================================================ */
.tb-input-area {
    background: var(--tb-card-bg);
    border: 1px solid var(--tb-border);
    border-radius: var(--tb-radius);
    padding: 1.5rem 1.8rem;
    box-shadow: var(--tb-card-shadow);
    margin-bottom: 1.5rem;
}
</style>
"""


def inject_css() -> None:
    """Inject TranscriptBuddy's global CSS. Safe to call once per rerun."""
    st.markdown(_CSS, unsafe_allow_html=True)
