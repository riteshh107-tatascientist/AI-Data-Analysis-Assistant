"""
utils.py
Custom CSS injection and reusable UI helper components.

Design concept: "Amber Terminal Ledger" — a phosphor-amber CRT-terminal aesthetic
crossed with a spreadsheet cell-grid, built specifically for a tabular-data product
(not a generic dark-glassmorphism template). See DESIGN_NOTES.md for the full
rationale.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --bg-base: #120f0c;
    --bg-panel: #1c1712;
    --bg-panel-hover: #241e17;
    --accent: #ffb000;
    --accent-dim: #8a6414;
    --accent-soft: rgba(255, 176, 0, 0.10);
    --ink: #ede6d6;
    --muted: #948a78;
    --grid-line: rgba(255, 176, 0, 0.07);
    --success: #8fbc6b;
    --warning: #e8871e;
    --danger: #d6584a;
    --mono: 'IBM Plex Mono', ui-monospace, monospace;
    --sans: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] { font-family: var(--sans); }

/* ---------- Base canvas: faint graph-paper grid over warm near-black ---------- */
.stApp {
    background-color: var(--bg-base);
    background-image:
        linear-gradient(var(--grid-line) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
    background-size: 34px 34px;
    color: var(--ink);
}

#MainMenu, footer { visibility: hidden; }

::selection { background: var(--accent); color: #120f0c; }

/* Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--accent-dim); border-radius: 2px; }

/* Visible keyboard focus (accessibility) */
a:focus-visible, button:focus-visible, [tabindex]:focus-visible {
    outline: 2px solid var(--accent) !important;
    outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
    * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}

/* ================= HERO ================= */
.hero-container { padding: 2.6rem 1rem 1.8rem 1rem; }
.hero-bootline {
    font-family: var(--mono);
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    opacity: 0;
    animation: hero-fade-in 0.5s ease forwards;
}
.hero-bootline::before { content: "▸ "; }
.hero-title {
    font-family: var(--mono);
    font-size: 2.6rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.01em;
    margin-bottom: 0.6rem;
    opacity: 0;
    animation: hero-fade-in 0.6s ease 0.15s forwards;
}
.hero-title .cursor {
    display: inline-block;
    width: 0.5em;
    background: var(--accent);
    margin-left: 0.15em;
    animation: blink 1.1s step-end infinite;
}
.hero-subtitle {
    font-family: var(--sans);
    font-size: 1.02rem;
    color: var(--muted);
    max-width: 620px;
    line-height: 1.6;
    opacity: 0;
    animation: hero-fade-in 0.6s ease 0.3s forwards;
}
@keyframes hero-fade-in {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes blink {
    0%, 45% { opacity: 1; }
    50%, 100% { opacity: 0; }
}

/* ================= CELL-REFERENCE FEATURE CARDS ================= */
.cell-card {
    background: var(--bg-panel);
    border: 1px solid rgba(255, 176, 0, 0.14);
    border-left: 2px solid var(--accent-dim);
    padding: 1.3rem 1.3rem 1.4rem 1.3rem;
    height: 100%;
    transition: border-color 0.15s ease, background 0.15s ease, transform 0.15s ease;
}
.cell-card:hover {
    border-color: var(--accent);
    border-left-color: var(--accent);
    background: var(--bg-panel-hover);
    transform: translateX(2px);
}
.cell-ref {
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--accent-dim);
    letter-spacing: 0.08em;
    display: block;
    margin-bottom: 0.5rem;
}
.cell-card h3 {
    font-family: var(--mono);
    font-size: 1rem;
    font-weight: 600;
    color: var(--ink);
    margin: 0 0 0.5rem 0;
}
.cell-card p {
    font-family: var(--sans);
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.55;
    margin: 0;
}

/* ================= PIPELINE STEPS ================= */
.pipeline-step { text-align: center; padding: 0.5rem; }
.pipeline-num {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--accent-dim);
    letter-spacing: 0.1em;
}
.pipeline-icon { font-size: 1.7rem; margin: 0.3rem 0; }
.pipeline-label {
    font-family: var(--mono);
    font-size: 0.82rem;
    color: var(--muted);
}

/* ================= FILE-FORMAT TAGS ================= */
.ext-tag {
    display: inline-block;
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--accent);
    background: var(--accent-soft);
    border: 1px solid var(--accent-dim);
    padding: 0.28rem 0.7rem;
    margin-right: 0.4rem;
}

/* ================= SECTION HEADERS ================= */
.section-header {
    font-family: var(--mono);
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink);
    border-bottom: 1px solid rgba(255, 176, 0, 0.18);
    padding-bottom: 0.5rem;
    margin: 1.6rem 0 1.1rem 0;
    letter-spacing: 0.01em;
}
.section-header::before { content: "// "; color: var(--accent-dim); }

/* ================= BADGE ================= */
.badge {
    display: inline-block;
    font-family: var(--mono);
    padding: 0.22rem 0.65rem;
    font-size: 0.74rem;
    font-weight: 500;
    background: var(--accent-soft);
    color: var(--accent);
    border: 1px solid var(--accent-dim);
}

/* ================= SIDEBAR: directory-list nav ================= */
[data-testid="stSidebar"] {
    background: #0d0b09;
    border-right: 1px solid rgba(255, 176, 0, 0.12);
}
[data-testid="stSidebar"] * { font-family: var(--mono) !important; }
[data-testid="stSidebar"] h2 {
    color: var(--ink);
    font-size: 1rem;
    letter-spacing: 0.02em;
}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
    color: var(--muted) !important;
}

/* Radio nav styled as a file directory list */
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 2px; }
[data-testid="stSidebar"] div[role="radiogroup"] label {
    border-left: 2px solid transparent;
    padding: 0.4rem 0.6rem !important;
    border-radius: 0 !important;
    transition: all 0.12s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: var(--accent-soft);
    border-left-color: var(--accent-dim);
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: var(--accent-soft);
    border-left-color: var(--accent);
}
[data-testid="stSidebar"] div[role="radiogroup"] p {
    font-size: 0.86rem !important;
    color: var(--ink) !important;
}

/* ================= BUTTONS ================= */
.stButton > button, .stDownloadButton > button {
    background: var(--accent);
    color: #120f0c;
    border: none;
    border-radius: 2px;
    font-family: var(--mono);
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.01em;
    padding: 0.5rem 1.1rem;
    transition: background 0.15s ease, transform 0.1s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #ffc233;
    color: #120f0c;
    transform: translateY(-1px);
}
.stButton > button:active, .stDownloadButton > button:active { transform: translateY(0); }

/* Secondary-feel buttons (outline) inside expanders/tabs keep same family but quieter via default kind param in future */

/* ================= INPUTS ================= */
[data-testid="stFileUploader"] section {
    background: var(--bg-panel);
    border: 1px dashed var(--accent-dim);
    border-radius: 2px;
}
[data-testid="stFileUploader"] section:hover { border-color: var(--accent); }

.stTextInput input, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
    background: var(--bg-panel) !important;
    border-color: rgba(255,176,0,0.2) !important;
    font-family: var(--mono) !important;
    color: var(--ink) !important;
}

/* ================= METRICS: ledger-style, right-aligned tabular figures ================= */
[data-testid="stMetric"] {
    background: var(--bg-panel);
    border: 1px solid rgba(255, 176, 0, 0.12);
    border-radius: 2px;
    padding: 0.85rem 1rem;
}
[data-testid="stMetricLabel"] {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
    font-variant-numeric: tabular-nums;
}

/* ================= TABS ================= */
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid rgba(255,176,0,0.15); }
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono);
    font-size: 0.85rem;
    color: var(--muted);
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ================= DATAFRAME / TABLE CONTAINER ================= */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 176, 0, 0.14);
    border-radius: 2px;
    overflow: hidden;
}

/* ================= EXPANDER ================= */
[data-testid="stExpander"] {
    background: var(--bg-panel);
    border: 1px solid rgba(255, 176, 0, 0.12);
    border-radius: 2px;
}

/* ================= ALERTS ================= */
[data-testid="stAlert"] { border-radius: 2px; font-family: var(--sans); }

/* ================= CHAT BUBBLES ================= */
.chat-user {
    background: var(--bg-panel);
    border: 1px solid rgba(255,176,0,0.15);
    border-left: 2px solid #6b7a99;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    color: var(--ink);
    font-size: 0.92rem;
}
.chat-ai {
    background: var(--bg-panel);
    border: 1px solid rgba(255,176,0,0.15);
    border-left: 2px solid var(--accent);
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    color: var(--ink);
    font-size: 0.92rem;
}
.chat-user b, .chat-ai b { font-family: var(--mono); font-size: 0.78rem; color: var(--muted); }

/* ================= FOOTER ================= */
.app-footer {
    text-align: left;
    color: var(--muted);
    font-family: var(--mono);
    font-size: 0.74rem;
    border-top: 1px solid rgba(255,176,0,0.12);
    padding: 1.2rem 0 0.5rem 0;
    margin-top: 2rem;
}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def hero_section():
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-bootline">SYSTEM :: AI_DATA_ANALYST — SESSION READY</div>
            <div class="hero-title">AI Data Analyst Pro<span class="cursor">&nbsp;</span></div>
            <div class="hero-subtitle">
                Upload your data. Get instant insights, visualizations, predictions,
                and AI-powered reports — no coding required.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(ref: str, icon: str, title: str, description: str) -> str:
    """ref: a spreadsheet-style cell reference, e.g. 'A1' — ties structure to the data-grid subject."""
    return f"""
    <div class="cell-card">
        <span class="cell-ref">[{ref}]</span>
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """


def pipeline_step(num: str, icon: str, label: str) -> str:
    return f"""
    <div class="pipeline-step">
        <div class="pipeline-num">STEP {num}</div>
        <div class="pipeline-icon">{icon}</div>
        <div class="pipeline-label">{label}</div>
    </div>
    """


def section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def badge(text: str) -> str:
    return f'<span class="badge">{text}</span>'


def ext_tag(text: str) -> str:
    return f'<span class="ext-tag">.{text}</span>'


def app_footer():
    st.markdown(
        """
        <div class="app-footer">
            AI_DATA_ANALYST_PRO :: BUILD 2026.07 — session data is processed in-memory
            and is never stored permanently.
        </div>
        """,
        unsafe_allow_html=True,
    )
