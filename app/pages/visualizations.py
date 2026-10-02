"""Readable views of the project's catalog analysis and saved ML outputs."""

import streamlit as st

from src.ml import load_saved_ml_results
from src.visualizations import (
    classification_box,
    classification_distribution,
    correlation_heatmap,
    feature_importance_chart,
    model_comparison_chart,
    relationship_scatter,
)


def render(data, source_label: str) -> None:
    """Render selected existing-analysis views in focused tabs."""

    st.title("Visualizations")
    st.caption("Descriptive views of the cleaned Kepler catalog and saved project results.")

    catalog_tab, transit_tab, star_tab, ml_tab = st.tabs(
        ["Catalog structure", "Transit relationships", "Host-star relationships", "ML evidence"]
    )

    with catalog_tab:
        st.subheader("Classification distribution")
        st.caption("Why: shows how the catalog is divided among confirmed objects, candidates, and false positives.")
        st.plotly_chart(classification_distribution(data), use_container_width=True, config={"displayModeBar": False})

        left, right = st.columns(2)
        with left:
            st.subheader("Planetary radius by classification")
            st.caption("Why: compares the spread of measured planet sizes across the catalog labels.")
            st.plotly_chart(
                classification_box(data, "koi_prad", "Planetary radius (Earth radii)"),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with right:
            st.subheader("Orbital period by classification")
            st.caption("Why: compares how orbital periods are distributed across the catalog labels.")
            st.plotly_chart(
                classification_box(data, "koi_period", "Orbital period (days)"),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with transit_tab:
        st.subheader("Planetary radius vs transit depth")
        st.caption("Why: shows how the measured transit signal relates to the estimated planet size.")
        st.plotly_chart(
            relationship_scatter(data, "koi_prad", "koi_depth", "Planetary radius (Earth radii)", "Transit depth (ppm)"),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        left, right = st.columns(2)
        with left:
            st.subheader("Orbital period vs temperature")
            st.caption("Why: helps inspect the relationship between orbit length and estimated equilibrium temperature.")
            st.plotly_chart(
                relationship_scatter(data, "koi_period", "koi_teq", "Orbital period (days)", "Equilibrium temperature (K)"),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with right:
            st.subheader("Orbital period vs transit duration")
            st.caption("Why: compares how long the transit lasts with the object's orbital period.")
            st.plotly_chart(
                relationship_scatter(data, "koi_period", "koi_duration", "Orbital period (days)", "Transit duration (hours)"),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with star_tab:
        st.subheader("Stellar temperature vs equilibrium temperature")
        st.caption("Why: places the estimated planet temperature alongside the temperature of its host star.")
        st.plotly_chart(
            relationship_scatter(data, "koi_steff", "koi_teq", "Stellar effective temperature (K)", "Equilibrium temperature (K)"),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.subheader("Correlation heatmap")
        st.caption("Why: summarizes linear relationships among selected measured catalog features; correlation is not causation.")
        st.plotly_chart(correlation_heatmap(data), use_container_width=True, config={"displayModeBar": False})

    with ml_tab:
        try:
            results = load_saved_ml_results()
        except (OSError, ValueError):
            st.warning("The saved project ML results could not be loaded.")
            return

        st.subheader("Random Forest feature importance")
        st.caption("Why: shows which prepared inputs contributed most to the saved Random Forest model's decisions.")
        st.plotly_chart(
            feature_importance_chart(results.feature_importance),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.subheader("Model comparison")
        st.caption("Why: compares the saved evaluation scores for the project's Logistic Regression and Random Forest models.")
        st.plotly_chart(
            model_comparison_chart(results.model_comparison),
            use_container_width=True,
            config={"displayModeBar": False},
        )
