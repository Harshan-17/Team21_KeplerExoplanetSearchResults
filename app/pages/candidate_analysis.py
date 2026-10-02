"""Selected-object analysis page."""

from datetime import timedelta

import pandas as pd
import streamlit as st

from app.data import load_raw_data
from src.ml import MODEL_NAMES, predict_selected
from src.screening import get_screening_result
from src.transit import TransitResult, calculate_next_transit


_MISSING = "Not available"


def _value(row: pd.Series, column: str, digits: int = 2, unit: str = "") -> str:
    """Format a measured value without replacing missing data with an estimate."""

    value = row.get(column)
    if pd.isna(value):
        return _MISSING
    return f"{float(value):,.{digits}f}{unit}"


def _official_names(raw_data: pd.DataFrame) -> pd.Series:
    """Return names that were present in the source catalog before cleaning."""

    names = raw_data.set_index("rowid")["kepler_name"].astype("string")
    return names.where(names.str.strip().ne(""))


def _object_label(row: pd.Series) -> str:
    """Create a readable picker label from repository identifiers."""

    koi = str(row.get("kepoi_name", _MISSING))
    kepid = row.get("kepid")
    kepid_label = _MISSING if pd.isna(kepid) else str(int(kepid))
    official = row.get("official_name")
    official_label = "" if pd.isna(official) or not str(official).strip() else f" · {official}"
    return f"{koi} · Kepler ID {kepid_label}{official_label}"


def _human_readable_summary(row: pd.Series) -> str:
    """Describe only values recorded on the selected catalog row."""

    disposition = str(row.get("koi_disposition", _MISSING)).lower()
    radius = _value(row, "koi_prad", 2, " Earth radii")
    period = _value(row, "koi_period", 3, " days")
    star_temperature = _value(row, "koi_steff", 0, " K")
    transit_depth = _value(row, "koi_depth", 1, " ppm")
    return (
        f"The catalog labels this observation {disposition}. "
        f"It records a planet radius of {radius} and an orbital period of {period}. "
        f"The host-star temperature is {star_temperature}, and the recorded transit depth is {transit_depth}."
    )


def _countdown_parts(remaining: timedelta) -> tuple[int, int, int, int]:
    total_seconds = max(0, int(remaining.total_seconds()))
    days, remainder = divmod(total_seconds, 86_400)
    hours, remainder = divmod(remainder, 3_600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds


def _render_transit_result(result: TransitResult) -> None:
    """Render the countdown or the factual unavailable state."""

    if not result.valid or result.remaining_time is None or result.next_expected_transit_utc is None:
        st.info("Next transit timing unavailable for this object.")
        st.caption("Calculated from the catalog transit epoch and orbital period.")
        st.caption("This is a mathematical timing estimate, not an ML prediction.")
        return

    days, hours, minutes, seconds = _countdown_parts(result.remaining_time)
    next_date = result.next_expected_transit_utc.strftime("%d %b %Y, %H:%M:%S UTC")
    st.markdown(
        f"""
        <div class="next-transit-panel" role="status" aria-live="polite">
            <div class="next-transit-label">NEXT TRANSIT</div>
            <div class="next-transit-countdown">{days:02d} : {hours:02d} : {minutes:02d} : {seconds:02d}</div>
            <div class="next-transit-units"><span>DAYS</span><span>HOURS</span><span>MINUTES</span><span>SECONDS</span></div>
            <div class="next-transit-date">Expected: {next_date}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Calculated from the catalog transit epoch and orbital period.")
    st.caption("This is a mathematical timing estimate, not an ML prediction.")


def _render_live_transit(epoch_bkjd, orbital_period_days) -> None:
    result = calculate_next_transit(epoch_bkjd, orbital_period_days)
    _render_transit_result(result)


if hasattr(st, "fragment"):
    _render_live_transit = st.fragment(run_every="1s")(_render_live_transit)


def _render_model_prediction(row: pd.Series) -> None:
    """Show the existing binary screening models for the selected row."""

    st.subheader("Model prediction")
    st.caption("The existing project models screen for CONFIRMED or FALSE POSITIVE.")

    catalog_label = row.get("koi_disposition", _MISSING)
    if pd.isna(catalog_label):
        catalog_label = _MISSING
    st.metric("Catalog label", str(catalog_label))

    model_columns = st.columns(2)
    for column, model_name in zip(model_columns, MODEL_NAMES):
        with column:
            prediction = predict_selected(row, model_name)
            st.markdown(f"**{prediction.model_name}**")
            if not prediction.available or prediction.predicted_class is None:
                st.info("Model prediction unavailable for this object.")
                continue

            st.metric("Predicted class", prediction.predicted_class)
            probability_columns = st.columns(len(prediction.probabilities))
            for probability_column, (label, probability) in zip(
                probability_columns, prediction.probabilities.items()
            ):
                probability_column.metric(label.title(), f"{probability:.1%}")
            if prediction.source:
                st.caption(prediction.source)

    st.caption("The model estimates the class from patterns learned from the prepared Kepler dataset.")
    st.caption("These are model screening results, not scientific validation.")
    st.caption(
        "The notebook did not train CANDIDATE as a third model class; it remains the catalog label."
    )


def _render_screening(row: pd.Series) -> None:
    """Show the saved candidate-screening score and indicators."""

    st.subheader("Screening")
    result = get_screening_result(row)
    if not result.available:
        st.info("No saved screening result is available for this object.")
        st.caption("Screening priority is for further review and is not scientific confirmation.")
        return

    summary_columns = st.columns(3)
    summary_columns[0].metric(
        "Screening score",
        "Not available" if result.score is None else f"{result.score:.1%}",
    )
    summary_columns[1].metric("Priority", result.priority or "Not available")
    summary_columns[2].metric(
        "Outlier flag",
        "Flagged" if result.outlier_flag else "No flagged outliers",
    )

    flagged_features = ", ".join(result.flagged_features) if result.flagged_features else "None recorded"
    st.caption(f"Feature indicators: {flagged_features}.")
    st.caption("The score is the saved Random Forest confirmed-probability output from the project screening artifact.")
    st.caption("Screening priority is for further review and is not scientific confirmation.")


def render(data, source_label: str) -> None:
    """Render a beginner-friendly profile for one Kepler object."""

    raw_data = load_raw_data()
    objects = data.copy()
    objects["official_name"] = objects["rowid"].map(_official_names(raw_data))

    st.title("Candidate analysis")
    st.caption("Choose one Kepler object to read the values recorded for that observation.")

    query = st.text_input(
        "Find an object",
        placeholder="Try a KOI identifier, Kepler ID, or official name",
    ).strip().lower()

    if query:
        search_fields = objects[["kepoi_name", "kepid", "official_name"]].astype("string").fillna("")
        matches = search_fields.apply(lambda column: column.str.lower().str.contains(query, regex=False)).any(axis=1)
        objects = objects.loc[matches]

    if objects.empty:
        st.warning("No matching object was found. Try a KOI identifier or Kepler ID.")
        return

    objects = objects.sort_values("kepoi_name", na_position="last")
    selected_index = st.selectbox(
        "Select one object",
        options=objects.index.tolist(),
        format_func=lambda index: _object_label(objects.loc[index]),
    )
    row = objects.loc[selected_index]

    st.caption(_human_readable_summary(row))

    st.markdown(
        """
        <style>
        .next-transit-panel {
            background: #241517;
            border: 1px solid #d95757;
            border-radius: 12px;
            margin: 1.25rem 0 0.75rem;
            padding: 1.25rem 1.5rem 1.35rem;
            text-align: center;
        }
        .next-transit-label {
            color: #f06a64;
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
        }
        .next-transit-countdown {
            animation: next-transit-pulse 2.4s ease-in-out infinite;
            color: #ff8179;
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: clamp(1.8rem, 4vw, 3rem);
            font-weight: 700;
            letter-spacing: 0.08em;
            margin: 0.7rem 0 0.35rem;
        }
        .next-transit-units {
            color: #d98b87;
            display: grid;
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: 0.62rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            letter-spacing: 0.1em;
        }
        .next-transit-date {
            color: #f1d4d2;
            font-size: 0.9rem;
            margin-top: 1rem;
        }
        @keyframes next-transit-pulse {
            0%, 100% { opacity: 0.86; }
            50% { opacity: 1; }
        }
        @media (prefers-reduced-motion: reduce) {
            .next-transit-countdown { animation: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    _render_live_transit(row.get("koi_time0bk"), row.get("koi_period"))
    _render_model_prediction(row)
    _render_screening(row)

    st.subheader("Identification")
    identification = st.columns(3)
    identification[0].metric("KOI identifier", str(row.get("kepoi_name", _MISSING)))
    identification[1].metric("Kepler ID", _value(row, "kepid", 0))
    identification[2].metric(
        "Official name",
        _MISSING if pd.isna(row.get("official_name")) else str(row.get("official_name")),
    )

    st.subheader("Planet")
    planet = st.columns(4)
    planet[0].metric("Planetary radius", _value(row, "koi_prad", 2, " R⊕"))
    planet[1].metric("Orbital period", _value(row, "koi_period", 3, " days"))
    planet[2].metric("Equilibrium temperature", _value(row, "koi_teq", 0, " K"))
    planet[3].metric("Insolation flux", _value(row, "koi_insol", 2, " Earth flux"))

    st.subheader("Host star")
    host = st.columns(4)
    host[0].metric("Effective temperature", _value(row, "koi_steff", 0, " K"))
    host[1].metric("Stellar radius", _value(row, "koi_srad", 2, " R☉"))
    host[2].metric("Surface gravity", _value(row, "koi_slogg", 2))
    host[3].metric("Kepler magnitude", _value(row, "koi_kepmag", 2))

    st.subheader("Transit")
    transit = st.columns(4)
    transit[0].metric("Transit depth", _value(row, "koi_depth", 1, " ppm"))
    transit[1].metric("Transit duration", _value(row, "koi_duration", 2))
    transit[2].metric("Signal-to-noise ratio", _value(row, "koi_model_snr", 1))
    transit[3].metric("Transit epoch", _value(row, "koi_time0bk", 5))

    st.caption(f"Source: `{source_label}`")
