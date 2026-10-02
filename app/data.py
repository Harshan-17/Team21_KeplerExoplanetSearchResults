"""Shared data access for the Streamlit application."""

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "processed" / "kepler_cleaned.csv"
SCREENING_PATH = PROJECT_ROOT / "results" / "tables" / "kepler_screening_results.csv"


@st.cache_data(show_spinner="Loading the cleaned Kepler catalog...")
def load_data() -> pd.DataFrame:
    """Load the repository's cleaned, normalized Kepler catalog."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Kepler dataset not found at: {DATA_PATH}")
    return pd.read_csv(DATA_PATH, low_memory=False)


@st.cache_data(show_spinner="Loading saved screening results...")
def load_screening_results() -> pd.DataFrame:
    """Load the existing top screening results produced by the project."""

    if not SCREENING_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(SCREENING_PATH, low_memory=False)


def data_source_label() -> str:
    """Return the repository-relative data path used by the application."""

    return str(DATA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/")
