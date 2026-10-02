"""Existing ML metrics and saved screening results."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.modeling import get_model_bundle


FEATURE_LABELS = {
    "orbital_period_days": "Orbital period (days)",
    "impact_parameter": "Impact parameter",
    "transit_duration_hours": "Transit duration (hours)",
    "transit_depth_ppm": "Transit depth (ppm)",
    "planetary_radius_earth_radii": "Planetary radius (Earth radii)",
    "equilibrium_temperature_k": "Equilibrium temperature (K)",
    "insolation_flux": "Insolation flux",
    "transit_signal_to_noise_ratio": "Transit signal-to-noise ratio",
    "stellar_effective_temperature_k": "Stellar effective temperature (K)",
    "stellar_surface_gravity_log10": "Stellar surface gravity",
    "stellar_radius_solar_radii": "Stellar radius (solar radii)",
    "kepler_band_magnitude": "Kepler magnitude",
}


def _screening_table(screening: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "koi_identifier": "KOI identifier",
        "kepler_id": "Kepler ID",
        "exoplanet_archive_disposition": "Classification",
        "screening_priority_score": "Screening score",
        "probability_confirmed": "Confirmed probability",
        "probability_candidate": "Candidate probability",
        "probability_false_positive": "False-positive probability",
        "transit_signal_to_noise_ratio": "Signal-to-noise ratio",
        "planetary_radius_earth_radii": "Radius (Earth radii)",
        "orbital_period_days": "Orbital period (days)",
    }
    available = [column for column in columns if column in screening.columns]
    return screening[available].rename(columns=columns)


def render(data: pd.DataFrame, screening: pd.DataFrame, source_label: str) -> None:
    """Render the project's existing ML workflow and saved screening output."""

    st.title("ML & screening")
    st.caption("Existing project results, shown as evidence for review rather than scientific validation.")

    try:
        bundle = get_model_bundle(data)
    except Exception as exc:
        st.error(f"The existing ML workflow could not be loaded: {exc}")
        return

    st.subheader("Logistic Regression metrics")
    st.dataframe(
        bundle["metrics"].loc[["Logistic Regression"]].round(3),
        use_container_width=True,
    )

    st.subheader("Random Forest metrics")
    st.dataframe(
        bundle["metrics"].loc[["Random Forest"]].round(3),
        use_container_width=True,
    )

    st.subheader("Model comparison")
    st.caption("This compares the metrics calculated by the existing train/test workflow.")
    st.bar_chart(bundle["metrics"].round(3))

    st.subheader("Random Forest feature importance")
    st.caption("This shows which prepared input features the existing Random Forest used most in its fitted model.")
    importance = bundle["feature_importance"].copy().head(10).sort_values("importance")
    importance["feature"] = importance["feature"].map(FEATURE_LABELS).fillna(importance["feature"])
    st.bar_chart(importance.set_index("feature")["importance"], horizontal=True)

    st.subheader("Screening results")
    st.write("The saved screening table contains the project’s priority scores and indicators for further review.")
    if screening.empty:
        st.info("No saved screening results are available.")
    else:
        st.dataframe(_screening_table(screening), hide_index=True, use_container_width=True)
        st.caption("Screening priority is for further review and is not scientific confirmation.")

    st.caption(f"Source: `{source_label}`; model results use the existing implementation in `src/ml.py`.")
