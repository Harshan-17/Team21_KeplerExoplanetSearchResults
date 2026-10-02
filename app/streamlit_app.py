"""Streamlit entry point for the Kepler Exoplanet Analysis Platform."""

import streamlit as st

from app.data import data_source_label, load_data, load_screening_results
from app.pages import ask_kepler, candidate_analysis, explorer, ml_screening, overview, visualizations


st.set_page_config(
    page_title="Kepler Exoplanet Analysis Platform",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --space: #11161b;
        --surface: #1b2229;
        --surface-soft: #202930;
        --text: #edf1f4;
        --muted: #aeb8c0;
        --line: #354049;
        --red: #d95555;
    }
    .stApp { background: var(--space); color: var(--text); }
    [data-testid="stSidebar"] { background: #151b20; border-right: 1px solid var(--line); }
    [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); padding: 0.8rem; }
    [data-testid="stMetricValue"] { color: var(--text); }
    h1, h2, h3 { letter-spacing: -0.02em; }
    h1 { font-weight: 650; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
    .transit-panel {
        border: 1px solid var(--red);
        border-left: 5px solid var(--red);
        background: #241b1e;
        padding: 1.25rem 1.4rem;
        margin: 0.35rem 0 0.85rem;
    }
    .transit-label { color: #ff9b9b; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.16em; }
    .transit-countdown { color: #ff7373; font-size: clamp(2rem, 5vw, 4rem); font-weight: 700; letter-spacing: 0.08em; line-height: 1.1; }
    .transit-units { color: #e6b0b0; font-size: 0.72rem; letter-spacing: 0.09em; margin-top: 0.35rem; }
    .transit-date { color: var(--text); margin-top: 0.7rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    data = load_data()
    screening = load_screening_results()
    source_label = data_source_label()

    with st.sidebar:
        st.markdown("## Kepler")
        st.caption("Catalog search and analysis")
        page = st.radio(
            "Navigate",
            [
                "Overview",
                "Explore catalog",
                "Candidate analysis",
                "ASK KEPLER",
                "ML & screening",
                "Visualizations",
            ],
        )
        st.divider()
        st.caption("Uses the repository's cleaned catalog, existing analysis, and saved results.")

    if page == "Overview":
        overview.render(data, source_label)
    elif page == "Explore catalog":
        explorer.render(data, source_label)
    elif page == "Candidate analysis":
        candidate_analysis.render(data, source_label)
    elif page == "ASK KEPLER":
        ask_kepler.render(data, source_label)
    elif page == "ML & screening":
        ml_screening.render(data, screening, source_label)
    else:
        visualizations.render(data, source_label)


if __name__ == "__main__":
    main()
