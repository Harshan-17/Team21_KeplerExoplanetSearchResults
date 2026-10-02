"""Overview page for the cleaned Kepler catalog."""

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURES = {
    "classification": PROJECT_ROOT / "results" / "figures" / "01_classification_distribution.png",
    "radius": PROJECT_ROOT / "results" / "figures" / "02_radius_by_classification.png",
    "period": PROJECT_ROOT / "results" / "figures" / "03_period_by_classification.png",
}


def render(data: pd.DataFrame, source_label: str) -> None:
    """Render the concise data-derived introduction to the platform."""

    counts = data["exoplanet_archive_disposition"].value_counts()

    st.title("Kepler Exoplanet Analysis Platform")
    st.write(
        "Search the Kepler catalog, understand its measurements, compare existing classifications, "
        "review screening results, and estimate the next catalog transit."
    )
    st.caption("SEARCH  →  UNDERSTAND  →  CLASSIFY  →  SCREEN  →  CHECK TRANSIT")

    metrics = st.columns(4)
    metrics[0].metric("Total objects", f"{len(data):,}")
    metrics[1].metric("Confirmed", f"{int(counts.get('CONFIRMED', 0)):,}")
    metrics[2].metric("Candidate", f"{int(counts.get('CANDIDATE', 0)):,}")
    metrics[3].metric("False positive", f"{int(counts.get('FALSE POSITIVE', 0)):,}")

    st.subheader("A quick view of the catalog")
    left, right = st.columns(2)
    with left:
        if FIGURES["classification"].exists():
            st.image(str(FIGURES["classification"]), use_container_width=True)
            st.caption("Classification distribution shows how the cleaned catalog is divided.")
        if FIGURES["radius"].exists():
            st.image(str(FIGURES["radius"]), use_container_width=True)
            st.caption("Planetary radius by class helps compare the recorded object groups.")
    with right:
        if FIGURES["period"].exists():
            st.image(str(FIGURES["period"]), use_container_width=True)
            st.caption("Orbital period by class shows the distribution of recorded periods.")

    st.caption(f"Source: `{source_label}`")
