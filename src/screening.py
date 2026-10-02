"""Access to the project's saved candidate-screening results."""

from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd

from src.ml import load_saved_ml_results


OUTLIER_LABELS = {
    "koi_period_outlier": "Orbital period",
    "koi_duration_outlier": "Transit duration",
    "koi_depth_outlier": "Transit depth",
    "koi_prad_outlier": "Planetary radius",
    "koi_teq_outlier": "Equilibrium temperature",
    "koi_insol_outlier": "Insolation flux",
    "koi_model_snr_outlier": "Signal-to-noise ratio",
    "koi_steff_outlier": "Stellar temperature",
    "koi_slogg_outlier": "Stellar surface gravity",
    "koi_srad_outlier": "Stellar radius",
    "koi_kepmag_outlier": "Kepler magnitude",
}


@dataclass(frozen=True)
class ScreeningResult:
    """Saved screening information for one catalog object."""

    available: bool
    score: float | None
    priority: str | None
    outlier_flag: bool | None
    flagged_features: tuple[str, ...]


def _rowid(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _flagged(value) -> bool:
    try:
        return int(float(value)) == 1
    except (TypeError, ValueError):
        return False


def get_screening_result(row: pd.Series) -> ScreeningResult:
    """Return the saved candidate-screening row for a selected object."""

    selected_rowid = _rowid(row.get("rowid"))
    if selected_rowid is None:
        return ScreeningResult(False, None, None, None, ())

    artifact = load_saved_ml_results().candidate_predictions
    matches = artifact[artifact["rowid"] == selected_rowid]
    if matches.empty:
        return ScreeningResult(False, None, None, None, ())

    screening_row = matches.iloc[0]
    score = screening_row.get("predicted_confirmed_probability")
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = None
    if score is not None and not math.isfinite(score):
        score = None

    outlier_features = tuple(
        label
        for column, label in OUTLIER_LABELS.items()
        if column in screening_row and _flagged(screening_row[column])
    )
    return ScreeningResult(
        available=True,
        score=score,
        priority=str(screening_row.get("priority")),
        outlier_flag=_flagged(screening_row.get("outlier_flag")),
        flagged_features=outlier_features,
    )
