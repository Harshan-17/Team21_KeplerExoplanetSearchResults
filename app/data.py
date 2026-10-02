"""Shared data access for the Streamlit application."""

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "processed" / "Data_cleaned.csv"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "cumulative.csv"


@st.cache_data(show_spinner="Loading the processed Kepler catalog...")
def load_data() -> pd.DataFrame:
    """Load the processed catalog once and reuse it across page navigation."""

    return pd.read_csv(DATA_PATH, low_memory=False)


@st.cache_data(show_spinner="Loading source identification fields...")
def load_raw_data() -> pd.DataFrame:
    """Load the source catalog for fields affected by cleaning imputation."""

    return pd.read_csv(RAW_DATA_PATH, low_memory=False)


def data_source_label() -> str:
    """Return the repository-relative source path for UI provenance text."""

    return str(DATA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/")
