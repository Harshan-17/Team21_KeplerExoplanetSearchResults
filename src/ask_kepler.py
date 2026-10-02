"""Small, deterministic natural-language interface for the Kepler catalog."""

from __future__ import annotations

from dataclasses import dataclass
import re

import pandas as pd

from src.ml import MODEL_NAMES, predict_selected
from src.screening import get_screening_result
from src.transit import calculate_next_transit


SUPPORTED_MESSAGE = (
    "I can currently help you search Kepler objects, view candidate details, "
    "check transit information, view ML results, and check screening."
)
_MISSING = "Not available"


@dataclass(frozen=True)
class AskResponse:
    """Text and optional real catalog rows returned by one user query."""

    text: str
    results: pd.DataFrame | None = None


DISPLAY_COLUMNS = {
    "kepoi_name": "KOI",
    "kepid": "Kepler ID",
    "kepler_name": "Official name",
    "koi_disposition": "Catalog class",
    "koi_prad": "Planetary radius (Earth radii)",
    "koi_period": "Orbital period (days)",
    "koi_model_snr": "Signal-to-noise ratio",
    "koi_depth": "Transit depth (ppm)",
}


def _value(row: pd.Series, column: str, digits: int = 2, unit: str = "") -> str:
    value = row.get(column)
    if pd.isna(value):
        return _MISSING
    return f"{float(value):,.{digits}f}{unit}"


def _object_label(row: pd.Series) -> str:
    koi = str(row.get("kepoi_name", _MISSING))
    kepid = row.get("kepid")
    if pd.isna(kepid):
        return koi
    return f"{koi} (Kepler ID {int(kepid)})"


def _result_frame(rows: pd.DataFrame) -> pd.DataFrame:
    """Return a compact table with human-readable labels and real values."""

    columns = [column for column in DISPLAY_COLUMNS if column in rows.columns]
    frame = rows.loc[:, columns].copy()
    frame = frame.rename(columns=DISPLAY_COLUMNS)
    if "Official name" in frame:
        frame["Official name"] = frame["Official name"].fillna("")
    return frame.reset_index(drop=True)


def _number_and_operator(query: str) -> tuple[str | None, float | None]:
    below = re.search(r"(?:below|under|less than|<)\s*(\d+(?:\.\d+)?)", query)
    if below:
        return "below", float(below.group(1))
    above = re.search(r"(?:above|over|greater than|more than|>)\s*(\d+(?:\.\d+)?)", query)
    if above:
        return "above", float(above.group(1))
    return None, None


def _dataset_search(query: str, data: pd.DataFrame) -> AskResponse | None:
    """Handle the deliberately small supported catalog-search vocabulary."""

    search_terms = ("show", "find", "list", "objects", "candidates", "confirmed", "false positive")
    has_search_intent = any(term in query for term in search_terms)
    mentions_radius = "radius" in query
    mentions_period = "period" in query
    mentions_snr = "signal-to-noise" in query or "signal to noise" in query or "snr" in query
    operator, threshold = _number_and_operator(query)

    if not has_search_intent and not (mentions_radius or mentions_period or mentions_snr):
        return None
    if mentions_snr and "high" in query and "koi_model_snr" in data:
        rows = data.loc[data["koi_disposition"].eq("CANDIDATE")].dropna(subset=["koi_model_snr"])
        rows = rows.sort_values("koi_model_snr", ascending=False)
        if rows.empty:
            return AskResponse("No candidate objects have a recorded signal-to-noise value.")
        shown = rows.head(25)
        return AskResponse(
            f"I found {len(rows):,} candidates with a recorded signal-to-noise value. "
            f"Showing the top {len(shown):,}, sorted by the catalog's recorded signal-to-noise ratio. "
            "The project does not define a separate high-SNR cutoff.",
            _result_frame(shown),
        )

    rows = data.copy()
    if "confirmed" in query and "false positive" not in query:
        rows = rows.loc[rows["koi_disposition"].eq("CONFIRMED")]
    elif "false positive" in query:
        rows = rows.loc[rows["koi_disposition"].eq("FALSE POSITIVE")]
    elif "candidate" in query:
        rows = rows.loc[rows["koi_disposition"].eq("CANDIDATE")]

    field = None
    label = None
    if mentions_radius:
        field, label = "koi_prad", "radius"
    elif mentions_period:
        field, label = "koi_period", "orbital period"

    descriptions = []
    if "confirmed" in query and "false positive" not in query:
        descriptions.append("confirmed objects")
    elif "false positive" in query:
        descriptions.append("false positive objects")
    elif "candidate" in query:
        descriptions.append("candidate objects")

    if field and operator and threshold is not None:
        rows = rows.dropna(subset=[field])
        if operator == "below":
            rows = rows.loc[rows[field] < threshold]
        else:
            rows = rows.loc[rows[field] > threshold]
        rows = rows.sort_values(field)
        descriptions.append(f"{label} {operator} {threshold:g}")
    elif "confirmed" in query or "candidate" in query or "false positive" in query:
        pass
    else:
        return None

    description = " matching ".join(descriptions) if len(descriptions) > 1 else descriptions[0]

    total = len(rows)
    shown = rows.head(100)
    if total == 0:
        return AskResponse("No catalog objects matched that request.")
    suffix = "" if total <= len(shown) else f" Showing the first {len(shown):,}."
    return AskResponse(
        f"Found {total:,} objects matching {description}.{suffix}",
        _result_frame(shown),
    )


def _selected_detail(query: str, row: pd.Series | None) -> AskResponse | None:
    if row is None:
        return AskResponse("Select a Kepler object above first so I can use its recorded values.")

    label = _object_label(row)
    if "tell me about" in query or "about this candidate" in query:
        disposition = str(row.get("koi_disposition", _MISSING)).lower()
        return AskResponse(
            f"{label} is labeled {disposition} in the catalog. "
            f"It has a recorded planetary radius of {_value(row, 'koi_prad', 2, ' Earth radii')}, "
            f"an orbital period of {_value(row, 'koi_period', 3, ' days')}, "
            f"a transit depth of {_value(row, 'koi_depth', 1, ' ppm')}, and "
            f"a host-star temperature of {_value(row, 'koi_steff', 0, ' K')}."
        )
    if "orbital period" in query or query in {"period", "what is the period"}:
        return AskResponse(f"The recorded orbital period for {label} is {_value(row, 'koi_period', 3, ' days')}.")
    if "transit depth" in query:
        return AskResponse(f"The recorded transit depth for {label} is {_value(row, 'koi_depth', 1, ' ppm')}.")
    if "star temperature" in query or "stellar temperature" in query or "host star" in query:
        return AskResponse(
            f"The recorded host-star effective temperature for {label} is "
            f"{_value(row, 'koi_steff', 0, ' K')}."
        )
    return None


def _transit_answer(row: pd.Series | None) -> AskResponse:
    if row is None:
        return AskResponse("Select a Kepler object above first so I can calculate its next transit.")
    result = calculate_next_transit(row.get("koi_time0bk"), row.get("koi_period"))
    if not result.valid or result.next_expected_transit_utc is None or result.remaining_time is None:
        return AskResponse("Next transit timing unavailable for this object.")
    total_seconds = max(0, int(result.remaining_time.total_seconds()))
    days, remainder = divmod(total_seconds, 86_400)
    hours, remainder = divmod(remainder, 3_600)
    minutes, seconds = divmod(remainder, 60)
    expected = result.next_expected_transit_utc.strftime("%d %b %Y, %H:%M:%S UTC")
    return AskResponse(
        f"The next expected transit for {_object_label(row)} is {expected}. "
        f"Time remaining at calculation: {days:02d} days, {hours:02d} hours, "
        f"{minutes:02d} minutes, {seconds:02d} seconds. "
        "Calculated from the catalog transit epoch and orbital period. "
        "This is a mathematical timing estimate, not an ML prediction."
    )


def _model_answer(row: pd.Series | None) -> AskResponse:
    if row is None:
        return AskResponse("Select a Kepler object above so I can use the existing model results.")
    parts = []
    for model_name in MODEL_NAMES:
        prediction = predict_selected(row, model_name)
        if not prediction.available or prediction.predicted_class is None:
            parts.append(f"{model_name}: prediction unavailable for this object.")
            continue
        probabilities = ", ".join(
            f"{label.title()} {probability:.1%}"
            for label, probability in prediction.probabilities.items()
        )
        parts.append(f"{model_name}: {prediction.predicted_class}; probabilities: {probabilities}.")
    return AskResponse(
        "The existing project models estimate the class from patterns learned from the prepared Kepler dataset. "
        + " ".join(parts)
        + " The existing notebook models output CONFIRMED or FALSE POSITIVE; CANDIDATE is the catalog label, not a third trained model class. "
        + "The model outputs are screening results, not scientific validation."
    )


def _screening_answer(row: pd.Series | None) -> AskResponse:
    if row is None:
        return AskResponse("Select a Kepler object above so I can use its saved screening result.")
    result = get_screening_result(row)
    if not result.available:
        return AskResponse("No saved screening result is available for this object.")
    score = _MISSING if result.score is None else f"{result.score:.1%}"
    flags = ", ".join(result.flagged_features) if result.flagged_features else "none recorded"
    return AskResponse(
        f"The saved screening score is {score}, with priority {result.priority or _MISSING}. "
        f"Outlier indicators: {flags}. Screening priority is for further review and is not scientific confirmation."
    )


def answer_query(query: str, data: pd.DataFrame, selected_row: pd.Series | None = None) -> AskResponse:
    """Answer one supported query using only catalog rows and project outputs."""

    normalized = re.sub(r"\s+", " ", str(query).strip().lower())
    if not normalized:
        return AskResponse("Ask me about a Kepler object, catalog filter, transit, model result, or screening priority.")

    if "next transit" in normalized or "show the next transit" in normalized:
        return _transit_answer(selected_row)
    if any(term in normalized for term in ("model predict", "model prediction", "probabilities", "what does the model")):
        return _model_answer(selected_row)
    if "screening" in normalized or "priority" in normalized:
        return _screening_answer(selected_row)

    search = _dataset_search(normalized, data)
    if search is not None:
        return search

    detail = _selected_detail(normalized, selected_row)
    if detail is not None:
        return detail

    return AskResponse(SUPPORTED_MESSAGE)
