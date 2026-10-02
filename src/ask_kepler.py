"""Small, deterministic natural-language queries over the Kepler catalog."""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

from src.transit import calculate_next_transit


SUPPORTED_MESSAGE = (
    "I can currently help you search Kepler objects, view candidate details, "
    "check transit information, view ML results, and check screening."
)


@dataclass
class AskResponse:
    text: str
    results: pd.DataFrame | None = None


def _number(pattern: str, question: str) -> float | None:
    match = re.search(pattern, question.lower())
    return float(match.group(1)) if match else None


def _result_table(data: pd.DataFrame) -> pd.DataFrame:
    columns = {
        "koi_identifier": "KOI identifier",
        "kepler_id": "Kepler ID",
        "official_name": "Official name",
        "exoplanet_archive_disposition": "Classification",
        "planetary_radius_earth_radii": "Radius (Earth radii)",
        "orbital_period_days": "Orbital period (days)",
        "transit_signal_to_noise_ratio": "Signal-to-noise ratio",
    }
    available = [column for column in columns if column in data.columns]
    return data[available].rename(columns=columns).head(100)


def _selected_summary(row: pd.Series | None) -> AskResponse:
    if row is None:
        return AskResponse("Select a Kepler object above so I can describe it.")
    name = row.get("official_name") or row.get("koi_identifier") or row.get("kepler_id")
    return AskResponse(
        f"{name} is recorded as {row.get('exoplanet_archive_disposition', 'unclassified')}. "
        f"Its planetary radius is {row.get('planetary_radius_earth_radii')} Earth radii, "
        f"its orbital period is {row.get('orbital_period_days')} days, and its transit signal-to-noise ratio is {row.get('transit_signal_to_noise_ratio')}. "
        "These are catalog measurements, not a scientific confirmation."
    )


def _transit_answer(row: pd.Series | None) -> AskResponse:
    if row is None:
        return AskResponse("Select a Kepler object above so I can calculate its next transit.")
    result = calculate_next_transit(row.get("transit_epoch_bkjd"), row.get("orbital_period_days"))
    if not result.validity:
        return AskResponse("Next transit timing unavailable for this object.")
    return AskResponse(
        f"The next expected transit is {result.next_expected_transit.strftime('%Y-%m-%d %H:%M:%S UTC')}. "
        "Calculated from the catalog transit epoch and orbital period. "
        "This is a mathematical timing estimate, not an ML prediction."
    )


def answer_question(
    question: str,
    data: pd.DataFrame,
    selected_row: pd.Series | None = None,
    prediction: dict | None = None,
    screening_row: pd.Series | None = None,
) -> AskResponse:
    """Answer the supported question patterns using real project values."""

    normalized = question.strip().lower()
    if not normalized:
        return AskResponse("Ask me a question about the catalog or selected object.")

    radius = _number(r"radius\s+(?:below|under|less than)\s+([0-9]*\.?[0-9]+)", normalized)
    if radius is not None:
        matches = data.loc[data["planetary_radius_earth_radii"] < radius]
        return AskResponse(
            f"I found {len(matches):,} objects with radius below {radius:g} Earth radii.",
            _result_table(matches),
        )

    period = _number(r"(?:orbital\s+)?period\s+(?:above|over|greater than)\s+([0-9]*\.?[0-9]+)", normalized)
    if period is not None:
        matches = data.loc[data["orbital_period_days"] > period]
        return AskResponse(
            f"I found {len(matches):,} objects with orbital period above {period:g} days.",
            _result_table(matches),
        )

    if "high signal" in normalized or "high signal-to-noise" in normalized:
        threshold = data["transit_signal_to_noise_ratio"].quantile(0.75)
        matches = data.loc[data["transit_signal_to_noise_ratio"] >= threshold]
        return AskResponse(
            f"I treated high signal-to-noise as the top 25% of this catalog, at or above {threshold:.2f}. "
            f"That returns {len(matches):,} objects.",
            _result_table(matches),
        )

    for label in ("CONFIRMED", "CANDIDATE", "FALSE POSITIVE"):
        if label.lower() in normalized and ("object" in normalized or "show" in normalized):
            matches = data.loc[data["exoplanet_archive_disposition"] == label]
            return AskResponse(
                f"I found {len(matches):,} {label.lower()} objects in the catalog.",
                _result_table(matches),
            )

    if "next transit" in normalized or "when is the transit" in normalized:
        return _transit_answer(selected_row)
    if "screening" in normalized or "priority" in normalized:
        if screening_row is None:
            return AskResponse("No saved screening result is available for this object.")
        score = screening_row.get("screening_priority_score")
        return AskResponse(
            f"The saved screening priority score is {float(score):.2f}. "
            "Screening priority is for further review and is not scientific confirmation."
        )
    if "probabilit" in normalized or "model predict" in normalized or "prediction" in normalized:
        if prediction is None:
            return AskResponse("A model prediction is unavailable for this object because required values are missing.")
        rf = prediction["random_forest_class"]
        probabilities = ", ".join(
            f"{label}: {float(value):.1%}"
            for label, value in prediction["random_forest_probabilities"].items()
        )
        return AskResponse(
            f"The Random Forest model estimates {rf}. Probabilities: {probabilities}. "
            "The model estimates the class from patterns learned from the prepared Kepler dataset. "
            "This is not scientific validation."
        )
    if "orbital period" in normalized or normalized == "what is the period":
        if selected_row is None:
            return AskResponse("Select a Kepler object above so I can read its orbital period.")
        return AskResponse(f"The catalog orbital period is {selected_row.get('orbital_period_days')} days.")
    if "transit depth" in normalized:
        if selected_row is None:
            return AskResponse("Select a Kepler object above so I can read its transit depth.")
        return AskResponse(f"The catalog transit depth is {selected_row.get('transit_depth_ppm')} ppm.")
    if "star temperature" in normalized or "stellar temperature" in normalized:
        if selected_row is None:
            return AskResponse("Select a Kepler object above so I can read its star temperature.")
        return AskResponse(f"The host star effective temperature is {selected_row.get('stellar_effective_temperature_k')} K.")
    if "tell me about" in normalized or "about this candidate" in normalized:
        return _selected_summary(selected_row)

    return AskResponse(SUPPORTED_MESSAGE)
