from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "raw" / "processed" / "Data_cleaned.csv"
PREDICTIONS_PATH = ROOT / "member 2" / "memeber2_candidate_predictions.csv"
MODEL_RESULTS_PATH = ROOT / "member 2" / "member2_model_comparison.csv"
NAV = ["Overview", "Data Explorer", "Exoplanet Analysis", "Host Star Analysis", "ML Prediction", "Advanced Visualizations", "About Project"]
COLORS = {"CONFIRMED": "#59d6be", "CANDIDATE": "#78a7ff", "FALSE POSITIVE": "#f18a8a"}
PLOT = "plotly_dark"

st.set_page_config(page_title="EXOINSIGHT | Kepler Discovery & Analysis", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#08111f; --panel:#0d1a2b; --panel2:#101f32; --line:#1e3046; --muted:#8495aa; --text:#eaf2fb; --mint:#59d6be; --blue:#78a7ff; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 76% 0%, #12263a 0%, #08111f 42%, #070e19 100%); color:var(--text); }
[data-testid="stSidebar"] { background:#091321; border-right:1px solid #1a2a3e; }
[data-testid="stSidebar"] > div:first-child { padding-top:1.2rem; }
.brand { font:800 1.32rem Manrope,sans-serif; letter-spacing:.13em; color:#f2f7fd; }
.brand span { color:var(--mint); }
.brand-sub { color:#71849b; font:500 .66rem 'DM Mono',monospace; letter-spacing:.16em; margin:4px 0 24px; }
.side-foot { color:#647990; font:500 .66rem 'DM Mono',monospace; letter-spacing:.05em; padding-top:22px; border-top:1px solid #1b2a3d; margin-top:22px; }
.eyebrow { color:var(--mint); font:500 .7rem 'DM Mono',monospace; letter-spacing:.15em; text-transform:uppercase; }
.hero { padding:32px 34px 30px; border:1px solid #21364a; border-radius:20px; background:linear-gradient(115deg,rgba(20,47,64,.92),rgba(14,29,47,.90) 55%,rgba(20,35,58,.84)), radial-gradient(circle at 84% 24%,rgba(89,214,190,.14),transparent 27%); position:relative; overflow:hidden; }
.hero:after { content:'✦'; position:absolute; right:8%; top:4%; color:rgba(120,167,255,.12); font-size:180px; line-height:1; }
.hero h1 { font:800 clamp(2rem,4vw,3.25rem)/1.08 Manrope,sans-serif; letter-spacing:-.045em; margin:13px 0 12px; max-width:700px; }
.hero p { color:#a6b6c8; font-size:1rem; line-height:1.65; max-width:670px; margin-bottom:20px; }
.kpi { border:1px solid #1d3045; background:linear-gradient(145deg,rgba(17,33,52,.94),rgba(11,24,39,.94)); border-radius:15px; padding:17px 18px; min-height:112px; }
.kpi-label { color:#93a4b8; font-size:.75rem; letter-spacing:.04em; }
.kpi-value { color:#f1f6fc; font:700 1.75rem Manrope,sans-serif; margin-top:7px; letter-spacing:-.035em; }
.kpi-note { color:#6f8297; font:400 .68rem 'DM Mono',monospace; margin-top:2px; }
.section-head { display:flex; align-items:end; justify-content:space-between; margin:27px 0 14px; }
.section-head h2 { font:700 1.18rem Manrope,sans-serif; margin:3px 0 0; }
.section-head p { color:#8294a9; font-size:.8rem; margin:0; }
.panel { border:1px solid #1d3045; background:rgba(13,26,43,.78); border-radius:16px; padding:18px 20px; }
.badge { display:inline-block; padding:5px 9px; border:1px solid #254156; background:#102536; border-radius:99px; color:#8de5d4; font:500 .68rem 'DM Mono',monospace; letter-spacing:.03em; }
.muted { color:#8395aa; }
div[data-testid="stMetric"] { border:1px solid #1d3045; background:rgba(13,26,43,.8); padding:14px 16px; border-radius:14px; }
div[data-testid="stMetricLabel"] { color:#91a3b7; }
div[data-testid="stMetricValue"] { color:#edf5fc; }
.stButton > button { border-radius:10px; font-weight:600; }
.stButton > button[kind="primary"] { background:#59d6be; border:0; color:#071521; }
.stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:1px solid #203147; }
.stTabs [data-baseweb="tab"] { color:#90a2b7; }
.stDataFrame { border:1px solid #203147; border-radius:12px; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading the processed Kepler catalog…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    for col in df.columns:
        if col.startswith("koi_") or col in {"kepid", "rowid"}:
            df[col] = pd.to_numeric(df[col], errors="coerce") if col not in {"koi_disposition", "koi_pdisposition", "koi_tce_delivname", "kepoi_name", "kepler_name"} else df[col]
    df["host_id"] = df.get("kepid", pd.Series(index=df.index, dtype="object")).astype("Int64").astype(str)
    df["display_name"] = df.get("kepler_name", pd.Series(index=df.index, dtype="object")).fillna("").astype(str).str.strip()
    df.loc[df["display_name"].eq(""), "display_name"] = df.loc[df["display_name"].eq(""), "kepoi_name"].astype(str)
    return df


@st.cache_data(show_spinner=False)
def load_optional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


DATA = load_data()
STATUS_COL = "koi_disposition"
STATUS_ORDER = [s for s in ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"] if s in DATA[STATUS_COL].dropna().unique()]


def fmt(value: float | int, digits: int = 1) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}"


def plotly_theme(fig, height=320):
    fig.update_layout(template=PLOT, height=height, margin=dict(l=8, r=8, t=20, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans", color="#b8c8d9", size=11), legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12, x=0), hoverlabel=dict(bgcolor="#112237", bordercolor="#29445d", font_color="#eaf2fb"))
    fig.update_xaxes(gridcolor="#1d3044", zerolinecolor="#1d3044", linecolor="#263b52")
    fig.update_yaxes(gridcolor="#1d3044", zerolinecolor="#1d3044", linecolor="#263b52")
    return fig


def section(title, subtitle=None):
    st.markdown(f'<div class="section-head"><div><div class="eyebrow">{title}</div><h2>{subtitle or ""}</h2></div></div>', unsafe_allow_html=True)


def kpi_row(df: pd.DataFrame):
    total = len(df)
    confirmed = int((df[STATUS_COL] == "CONFIRMED").sum())
    candidates = int((df[STATUS_COL] == "CANDIDATE").sum())
    false = int((df[STATUS_COL] == "FALSE POSITIVE").sum())
    stars = df["host_id"].nunique()
    vals = [("Observations", total, "processed catalog rows"), ("Confirmed planets", confirmed, "NASA disposition"), ("Candidates", candidates, "awaiting confirmation"), ("False positives", false, "screened observations"), ("Host stars", stars, "unique Kepler targets")]
    cols = st.columns(5)
    for c, (label, val, note) in zip(cols, vals):
        c.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{val:,}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)


def sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="brand">EXO<span>INSIGHT</span></div><div class="brand-sub">KEPLER DISCOVERY PLATFORM</div>', unsafe_allow_html=True)
        page = st.radio("Workspace", NAV, label_visibility="collapsed", format_func=lambda x: {"Overview":"⌂  Overview", "Data Explorer":"⌕  Data Explorer", "Exoplanet Analysis":"◉  Exoplanet Analysis", "Host Star Analysis":"✧  Host Star Analysis", "ML Prediction":"⌘  ML Prediction", "Advanced Visualizations":"▦  Advanced Visualizations", "About Project":"ⓘ  About Project"}[x])
        st.markdown('<div class="side-foot">KEPLER EXOPLANET ANALYSIS<br>CAPSTONE 2026 · DATA PREVIEW</div>', unsafe_allow_html=True)
    return page


def chart_controls(df: pd.DataFrame):
    with st.expander("Analysis filters", expanded=False):
        a, b, c = st.columns([1, 1, 2])
        selected = a.multiselect("Disposition", STATUS_ORDER, default=STATUS_ORDER, key="analysis_status")
        period_max = float(df["koi_period"].quantile(.99)) if "koi_period" in df else 500
        pmin, pmax = b.slider("Orbital period (days)", 0.0, max(period_max, 1.0), (0.0, max(period_max, 1.0)), key="analysis_period")
        radius_max = float(df["koi_prad"].quantile(.99)) if "koi_prad" in df else 100
        rmin, rmax = c.slider("Planet radius (Earth radii)", 0.0, max(radius_max, 1.0), (0.0, max(radius_max, 1.0)), key="analysis_radius")
    mask = df[STATUS_COL].isin(selected) & df["koi_period"].between(pmin, pmax) & df["koi_prad"].between(rmin, rmax)
    return df.loc[mask]


def overview():
    st.markdown('<div class="hero"><div class="eyebrow">NASA KEPLER · PROCESSED DATASET</div><h1>Explore the hidden worlds<br>of the Kepler mission.</h1><p>Analyze stellar observations, investigate planetary patterns, and explore a machine learning workflow built around real Kepler KOI data.</p><span class="badge">DATA → ANALYSIS → VISUALIZATION → ML → INSIGHT</span></div>', unsafe_allow_html=True)
    st.write("")
    kpi_row(DATA)
    left, right = st.columns([1.25, 1])
    with left:
        section("CATALOG SNAPSHOT", "Disposition overview")
        counts = DATA[STATUS_COL].value_counts().reindex(STATUS_ORDER, fill_value=0).rename_axis("Disposition").reset_index(name="Observations")
        fig = px.bar(counts, x="Disposition", y="Observations", color="Disposition", color_discrete_map=COLORS, text_auto=".2s")
        fig.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(plotly_theme(fig, 300), use_container_width=True, config={"displayModeBar": False})
    with right:
        section("PLANETARY PARAMETERS", "Radius and orbital period")
        sample = DATA.dropna(subset=["koi_period", "koi_prad"]).copy()
        sample = sample[sample.koi_period <= sample.koi_period.quantile(.99)]
        sample = sample[sample.koi_prad <= sample.koi_prad.quantile(.99)]
        fig = px.scatter(sample, x="koi_period", y="koi_prad", color=STATUS_COL, color_discrete_map=COLORS, hover_name="display_name", opacity=.72, labels={"koi_period":"Orbital period · days", "koi_prad":"Planet radius · R⊕", STATUS_COL:"Disposition"})
        st.plotly_chart(plotly_theme(fig, 300), use_container_width=True, config={"displayModeBar": False})
    section("SCIENTIFIC INSIGHTS", "Read the catalog without overclaiming")
    i1, i2, i3 = st.columns(3)
    false_rate = (DATA[STATUS_COL].eq("FALSE POSITIVE").mean() * 100)
    med_period = DATA.loc[DATA[STATUS_COL].eq("CONFIRMED"), "koi_period"].median()
    med_radius = DATA.loc[DATA[STATUS_COL].eq("CONFIRMED"), "koi_prad"].median()
    i1.markdown(f'<div class="panel"><div class="eyebrow">CATALOG COMPOSITION</div><h3>{false_rate:.1f}%</h3><span class="muted">of processed observations carry a false-positive disposition.</span></div>', unsafe_allow_html=True)
    i2.markdown(f'<div class="panel"><div class="eyebrow">CONFIRMED · MEDIAN ORBIT</div><h3>{fmt(med_period, 1)} days</h3><span class="muted">Derived from rows labeled confirmed in this dataset.</span></div>', unsafe_allow_html=True)
    i3.markdown(f'<div class="panel"><div class="eyebrow">CONFIRMED · MEDIAN RADIUS</div><h3>{fmt(med_radius, 2)} R⊕</h3><span class="muted">Descriptive statistic, not a population estimate.</span></div>', unsafe_allow_html=True)
    st.caption("Source: project processed catalog. Visuals and summary statistics update from the included CSV; catalog labels are not predictions.")


def explorer():
    section("OBSERVATION CATALOG", "Data Explorer")
    st.caption("Search the processed dataset and narrow it by status and physical parameters. Values are reported in the source catalog units.")
    with st.container(border=True):
        a, b, c = st.columns([1.5, 1, 1])
        query = a.text_input("Search KOI, planet or host ID", placeholder="e.g. K00752 · Kepler-227 · 10797460")
        statuses = b.multiselect("Planet status", STATUS_ORDER, default=STATUS_ORDER)
        delivery = c.multiselect("Data release", sorted(DATA["koi_tce_delivname"].dropna().astype(str).unique().tolist()), default=[])
        ranges = st.columns(3)
        period_hi = float(DATA.koi_period.quantile(.99))
        prad_hi = float(DATA.koi_prad.quantile(.99))
        depth_hi = float(DATA.koi_depth.quantile(.99))
        period_range = ranges[0].slider("Orbital period · days", 0.0, period_hi, (0.0, period_hi))
        radius_range = ranges[1].slider("Planet radius · R⊕", 0.0, prad_hi, (0.0, prad_hi))
        depth_range = ranges[2].slider("Transit depth · ppm", 0.0, depth_hi, (0.0, depth_hi))
        if st.button("Reset filters", key="reset_explorer"):
            st.rerun()
    filtered = DATA[DATA[STATUS_COL].isin(statuses)].copy()
    filtered = filtered[filtered.koi_period.between(*period_range) & filtered.koi_prad.between(*radius_range) & filtered.koi_depth.between(*depth_range)]
    if delivery:
        filtered = filtered[filtered.koi_tce_delivname.astype(str).isin(delivery)]
    if query.strip():
        q = query.strip().lower()
        hit = filtered[["kepoi_name", "kepler_name", "kepid", "display_name"]].astype(str).apply(lambda col: col.str.lower().str.contains(q, regex=False)).any(axis=1)
        filtered = filtered[hit]
    st.markdown(f'<span class="badge">{len(filtered):,} MATCHING OBSERVATIONS</span>', unsafe_allow_html=True)
    show_cols = ["kepoi_name", "kepler_name", STATUS_COL, "koi_prad", "koi_period", "koi_depth", "koi_steff", "koi_srad", "kepid"]
    names = {"kepoi_name":"KOI ID", "kepler_name":"Planet name", STATUS_COL:"Status", "koi_prad":"Radius · R⊕", "koi_period":"Period · d", "koi_depth":"Depth · ppm", "koi_steff":"Star temp · K", "koi_srad":"Star radius · R☉", "kepid":"Host ID"}
    table = filtered[show_cols].rename(columns=names).sort_values("KOI ID", na_position="last")
    st.dataframe(table, hide_index=True, use_container_width=True, height=440, column_config={"Status":st.column_config.TextColumn("Status"), "Radius · R⊕":st.column_config.NumberColumn(format="%.2f"), "Period · d":st.column_config.NumberColumn(format="%.3f"), "Depth · ppm":st.column_config.NumberColumn(format="%.1f"), "Star temp · K":st.column_config.NumberColumn(format="%.0f"), "Star radius · R☉":st.column_config.NumberColumn(format="%.2f")})
    options = filtered.index.tolist()
    if options:
        selected = st.selectbox("Open observation profile", options, format_func=lambda idx: f"{filtered.loc[idx, 'kepoi_name']} · {filtered.loc[idx, 'display_name']} · {filtered.loc[idx, STATUS_COL]}")
        row = filtered.loc[selected]
        st.markdown("#### Observation profile")
        a,b,c,d = st.columns(4)
        a.metric("KOI", str(row.get("kepoi_name", "—")))
        b.metric("Disposition", str(row.get(STATUS_COL, "—")))
        c.metric("Planet radius", f"{fmt(row.get('koi_prad'), 2)} R⊕")
        d.metric("Orbital period", f"{fmt(row.get('koi_period'), 2)} d")
        st.caption(f"Host {row.get('kepid', '—')} · transit depth {fmt(row.get('koi_depth'), 1)} ppm · stellar temperature {fmt(row.get('koi_steff'), 0)} K · stellar radius {fmt(row.get('koi_srad'), 2)} R☉")
    else:
        st.info("No observations match these filters. Expand a range or reset the search.")


def exoplanet_analysis():
    section("PLANET CHARACTERISTICS", "Exoplanet Analysis")
    df = chart_controls(DATA)
    st.caption(f"{len(df):,} rows included · distributions use catalog values and omit missing measurements.")
    a,b = st.columns(2)
    for col, title, units, container in [("koi_prad","Planet radius distribution","Radius · R⊕",a),("koi_period","Orbital period distribution","Period · days",b)]:
        dat = df[col].dropna()
        dat = dat[dat <= dat.quantile(.99)] if len(dat) else dat
        fig = px.histogram(x=dat, nbins=42, labels={"x":units,"count":"Observations"}, color_discrete_sequence=["#59d6be" if col=="koi_prad" else "#78a7ff"])
        fig.update_traces(marker_line_color="#0b1725", marker_line_width=1)
        with container:
            section("DISTRIBUTION", title)
            st.plotly_chart(plotly_theme(fig), use_container_width=True, config={"displayModeBar":False})
    c,d = st.columns(2)
    sample = df.dropna(subset=["koi_prad","koi_period",STATUS_COL]).copy()
    sample = sample[(sample.koi_prad <= sample.koi_prad.quantile(.99)) & (sample.koi_period <= sample.koi_period.quantile(.99))]
    fig = px.scatter(sample, x="koi_period", y="koi_prad", color=STATUS_COL, color_discrete_map=COLORS, opacity=.7, hover_name="display_name", labels={"koi_period":"Orbital period · days","koi_prad":"Planet radius · R⊕",STATUS_COL:"Status"})
    with c:
        section("RELATIONSHIP", "Radius vs orbital period")
        st.plotly_chart(plotly_theme(fig), use_container_width=True, config={"displayModeBar":False})
    sample = df.dropna(subset=["koi_prad","koi_depth",STATUS_COL]).copy()
    sample = sample[(sample.koi_prad <= sample.koi_prad.quantile(.99)) & (sample.koi_depth <= sample.koi_depth.quantile(.99))]
    fig = px.scatter(sample, x="koi_prad", y="koi_depth", color=STATUS_COL, color_discrete_map=COLORS, opacity=.7, hover_name="display_name", labels={"koi_prad":"Planet radius · R⊕","koi_depth":"Transit depth · ppm",STATUS_COL:"Status"})
    with d:
        section("RELATIONSHIP", "Transit depth vs radius")
        st.plotly_chart(plotly_theme(fig), use_container_width=True, config={"displayModeBar":False})


def host_star_analysis():
    section("STELLAR CHARACTERISTICS", "Host Star Analysis")
    query = st.text_input("Find a host star by Kepler ID or planet name", placeholder="e.g. 10797460 or Kepler-227")
    d = DATA
    if query.strip():
        q = query.lower().strip()
        mask = d["host_id"].str.lower().str.contains(q, regex=False) | d["display_name"].str.lower().str.contains(q, regex=False)
        d = d[mask]
    if d.empty:
        st.info("No host stars found. Try a Kepler ID or KOI planet name.")
        return
    host_options = d["host_id"].dropna().unique().tolist()
    chosen = st.selectbox("Select host star", host_options, format_func=lambda x: f"Kepler ID {x}")
    star = DATA[DATA.host_id.eq(chosen)]
    confirmed = int(star[STATUS_COL].eq("CONFIRMED").sum())
    candidates = int(star[STATUS_COL].eq("CANDIDATE").sum())
    a,b,c,dcol,e = st.columns(5)
    a.metric("Observed planets", len(star)); b.metric("Confirmed", confirmed); c.metric("Candidates", candidates)
    dcol.metric("Mean planet radius", f"{fmt(star.koi_prad.mean(),2)} R⊕"); e.metric("Mean orbital period", f"{fmt(star.koi_period.mean(),1)} d")
    st.markdown(f"**Stellar profile** · {fmt(star.koi_steff.median(),0)} K · {fmt(star.koi_srad.median(),2)} R☉ · log g {fmt(star.koi_slogg.median(),2)}")
    left,right = st.columns(2)
    for col,title,unit,container in [("koi_steff","Host star temperature","Temperature · K",left),("koi_srad","Host star radius","Radius · R☉",right)]:
        fig = px.histogram(DATA.dropna(subset=[col]), x=col, nbins=40, color=STATUS_COL, barmode="overlay", opacity=.72, color_discrete_map=COLORS, labels={col:unit,STATUS_COL:"Status"})
        with container:
            section("CATALOG DISTRIBUTION", title)
            st.plotly_chart(plotly_theme(fig), use_container_width=True, config={"displayModeBar":False})
    fig = px.scatter(DATA.dropna(subset=["koi_steff","koi_prad"]), x="koi_steff", y="koi_prad", color=STATUS_COL, color_discrete_map=COLORS, opacity=.66, labels={"koi_steff":"Stellar temperature · K","koi_prad":"Planet radius · R⊕",STATUS_COL:"Status"})
    section("STELLAR / PLANETARY RELATIONSHIP", "Temperature vs planet radius")
    st.plotly_chart(plotly_theme(fig,330), use_container_width=True, config={"displayModeBar":False})
    st.markdown("**Observations in this system**")
    st.dataframe(star[["kepoi_name","kepler_name",STATUS_COL,"koi_prad","koi_period","koi_depth"]].rename(columns={"kepoi_name":"KOI","kepler_name":"Planet",STATUS_COL:"Status","koi_prad":"Radius · R⊕","koi_period":"Period · d","koi_depth":"Depth · ppm"}), hide_index=True, use_container_width=True)


def ml_prediction():
    section("CLASSIFICATION WORKFLOW", "Exoplanet Classification Engine")
    st.markdown("Estimate the likely catalog class for an observation using an illustrative prototype score. This page is not a scientific classifier; connect the team's trained model before using predictions as model output.")
    st.warning("Prototype scoring only · displayed probabilities are illustrative and must not be treated as scientific confirmation.")
    with st.form("prediction_form"):
        a,b,c = st.columns(3)
        radius = a.number_input("Planet radius · R⊕", min_value=.01, value=2.0, step=.1)
        period = b.number_input("Orbital period · days", min_value=.01, value=20.0, step=1.0)
        depth = c.number_input("Transit depth · ppm", min_value=0.0, value=500.0, step=10.0)
        d,e,f = st.columns(3)
        temp = d.number_input("Host temperature · K", min_value=100.0, value=5500.0, step=50.0)
        sradius = e.number_input("Host radius · R☉", min_value=.01, value=1.0, step=.05)
        snr = f.number_input("Model SNR", min_value=0.0, value=25.0, step=1.0)
        submitted = st.form_submit_button("Estimate class", type="primary", use_container_width=True)
    if submitted:
        # A clearly disclosed demo scoring rule, intentionally separate from any trained model.
        confirmed_score = 1.45 - .18 * abs(np.log1p(radius) - 1.0) - .12 * abs(np.log1p(period) - 3.0) + .18 * np.tanh((snr - 15) / 20) + .10 * np.tanh((depth - 300) / 800)
        fp_score = .95 * np.tanh(max(radius - 15, 0) / 15) + .65 * np.tanh(max(depth - 4000, 0) / 4000) + .15 * np.tanh(abs(temp - 5700) / 3000)
        logits = np.array([confirmed_score, .72, fp_score], dtype=float)
        probs = np.exp(logits - logits.max()); probs = probs / probs.sum()
        classes = ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
        winner = classes[int(probs.argmax())]
        st.markdown("### Prototype estimate")
        st.markdown(f'<div class="panel"><div class="eyebrow">LIKELY CLASS · DEMO SCORE</div><h2 style="font:800 1.8rem Manrope;color:#59d6be">{winner}</h2><span class="muted">Illustrative rule output only. No trained model was invoked.</span></div>', unsafe_allow_html=True)
        for name,p in zip(classes,probs):
            st.progress(float(p), text=f"{name.title()}: {p*100:.1f}%")
    st.divider()
    st.markdown("#### Team model artifacts")
    metrics = load_optional(MODEL_RESULTS_PATH)
    if not metrics.empty:
        st.caption("Reported evaluation metrics from the included member 2 model comparison file. These are project artifacts, not a guarantee of current model performance.")
        st.dataframe(metrics.style.format({c:"{:.3f}" for c in metrics.select_dtypes(include="number").columns}), hide_index=True, use_container_width=True)
    preds = load_optional(PREDICTIONS_PATH)
    if not preds.empty and "predicted_confirmed_probability" in preds:
        st.caption(f"Candidate prediction artifact: {len(preds):,} rows · shown as provided by the project package.")
        st.dataframe(preds[[c for c in ["kepoi_name","kepler_name","predicted_confirmed_probability","priority"] if c in preds]].head(8), hide_index=True, use_container_width=True)


def advanced_visualizations():
    section("EXPLORE RELATIONSHIPS", "Discover Patterns")
    numeric = [c for c in ["koi_prad","koi_period","koi_depth","koi_teq","koi_insol","koi_steff","koi_srad","koi_slogg","koi_model_snr"] if c in DATA]
    labels = {"koi_prad":"Planet radius · R⊕","koi_period":"Orbital period · days","koi_depth":"Transit depth · ppm","koi_teq":"Equilibrium temperature · K","koi_insol":"Insolation · Earth flux","koi_steff":"Host temperature · K","koi_srad":"Host radius · R☉","koi_slogg":"Stellar log g","koi_model_snr":"Transit SNR"}
    x,y,color = st.columns([1,1,1])
    xcol = x.selectbox("X-axis", numeric, index=1, format_func=lambda c:labels[c])
    ycol = y.selectbox("Y-axis", numeric, index=0, format_func=lambda c:labels[c])
    colorby = color.selectbox("Color by", [STATUS_COL,"koi_tce_delivname"], format_func=lambda c:"Planet status" if c==STATUS_COL else "Data release")
    data = DATA.dropna(subset=[xcol,ycol,colorby]).copy()
    for col in [xcol,ycol]:
        q = data[col].quantile(.99)
        data = data[data[col] <= q]
    fig = px.scatter(data, x=xcol, y=ycol, color=colorby, color_discrete_map=COLORS if colorby==STATUS_COL else None, hover_name="display_name", opacity=.65, labels={xcol:labels[xcol],ycol:labels[ycol],STATUS_COL:"Status", "koi_tce_delivname":"Data release"})
    section("PAIRWISE FEATURE VIEW", f"{labels[xcol]} × {labels[ycol]}")
    st.plotly_chart(plotly_theme(fig,430), use_container_width=True)
    left,right = st.columns([1.25,1])
    corr = DATA[numeric].corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale=[[0,"#3865a0"],[.5,"#0d1a2b"],[1,"#49cbb4"]], zmin=-1,zmax=1, labels={"color":"Correlation"})
    with left:
        section("FEATURE CORRELATION", "Catalog correlation matrix")
        st.plotly_chart(plotly_theme(fig,380), use_container_width=True, config={"displayModeBar":False})
    with right:
        section("HOW TO READ", "Correlation is not causation")
        st.markdown('<div class="panel"><p class="muted">Pearson correlations are calculated pairwise from available processed catalog values. They describe linear association in these observations and do not establish physical causation.</p><p class="muted">The scatter view trims only its visual axis extremes at the 99th percentile so the central structure remains legible. Hover a point for the planet label and disposition.</p></div>', unsafe_allow_html=True)


def about():
    section("PROJECT NOTES", "Kepler Exoplanet Search Results Analysis")
    st.markdown("Analyze Kepler observations with data preparation, exploratory analysis, planet and host-star characteristics, and a classification workflow. This capstone prototype connects those outputs in one interactive Streamlit dashboard.")
    a,b = st.columns([1,1])
    with a:
        st.markdown("#### Project modules")
        for item in ["Data preparation and quality review", "Exploratory data analysis", "ML classification artifacts", "Planet characteristic analysis", "Host star analysis", "Interactive dashboard"]:
            st.markdown(f"- {item}")
        st.markdown("#### Technology")
        st.markdown("Python · Pandas · NumPy · Plotly · Scikit-learn · Streamlit · GitHub")
    with b:
        st.markdown("#### Data flow")
        st.markdown('<div class="panel"><div class="eyebrow">PROJECT PIPELINE</div><h3>Raw Kepler catalog</h3><p class="muted">↓ cleaning and feature preparation</p><h3>Processed dataframe</h3><p class="muted">↓ EDA and model artifacts</p><h3>EXOINSIGHT dashboard</h3><p class="muted">↓ student-friendly investigation</p></div>', unsafe_allow_html=True)
        st.markdown("#### Data provenance")
        st.caption(f"Dashboard data: `{DATA_PATH.relative_to(ROOT)}` · {len(DATA):,} rows · {DATA.shape[1]} columns. Individual values and class labels come from the bundled processed CSV.")
    st.info("The prototype reads from the included processed CSV. Reusable `exoinsight` functions can be integrated behind these views as the team package evolves.")


page = sidebar()
if page == "Overview":
    overview()
elif page == "Data Explorer":
    explorer()
elif page == "Exoplanet Analysis":
    exoplanet_analysis()
elif page == "Host Star Analysis":
    host_star_analysis()
elif page == "ML Prediction":
    ml_prediction()
elif page == "Advanced Visualizations":
    advanced_visualizations()
else:
    about()
