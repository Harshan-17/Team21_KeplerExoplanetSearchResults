import pandas as pd

from src.data_loader import load_data


# ============================================================
# DATASET OVERVIEW
# ============================================================

def get_dataset_shape(df: pd.DataFrame) -> tuple[int, int]:
    """Return the number of rows and columns."""
    return df.shape


def get_column_names(df: pd.DataFrame) -> list[str]:
    """Return all column names."""
    return df.columns.tolist()


def get_data_types(df: pd.DataFrame) -> pd.Series:
    """Return the data type of every column."""
    return df.dtypes


def get_descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return descriptive statistics for numerical columns.
    """
    return df.describe()


# ============================================================
# KEPLER CLASSIFICATION ANALYSIS
# ============================================================

def get_class_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Return the number of objects in each Kepler archive
    disposition category.
    """
    column = "exoplanet_archive_disposition"

    if column not in df.columns:
        raise KeyError(f"Missing required column: {column}")

    return df[column].value_counts(dropna=False)


def get_class_percentages(df: pd.DataFrame) -> pd.Series:
    """
    Return the percentage of objects in each classification.
    """
    column = "exoplanet_archive_disposition"

    if column not in df.columns:
        raise KeyError(f"Missing required column: {column}")

    return df[column].value_counts(normalize=True, dropna=False) * 100


# ============================================================
# IMPORTANT KEPLER FEATURE SUMMARIES
# ============================================================

PLANET_FEATURES = [
    "orbital_period_days",
    "transit_depth_ppm",
    "transit_duration_hours",
    "planetary_radius_earth_radii",
    "equilibrium_temperature_k",
    "insolation_flux",
]

STELLAR_FEATURES = [
    "stellar_effective_temperature_k",
    "stellar_surface_gravity_log10",
    "stellar_radius_solar_radii",
    "kepler_band_magnitude",
]

TRANSIT_FEATURES = [
    "impact_parameter",
    "transit_depth_ppm",
    "transit_duration_hours",
    "transit_signal_to_noise_ratio",
]


def summarize_features(
    df: pd.DataFrame,
    features: list[str]
) -> pd.DataFrame:
    """
    Return descriptive statistics for a selected group of features.
    """
    available_features = [
        feature for feature in features
        if feature in df.columns
    ]

    if not available_features:
        raise ValueError("None of the requested features exist in the dataset.")

    return df[available_features].describe().T


# ============================================================
# MISSING VALUE CHECK
# ============================================================

def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return missing-value counts and percentages.
    """
    missing_count = df.isnull().sum()
    missing_percentage = (missing_count / len(df)) * 100

    summary = pd.DataFrame({
        "missing_count": missing_count,
        "missing_percentage": missing_percentage,
    })

    return summary.sort_values(
        by="missing_count",
        ascending=False
    )


# ============================================================
# CORRELATION DATA
# ============================================================

def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return the correlation matrix for important numerical
    Kepler properties.
    """
    features = [
        "orbital_period_days",
        "impact_parameter",
        "transit_duration_hours",
        "transit_depth_ppm",
        "planetary_radius_earth_radii",
        "equilibrium_temperature_k",
        "insolation_flux",
        "transit_signal_to_noise_ratio",
        "stellar_effective_temperature_k",
        "stellar_surface_gravity_log10",
        "stellar_radius_solar_radii",
        "kepler_band_magnitude",
    ]

    available_features = [
        feature for feature in features
        if feature in df.columns
    ]

    return df[available_features].corr()


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    # Load cleaned Kepler dataset
    df = load_data()

    print("=" * 60)
    print("KEPLER EXOPLANET DATASET - EDA")
    print("=" * 60)

    # Dataset shape
    rows, columns = get_dataset_shape(df)
    print(f"\nDataset shape: {rows} rows × {columns} columns")

    # Column names
    print("\nNumber of columns:", len(get_column_names(df)))

    # Data types
    print("\nData types:")
    print(get_data_types(df))

    # Descriptive statistics
    print("\nDescriptive statistics:")
    print(get_descriptive_statistics(df))

    # Classification distribution
    print("\nClassification distribution:")
    print(get_class_distribution(df))

    # Classification percentages
    print("\nClassification percentages:")
    print(get_class_percentages(df).round(2))

    # Missing values
    print("\nMissing-value summary:")
    print(get_missing_value_summary(df).head(15))

    # Planet features
    print("\nPlanet feature summary:")
    print(summarize_features(df, PLANET_FEATURES))

    # Stellar features
    print("\nStellar feature summary:")
    print(summarize_features(df, STELLAR_FEATURES))

    # Transit features
    print("\nTransit feature summary:")
    print(summarize_features(df, TRANSIT_FEATURES))

    # Correlations
    print("\nCorrelation matrix:")
    print(get_correlation_matrix(df).round(2))