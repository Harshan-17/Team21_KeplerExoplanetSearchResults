import pandas as pd
from scipy.stats import pearsonr, spearmanr

from src.data_loader import load_data


# ============================================================
# IMPORTANT FEATURES
# ============================================================

FEATURES = [
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


# ============================================================
# PEARSON CORRELATION
# ============================================================

def calculate_pearson_correlation(
    df: pd.DataFrame,
    column1: str,
    column2: str
) -> dict:
    """
    Calculate Pearson correlation and p-value
    between two numerical variables.
    """

    data = df[[column1, column2]].dropna()

    correlation, p_value = pearsonr(
        data[column1],
        data[column2]
    )

    return {
        "variable_1": column1,
        "variable_2": column2,
        "correlation": correlation,
        "p_value": p_value,
        "sample_size": len(data),
    }


# ============================================================
# SPEARMAN CORRELATION
# ============================================================

def calculate_spearman_correlation(
    df: pd.DataFrame,
    column1: str,
    column2: str
) -> dict:
    """
    Calculate Spearman rank correlation and p-value
    between two numerical variables.
    """

    data = df[[column1, column2]].dropna()

    correlation, p_value = spearmanr(
        data[column1],
        data[column2]
    )

    return {
        "variable_1": column1,
        "variable_2": column2,
        "correlation": correlation,
        "p_value": p_value,
        "sample_size": len(data),
    }


# ============================================================
# IMPORTANT RELATIONSHIPS
# ============================================================

RELATIONSHIPS = [
    (
        "planetary_radius_earth_radii",
        "transit_depth_ppm"
    ),
    (
        "orbital_period_days",
        "equilibrium_temperature_k"
    ),
    (
        "orbital_period_days",
        "transit_duration_hours"
    ),
    (
        "stellar_effective_temperature_k",
        "equilibrium_temperature_k"
    ),
    (
        "planetary_radius_earth_radii",
        "transit_signal_to_noise_ratio"
    ),
]


# ============================================================
# ANALYZE IMPORTANT RELATIONSHIPS
# ============================================================

def analyze_relationships(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate Pearson and Spearman correlations
    for selected Kepler relationships.
    """

    results = []

    for column1, column2 in RELATIONSHIPS:

        pearson_result = calculate_pearson_correlation(
            df,
            column1,
            column2
        )

        spearman_result = calculate_spearman_correlation(
            df,
            column1,
            column2
        )

        results.append({
            "variable_1": column1,
            "variable_2": column2,
            "pearson_r": pearson_result["correlation"],
            "pearson_p": pearson_result["p_value"],
            "spearman_rho": spearman_result["correlation"],
            "spearman_p": spearman_result["p_value"],
            "sample_size": pearson_result["sample_size"],
        })

    return pd.DataFrame(results)


# ============================================================
# FULL CORRELATION MATRIX
# ============================================================

def get_correlation_matrix(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Return Pearson correlation matrix
    for available numerical features.
    """

    available_features = [
        feature
        for feature in FEATURES
        if feature in df.columns
    ]

    return df[available_features].corr()


# ============================================================
# FIND STRONGEST CORRELATIONS
# ============================================================

def get_strongest_correlations(
    df: pd.DataFrame,
    minimum_correlation: float = 0.5
) -> pd.DataFrame:
    """
    Find variable pairs with absolute Pearson
    correlation greater than the selected threshold.
    """

    correlation_matrix = get_correlation_matrix(df)

    results = []

    columns = correlation_matrix.columns

    for i in range(len(columns)):

        for j in range(i + 1, len(columns)):

            variable1 = columns[i]
            variable2 = columns[j]

            correlation = correlation_matrix.iloc[i, j]

            if pd.notna(correlation):

                if abs(correlation) >= minimum_correlation:

                    results.append({
                        "variable_1": variable1,
                        "variable_2": variable2,
                        "correlation": correlation,
                        "absolute_correlation": abs(correlation),
                    })

    result_df = pd.DataFrame(results)

    if not result_df.empty:
        result_df = result_df.sort_values(
            by="absolute_correlation",
            ascending=False
        )

    return result_df


# ============================================================
# INTERPRETATION
# ============================================================

def interpret_correlation(
    correlation: float
) -> str:
    """
    Provide a basic interpretation of correlation strength.
    """

    absolute_value = abs(correlation)

    if absolute_value < 0.1:
        strength = "very weak"
    elif absolute_value < 0.3:
        strength = "weak"
    elif absolute_value < 0.5:
        strength = "moderate"
    elif absolute_value < 0.7:
        strength = "strong"
    else:
        strength = "very strong"

    if correlation > 0:
        direction = "positive"
    elif correlation < 0:
        direction = "negative"
    else:
        direction = "no"

    return f"{strength} {direction} relationship"


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("KEPLER EXOPLANET STATISTICAL ANALYSIS")
    print("=" * 70)

    # Load dataset
    df = load_data()

    print(
        f"\nDataset: {df.shape[0]} rows × {df.shape[1]} columns"
    )

    # --------------------------------------------------------
    # Selected relationships
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SELECTED KEPLER RELATIONSHIPS")
    print("=" * 70)

    relationship_results = analyze_relationships(df)

    print(
        relationship_results.to_string(index=False)
    )

    # --------------------------------------------------------
    # Interpret selected relationships
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    for _, row in relationship_results.iterrows():

        interpretation = interpret_correlation(
            row["pearson_r"]
        )

        print(
            f"\n{row['variable_1']} "
            f"vs "
            f"{row['variable_2']}"
        )

        print(
            f"Pearson r: "
            f"{row['pearson_r']:.4f}"
        )

        print(
            f"Pearson p-value: "
            f"{row['pearson_p']:.6g}"
        )

        print(
            f"Spearman rho: "
            f"{row['spearman_rho']:.4f}"
        )

        print(
            f"Spearman p-value: "
            f"{row['spearman_p']:.6g}"
        )

        print(
            f"Interpretation: "
            f"{interpretation}"
        )

    # --------------------------------------------------------
    # Strongest correlations
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("STRONGEST CORRELATIONS")
    print("=" * 70)

    strongest = get_strongest_correlations(
        df,
        minimum_correlation=0.5
    )

    if strongest.empty:

        print(
            "No correlations above the selected threshold."
        )

    else:

        print(
            strongest.to_string(index=False)
        )

    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS COMPLETED")
    print("=" * 70)