"""Search and filter the cleaned Kepler catalog."""

import pandas as pd
import streamlit as st


DISPLAY_COLUMNS = {
    "koi_identifier": "KOI identifier",
    "kepler_id": "Kepler ID",
    "official_name": "Official name",
    "exoplanet_archive_disposition": "Classification",
    "planetary_radius_earth_radii": "Radius (Earth radii)",
    "orbital_period_days": "Orbital period (days)",
    "transit_signal_to_noise_ratio": "Signal-to-noise ratio",
}


def _text_search(data: pd.DataFrame, query: str) -> pd.Series:
    fields = ["koi_identifier", "kepler_id", "official_name"]
    searchable = data[fields].fillna("").astype(str).agg(" ".join, axis=1)
    return searchable.str.contains(query, case=False, regex=False)


def render(data: pd.DataFrame, source_label: str) -> None:
    """Render the catalog search and filters."""

    st.title("Explore catalog")
    st.caption("Search by identification fields, then narrow the results with recorded measurements.")

    query = st.text_input(
        "Search by KOI identifier, Kepler ID, or official name",
        placeholder="For example: K00749 or Kepler-226",
    )
    dispositions = sorted(data["exoplanet_archive_disposition"].dropna().astype(str).unique())
    selected_dispositions = st.multiselect("Classification", dispositions, default=dispositions)

    left, middle, right = st.columns(3)
    with left:
        min_radius = st.number_input("Minimum radius (Earth radii)", min_value=0.0, value=0.0, step=0.1)
    with middle:
        max_radius = st.number_input("Maximum radius (Earth radii)", min_value=0.0, value=0.0, step=0.1)
    with right:
        min_period = st.number_input("Minimum orbital period (days)", min_value=0.0, value=0.0, step=1.0)

    filtered = data.copy()
    if query.strip():
        filtered = filtered.loc[_text_search(filtered, query.strip())]
    if selected_dispositions:
        filtered = filtered.loc[filtered["exoplanet_archive_disposition"].isin(selected_dispositions)]
    else:
        filtered = filtered.iloc[0:0]
    if min_radius > 0:
        filtered = filtered.loc[filtered["planetary_radius_earth_radii"] >= min_radius]
    if max_radius > 0:
        filtered = filtered.loc[filtered["planetary_radius_earth_radii"] <= max_radius]
    if min_period > 0:
        filtered = filtered.loc[filtered["orbital_period_days"] >= min_period]

    st.write(f"Showing {len(filtered):,} matching objects")
    st.caption(f"Source: `{source_label}`")
    if filtered.empty:
        st.info("No objects match these filters.")
        return

    table = filtered[list(DISPLAY_COLUMNS)].rename(columns=DISPLAY_COLUMNS)
    st.dataframe(table.head(200), hide_index=True, use_container_width=True)
    if len(filtered) > 200:
        st.caption("The table is limited to the first 200 matches. Refine the filters to narrow it further.")
