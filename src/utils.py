"""
utils.py
Custom CSS injection and small reusable UI helper components.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* App background */
.stApp {
    background: radial-gradient(circle at 10% 0%, #0f2027 0%, #0a0e14 45%, #060809 100%);
    color: #e2e8f0;
}

/* Hide default streamlit chrome */
#MainMenu, footer {visibility: hidden;}

/* Hero section */
.hero-container {
    text-align: center;
    padding: 3rem 1rem 2rem 1rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #2dd4bf, #38bdf8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    animation: fadein 1.2s ease-in-out;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #94a3b8;
    max-width: 700px;
    margin: 0 auto 1.5rem auto;
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Glassmorphism cards */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 1.4rem 1.3rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}
.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(45, 212, 191, 0.15);
    border-color: rgba(45, 212, 191, 0.35);
}
.glass-card h3 {
    margin-top: 0;
    color: #2dd4bf;
    font-size: 1.05rem;
}
.glass-card p {
    color: #94a3b8;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* Metric-style badge */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    background: rgba(45, 212, 191, 0.12);
    color: #2dd4bf;
    border: 1px solid rgba(45, 212, 191, 0.3);
}

/* Section headers */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    border-left: 4px solid #2dd4bf;
    padding-left: 0.7rem;
    margin: 1.5rem 0 1rem 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #060809 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #14b8a6, #38bdf8);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    transition: opacity 0.2s ease;
}
.stButton > button:hover {
    opacity: 0.88;
    color: white;
}

/* Dataframe container */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Chat bubbles */
.chat-user {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px 14px 2px 14px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    color: #e2e8f0;
}
.chat-ai {
    background: rgba(45, 212, 191, 0.1);
    border: 1px solid rgba(45, 212, 191, 0.25);
    border-radius: 14px 14px 14px 2px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    color: #e2e8f0;
}

/* Footer */
.app-footer {
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    padding: 2rem 0 1rem 0;
}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def hero_section():
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">📊 AI Data Analyst Pro</div>
            <div class="hero-subtitle">
                Upload your data. Get instant insights, visualizations, predictions,
                and AI-powered reports — no coding required.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(icon: str, title: str, description: str) -> str:
    return f"""
    <div class="glass-card">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """


def section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def badge(text: str) -> str:
    return f'<span class="badge">{text}</span>'


def app_footer():
    st.markdown(
        """
        <div class="app-footer">
            Built with ❤️ using Streamlit • AI Data Analyst Pro © 2026 •
            Your data is processed in-session and never stored permanently.
        </div>
        """,
        unsafe_allow_html=True,
    )
