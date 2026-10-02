import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from src.data_loader import load_data


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

TARGET = "exoplanet_archive_disposition"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def prepare_data(df):
    """
    Select the features needed for screening
    and remove rows with missing values.
    """

    available_features = [
        feature for feature in FEATURES
        if feature in df.columns
    ]

    required_columns = available_features + [TARGET]

    data = df[required_columns].dropna()

    X = data[available_features]
    y = data[TARGET]

    return X, y


def train_screening_model(X, y):
    """
    Train a Random Forest model for screening.
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    return model


def generate_screening_results(df, model, X):
    """
    Generate predicted class probabilities
    and calculate a screening priority score.
    """

    probabilities = model.predict_proba(X)

    class_names = model.classes_

    probability_df = pd.DataFrame(
        probabilities,
        columns=[
            f"probability_{class_name.lower().replace(' ', '_')}"
            for class_name in class_names
        ],
        index=X.index
    )

    results = df.loc[X.index].copy()

    results = pd.concat(
        [
            results,
            probability_df
        ],
        axis=1
    )

    confirmed_column = "probability_confirmed"
    candidate_column = "probability_candidate"

    results["screening_priority_score"] = (
        results[confirmed_column] +
        results[candidate_column]
    )

    results["screening_priority_score"] = (
        results["screening_priority_score"] * 100
    )

    results = results.sort_values(
        by="screening_priority_score",
        ascending=False
    )

    return results


if __name__ == "__main__":

    print("=" * 70)
    print("KEPLER EXOPLANET SCREENING")
    print("=" * 70)

    # Load dataset
    df = load_data()

    print(
        f"\nOriginal dataset: "
        f"{df.shape[0]} rows × {df.shape[1]} columns"
    )

    # Prepare data
    X, y = prepare_data(df)

    print(
        f"\nScreening dataset: "
        f"{X.shape[0]} objects"
    )

    # Train model
    print("\nTraining Random Forest screening model...")

    model = train_screening_model(X, y)

    print("Model trained successfully.")

    # Generate screening results
    results = generate_screening_results(
        df,
        model,
        X
    )

    # Select top 50
    top_candidates = results.head(50)

    # Save results
    output_path = (
        RESULTS_DIR /
        "kepler_screening_results.csv"
    )

    top_candidates.to_csv(
        output_path,
        index=False
    )

    print("\n" + "=" * 70)
    print("TOP 10 SCREENING RESULTS")
    print("=" * 70)

    columns_to_show = [
        "exoplanet_archive_disposition",
        "screening_priority_score",
        "probability_confirmed",
        "probability_candidate",
        "probability_false_positive",
        "transit_signal_to_noise_ratio",
        "planetary_radius_earth_radii",
        "orbital_period_days",
    ]

    available_columns = [
        column
        for column in columns_to_show
        if column in top_candidates.columns
    ]

    print(
        top_candidates[available_columns]
        .head(10)
        .to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("SCREENING COMPLETED")
    print("=" * 70)

    print(f"\nSaved top 50 results to:")
    print(output_path)