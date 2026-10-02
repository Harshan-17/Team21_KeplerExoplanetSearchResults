import pandas as pd
import matplotlib.pyplot as plt
def analyze_planet_characteristics(df):
    columns = [
        "koi_prad",
        "koi_period",
        "koi_depth",
        "koi_teq",
        "koi_insol"
    ]
    return df[columns].describe()
def analyze_host_star(df):
    columns = [
        "koi_steff",
        "koi_srad",
        "koi_slogg",
        "koi_kepmag"
    ]
    return df[columns].describe()
def calculate_correlations(df):
    columns = [
        "koi_prad",
        "koi_period",
        "koi_depth",
        "koi_teq",
        "koi_insol"
    ]
    return df[columns].corr()
def find_earth_sized_candidates(df):
    return df[
        (df["koi_prad"] >= 0.8) &
        (df["koi_prad"] <= 1.5)
    ]
def find_temperate_candidates(df):
    return df[
        (df["koi_teq"] >= 180) &
        (df["koi_teq"] <= 350)
    ]
def find_screened_candidates(df):
    return df[
        (df["koi_prad"] >= 0.8) &
        (df["koi_prad"] <= 1.5) &
        (df["koi_teq"] >= 180) &
        (df["koi_teq"] <= 350) &
        (df["koi_period"] >= 20)
    ]
def plot_radius_distribution(df):
    plt.figure(figsize=(8, 5))
    plt.hist(
        df["koi_prad"].dropna(),
        bins=50
    )
    plt.xlabel("Planet Radius (Earth Radii)")
    plt.ylabel("Number of Candidates")
    plt.title("Planet Radius Distribution")
    plt.show()
def plot_transit_depth_distribution(df):
    plt.figure(figsize=(8, 5))
    plt.hist(
        df["koi_depth"].dropna(),
        bins=50
    )
    plt.xlabel("Transit Depth (ppm)")
    plt.ylabel("Number of Candidates")
    plt.title("Transit Depth Distribution")
    plt.show()