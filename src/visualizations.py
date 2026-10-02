import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from src.data_loader import load_data


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"

# Create the output directory if it does not exist
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def save_figure(filename: str) -> None:
    """
    Save the current Matplotlib figure into results/figures.
    """
    plt.tight_layout()

    output_path = FIGURE_DIR / filename

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    print(f"Saved: {output_path}")


# ============================================================
# 1. CLASSIFICATION DISTRIBUTION
# ============================================================

def plot_class_distribution(df: pd.DataFrame) -> None:
    """
    Plot the number of objects in each Kepler classification.
    """

    column = "exoplanet_archive_disposition"

    counts = df[column].value_counts()

    plt.figure(figsize=(8, 5))

    counts.plot(kind="bar")

    plt.title("Kepler Object Classification Distribution")
    plt.xlabel("Classification")
    plt.ylabel("Number of Objects")

    plt.xticks(rotation=0)

    save_figure("01_classification_distribution.png")


# ============================================================
# 2. PLANET RADIUS BY CLASSIFICATION
# ============================================================

def plot_radius_by_classification(df: pd.DataFrame) -> None:
    """
    Compare planetary radius across Kepler classification groups.
    """

    required_columns = [
        "exoplanet_archive_disposition",
        "planetary_radius_earth_radii"
    ]

    data = df[required_columns].dropna()

    groups = []
    labels = []

    for classification, group in data.groupby(
        "exoplanet_archive_disposition"
    ):
        groups.append(
            group["planetary_radius_earth_radii"]
        )

        labels.append(classification)

    plt.figure(figsize=(8, 5))

    # tick_labels is used by newer Matplotlib versions
    plt.boxplot(
        groups,
        tick_labels=labels
    )

    plt.title("Planetary Radius by Kepler Classification")
    plt.xlabel("Classification")
    plt.ylabel("Planetary Radius (Earth Radii)")

    plt.xticks(rotation=15)

    save_figure("02_radius_by_classification.png")


# ============================================================
# 3. ORBITAL PERIOD BY CLASSIFICATION
# ============================================================

def plot_period_by_classification(df: pd.DataFrame) -> None:
    """
    Compare orbital period across Kepler classification groups.
    """

    required_columns = [
        "exoplanet_archive_disposition",
        "orbital_period_days"
    ]

    data = df[required_columns].dropna()

    groups = []
    labels = []

    for classification, group in data.groupby(
        "exoplanet_archive_disposition"
    ):
        groups.append(
            group["orbital_period_days"]
        )

        labels.append(classification)

    plt.figure(figsize=(8, 5))

    # tick_labels is used by newer Matplotlib versions
    plt.boxplot(
        groups,
        tick_labels=labels
    )

    plt.title("Orbital Period by Kepler Classification")
    plt.xlabel("Classification")
    plt.ylabel("Orbital Period (Days)")

    plt.xticks(rotation=15)

    save_figure("03_period_by_classification.png")


# ============================================================
# 4. PLANET RADIUS VS TRANSIT DEPTH
# ============================================================

def plot_radius_vs_transit_depth(df: pd.DataFrame) -> None:
    """
    Show the relationship between planetary radius
    and transit depth.
    """

    required_columns = [
        "planetary_radius_earth_radii",
        "transit_depth_ppm"
    ]

    data = df[required_columns].dropna()

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["planetary_radius_earth_radii"],
        data["transit_depth_ppm"],
        alpha=0.5
    )

    plt.title("Planetary Radius vs Transit Depth")
    plt.xlabel("Planetary Radius (Earth Radii)")
    plt.ylabel("Transit Depth (ppm)")

    save_figure("04_radius_vs_transit_depth.png")


# ============================================================
# 5. ORBITAL PERIOD VS EQUILIBRIUM TEMPERATURE
# ============================================================

def plot_period_vs_temperature(df: pd.DataFrame) -> None:
    """
    Show the relationship between orbital period
    and planet equilibrium temperature.
    """

    required_columns = [
        "orbital_period_days",
        "equilibrium_temperature_k"
    ]

    data = df[required_columns].dropna()

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["orbital_period_days"],
        data["equilibrium_temperature_k"],
        alpha=0.5
    )

    plt.title(
        "Orbital Period vs Equilibrium Temperature"
    )

    plt.xlabel("Orbital Period (Days)")
    plt.ylabel("Equilibrium Temperature (K)")

    save_figure("05_period_vs_temperature.png")


# ============================================================
# 6. TRANSIT DURATION VS ORBITAL PERIOD
# ============================================================

def plot_transit_duration_vs_period(df: pd.DataFrame) -> None:
    """
    Show the relationship between transit duration
    and orbital period.
    """

    required_columns = [
        "transit_duration_hours",
        "orbital_period_days"
    ]

    data = df[required_columns].dropna()

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["orbital_period_days"],
        data["transit_duration_hours"],
        alpha=0.5
    )

    plt.title(
        "Orbital Period vs Transit Duration"
    )

    plt.xlabel("Orbital Period (Days)")
    plt.ylabel("Transit Duration (Hours)")

    save_figure("06_period_vs_transit_duration.png")


# ============================================================
# 7. STELLAR TEMPERATURE VS PLANET TEMPERATURE
# ============================================================

def plot_star_vs_planet_temperature(df: pd.DataFrame) -> None:
    """
    Show the relationship between stellar effective
    temperature and planet equilibrium temperature.
    """

    required_columns = [
        "stellar_effective_temperature_k",
        "equilibrium_temperature_k"
    ]

    data = df[required_columns].dropna()

    plt.figure(figsize=(8, 5))

    plt.scatter(
        data["stellar_effective_temperature_k"],
        data["equilibrium_temperature_k"],
        alpha=0.5
    )

    plt.title(
        "Stellar Temperature vs Planet Equilibrium Temperature"
    )

    plt.xlabel(
        "Stellar Effective Temperature (K)"
    )

    plt.ylabel(
        "Planet Equilibrium Temperature (K)"
    )

    save_figure("07_star_vs_planet_temperature.png")


# ============================================================
# 8. CORRELATION HEATMAP
# ============================================================

def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    """
    Plot a correlation matrix for important numerical
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
        "kepler_band_magnitude"
    ]

    available_features = [
        feature
        for feature in features
        if feature in df.columns
    ]

    correlation = df[available_features].corr()

    plt.figure(figsize=(12, 9))

    plt.imshow(
        correlation,
        interpolation="nearest",
        aspect="auto"
    )

    plt.colorbar(
        label="Correlation"
    )

    plt.xticks(
        range(len(correlation.columns)),
        correlation.columns,
        rotation=90
    )

    plt.yticks(
        range(len(correlation.columns)),
        correlation.columns
    )

    plt.title(
        "Correlation Heatmap of Kepler Properties"
    )

    save_figure("08_correlation_heatmap.png")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KEPLER EXOPLANET VISUALIZATION")
    print("=" * 60)

    # Load cleaned dataset
    df = load_data()

    print(f"\nDataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

    print("\nGenerating visualizations...\n")

    # 1
    plot_class_distribution(df)

    # 2
    plot_radius_by_classification(df)

    # 3
    plot_period_by_classification(df)

    # 4
    plot_radius_vs_transit_depth(df)

    # 5
    plot_period_vs_temperature(df)

    # 6
    plot_transit_duration_vs_period(df)

    # 7
    plot_star_vs_planet_temperature(df)

    # 8
    plot_correlation_heatmap(df)

    print("\n" + "=" * 60)
    print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
    print("=" * 60)