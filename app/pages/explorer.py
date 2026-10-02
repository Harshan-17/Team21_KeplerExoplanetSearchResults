"""Catalog explorer page shell."""


def render(data, source_label: str) -> None:
    """Render the explorer placeholder."""

    import streamlit as st

    st.title("Explore catalog")
    st.caption("Search and filters will be connected to the existing catalog fields here.")
    st.info("Detailed catalog exploration is not implemented in this shell step.")
