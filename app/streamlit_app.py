"""Application shell and navigation for the Kepler project."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.data import data_source_label, load_data
from app.pages import ask_kepler, candidate_analysis, explorer, ml_screening, overview, visualizations


st.set_page_config(
    page_title="EXOINSIGHT | Kepler catalog",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #0b0d10;
        --surface: #15181d;
        --surface-strong: #1b1f25;
        --border: #30353d;
        --text: #f1f3f5;
        --muted: #a4acb6;
        --accent: #d95757;
    }

    .stApp { background: var(--bg); color: var(--text); }
    [data-testid="stSidebar"] {
        background: #101216;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stRadio label { color: var(--muted); }
    [data-testid="stSidebar"] .stRadio label:hover { color: var(--text); }
    [data-testid="stSidebar"] [aria-checked="true"] + div { color: var(--accent); }
    h1, h2, h3 { color: var(--text); letter-spacing: -0.02em; }
    p, li, label, .stCaption { color: var(--muted); }
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: var(--text); }
    .shell-brand {
        color: var(--text);
        font-family: ui-sans-serif, system-ui, sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }
    .shell-brand span { color: var(--accent); }
    .shell-note {
        color: var(--muted);
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 0.72rem;
        line-height: 1.5;
    }
    .shell-footer {
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 0.72rem;
        margin-top: 2rem;
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


DATA = load_data()
SOURCE_LABEL = data_source_label()


def render_sidebar() -> str:
    """Render the shell navigation and return the selected destination."""

    with st.sidebar:
        st.markdown('<div class="shell-brand">EXO<span>INSIGHT</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="shell-note">Kepler catalog explorer</div>', unsafe_allow_html=True)
        st.divider()
        page = st.radio(
            "Navigate",
            ["Overview", "Explore catalog", "Candidate analysis", "ASK KEPLER", "ML evidence", "Visualizations"],
            label_visibility="collapsed",
        )
        st.markdown("<div class='shell-footer'>Processed project catalog<br>Navigation shell</div>", unsafe_allow_html=True)
    return page


page = render_sidebar()

if page == "Overview":
    overview.render(DATA, SOURCE_LABEL)
elif page == "Explore catalog":
    explorer.render(DATA, SOURCE_LABEL)
elif page == "Candidate analysis":
    candidate_analysis.render(DATA, SOURCE_LABEL)
elif page == "ASK KEPLER":
    ask_kepler.render(DATA, SOURCE_LABEL)
elif page == "ML evidence":
    ml_screening.render(DATA, SOURCE_LABEL)
else:
    visualizations.render(DATA, SOURCE_LABEL)
