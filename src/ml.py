import pandas as pd

from src.data_loader import load_data

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# ============================================================
# FEATURES AND TARGET
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

TARGET = "exoplanet_archive_disposition"


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_ml_data(df: pd.DataFrame):

    available_features = [
        feature
        for feature in FEATURES
        if feature in df.columns
    ]

    required_columns = available_features + [TARGET]

    data = df[required_columns].dropna()

    X = data[available_features]
    y = data[TARGET]

    return X, y


# ============================================================
# TRAIN LOGISTIC REGRESSION
# ============================================================

def train_logistic_regression(X_train, X_test, y_train, y_test):

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    model.fit(
        X_train_scaled,
        y_train
    )

    predictions = model.predict(X_test_scaled)

    return model, scaler, predictions


# ============================================================
# TRAIN RANDOM FOREST
# ============================================================

def train_random_forest(X_train, X_test, y_train, y_test):

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(X_test)

    return model, predictions


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(y_test, predictions):

    return {
        "accuracy": accuracy_score(
            y_test,
            predictions
        ),

        "precision": precision_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        ),

        "recall": recall_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        ),

        "f1": f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        )
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("KEPLER EXOPLANET MACHINE LEARNING")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_data()

    print(
        f"\nOriginal dataset: "
        f"{df.shape[0]} rows × {df.shape[1]} columns"
    )

    # --------------------------------------------------------
    # Prepare ML dataset
    # --------------------------------------------------------

    X, y = prepare_ml_data(df)

    print(
        f"\nML dataset after removing missing values: "
        f"{X.shape[0]} rows"
    )

    print("\nFeatures:")
    print(X.columns.tolist())

    print("\nTarget distribution:")
    print(y.value_counts())

    # --------------------------------------------------------
    # Train/test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(
        f"\nTraining samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # ========================================================
    # LOGISTIC REGRESSION
    # ========================================================

    print("\n" + "=" * 70)
    print("LOGISTIC REGRESSION")
    print("=" * 70)

    logistic_model, scaler, logistic_predictions = (
        train_logistic_regression(
            X_train,
            X_test,
            y_train,
            y_test
        )
    )

    logistic_metrics = evaluate_model(
        y_test,
        logistic_predictions
    )

    print("\nPerformance:")

    for metric, value in logistic_metrics.items():
        print(
            f"{metric.capitalize()}: "
            f"{value:.4f}"
        )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            logistic_predictions,
            zero_division=0
        )
    )

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            logistic_predictions
        )
    )

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    print("\n" + "=" * 70)
    print("RANDOM FOREST")
    print("=" * 70)

    random_forest_model, rf_predictions = (
        train_random_forest(
            X_train,
            X_test,
            y_train,
            y_test
        )
    )

    rf_metrics = evaluate_model(
        y_test,
        rf_predictions
    )

    print("\nPerformance:")

    for metric, value in rf_metrics.items():
        print(
            f"{metric.capitalize()}: "
            f"{value:.4f}"
        )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            rf_predictions,
            zero_division=0
        )
    )

    print("Confusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            rf_predictions
        )
    )

    # ========================================================
    # MODEL COMPARISON
    # ========================================================

    comparison = pd.DataFrame(
        {
            "Logistic Regression": logistic_metrics,
            "Random Forest": rf_metrics
        }
    )

    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)

    print(
        comparison.round(4)
    )

    # ========================================================
    # RANDOM FOREST FEATURE IMPORTANCE
    # ========================================================

    importance = pd.DataFrame(
        {
            "feature": X.columns,
            "importance": random_forest_model.feature_importances_
        }
    )

    importance = importance.sort_values(
        by="importance",
        ascending=False
    )

    print("\n" + "=" * 70)
    print("RANDOM FOREST FEATURE IMPORTANCE")
    print("=" * 70)

    print(
        importance.to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("MACHINE LEARNING COMPLETED")
    print("=" * 70)