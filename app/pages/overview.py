"""Overview page for the Streamlit application."""

import pandas as pd
import plotly.express as px


STATUS_COLUMN = "koi_disposition"
STATUS_COLORS = {
    "CONFIRMED": "#d95757",
    "CANDIDATE": "#aab2bd",
    "FALSE POSITIVE": "#5f6670",
}


def _chart_theme(figure, height: int = 320):
    """Apply the shell's dark, low-decoration chart treatment."""

    figure.update_layout(
        template="plotly_dark",
        height=height,
        margin={"l": 8, "r": 8, "t": 20, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "system-ui, sans-serif", "color": "#a4acb6", "size": 11},
        legend={"bgcolor": "rgba(0,0,0,0)", "orientation": "h", "y": 1.12, "x": 0},
        hoverlabel={"bgcolor": "#1b1f25", "bordercolor": "#30353d", "font_color": "#f1f3f5"},
    )
    figure.update_xaxes(gridcolor="#30353d", zerolinecolor="#30353d", linecolor="#30353d")
    figure.update_yaxes(gridcolor="#30353d", zerolinecolor="#30353d", linecolor="#30353d")
    return figure


def _disposition_chart(data: pd.DataFrame):
    counts = (
        data[STATUS_COLUMN]
        .value_counts()
        .reindex(["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"], fill_value=0)
        .rename_axis("Disposition")
        .reset_index(name="Objects")
    )
    figure = px.bar(
        counts,
        x="Disposition",
        y="Objects",
        color="Disposition",
        color_discrete_map=STATUS_COLORS,
        labels={"Objects": "Objects"},
        text_auto=".2s",
    )
    figure.update_traces(marker_line_width=0, textposition="outside")
    return _chart_theme(figure, height=320)


def _planet_parameter_chart(data: pd.DataFrame):
    sample = data.dropna(subset=["koi_period", "koi_prad", STATUS_COLUMN]).copy()
    if not sample.empty:
        sample = sample[sample["koi_period"] <= sample["koi_period"].quantile(0.99)]
        sample = sample[sample["koi_prad"] <= sample["koi_prad"].quantile(0.99)]

    figure = px.scatter(
        sample,
        x="koi_period",
        y="koi_prad",
        color=STATUS_COLUMN,
        color_discrete_map=STATUS_COLORS,
        hover_name="kepoi_name",
        opacity=0.72,
        labels={
            "koi_period": "Orbital period, days",
            "koi_prad": "Planet radius, Earth radii",
            STATUS_COLUMN: "Disposition",
        },
    )
    return _chart_theme(figure, height=320)


def render(data, source_label: str) -> None:
    """Render the overview using values and charts from the cleaned catalog."""

    import streamlit as st

    st.markdown(
        """
        <style>
        .workflow {
            align-items: center;
            border-bottom: 1px solid #30353d;
            border-top: 1px solid #30353d;
            color: #a4acb6;
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin: 1.5rem 0 2rem;
            padding: 0.85rem 0;
        }
        .workflow span {
            color: #f1f3f5;
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
        }
        .workflow b { color: #d95757; font-weight: 500; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Explore the Kepler catalog")
    st.write(
        "Search observations, understand their measured properties, and compare the existing classification and screening results."
    )

    st.markdown(
        "<div class='workflow' aria-label='Application workflow'>"
        "<span>SEARCH</span><b>→</b><span>UNDERSTAND</span><b>→</b>"
        "<span>CLASSIFY</span><b>→</b><span>SCREEN</span><b>→</b><span>CHECK TRANSIT</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    counts = data[STATUS_COLUMN].value_counts()
    kpi_columns = st.columns(4)
    kpi_columns[0].metric("Total objects", f"{len(data):,}")
    kpi_columns[1].metric("Confirmed", f"{int(counts.get('CONFIRMED', 0)):,}")
    kpi_columns[2].metric("Candidates", f"{int(counts.get('CANDIDATE', 0)):,}")
    kpi_columns[3].metric("False positives", f"{int(counts.get('FALSE POSITIVE', 0)):,}")

    st.subheader("What is in the catalog?")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(_disposition_chart(data), use_container_width=True, config={"displayModeBar": False})
    with right:
        st.plotly_chart(_planet_parameter_chart(data), use_container_width=True, config={"displayModeBar": False})

    st.caption(f"Source: `{source_label}`")
