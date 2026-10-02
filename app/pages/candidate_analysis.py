"""Detailed analysis of one selected Kepler object."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.data import load_screening_results
from app.modeling import get_model_bundle, get_screening_result, predict_selected
from src.transit import calculate_next_transit, format_countdown


def _value(value: object, digits: int = 3) -> str:
    if pd.isna(value):
        return "Not available"
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return str(value)


def _candidate_options(data: pd.DataFrame) -> list[str]:
    options = data["koi_identifier"].fillna(data["rowid"].astype(str)).astype(str).tolist()
    return sorted(options)


def _render_transit(row: pd.Series) -> None:
    result = calculate_next_transit(row.get("transit_epoch_bkjd"), row.get("orbital_period_days"))
    st.subheader("Next transit")
    if not result.validity:
        st.warning("Next transit timing unavailable for this object.")
        return

    st.markdown(
        f"<div class='transit-panel'><div class='transit-label'>NEXT TRANSIT</div>"
        f"<div class='transit-countdown'>{format_countdown(result.remaining)}</div>"
        f"<div class='transit-units'>DAYS&nbsp;&nbsp;&nbsp;&nbsp; HOURS&nbsp;&nbsp;&nbsp;&nbsp; MINUTES&nbsp;&nbsp;&nbsp;&nbsp; SECONDS</div>"
        f"<div class='transit-date'>Expected: {result.next_expected_transit.strftime('%Y-%m-%d %H:%M:%S UTC')}</div></div>",
        unsafe_allow_html=True,
    )
    st.caption("Calculated from the catalog transit epoch and orbital period.")
    st.caption("This is a mathematical timing estimate, not an ML prediction.")


def _render_model(row: pd.Series, data: pd.DataFrame) -> None:
    st.subheader("Model prediction")
    try:
        prediction = predict_selected(row, get_model_bundle(data))
    except Exception as exc:
        st.warning(f"Model output unavailable: {exc}")
        return
    if prediction is None:
        st.info("Model output is unavailable because this object has missing model features.")
        return

    st.write("The model estimates the class from patterns learned from the prepared Kepler dataset.")
    st.caption("These are dataset-based model outputs, not scientific validation.")
    columns = st.columns(2)
    columns[0].metric("Logistic Regression", prediction["logistic_class"])
    columns[1].metric("Random Forest", prediction["random_forest_class"])
    probability_table = pd.DataFrame(
        {
            "Class": list(prediction["random_forest_probabilities"]),
            "Random Forest probability": [
                f"{float(value):.1%}" for value in prediction["random_forest_probabilities"].values()
            ],
        }
    )
    st.dataframe(probability_table, hide_index=True, use_container_width=True)


def _render_screening(row: pd.Series) -> None:
    st.subheader("Screening")
    result = get_screening_result(row, load_screening_results())
    if result is None:
        st.info("No saved screening result is available for this object.")
        return

    score = result.get("screening_priority_score")
    st.metric("Screening score", _value(score, 2))
    st.write("The saved result is available for further review in the project screening table.")
    indicators = {
        "Not transit-like": result.get("flag_not_transit_like"),
        "Stellar eclipse": result.get("flag_stellar_eclipse"),
        "Centroid offset": result.get("flag_centroid_offset"),
        "Contamination match": result.get("flag_ephemeris_match_contamination"),
    }
    st.dataframe(
        pd.DataFrame({"Indicator": list(indicators), "Recorded value": list(indicators.values())}),
        hide_index=True,
        use_container_width=True,
    )
    st.caption("Screening priority is for further review and is not scientific confirmation.")


def render(data: pd.DataFrame, source_label: str) -> None:
    """Render the selected object's recorded values and derived views."""

    st.title("Candidate analysis")
    st.caption("Select one object to read its catalog measurements and existing project results.")
    selected_id = st.selectbox("Kepler object", _candidate_options(data))
    row = data.loc[data["koi_identifier"].astype(str) == selected_id].iloc[0]

    st.caption(f"Source: `{source_label}`")
    _render_transit(row)
    _render_model(row, data)
    _render_screening(row)

    st.subheader("Recorded details")
    identification = st.columns(3)
    identification[0].metric("KOI identifier", _value(row.get("koi_identifier"), 0))
    identification[1].metric("Kepler ID", _value(row.get("kepler_id"), 0))
    identification[2].metric("Official name", _value(row.get("official_name"), 0))

    st.markdown("**Planet**")
    planet = st.columns(4)
    planet[0].metric("Planetary radius", f"{_value(row.get('planetary_radius_earth_radii'))} Earth radii")
    planet[1].metric("Orbital period", f"{_value(row.get('orbital_period_days'))} days")
    planet[2].metric("Equilibrium temperature", f"{_value(row.get('equilibrium_temperature_k'), 1)} K")
    planet[3].metric("Insolation flux", _value(row.get("insolation_flux")))

    st.markdown("**Host star**")
    star = st.columns(4)
    star[0].metric("Effective temperature", f"{_value(row.get('stellar_effective_temperature_k'), 1)} K")
    star[1].metric("Stellar radius", f"{_value(row.get('stellar_radius_solar_radii'))} solar radii")
    star[2].metric("Surface gravity", _value(row.get("stellar_surface_gravity_log10")))
    star[3].metric("Kepler magnitude", _value(row.get("kepler_band_magnitude")))

    st.markdown("**Transit**")
    transit = st.columns(4)
    transit[0].metric("Transit depth", f"{_value(row.get('transit_depth_ppm'), 1)} ppm")
    transit[1].metric("Transit duration", f"{_value(row.get('transit_duration_hours'), 2)} hours")
    transit[2].metric("Signal-to-noise ratio", _value(row.get("transit_signal_to_noise_ratio")))
    transit[3].metric("Transit epoch", f"{_value(row.get('transit_epoch_bkjd'), 5)} BKJD")

    st.info(
        f"This row records {row.get('official_name') or row.get('koi_identifier')} as "
        f"{row.get('exoplanet_archive_disposition')}. The values above describe the catalog record and do not by themselves validate an exoplanet."
    )
