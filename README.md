<!--
KEPLER OBSERVATORY
README visual showcase — GitHub-renderable Markdown + Mermaid.
Replace the screenshot placeholders with real application screenshots when available.
-->

<div align="center">

# ✦ KEPLER OBSERVATORY
### AI-Assisted Exoplanet Discovery, Transit Telemetry & Scientific Analysis

**Explore distant worlds. Follow predicted transits. Investigate the data behind discovery.**

[![Repository](https://img.shields.io/badge/GitHub-Source%20Code-181717?style=for-the-badge&logo=github)](https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults)
[![Mission](https://img.shields.io/badge/Mission-NASA%20Kepler-0B3D91?style=for-the-badge)](https://science.nasa.gov/mission/kepler/)
[![Data](https://img.shields.io/badge/Data-Kepler%20DR25-00B8D9?style=for-the-badge)](https://exoplanetarchive.ipac.caltech.edu/)

<br/>

![Kepler Observatory — conceptual project banner](docs/kepler-observatory-banner.svg)

*A space-inspired research platform bringing together Kepler Objects of Interest (KOIs), interactive orbital visualisation, transit timing, machine-learning screening, and statistical exploration.*

</div>

---

## 🌌 The idea

**Kepler Observatory** is an interactive exoplanet research and analysis platform built around NASA's Kepler mission data. It aims to make a large scientific catalogue easier to explore by combining a cinematic observatory with searchable records, calculated transit telemetry, screening results, scientific plots, and an AI research assistant.

Instead of treating the dataset as a spreadsheet alone, the platform connects a selected candidate to its parameters, predicted transit timing, light-curve simulation, and analytical context.

> **Core principle:** the interface should make science easier to investigate—not disguise missing observations with invented data. Observed measurements, calculated predictions, model outputs, and simulations should be clearly distinguished.

<div align="center">

| ✨ Observe | 🔎 Explore | 🛰️ Predict | 🧠 Analyse |
|:---:|:---:|:---:|:---:|
| 3D star–planet scene | Searchable KOI catalogue | Live-updating transit countdown | ML and statistical insights |

</div>

## 🪐 Main experiences

### 1. Interactive 3D Observatory

A cinematic view of a host star and an orbiting exoplanet, designed as the main entry point to the platform.

- Central host star, orbital path, and continuously moving planet.
- Temperature-inspired stellar and planet palettes.
- Procedural surface detail, atmospheric glow, and pointer/touch interaction where supported.
- Observatory telemetry that follows the selected candidate.
- A space-themed HUD with concise scientific parameters.

### 2. Live transit countdown

The Observatory's signature telemetry feature is a countdown to a candidate's next **calculated transit**.

The intended display brings together the target name and KOI, next predicted transit time, a days–hours–minutes–seconds countdown, orbital period, transit duration, transit depth, and an `UPCOMING` / `IN PROGRESS` status.

Transit timing is derived from the candidate's reference epoch and orbital period:

\[
t_n = t_0 + nP
\]

where \(t_0\) is the reference transit epoch, \(P\) is the orbital period, and \(n\) is the integer transit cycle.

For Kepler time values, the project uses the convention:

\[
\mathrm{BKJD} = \mathrm{BJD} - 2454833.0
\]

Countdowns are **ephemeris calculations**, not a claim that a telescope is currently observing the event. Accurate predictions depend on valid source parameters and their uncertainties.

### 3. Explore the Kepler catalogue

Browse the cleaned KOI dataset with candidate search, filters, sorting, pagination, and individual candidate details.

Candidate parameters represented in the project include:

- Archive disposition and disposition score
- Planet radius and orbital period
- Transit epoch, duration, and depth
- Equilibrium temperature and insolation flux
- Transit signal-to-noise ratio (SNR)
- Impact parameter
- Stellar temperature, radius, surface gravity, and Kepler-band magnitude

Missing measurements should be presented as unavailable rather than filled with fabricated values.

### 4. Candidate Screening

A ranked view of the supplied screening results for follow-up prioritisation, including screening probabilities, score and priority tier where present in the data.

The repository's application documentation describes this score as:

\[
\mathrm{Priority\ Score} =
\big(P(\mathrm{confirmed}) + P(\mathrm{candidate})\big) \times 100
\]

The score supports **algorithmic prioritisation**. It is not itself scientific confirmation of a planet.

### 5. Transit Studio

An interactive way to understand how a planet passing in front of its host star produces a dip in measured brightness.

The simulator is based on the approximate depth relationship:

\[
\frac{\Delta F}{F} \approx \left(\frac{R_p}{R_\star}\right)^2
\]

where \(R_p\) is the planet radius and \(R_\star\) is the stellar radius. This is a simplified approximation; stellar limb darkening and transit geometry affect a realistic light curve.

**Simulations must be labelled as simulations**, not as new NASA observations.

### 6. ML Models

A research view for understanding the project's documented model benchmarks, screening signals, model comparisons, and feature diagnostics.

The project materials describe Random Forest and Logistic Regression baselines. Reported benchmark values should be interpreted in the context of the associated training/evaluation workflow, split strategy, and stored outputs; they are not a guarantee of generalisation to unseen data.

### 7. Statistical Insights

Explore the distributions and relationships between exoplanet and stellar parameters through statistical summaries, correlation analysis, heatmaps, and scatter plots where the relevant results are available.

Potential relationships include radius vs. transit depth, orbital period vs. temperature, and transit SNR vs. planet radius. Correlation indicates association, not causation.

### 8. Kepler AI research assistant

A conversational interface intended to help users interpret candidate parameters, transit terminology, screening outputs, and statistical results. When enabled, the Gemini integration should call the model from the server side and keep the API key out of browser code.

AI-generated explanations should be grounded in available data and labelled appropriately. AI access may require a configured API key; data exploration should not depend on the AI service being available.

---

## 🖼️ Visual tour

The diagrams below are **concept illustrations of the product experience**, not screenshots of a verified live deployment. They explain the intended information hierarchy and scientific workflow.

<div align="center">

### Live transit countdown · Concept visual

<img src="docs/transit-countdown-concept.svg" alt="Illustrative transit countdown and orbital telemetry panel" width="900"/>

*Predicted transit time, live-updating timer, orbital parameters, and transit status belong together in one Observatory HUD. Example digits in this illustration are decorative, not live data.*

### Research / Analysis · Concept visual

<img src="docs/research-dashboard-concept.svg" alt="Illustrative research dashboard with screening table, scatter plot, correlation matrix, and model feature bars" width="900"/>

*The research experience brings candidate prioritisation, scientific relationships, correlation views, and model diagnostics together. Charts should use actual project outputs when running.*

</div>

---

### How the platform connects the science

```mermaid
flowchart TD
    A["Kepler archive / supplied CSV data"] --> B["Data parsing and validation"]
    B --> C["Candidate catalogue"]
    B --> D["Screening results"]
    B --> E["Statistical analysis"]
    C --> F["Candidate profile"]
    F --> G["3D Observatory"]
    F --> H["Transit Studio"]
    C --> I["Calculated ephemeris"]
    I --> J["Next-transit countdown"]
    D --> K["Screening and ML views"]
    E --> L["Charts and correlations"]
    C --> M["Kepler AI context"]
    D --> M
    E --> M
```

---

## 📊 Dataset & scientific outputs

The repository includes the following important data and research assets:

| Path | Purpose |
|---|---|
| `data/raw/cumulative.csv` | Raw cumulative Kepler catalogue file |
| `data/raw/processed/kepler_cleaned.csv` | Cleaned dataset used by the project |
| `results/tables/kepler_screening_results.csv` | Candidate screening outputs |
| `notebooks/final_analysis.ipynb` | Research analysis notebook |
| `results/figures/` | Analysis figures, when present |
| `results/tables/` | Tabular analysis results |
| `docs/` | Project presentation and report documents |

The project has been documented around approximately **9,201 Kepler Objects of Interest (KOIs)**. Always use the actual current data file and report the valid loaded row count at runtime; a repository description or an old benchmark should not replace data validation.

### Scientific terms at a glance

| Term | Meaning |
|---|---|
| **KOI** | Kepler Object of Interest; a target associated with a possible transit signal |
| **Transit** | A planet passes in front of its host star from the observer's viewpoint |
| **Transit depth** | The fractional reduction in observed stellar brightness, often expressed in ppm |
| **Transit SNR** | Signal-to-noise ratio used to describe the strength of a transit signal |
| **BKJD** | Barycentric Kepler Julian Date, using the Kepler reference offset convention |
| **Ephemeris** | A model of event timing based on a reference epoch and period |
| **Screening score** | A model-derived prioritisation measure—not an observational confirmation |

---

## 🧰 Technology

The application repository includes technologies for interactive UI, 3D rendering, server-side API handling, and scientific analysis.

<div align="center">

![React](https://img.shields.io/badge/React-19-149ECA?style=flat-square&logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=flat-square&logo=vite&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-WebGL-black?style=flat-square&logo=threedotjs&logoColor=white)
![Express](https://img.shields.io/badge/Express-API-555555?style=flat-square&logo=express&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scientific%20analysis-3776AB?style=flat-square&logo=python&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)

</div>

The repository contains a React + TypeScript + Vite frontend, React Three Fiber / Three.js components, an Express TypeScript server, CSV-based scientific data, and Python analysis dependencies including NumPy, pandas, SciPy, Matplotlib, and scikit-learn. Exact runtime and deployment compatibility depends on the active project configuration.

---

## 🚀 Run locally

### Prerequisites

- Node.js (use a version supported by the project's dependencies)
- npm
- Python for the separate analysis notebooks/pipeline, if you plan to run them

### Web application

```bash
git clone https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults.git
cd Team21_KeplerExoplanetSearchResults
npm install
npm run dev
```

The repository's current `package.json` and server configuration are the source of truth for available commands. If a command fails, check the package scripts and README's deployment notes against the current branch.

### Environment variables

If the Gemini assistant is enabled, configure its server-side key in your local environment (for example, in a `.env` file if supported by the server configuration):

```dotenv
GEMINI_API_KEY=your_key_here
```

- Do not commit real secrets.
- Do not expose the key through client-side code or public environment variables.
- The AI assistant may require a key; core dataset features should remain usable without one when the application supports a fallback.

### Python analysis environment

```bash
python -m venv .venv
```

Activate the environment, then install the repository's scientific dependencies:

```bash
pip install -r requirements.txt
```

Open `notebooks/final_analysis.ipynb` with Jupyter to inspect the analysis workflow.

---

## ☁️ Deployment notes

The repository has been connected to a Vercel deployment during development, but a successful frontend build alone does not verify that the API functions, CSV file loading, Gemini integration, or every dashboard works in production.

Before considering a deployment healthy, verify:
- The root path displays the actual Observatory interface.
- API endpoints return JSON with populated data where expected.
- CSV datasets resolve correctly in the hosted runtime.
- The countdown is derived from valid epoch/period parameters.
- Candidate search, filtering, screening, statistics, and chart data work.
- Gemini credentials are configured server-side if AI features are enabled.
- Browser console and serverless logs contain no unresolved runtime errors.

Deployment setup may need to be adapted to the hosting platform's serverless runtime and filesystem rules.

---

## 🧭 Project navigation

- **Source code:** [Browse the repository](https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults)
- **Data:** [Cleaned Kepler dataset](https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults/tree/main/data/raw/processed)
- **Screening outputs:** [Results tables](https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults/tree/main/results/tables)
- **Analysis notebook:** [final_analysis.ipynb](https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults/blob/main/notebooks/final_analysis.ipynb)
- **Project documents:** [Presentation and report files](https://github.com/Harshan-17/Team21_KeplerExoplanetSearchResults/tree/main/docs)
- **NASA Kepler mission:** [NASA Science](https://science.nasa.gov/mission/kepler/)
- **NASA Exoplanet Archive:** [Archive portal](https://exoplanetarchive.ipac.caltech.edu/)

## ⚠️ Interpretation & limitations

- A KOI is not automatically a confirmed planet.
- A machine-learning score indicates a model assessment; it does not replace scientific confirmation.
- Transit countdowns are calculated from ephemerides and can be affected by parameter uncertainty.
- Transit light curves generated by the simulator are simulations, not direct observations.
- AI responses can be incomplete or incorrect and should be checked against source data.
- Missing or unavailable measurements must not be silently replaced with fabricated values.
- A visual planet surface is an illustrative representation, not a direct image of an exoplanet.

---

<div align="center">

### ✦ From transit signals to scientific insight

**KEPLER OBSERVATORY**  
*Observe · Explore · Predict · Analyse*

Built as an exoplanet data exploration and research project by **Team 21 — Hack vok**.

</div>
