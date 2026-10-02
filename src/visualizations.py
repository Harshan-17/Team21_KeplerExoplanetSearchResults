"""Reusable charts built from the cleaned catalog and saved project outputs."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

STATUS_COLUMN = "koi_disposition"
STATUS_ORDER = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
STATUS_COLORS = {
    "CONFIRMED": "#d95757",
    "CANDIDATE": "#aab2bd",
    "FALSE POSITIVE": "#5f6670",
}
FEATURE_LABELS = {
    "koi_period": "Orbital period",
    "koi_duration": "Transit duration",
    "koi_prad": "Planetary radius",
    "koi_teq": "Equilibrium temperature",
    "koi_insol": "Insolation flux",
    "koi_model_snr": "Signal-to-noise ratio",
    "koi_steff": "Stellar temperature",
    "koi_slogg": "Stellar surface gravity",
    "koi_srad": "Stellar radius",
    "koi_kepmag": "Kepler magnitude",
}


def chart_theme(figure: go.Figure, height: int = 360) -> go.Figure:
    """Apply the app's restrained dark chart styling."""

    figure.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=12, r=12, t=48, b=12),
        legend_title_text="",
    )
    figure.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.10)")
    figure.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.10)")
    return figure


def _clean(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    available = [column for column in columns if column in data.columns]
    return data.loc[:, available].dropna().copy()


def classification_distribution(data: pd.DataFrame) -> go.Figure:
    counts = data[STATUS_COLUMN].value_counts().reindex(STATUS_ORDER, fill_value=0)
    frame = counts.rename_axis("Disposition").reset_index(name="Objects")
    figure = px.bar(
        frame,
        x="Disposition",
        y="Objects",
        color="Disposition",
        category_orders={"Disposition": STATUS_ORDER},
        color_discrete_map=STATUS_COLORS,
        labels={"Objects": "Catalog objects", "Disposition": ""},
        text_auto=True,
    )
    return chart_theme(figure, 320)


def classification_box(data: pd.DataFrame, column: str, label: str) -> go.Figure:
    frame = _clean(data, [STATUS_COLUMN, column])
    figure = px.box(
        frame,
        x=STATUS_COLUMN,
        y=column,
        color=STATUS_COLUMN,
        category_orders={STATUS_COLUMN: STATUS_ORDER},
        color_discrete_map=STATUS_COLORS,
        points=False,
        labels={STATUS_COLUMN: "", column: label},
    )
    return chart_theme(figure, 380)


def relationship_scatter(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    x_label: str,
    y_label: str,
) -> go.Figure:
    frame = _clean(data, [STATUS_COLUMN, x_column, y_column, "kepoi_name"])
    # The legacy project visualization uses the 99th percentile to keep dense
    # relationships readable without changing the underlying catalog.
    for column in [x_column, y_column]:
        upper = frame[column].quantile(0.99)
        frame = frame[frame[column] <= upper]
    figure = px.scatter(
        frame,
        x=x_column,
        y=y_column,
        color=STATUS_COLUMN,
        hover_name="kepoi_name" if "kepoi_name" in frame else None,
        color_discrete_map=STATUS_COLORS,
        labels={x_column: x_label, y_column: y_label, STATUS_COLUMN: ""},
        opacity=0.62,
    )
    figure.update_traces(marker=dict(size=6))
    figure = chart_theme(figure, 380)
    figure.add_annotation(
        text="Values above the 99th percentile are omitted for readability.",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.18,
        showarrow=False,
        font=dict(size=10, color="#aab2bd"),
    )
    return figure


def correlation_heatmap(data: pd.DataFrame) -> go.Figure:
    columns = [
        "koi_prad",
        "koi_period",
        "koi_depth",
        "koi_teq",
        "koi_insol",
        "koi_steff",
        "koi_srad",
        "koi_slogg",
        "koi_model_snr",
    ]
    frame = _clean(data, columns).rename(columns=FEATURE_LABELS | {"koi_depth": "Transit depth"})
    correlation = frame.corr(numeric_only=True)
    figure = px.imshow(
        correlation,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        color_continuous_scale=["#303640", "#aab2bd", "#d95757"],
        labels={"color": "Correlation"},
    )
    return chart_theme(figure, 560)


def feature_importance_chart(importance: pd.DataFrame) -> go.Figure:
    frame = importance.copy()
    frame["Feature"] = frame["Feature"].map(FEATURE_LABELS).fillna(frame["Feature"])
    frame = frame.sort_values("Importance", ascending=False).head(8)
    figure = px.bar(
        frame.sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        labels={"Importance": "Saved importance", "Feature": ""},
        color_discrete_sequence=["#d95757"],
    )
    return chart_theme(figure, 400)


def model_comparison_chart(model_metrics: pd.DataFrame) -> go.Figure:
    metrics = [column for column in ["Accuracy", "F1 Score", "ROC-AUC"] if column in model_metrics]
    frame = model_metrics.melt(
        id_vars="Model",
        value_vars=metrics,
        var_name="Metric",
        value_name="Score",
    )
    figure = px.bar(
        frame,
        x="Score",
        y="Metric",
        color="Model",
        barmode="group",
        orientation="h",
        range_x=[0, 1],
        labels={"Score": "Saved score", "Metric": ""},
        color_discrete_sequence=["#d95757", "#aab2bd"],
    )
    return chart_theme(figure, 340)
