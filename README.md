# Kepler Exoplanet Analysis Platform

## Problem Statement

The Kepler catalog contains thousands of records and many technical measurements. Manually searching those records and interpreting planet, host-star, transit, and classification fields is difficult.

## Proposed Solution

This project provides a small Streamlit application for searching and exploring the cleaned Kepler catalog. It presents measured planet and host-star properties, transit information, existing machine-learning results, screening priority, expected next-transit timing, visual analysis, and plain-language explanations.

## Main Features

- **Overview** — explains the workflow and shows data-derived catalog counts and graphs.
- **Explore catalog** — searches by KOI identifier, Kepler ID, or official name and filters by classification, radius, and orbital period.
- **Candidate analysis** — shows the selected object's identification, planet, host-star, and transit fields.
- **Next Transit** — calculates the next expected event from the catalog timing fields when they are valid.
- **ML evidence** — shows the existing Logistic Regression and Random Forest results, probabilities, and feature importance.
- **Screening** — shows the existing screening score, priority, and indicators for further review.
- **Visualizations** — organizes useful catalog, model, and screening plots.
- **ASK KEPLER** — supports a small set of natural-language searches and questions using the real dataframe and existing project results.

## Next Transit

The application calculates the next expected transit mathematically:

```text
next_transit = epoch + n × orbital_period
```

The application uses the repository's user-facing timing fields:

- `transit_epoch_bkjd` comes from `koi_time0bk`.
- `orbital_period_days` comes from `koi_period`.

The current UTC time is converted to the same BKJD time basis before selecting the next future event. This is a mathematical timing estimate, not an ML prediction, and it does not scientifically confirm an exoplanet. If the timing fields are missing or invalid, the application reports that timing is unavailable.

## Machine Learning

The application reuses the project's existing Logistic Regression and Random Forest workflow. The models use prepared Kepler features to estimate the available catalog classes. Results are dataset-based classifications, not scientific validation.

## Screening

Screening uses the project's existing candidate-prediction results, including class probabilities and screening priority. Screening priority is for further review and is not scientific confirmation.

## Dataset

The application uses:

```text
data/raw/processed/Data_cleaned.csv
```

The current cleaned file contains **9,564 rows and 48 columns**. The app uses the actual repository fields, including:

- `koi_identifier`, `kepler_id`, `official_name`
- `exoplanet_archive_disposition`
- `planetary_radius_earth_radii`, `orbital_period_days`
- `equilibrium_temperature_k`, `insolation_flux`
- `stellar_effective_temperature_k`, `stellar_radius_solar_radii`
- `stellar_surface_gravity_log10`, `kepler_band_magnitude`
- `transit_depth_ppm`, `transit_duration_hours`
- `transit_signal_to_noise_ratio`, `transit_epoch_bkjd`

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- SciPy
- scikit-learn
- Joblib
- Jupyter notebooks

## Project Structure

```text
.
├── app/
│   ├── streamlit_app.py
│   ├── data.py
│   └── pages/
│       ├── overview.py
│       ├── explorer.py
│       ├── candidate_analysis.py
│       ├── ask_kepler.py
│       ├── ml_screening.py
│       └── visualizations.py
├── data/raw/
│   ├── cumulative.csv
│   └── processed/
│       └── Data_cleaned.csv
├── member 2/
├── notebooks/
├── reports/
├── src/
│   ├── ask_kepler.py
│   ├── ml.py
│   ├── screening.py
│   ├── transit.py
│   └── visualizations.py
├── kepler_Package/
├── requirements.txt
└── README.md
```

## How to Run

From the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Limitations

- ML outputs are classifications learned from the prepared dataset.
- Screening is prioritization for further review.
- Next-transit output is a mathematical timing estimate.
- The application does not scientifically validate exoplanets.
- Full light-curve time-series analysis is not available.

No application screenshots are included in the repository.
