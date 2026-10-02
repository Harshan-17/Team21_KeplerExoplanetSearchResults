# Kepler Exoplanet Analysis Platform

## Problem Statement

The Kepler catalog contains thousands of observations and many technical parameters. Manually searching those records, understanding the measurements, and interpreting the available classification and screening results is difficult, especially for users who are new to astronomy.

## Proposed Solution

This project provides an interactive Streamlit application for searching and exploring Kepler objects. It presents planet properties, host-star properties, transit information, existing machine-learning classification results, screening priority, expected next-transit timing, visual analysis, and human-readable explanations. The application also includes ASK KEPLER, a small natural-language interface for supported catalog searches and selected-object questions.

## Main Features

- **Overview**: explains the application workflow and shows data-derived catalog counts and overview graphs.
- **Explore/Search**: the application includes an Explore catalog navigation page, while supported natural-language search is available through ASK KEPLER.
- **Candidate Analysis**: select one Kepler object and inspect its recorded values.
- **Planet information**: planetary radius, orbital period, equilibrium temperature, and insolation flux.
- **Host-star information**: stellar effective temperature, stellar radius, stellar surface gravity, and Kepler magnitude.
- **Transit information**: transit depth, transit duration, signal-to-noise ratio, and transit epoch.
- **Next Transit Countdown**: calculates the next expected transit for the selected object when timing fields are valid.
- **ML classification**: shows the existing Logistic Regression and Random Forest outputs and saved evaluation results.
- **Screening**: shows saved screening score, priority, and recorded screening indicators.
- **Visualizations**: organizes catalog relationships, classification distributions, correlations, feature importance, and model comparison into focused tabs.
- **ASK KEPLER chatbot**: supports a small set of natural-language catalog filters and selected-object questions using the real dataframe and existing project functions.

## Next Transit

The application calculates the next expected transit mathematically from the catalog transit epoch and orbital period:

```text
next_transit = epoch + n × orbital_period
```

The application maps the user-facing timing fields to the repository fields:

- `transit_epoch_bkjd` -> `koi_time0bk`
- `orbital_period_days` -> `koi_period`

The current UTC time is converted to the same BKJD time basis before the next future event is selected. This is a mathematical expected-transit calculation, not an ML prediction. It does not scientifically confirm an exoplanet.

If either timing value is missing or invalid, the application reports that next-transit timing is unavailable for the selected object.

## Machine Learning

The application reuses the project's existing Logistic Regression and Random Forest workflow. The existing prepared features and saved outputs are used to estimate available dataset labels for selected objects. The project models provide `CONFIRMED` and `FALSE POSITIVE` outputs; `CANDIDATE` remains the catalog label rather than a third trained model class.

Model outputs are dataset-based screening results. They are not scientific validation.

## Screening

Screening uses the project's saved candidate-prediction artifact, including the recorded confirmed-probability output, priority, outlier flag, and relevant indicators. Screening priority is for further review and is not scientific confirmation.

## Dataset

The application source of truth is the cleaned CSV loaded by `app/data.py`:

```text
data/raw/processed/Data_cleaned.csv
```

This file currently contains 9,564 rows and 48 columns. The requested path `data/processed/kepler_cleaned.csv` is not present in this repository. The original repository file `data/raw/processed/kepler_cleaned.csv` is preserved separately; the running application uses the path shown above.

The application uses the repository's actual column names, including `koi_disposition`, `koi_prad`, `koi_period`, `koi_time0bk`, `koi_depth`, `koi_model_snr`, `koi_steff`, and related fields.

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- scikit-learn
- CSV data files and Jupyter notebooks from the project

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
├── data/
│   └── raw/
│       ├── cumulative.csv
│       └── processed/
├── docs/
├── kepler_Package/
├── member 2/
├── notebooks/
├── reports/
├── results/
│   ├── figures/
│   └── tables/
├── src/
│   ├── ask_kepler.py
│   ├── ml.py
│   ├── screening.py
│   ├── transit.py
│   └── visualizations.py
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

- ML predictions are classifications based on the prepared dataset and existing project workflow.
- Screening is prioritization for further review.
- Next-transit output is a mathematical timing estimate.
- The application does not scientifically validate exoplanets.
- Full light-curve time-series analysis is not available in the application.
- The separate Explore catalog page is currently a navigation shell; ASK KEPLER provides the implemented natural-language search patterns.

## Application Preview

No application screenshots are included in the repository.
