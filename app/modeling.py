"""Cached orchestration around the project's existing ML functions."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

from src.ml import (
    evaluate_model,
    prepare_ml_data,
    train_logistic_regression,
    train_random_forest,
)


@st.cache_resource(show_spinner="Preparing the existing ML workflow...")
def get_model_bundle(data: pd.DataFrame) -> dict[str, Any]:
    """Fit the existing models once per dataframe and reuse them in the UI."""

    X, y = prepare_ml_data(data)
    if X.empty or y.nunique() < 2:
        raise ValueError("The prepared dataset does not contain enough classes for ML.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    logistic_model, scaler, logistic_predictions = train_logistic_regression(
        X_train, X_test, y_train, y_test
    )
    random_forest_model, rf_predictions = train_random_forest(
        X_train, X_test, y_train, y_test
    )

    logistic_metrics = evaluate_model(y_test, logistic_predictions)
    rf_metrics = evaluate_model(y_test, rf_predictions)
    metrics = pd.DataFrame(
        [logistic_metrics, rf_metrics],
        index=["Logistic Regression", "Random Forest"],
    )

    importance = pd.DataFrame(
        {
            "feature": X.columns,
            "importance": random_forest_model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    return {
        "features": list(X.columns),
        "logistic_model": logistic_model,
        "scaler": scaler,
        "random_forest_model": random_forest_model,
        "metrics": metrics,
        "feature_importance": importance,
    }


def predict_selected(row: pd.Series, bundle: dict[str, Any]) -> dict[str, Any] | None:
    """Return both existing model predictions for one selected catalog row."""

    features = bundle["features"]
    values = pd.DataFrame([{feature: row.get(feature) for feature in features}])
    values = values.apply(pd.to_numeric, errors="coerce")
    if values.isna().any(axis=None):
        return None

    logistic_input = bundle["scaler"].transform(values)
    logistic_model = bundle["logistic_model"]
    random_forest_model = bundle["random_forest_model"]

    return {
        "logistic_class": str(logistic_model.predict(logistic_input)[0]),
        "logistic_probabilities": dict(
            zip(logistic_model.classes_, logistic_model.predict_proba(logistic_input)[0])
        ),
        "random_forest_class": str(random_forest_model.predict(values)[0]),
        "random_forest_probabilities": dict(
            zip(random_forest_model.classes_, random_forest_model.predict_proba(values)[0])
        ),
    }


def get_screening_result(row: pd.Series, screening: pd.DataFrame) -> pd.Series | None:
    """Find the existing saved screening row for a selected object."""

    if screening.empty or "rowid" not in screening.columns:
        return None
    matches = screening.loc[screening["rowid"] == row.get("rowid")]
    if matches.empty:
        return None
    return matches.iloc[0]
