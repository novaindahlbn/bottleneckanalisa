import streamlit as st
import pandas as pd
import re
import io
import os
import tempfile
import warnings
import traceback
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")

# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="ProcessMine — Enterprise Batch Job Analyzer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #fffdf8;
    --bg2: #f8f4ea;
    --bg3: #f1eadf;

    --border: #e6dccd;
    --border2: #d8c8b2;

    --accent: #9a6b2f;
    --accent2: #b07a36;
    --accent3: #d4a76a;

    --warn: #ffb800;
    --danger: #ff4757;

    --text: #5b4636;
    --text2: #8b7355;
    --text3: #b89b7a;

    --mono: 'Space Mono', monospace;
    --sans: 'DM Sans', sans-serif;
}
            
.block-container {
    padding-top: 1.5rem !important;
}

html, body, .stApp {
    font-family: var(--sans) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Main area */
.main .block-container {
    background: var(--bg) !important;
    padding: 2rem 2.5rem !important;
    max-width: 1400px !important;
}

/* Hide default elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── HEADER BANNER ── */
.pm-header {
    background: linear-gradient(135deg,
var(--bg) 0%,
var(--bg2) 100%);
    border: 1px solid var(--border);
box-shadow:
    0 2px 10px rgba(15, 23, 42, 0.04),
    0 1px 2px rgba(15, 23, 42, 0.06);
    border-radius: 12px;
    padding: 1.2rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.pm-title {
    font-family: var(--mono) !important;
    font-size: 1.8rem !important;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -1px;
    margin: 0;
    line-height: 1.1;
}
.pm-subtitle {
    font-size: 0.95rem;
    color: var(--text2);
    margin-top: 0.4rem;
    letter-spacing: 0.02em;
}
.pm-badge {
     display: inline-block;
    background: rgba(181,122,46,0.12);
    border: 1px solid rgba(181,122,46,0.25);
    color: var(--accent);
    font-family: var(--mono);
    font-size: 0.7rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin-right: 8px;
    letter-spacing: 0.05em;
}

/* ── SECTION HEADERS ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 2rem 0 1.2rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}
.section-num {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--accent);
    background: rgba(181,122,46,0.10);
    border: 1px solid rgba(181,122,46,0.20);
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.1em;
}
.section-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
    margin: 0;
}

/* ── METRIC CARDS ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 1rem 0;
}
.metric-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--border2); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.blue::before  { background: var(--accent); }
.metric-card.green::before { background: var(--accent3); }
.metric-card.yellow::before{ background: var(--warn); }
.metric-card.red::before   { background: var(--danger); }
.metric-label {
    font-size: 0.72rem;
    color: var(--text3);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    font-family: var(--mono);
}
.metric-value {
    font-family: var(--mono);
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--text2);
    margin-top: 0.3rem;
}

/* ── CARDS ── */
.pm-card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── STATUS PILLS ── */
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-family: var(--mono);
    font-weight: 700;
}
.pill-green  {
    background: rgba(181,122,46,0.10);
    color: var(--accent);
    border: 1px solid rgba(181,122,46,0.20);
}

.pill-blue   {
    background: rgba(212,167,106,0.14);
    color: var(--accent);
    border: 1px solid rgba(212,167,106,0.24);
}
.pill-yellow { background: rgba(255,184,0,0.12); color: var(--warn);    border: 1px solid rgba(255,184,0,0.3); }
.pill-red    { background: rgba(255,71,87,0.12);  color: var(--danger);  border: 1px solid rgba(255,71,87,0.3); }

/* ── TABLES ── */
.stDataFrame { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: white !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── INPUTS ── */
.stFileUploader > div, .stSelectbox > div, .stTextInput > div, .stTextArea > div {
    background: var(--bg3) !important;
    border-color: var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stFileUploader label, .stSelectbox label, .stTextInput label, .stTextArea label,
.stNumberInput label, .stSlider label {
    color: var(--text2) !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.03em !important;
}

/* ── EXPANDER ── */
.stExpander {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
/* Expander OPEN */
details[open] summary {
    background: var(--bg2) !important;
}

/* Text preview saat OPEN */
details[open] summary * {
    color: var(--text) !important;
}
/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 8px 8px 0 0 !important;
    gap: 24px !important;
    padding: 0.7rem 1.5rem !important;
    margin-right: 0.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    border-radius: 6px 6px 0 0 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(181,122,46,0.12) !important;
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── ALERTS ── */
.stSuccess { background: rgba(0,255,157,0.08) !important; border-color: var(--accent3) !important; border-radius: 8px !important; }
.stWarning { background: rgba(255,184,0,0.08) !important; border-color: var(--warn) !important; border-radius: 8px !important; }
.stError   { background: rgba(255,71,87,0.08)  !important; border-color: var(--danger) !important; border-radius: 8px !important; }
.stInfo    {  background: rgba(181,122,46,0.08) !important; border-color: var(--accent2) !important; border-radius: 8px !important; }

/* ── SIDEBAR STYLES ── */
.sidebar-logo {
    font-family: var(--mono);
    font-size: 1.1rem;
    color: var(--accent);
    font-weight: 700;
    letter-spacing: -0.5px;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.sidebar-section {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--text3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.6rem 0;
}
.step-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    font-size: 0.82rem;
}
.step-done   { background: rgba(0,255,157,0.08); color: var(--accent3); }
.step-active { background: rgba(181,122,46,0.12); color: var(--accent); }
.step-idle   { color: var(--text3); }

/* Progress bar custom */
.stProgress > div > div { background: linear-gradient(90deg, var(--accent2), var(--accent)) !important; border-radius: 4px !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg,
var(--bg) 0%,
var(--bg2) 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 0.5rem !important;
    box-shadow:
        0 2px 10px rgba(15, 23, 42, 0.04),
        0 1px 2px rgba(15, 23, 42, 0.06);
}

[data-testid="stFileUploader"] section:hover {
    border-color: var(--accent) !important;
}

/* Text drag and drop */
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section div,
[data-testid="stFileUploader"] label {
    color: var(--text) !important;
}

/* Browse button ONLY */
[data-testid="stFileUploader"] section button {
    background: #9a6b2f !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

[data-testid="stFileUploader"] section button:hover {
    background: #7c5422 !important;
}

            
/* Uploaded file area */
[data-testid="stFileUploaderFile"] {
    background: #f8f4ea !important;

    border: 1px solid #ebe7df !important;

    border-radius: 14px !important;

    padding: 0.85rem 1rem !important;

    box-shadow:
        0 1px 3px rgba(0,0,0,0.04);
}

/* Hilangkan background abu bawaan */
[data-testid="stFileUploaderFileData"] {
    background: transparent !important;
}

/* Nama file */
[data-testid="stFileUploaderFileName"] {
    color: var(--text) !important;

    font-weight: 500 !important;

    font-size: 0.95rem !important;
}

/* File size */
[data-testid="stFileUploaderFileSize"] {
    color: var(--text2) !important;
}

/* Semua text di uploader */
[data-testid="stFileUploaderFile"] * {
    color: var(--text) !important;
}

/* Icon file */
[data-testid="stFileUploaderFile"] svg {
    color: #9a6b2f !important;
}

/* Tombol X */
[data-testid="stFileUploaderDeleteBtn"] {
    border-radius: 0 !important;

    background: transparent !important;

    padding: 0 !important;

    width: auto !important;
    height: auto !important;

    min-width: unset !important;
}

/* Icon X */
[data-testid="stFileUploaderDeleteBtn"] svg {
    color: var(--accent) !important;

    width: 18px !important;
    height: 18px !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def parse_log_with_mapping(log_text: str, mapping: list[dict]) -> pd.DataFrame:
    """
    Generic log parser. mapping = [{'keyword': '...', 'activity': '...'}, ...]
    Automatically detects case boundaries using configurable begin/end keywords.
    """
    time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[,.]?\d*)")

    # Sort mapping: longer keywords first to avoid partial matches
    sorted_mapping = sorted(
        mapping, key=lambda x: len(x.get("keyword", "0")), reverse=True
    )

    begin_kw = next(
        (m["keyword"] for m in mapping if m["activity"] == "Start Batch"), "BEGIN"
    )
    end_kw = next(
        (m["keyword"] for m in mapping if m["activity"] == "End Process"), "END"
    )
    case_kw = next(
        (m.get("case_keyword", "") for m in mapping if m.get("case_keyword")), ""
    )
    case_pat = re.compile(m.get("case_pattern", r"([A-Z0-9_]+)")) if case_kw else None

    events = []
    current_case_id = None
    case_counter = 0
    temp_events = []
    seen_flags = {}  # for dedup per case

    lines = log_text.splitlines()

    for line in lines:
        # Skip noise lines
        if any(skip in line for skip in [" at ", "parameters:", "Caused by:", "\tat "]):
            continue

        m_time = time_pattern.search(line)
        if not m_time:
            continue

        raw_ts = m_time.group(1).replace(",", ".")
        try:
            # Try multiple formats
            for fmt in [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
            ]:
                try:
                    ts = datetime.strptime(raw_ts[:26], fmt)
                    break
                except:
                    continue
            else:
                continue
        except:
            continue

        # Detect case start
        if begin_kw and begin_kw in line:
            case_counter += 1
            current_case_id = f"CASE_{case_counter:05d}"
            seen_flags = {}
            temp_events = []

        if current_case_id is None:
            continue

        # Try to extract a more meaningful case ID if case_keyword is configured
        if case_kw and case_kw in line and case_pat:
            m_case = case_pat.search(line)
            if m_case:
                current_case_id = f"{m_case.group(1)}_{case_counter:05d}"
                # Backfill
                for ev in temp_events:
                    ev["case:concept:name"] = current_case_id

        # Match activity
        matched_activity = None
        for rule in sorted_mapping:
            kw = rule.get("keyword", "")
            act = rule.get("activity", "")
            dedup = rule.get("dedup", False)

            if kw and kw in line:
                if dedup:
                    if act in seen_flags:
                        break
                    seen_flags[act] = True
                matched_activity = act
                break

        if matched_activity:
            ev = {
                "case:concept:name": current_case_id,
                "concept:name": matched_activity,
                "time:timestamp": ts,
            }
            events.append(ev)
            temp_events.append(ev)

    if not events:
        return pd.DataFrame()

    df = pd.DataFrame(events)
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    df = df.sort_values(["case:concept:name", "time:timestamp"]).reset_index(drop=True)
    return df


def compute_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Add duration_ms = inter-event time within each case."""
    df = df.copy().sort_values(["case:concept:name", "time:timestamp"])
    df["next_ts"] = df.groupby("case:concept:name")["time:timestamp"].shift(-1)
    df["duration_ms"] = (df["next_ts"] - df["time:timestamp"]).dt.total_seconds() * 1000
    df = df.dropna(subset=["duration_ms"])
    # Remove extreme outliers (>P99)
    q99 = df["duration_ms"].quantile(0.99)
    df = df[df["duration_ms"] <= q99].copy()
    return df


def compute_bottleneck_table(
    df_dur: pd.DataFrame, exclude_activities: list = None
) -> pd.DataFrame:
    """Compute per-activity performance metrics."""
    # Default exclude start/end markers, bisa di-override dari luar
    default_exclude = ["Start Batch", "End Process", "End Batch", "Start Process"]
    all_exclude = list(set(default_exclude + (exclude_activities or [])))
    df_f = df_dur[~df_dur["concept:name"].isin(all_exclude)]

    grp = (
        df_f.groupby("concept:name")["duration_ms"]
        .agg(
            frekuensi="count",
            total_waktu="sum",
            rata_rata="mean",
            median="median",
            p95=lambda x: x.quantile(0.95),
            maks="max",
        )
        .reset_index()
    )

    grp["pct_total"] = (grp["total_waktu"] / grp["total_waktu"].sum() * 100).round(1)
    grp["variasi"] = grp["maks"] - grp["median"]
    grp = grp.sort_values("total_waktu", ascending=False).reset_index(drop=True)
    grp.index = grp.index + 1

    # Format numerics
    for col in ["total_waktu", "rata_rata", "median", "p95", "maks", "variasi"]:
        grp[col] = grp[col].round(1)

    return grp


def compute_transition_delay(df_dur: pd.DataFrame) -> pd.DataFrame:
    df_s = df_dur.sort_values(["case:concept:name", "time:timestamp"]).copy()
    df_s["next_act"] = df_s.groupby("case:concept:name")["concept:name"].shift(-1)
    df_s = df_s.dropna(subset=["next_act"])
    df_s["transition"] = df_s["concept:name"] + " → " + df_s["next_act"]
    result = (
        df_s.groupby("transition")["duration_ms"]
        .agg(
            frekuensi="count",
            rata_rata="mean",
            median="median",
            p95=lambda x: x.quantile(0.95),
        )
        .reset_index()
    )
    result = result.sort_values("rata_rata", ascending=False).reset_index(drop=True)
    result.index = result.index + 1
    for col in ["rata_rata", "median", "p95"]:
        result[col] = result[col].round(1)
    return result


def make_plotly_bar(df, x_col, y_col, title, color="#00d4ff", h=400):
    df_plot = df.head(10).copy()
    fig = go.Figure(
        go.Bar(
            x=df_plot[x_col],
            y=df_plot[y_col].str[:35]
            + ("…" if df_plot[y_col].str.len().max() > 35 else ""),
            orientation="h",
            marker=dict(
                color=df_plot[x_col],
                colorscale=[[0, "#E8DDD0"], [0.5, "#C4872F"], [1, "#B57A2E"]],
                showscale=False,
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=df_plot[x_col].round(1).astype(str),
            textposition="outside",
            textfont=dict(family="Space Mono", size=11, color="#5B4636"),
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(family="DM Sans", size=14, color="#5B4636")),
        paper_bgcolor="#F5F1EB",
        plot_bgcolor="#F5F1EB",
        font=dict(family="DM Sans", color="#5B4636"),
        height=h,
        yaxis=dict(
            autorange="reversed",
            gridcolor="#D6C2A8",
            tickfont=dict(size=11, family="Space Mono"),
        ),
        xaxis=dict(gridcolor="#D6C2A8", tickfont=dict(size=10)),
        margin=dict(l=10, r=80, t=40, b=20),
    )
    return fig


def fitness_gauge(value: float, label: str):

    percent = round(value * 100, 1)

    if value >= 0.8:
        color = "#B57A2E"
        status = "Excellent"
    elif value >= 0.5:
        color = "#D4A76A"
        status = "Moderate"
    else:
        color = "#D9534F"
        status = "Low"

    fig = go.Figure()

    # Progress bar
    fig.add_trace(
        go.Bar(
            x=[percent],
            y=[""],
            orientation="h",
            marker=dict(color=color, line=dict(color=color)),
            width=0.35,
            text=f"{percent}%",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(family="Space Mono", size=18, color="white"),
            hoverinfo="skip",
        )
    )

    # Background bar
    fig.add_trace(
        go.Bar(
            x=[100 - percent],
            y=[""],
            orientation="h",
            marker=dict(color="#E8DDD0"),
            width=0.35,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        barmode="stack",
        title=dict(
            text=label, font=dict(family="DM Sans", size=18, color="#5B4636"), x=0
        ),
        paper_bgcolor="#F5F1EB",
        plot_bgcolor="#F5F1EB",
        font=dict(family="DM Sans", color="#5B4636"),
        xaxis=dict(
            range=[0, 100], showgrid=False, showticklabels=False, zeroline=False
        ),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        annotations=[
            dict(
                text=status,
                x=100,
                y=0,
                showarrow=False,
                font=dict(size=14, color=color, family="DM Sans"),
                xanchor="right",
            )
        ],
        height=180,
        margin=dict(t=60, b=20, l=20, r=20),
        showlegend=False,
    )

    return fig


def run_conformance(df: pd.DataFrame, bpmn_bytes):
    """Run conformance checking using pm4py."""
    import pm4py
    from pm4py.objects.log.util import dataframe_utils

    df_pm = df[["case:concept:name", "concept:name", "time:timestamp"]].copy()
    df_pm = pm4py.format_dataframe(
        df_pm,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    log = pm4py.convert_to_event_log(df_pm)

    # Load BPMN
    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as f:
        f.write(bpmn_bytes)
        bpmn_path = f.name

    bpmn = pm4py.read_bpmn(bpmn_path)
    os.unlink(bpmn_path)
    net, im, fm = pm4py.convert_to_petri_net(bpmn)

    # Fitness
    fitness = pm4py.fitness_token_based_replay(log, net, im, fm)

    # FIX: Normalize perc_fit_traces — handle berbagai key & format pm4py
    raw_pct = (
        fitness.get("perc_fit_traces")
        or fitness.get("percentage_of_fitting_traces")
        or fitness.get("percFitTraces")
        or 0
    )
    fitness["perc_fit_traces"] = raw_pct  # pastikan key ini selalu ada & benar

    # Precision
    try:
        precision = pm4py.precision_token_based_replay(log, net, im, fm)
    except:
        try:
            precision = pm4py.precision_alignments(log, net, im, fm)
        except:
            precision = None

    # Alignments / deviations
    try:
        aligned = pm4py.conformance_diagnostics_alignments(log, net, im, fm)
        deviations = {}
        for trace_result in aligned:
            for move in trace_result.get("alignment", []):
                log_m, model_m = move
                if log_m == ">>" or model_m == ">>":
                    key = f"log: {log_m}  |  model: {model_m}"
                    deviations[key] = deviations.get(key, 0) + 1
        sorted_dev = sorted(deviations.items(), key=lambda x: x[1], reverse=True)
    except:
        sorted_dev = []

    return fitness, precision, sorted_dev


def run_discovery_viz(df: pd.DataFrame):
    """Run Heuristic Miner and return figure bytes."""
    import pm4py
    from pm4py.visualization.heuristics_net import visualizer as hn_viz

    df_pm = df[["case:concept:name", "concept:name", "time:timestamp"]].copy()
    df_pm = pm4py.format_dataframe(
        df_pm,
        case_id="case:concept:name",
        activity_key="concept:name",
        timestamp_key="time:timestamp",
    )
    log = pm4py.convert_to_event_log(df_pm)

    heu_net = pm4py.discover_heuristics_net(
        log,
        dependency_threshold=st.session_state.get("dep_thresh", 0.8),
        and_threshold=st.session_state.get("and_thresh", 0.65),
        loop_two_threshold=0.5,
    )

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        out_path = f.name

    gviz = hn_viz.apply(
        heu_net, parameters={hn_viz.Variants.PYDOTPLUS.value.Parameters.FORMAT: "png"}
    )
    hn_viz.save(gviz, out_path)

    with open(out_path, "rb") as f:
        img_bytes = f.read()
    os.unlink(out_path)
    return img_bytes


def get_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Get process variants with frequency."""
    variants = df.groupby("case:concept:name")["concept:name"].apply(
        lambda x: " → ".join(x.tolist())
    )
    vc = variants.value_counts().reset_index()
    vc.columns = ["Variant Path", "Frequency"]
    vc["%"] = (vc["Frequency"] / vc["Frequency"].sum() * 100).round(1)
    vc.index = vc.index + 1
    return vc


def generate_bpi_recommendations(
    bottleneck_df: pd.DataFrame, deviations: list, fitness: float
) -> pd.DataFrame:
    """Auto-generate BPI recommendations based on analysis results."""
    recs = []

    # From bottleneck
    if not bottleneck_df.empty:
        top3 = bottleneck_df.head(3)
        for _, row in top3.iterrows():
            act = row["concept:name"]
            mean_ms = row["rata_rata"]
            p95_ms = row["p95"]
            volatility = (p95_ms - row["median"]) / (row["median"] + 1)

            if volatility > 3:
                tech = f"Aktivitas '{act}' memiliki variasi tinggi (P95/Median ratio: {volatility:.1f}x). Rekomendasikan: implementasi timeout + retry mechanism, tambahkan index pada kolom yang sering di-query."
                biz = f"Evaluasi SLA untuk aktivitas '{act}'. Tetapkan threshold maksimum {int(p95_ms/1000)}s dan lakukan monitoring alert jika terlampaui."
            elif mean_ms > 5000:
                tech = f"Aktivitas '{act}' rata-rata membutuhkan {mean_ms/1000:.1f}s per eksekusi. Rekomendasikan: query optimization (EXPLAIN ANALYZE), connection pooling, atau caching hasil query yang statis."
                biz = f"Pertimbangkan pemindahan aktivitas '{act}' ke off-peak hours atau implementasi asynchronous processing untuk mengurangi dampak pada throughput sistem."
            else:
                tech = f"Aktivitas '{act}' berkontribusi tinggi pada total waktu kumulatif. Rekomendasikan: batch processing optimization, pre-fetching data, atau parallelisasi jika memungkinkan."
                biz = f"Review frekuensi eksekusi aktivitas '{act}'. Pertimbangkan apakah semua eksekusi diperlukan atau dapat digabung untuk mengurangi overhead."

            recs.append(
                {
                    "Prioritas": "🔴 Tinggi" if len(recs) == 0 else "🟡 Sedang",
                    "Aktivitas / Area": act,
                    "Dimensi": "Bottleneck (Waktu)",
                    "Rekomendasi Teknis": tech,
                    "Rekomendasi Bisnis": biz,
                }
            )

    # From fitness
    if fitness is not None:
        fit_val = (
            fitness.get("average_trace_fitness", 0) if isinstance(fitness, dict) else 0
        )
        if fit_val < 0.8:
            recs.append(
                {
                    "Prioritas": "🔴 Tinggi",
                    "Aktivitas / Area": "Alur Proses Keseluruhan",
                    "Dimensi": "Conformance (Fitness)",
                    "Rekomendasi Teknis": f"Nilai fitness {fit_val:.2f} di bawah threshold 0.80. Update model BPMN untuk mencerminkan alur aktual sistem, atau perbaiki sistem agar mengikuti BPMN yang telah ditetapkan.",
                    "Rekomendasi Bisnis": "Lakukan workshop bersama tim IT dan bisnis untuk menyelaraskan SOP (BPMN) dengan implementasi aktual sistem. Dokumentasikan deviasi yang ditemukan sebagai perubahan SOP resmi.",
                }
            )

    # From deviations
    if deviations and len(deviations) > 0:
        top_dev = deviations[0]
        recs.append(
            {
                "Prioritas": "🟡 Sedang",
                "Aktivitas / Area": "Deviasi Proses",
                "Dimensi": "Conformance (Deviasi)",
                "Rekomendasi Teknis": f"Deviasi paling sering: '{top_dev[0]}' ({top_dev[1]}x). Rekomendasikan: review source code untuk memastikan setiap aktivitas yang terdefinisi dalam BPMN terimplementasi dengan benar.",
                "Rekomendasi Bisnis": "Perbarui dokumentasi BPMN secara berkala (minimal per kuartal) untuk menjaga kesesuaian dengan implementasi sistem yang terus berkembang.",
            }
        )

    # General recommendation
    recs.append(
        {
            "Prioritas": "🟢 Rendah",
            "Aktivitas / Area": "Monitoring & Observability",
            "Dimensi": "Enhancement Umum",
            "Rekomendasi Teknis": "Implementasi real-time performance monitoring pada setiap aktivitas batch job menggunakan APM tools (contoh: Grafana + Prometheus). Log duration per aktivitas secara eksplisit.",
            "Rekomendasi Bisnis": "Tetapkan KPI performa batch job (misal: P95 duration < X detik) dan lakukan review berkala terhadap tren kinerja untuk deteksi dini degradasi performa.",
        }
    )

    return pd.DataFrame(recs)


def export_summary_csv(
    stats: dict,
    bottleneck_df: pd.DataFrame,
    transition_df: pd.DataFrame,
    bpi_df: pd.DataFrame,
) -> bytes:
    output = io.StringIO()
    output.write("=== PROCESSMINE ANALYSIS SUMMARY ===\n\n")
    output.write("--- EVENT LOG STATISTICS ---\n")
    for k, v in stats.items():
        output.write(f"{k},{v}\n")
    output.write("\n--- TOP BOTTLENECK ACTIVITIES ---\n")
    bottleneck_df.head(10).to_csv(output, index=True)
    output.write("\n--- TOP TRANSITION DELAYS ---\n")
    transition_df.head(10).to_csv(output, index=True)
    output.write("\n--- BPI RECOMMENDATIONS ---\n")
    bpi_df.to_csv(output, index=False)
    return output.getvalue().encode()


# ═══════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════

defaults = {
    "df_raw": None,
    "df_clean": None,
    "df_dur": None,
    "mapping": [],
    "log_stats": {},
    "bottleneck_df": None,
    "transition_df": None,
    "fitness": None,
    "precision": None,
    "deviations": [],
    "discovery_img": None,
    "bpi_df": None,
    "step": 0,  # 0=upload, 1=mapping, 2=parsed, 3=analyzed
    "dep_thresh": 0.8,
    "and_thresh": 0.65,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

# with st.sidebar:
#     st.markdown('<div class="sidebar-logo">⬡ ProcessMine</div>', unsafe_allow_html=True)

#     st.markdown('<div class="sidebar-section">PIPELINE STATUS</div>', unsafe_allow_html=True)

#     steps = [
#         (0, "01 — Upload Log File"),
#         (1, "02 — Configure Mapping"),
#         (2, "03 — Parse & Preview"),
#         (3, "04 — Run Analysis"),
#     ]
#     current = st.session_state.step
#     for idx, label in steps:
#         if idx < current:
#             cls = 'step-done'; icon = '✓'
#         elif idx == current:
#             cls = 'step-active'; icon = '▶'
#         else:
#             cls = 'step-idle'; icon = '○'
#         st.markdown(f'<div class="step-indicator {cls}">{icon} &nbsp;{label}</div>', unsafe_allow_html=True)

#     st.markdown('<div class="sidebar-section">DISCOVERY PARAMS</div>', unsafe_allow_html=True)
#     st.session_state.dep_thresh = st.slider("Dependency Threshold", 0.1, 1.0, 0.8, 0.05,
#         help="Min dependency strength to show an edge. Higher = simpler model.")
#     st.session_state.and_thresh = st.slider("AND Threshold", 0.1, 1.0, 0.65, 0.05,
#         help="Threshold for AND-split/join detection.")

#     st.markdown('<div class="sidebar-section">ABOUT</div>', unsafe_allow_html=True)
#     st.markdown("""<div style="font-size:0.78rem; color:#4a6278; line-height:1.6;">
#         Generic Process Mining Tool for Enterprise Batch Jobs.<br><br>
#         Supports any log format via configurable keyword mapping.<br><br>
#         Built with PM4Py + Streamlit.
#     </div>""", unsafe_allow_html=True)

#     if st.session_state.step >= 2 and st.session_state.df_clean is not None:
#         st.markdown('<div class="sidebar-section">QUICK STATS</div>', unsafe_allow_html=True)
#         s = st.session_state.log_stats
#         for label, val in [("Cases", s.get('total_cases','-')), ("Events", s.get('total_events','-')), ("Activities", s.get('unique_activities','-'))]:
#             st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #1e2a38;">
#                 <span style="font-size:0.78rem;color:#4a6278;">{label}</span>
#                 <span style="font-family:Space Mono;font-size:0.82rem;color:#00d4ff;">{val}</span>
#             </div>""", unsafe_allow_html=True)

#     if st.session_state.step >= 3:
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("🔄  Reset All"):
#             for k, v in defaults.items():
#                 st.session_state[k] = v
#             st.rerun()


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="pm-header">
    <p class="pm-title">Analisa Confermance Checking dan Deteksi Bottleneck</p>
    <p class="pm-subtitle">Enterprise Batch Job — Process Mining & BPI Dashboard</p>
    
</div>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════
# STEP 0: UPLOAD
# ═══════════════════════════════════════════════════════════════

st.markdown(
    """<div class="section-header">  
    <span class="section-title">Upload Event Log</span>
</div>""",
    unsafe_allow_html=True,
)

# col_up1, col_up2 = st.columns([2, 1])

# with col_up1:
#     uploaded_log = st.file_uploader(
#         "Upload file log (.txt, .log, .csv)",
#         type=['txt','log','csv'],
#         help="Upload raw log file dari sistem backend. Bisa dari job apapun."
#     )
uploaded_log = st.file_uploader(
    "Upload file log (.txt, .log, .csv)",
    type=["txt", "log", "csv"],
    help="Upload raw log file dari sistem backend. Bisa dari job apapun.",
)

st.markdown(
    """
    </div>
</div>
""",
    unsafe_allow_html=True,
)
# with col_up2:
#     st.markdown("""<div class="pm-card" style="height:100%;">
#         <div style="font-size:0.75rem;color:#4a6278;font-family:Space Mono;letter-spacing:0.05em;margin-bottom:0.8rem;">FORMAT YANG DIDUKUNG</div>
#         <div style="font-size:0.82rem;color:#8fa3bc;line-height:1.8;">
#         ✓ &nbsp;Raw text log (Java/Spring)<br>
#         ✓ &nbsp;Structured log (.log)<br>
#         ✓ &nbsp;CSV event log<br>
#         ✓ &nbsp;Any timestamp-based log
#         </div>
#     </div>""", unsafe_allow_html=True)

if uploaded_log:
    raw_bytes = uploaded_log.read()
    try:
        log_text = raw_bytes.decode("utf-8")
    except:
        log_text = raw_bytes.decode("latin-1")

    st.session_state["log_text"] = log_text

    # CSV path: auto-parse
    if uploaded_log.name.endswith(".csv"):
        try:
            df_csv = pd.read_csv(io.StringIO(log_text))
            # Try to auto-detect columns
            cols = df_csv.columns.str.lower().tolist()
            case_col = next(
                (
                    c
                    for c in df_csv.columns
                    if any(k in c.lower() for k in ["case", "id", "batch"])
                ),
                df_csv.columns[0],
            )
            act_col = next(
                (
                    c
                    for c in df_csv.columns
                    if any(
                        k in c.lower() for k in ["activity", "event", "action", "name"]
                    )
                ),
                df_csv.columns[1] if len(df_csv.columns) > 1 else df_csv.columns[0],
            )
            ts_col = next(
                (
                    c
                    for c in df_csv.columns
                    if any(k in c.lower() for k in ["time", "timestamp", "date", "ts"])
                ),
                df_csv.columns[2] if len(df_csv.columns) > 2 else df_csv.columns[0],
            )

            df_csv = df_csv.rename(
                columns={
                    case_col: "case:concept:name",
                    act_col: "concept:name",
                    ts_col: "time:timestamp",
                }
            )
            df_csv["time:timestamp"] = pd.to_datetime(
                df_csv["time:timestamp"], errors="coerce"
            )
            df_csv = df_csv.dropna(
                subset=["case:concept:name", "concept:name", "time:timestamp"]
            )
            df_csv = df_csv.sort_values(
                ["case:concept:name", "time:timestamp"]
            ).reset_index(drop=True)
            st.session_state.df_raw = df_csv
            st.session_state.step = 2
            st.success(
                f"✓ CSV parsed: {len(df_csv)} events, {df_csv['case:concept:name'].nunique()} cases"
            )
        except Exception as e:
            st.error(f"CSV parse error: {e}")
    else:
        st.session_state.step = max(st.session_state.step, 1)
        # Preview
        with st.expander("👁  Preview Log File (first 30 lines)", expanded=False):
            preview_lines = log_text.splitlines()[:30]
            st.code("\n".join(preview_lines), language="text")
        st.success(
            f"✓ File loaded: **{uploaded_log.name}** ({len(log_text):,} characters, {len(log_text.splitlines()):,} lines)"
        )


# ═══════════════════════════════════════════════════════════════
# STEP 1: MAPPING CONFIGURATION
# ═══════════════════════════════════════════════════════════════

if st.session_state.step >= 1 and not (
    uploaded_log and uploaded_log.name.endswith(".csv")
):
    st.markdown(
        """<div class="section-header">
        <span class="section-title">Configure Activity Mapping</span>
    </div>""",
        unsafe_allow_html=True,
    )

    # st.markdown("""<div class="pm-card">
    #     <div style="font-size:0.85rem;color:#8fa3bc;line-height:1.7;">
    #     Define how keywords in your log file map to activity names.
    #     This makes ProcessMine work with <b style="color:#00d4ff;">any batch job</b> — not just one specific system.<br>
    #     <span style="color:#4a6278;font-size:0.78rem;">💡 Tip: Keywords are matched in order — put more specific keywords first.</span>
    #     </div>
    # </div>""", unsafe_allow_html=True)

    tab_manual, tab_upload, tab_template = st.tabs(["Manual Entry", "   ", "   "])

    with tab_template:
        st.markdown("**Available Templates:**")
        col_t1, col_t2, col_t3 = st.columns(3)

        template_repayment = [
            {"keyword": "BEGIN", "activity": "Start Batch", "dedup": False},
            {
                "keyword": "File name timestamp",
                "activity": "Get File Name",
                "dedup": False,
            },
            {"keyword": "batchMode", "activity": "Check Batch Mode", "dedup": False},
            {
                "keyword": "No repayment files found",
                "activity": "No File Found",
                "dedup": False,
            },
            {"keyword": "File get", "activity": "Download File", "dedup": False},
            {
                "keyword": "Processing repayment",
                "activity": "Process Repayment File",
                "dedup": False,
            },
            {
                "keyword": "Populate applicationNumbers",
                "activity": "Extract App Number",
                "dedup": False,
            },
            {"keyword": "There are", "activity": "Count Data", "dedup": False},
            {"keyword": "CreateLoan", "activity": "Get Loan Data", "dedup": False},
            {
                "keyword": "applicationNumbersIDV",
                "activity": "Split IDV & BU",
                "dedup": False,
            },
            {
                "keyword": "RealizationCoBorrowing",
                "activity": "Get Realization",
                "dedup": False,
            },
            {
                "keyword": "PartnerFeedBackFile",
                "activity": "Get Partner Feedback",
                "dedup": False,
            },
            {
                "keyword": "NotifikasiData",
                "activity": "Get Notification",
                "dedup": False,
            },
            {
                "keyword": "existingRepaymentFiles",
                "activity": "Check Existing Data",
                "dedup": False,
            },
            {
                "keyword": "SELECT batchNumber",
                "activity": "Generate Batch Number",
                "dedup": False,
            },
            {
                "keyword": "Populate repayments",
                "activity": "Populate Repayments",
                "dedup": False,
            },
            {"keyword": "Processing", "activity": "Process Data", "dedup": False},
            {
                "keyword": "DELETE FROM RepaymentFile",
                "activity": "Delete Old Data",
                "dedup": False,
            },
            {
                "keyword": "INSERT INTO RepaymentFile",
                "activity": "Insert Data",
                "dedup": False,
            },
            {"keyword": "Total files processed", "activity": "Summary", "dedup": False},
            {
                "keyword": "saveMonitoringDetail",
                "activity": "Save Monitoring",
                "dedup": False,
            },
            {
                "keyword": "NOTIF NUMBER",
                "activity": "Process Notification",
                "dedup": True,
            },
            {"keyword": "END", "activity": "End Process", "dedup": False},
        ]

        template_generic = [
            {"keyword": "START", "activity": "Start Job", "dedup": False},
            {"keyword": "INIT", "activity": "Initialize", "dedup": False},
            {"keyword": "FETCH", "activity": "Fetch Data", "dedup": False},
            {"keyword": "VALIDATE", "activity": "Validate Data", "dedup": False},
            {"keyword": "PROCESS", "activity": "Process Data", "dedup": False},
            {"keyword": "INSERT", "activity": "Insert Data", "dedup": False},
            {"keyword": "COMPLETE", "activity": "Complete Job", "dedup": False},
            {"keyword": "END", "activity": "End Job", "dedup": False},
        ]

        with col_t1:
            if st.button("📁  Repayment Job Template", use_container_width=True):
                st.session_state.mapping = template_repayment
                st.success("✓ Repayment template loaded!")
        with col_t2:
            if st.button("📁  Generic Batch Template", use_container_width=True):
                st.session_state.mapping = template_generic
                st.success("✓ Generic template loaded!")
        with col_t3:
            tpl_df = pd.DataFrame(
                [
                    {
                        "keyword": "YOUR_KEYWORD",
                        "activity": "Activity Name",
                        "dedup": False,
                    }
                ]
            )
            csv_tpl = tpl_df.to_csv(index=False).encode()
            st.download_button(
                "⬇️  Download CSV Template",
                csv_tpl,
                "mapping_template.csv",
                "text/csv",
                use_container_width=True,
            )

    with tab_upload:
        mapping_file = st.file_uploader(
            "Upload mapping CSV (columns: keyword, activity, dedup)",
            type=["csv"],
            key="mapping_upload",
        )
        if mapping_file:
            try:
                df_map = pd.read_csv(mapping_file)
                if "keyword" not in df_map.columns or "activity" not in df_map.columns:
                    st.error("CSV must have 'keyword' and 'activity' columns.")
                else:
                    if "dedup" not in df_map.columns:
                        df_map["dedup"] = False
                    st.session_state.mapping = df_map.to_dict("records")
                    st.success(
                        f"✓ Loaded {len(st.session_state.mapping)} mapping rules"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

    with tab_manual:
        st.markdown(
            '<div style="font-size:0.82rem;color:#4a6278;margin-bottom:0.8rem;">Add mapping rules manually. Each rule maps a keyword in the log to an activity name.</div>',
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns([3, 3, 1, 1])
        with c1:
            new_kw = st.text_input(
                "Keyword (substring in log line)",
                key="new_kw",
                placeholder="e.g. BEGIN",
            )
        with c2:
            new_act = st.text_input(
                "Activity Name", key="new_act", placeholder="e.g. Start Batch"
            )
        with c3:
            new_dd = st.checkbox(
                "Dedup", key="new_dd", help="Only record this activity once per case"
            )
        with c4:
            st.write("")
            st.write("")
            if st.button("+ Add", use_container_width=True):
                if new_kw and new_act:
                    st.session_state.mapping.append(
                        {"keyword": new_kw, "activity": new_act, "dedup": new_dd}
                    )
                    st.rerun()

        if st.session_state.mapping:
            df_m = pd.DataFrame(st.session_state.mapping)
            st.dataframe(df_m, use_container_width=True, height=200)
            cols_m = st.columns([5, 1])
            with cols_m[1]:
                if st.button("🗑  Clear All"):
                    st.session_state.mapping = []
                    st.rerun()

    # PARSE BUTTON
    st.markdown("<br>", unsafe_allow_html=True)
    col_parse1, col_parse2, _ = st.columns([1, 2, 3])
    with col_parse2:
        if st.button("▶  PARSE EVENT LOG", use_container_width=True):
            if not st.session_state.mapping:
                st.error("Please configure at least one mapping rule first.")
            elif "log_text" not in st.session_state:
                st.error("Please upload a log file first.")
            else:
                with st.spinner("Parsing log file..."):
                    try:
                        df_raw = parse_log_with_mapping(
                            st.session_state.log_text, st.session_state.mapping
                        )
                        if df_raw.empty:
                            st.error(
                                "No events could be extracted. Check your keyword mapping."
                            )
                        else:
                            st.session_state.df_raw = df_raw
                            st.session_state.step = 2
                            st.rerun()
                    except Exception as e:
                        st.error(f"Parse error: {e}\n{traceback.format_exc()}")


# ═══════════════════════════════════════════════════════════════
# STEP 2: PREVIEW & STATS
# ═══════════════════════════════════════════════════════════════

if st.session_state.step >= 2 and st.session_state.df_raw is not None:
    df = st.session_state.df_raw.copy()

    # Compute stats
    n_cases = df["case:concept:name"].nunique()
    n_events = len(df)
    n_acts = df["concept:name"].nunique()
    avg_acts = round(n_events / n_cases, 1) if n_cases else 0
    ts_min = df["time:timestamp"].min()
    ts_max = df["time:timestamp"].max()

    st.session_state.df_clean = df
    st.session_state.log_stats = {
        "total_cases": n_cases,
        "total_events": n_events,
        "unique_activities": n_acts,
        "avg_acts_per_case": avg_acts,
        "date_start": str(ts_min.date()),
        "date_end": str(ts_max.date()),
    }

    st.markdown(
        """<div class="section-header">
        <span class="section-title">Event Log Preview & Statistics</span>
    </div>""",
        unsafe_allow_html=True,
    )

    # Metric cards
    st.markdown(
        f"""<div class="metric-grid">
        <div class="metric-card blue">
            <div class="metric-label">Total Cases</div>
            <div class="metric-value">{n_cases:,}</div>
            <div class="metric-sub">unique executions</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Total Events</div>
            <div class="metric-value">{n_events:,}</div>
            <div class="metric-sub">log entries parsed</div>
        </div>
        <div class="metric-card yellow">
            <div class="metric-label">Activity Types</div>
            <div class="metric-value">{n_acts}</div>
            <div class="metric-sub">unique activities</div>
        </div>
        <div class="metric-card blue">
            <div class="metric-label">Avg Events/Case</div>
            <div class="metric-value">{avg_acts}</div>
            <div class="metric-sub">activities per run</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Observation Start</div>
            <div class="metric-value" style="font-size:1.1rem;">{ts_min.strftime('%d %b %Y')}</div>
            <div class="metric-sub">{ts_min.strftime('%H:%M:%S')}</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Observation End</div>
            <div class="metric-value" style="font-size:1.1rem;">{ts_max.strftime('%d %b %Y')}</div>
            <div class="metric-sub">{ts_max.strftime('%H:%M:%S')}</div>
        </div>
    </div>""",
        unsafe_allow_html=True,
    )

    # Preview tabs
    tab_prev1, tab_prev2, tab_prev3 = st.tabs(
        ["  Event Log Table", "  Activity Distribution", " "]
    )

    with tab_prev1:
        st.dataframe(df.head(200), use_container_width=True, height=300)
        st.caption(f"Showing first 200 of {n_events:,} events")

    with tab_prev2:
        act_counts = df["concept:name"].value_counts().reset_index()
        act_counts.columns = ["Activity", "Count"]
        fig_act = make_plotly_bar(
            act_counts,
            "Count",
            "Activity",
            "Activity Frequency Distribution",
            h=max(300, min(600, len(act_counts) * 28)),
        )
        st.plotly_chart(fig_act, use_container_width=True)

    with tab_prev3:
        ts_daily = df.groupby(df["time:timestamp"].dt.date).size().reset_index()
        ts_daily.columns = ["Date", "Event Count"]
        fig_ts = px.area(
            ts_daily,
            x="Date",
            y="Event Count",
            title="Daily Event Volume",
            color_discrete_sequence=["#00d4ff"],
        )
        fig_ts.update_layout(
            paper_bgcolor="#151b24",
            plot_bgcolor="#151b24",
            font=dict(family="DM Sans", color="#8fa3bc"),
            title_font=dict(size=14, color="#e2eaf4"),
            xaxis=dict(gridcolor="#1e2a38"),
            yaxis=dict(gridcolor="#1e2a38"),
            height=280,
            margin=dict(t=40, b=20, l=20, r=20),
        )
        fig_ts.update_traces(fillcolor="rgba(0,144,255,0.15)", line_color="#00d4ff")
        st.plotly_chart(fig_ts, use_container_width=True)

    # Compute duration dari df LENGKAP dulu (sama seperti notebook)
    df_dur = compute_duration(df)
    st.session_state.df_dur = df_dur

    # Pilih activity yang mau dibuang dari bottleneck
    all_activities = sorted(df["concept:name"].unique().tolist())

    # Default: activity start/end dari mapping user
    start_acts = [
        m["activity"]
        for m in st.session_state.mapping
        if m["activity"] in all_activities
        and any(k in m["activity"].lower() for k in ["start", "begin"])
    ]
    end_acts = [
        m["activity"]
        for m in st.session_state.mapping
        if m["activity"] in all_activities
        and any(k in m["activity"].lower() for k in ["end", "finish"])
    ]
    default_exclude = list(set(start_acts + end_acts))

    noise_acts = st.multiselect(
        "Exclude activities from bottleneck (optional) — pilih activity yang tidak relevan",
        options=all_activities,
        default=[a for a in default_exclude if a in all_activities],
        help="Activity ini tidak akan dihitung di bottleneck analysis. Duration tetap dihitung dari log lengkap.",
    )
    st.session_state["noise_acts"] = noise_acts

    # Run Analysis button
    st.markdown("<br>", unsafe_allow_html=True)
    col_run1, col_run2, _ = st.columns([1, 2, 3])
    with col_run2:
        if st.button("▶  RUN FULL ANALYSIS", use_container_width=True):
            with st.spinner("Running bottleneck analysis..."):
                st.session_state.bottleneck_df = compute_bottleneck_table(
                    df_dur, noise_acts
                )
                st.session_state.transition_df = compute_transition_delay(df_dur)
                st.session_state.step = 3
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# STEP 3: FULL ANALYSIS
# ═══════════════════════════════════════════════════════════════

if st.session_state.step >= 3:
    df = st.session_state.df_clean
    df_dur = st.session_state.df_dur
    bn_df = st.session_state.bottleneck_df
    tr_df = st.session_state.transition_df

    st.markdown(
        """<div class="section-header">
        <span class="section-title">Analysis Results</span>
    </div>""",
        unsafe_allow_html=True,
    )

    main_tab1, main_tab2, main_tab3, main_tab4, main_tab5 = st.tabs(
        [
            "  Process Discovery",
            "  Conformance Check",
            "  Bottleneck Analysis",
            "  ",
            "  ",
        ]
    )

    # ─────────────────────────────────────────────────────────
    # TAB 1: PROCESS DISCOVERY
    # ─────────────────────────────────────────────────────────
    with main_tab1:
        st.markdown("### Process Discovery")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Extracted process model from event log using Heuristic Miner algorithm.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            # Variants
            st.markdown("#### Process Variants")
            var_df = get_variants(df)
            top_vars = var_df.head(10).copy()
            top_vars["Variant Path"] = top_vars["Variant Path"].str[:80] + "…"
            st.dataframe(top_vars, use_container_width=True, height=300)

        with col_d2:
            # Case duration distribution
            st.markdown("#### Case Duration Distribution")
            case_dur = (
                df.groupby("case:concept:name")
                .agg(start=("time:timestamp", "min"), end=("time:timestamp", "max"))
                .reset_index()
            )
            case_dur["duration_sec"] = (
                case_dur["end"] - case_dur["start"]
            ).dt.total_seconds()
            case_dur = case_dur[case_dur["duration_sec"] > 0]

            fig_dur = px.histogram(
                case_dur,
                x="duration_sec",
                nbins=40,
                title="Case Duration Distribution (seconds)",
                color_discrete_sequence=["#C4872F"],
            )
            fig_dur.update_layout(
                paper_bgcolor="#F5F1EB",
                plot_bgcolor="#F5F1EB",
                font=dict(family="DM Sans", color="#5B4636"),
                title_font=dict(size=13, color="#5B4636"),
                xaxis=dict(gridcolor="#D6C2A8", title="Duration (s)"),
                yaxis=dict(gridcolor="#D6C2A8", title="Count"),
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_dur, use_container_width=True)

        # Heuristic Net
        st.markdown("#### Heuristic Net (Process Model)")
        col_viz1, col_viz2 = st.columns([3, 1])
        with col_viz2:
            # filter_company = None
            # companies = df['case:concept:name'].str.extract(r'^([^_]+)').dropna()[0].unique().tolist() if '_' in df['case:concept:name'].iloc[0] else ['All']
            # company_choices = ['All (Global)'] + companies
            # sel = st.selectbox("Filter by company/group", company_choices)
            # if sel != 'All (Global)':
            #     filter_company = sel

            st.markdown(
                f"""<div class="pm-card">
                <div class="metric-label">PARAMS</div>
                <div style="font-size:0.8rem;color:#8fa3bc;line-height:1.8;">
                Dep threshold: <b style="color:#00d4ff;">{st.session_state.dep_thresh}</b><br>
                AND threshold: <b style="color:#00d4ff;">{st.session_state.and_thresh}</b>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )
            run_viz = st.button("⬡  Generate Heuristic Net", use_container_width=True)

        with col_viz1:
            if run_viz or st.session_state.discovery_img:
                if run_viz:
                    df_viz = df.copy()
                    # if filter_company and filter_company != 'All (Global)':
                    #     df_viz = df_viz[df_viz['case:concept:name'].str.startswith(filter_company + '_')]
                    with st.spinner("Running Heuristic Miner..."):
                        try:
                            img = run_discovery_viz(df_viz)
                            st.session_state.discovery_img = img
                        except Exception as e:
                            st.error(f"Discovery error: {e}")
                            st.info(
                                "💡 Make sure graphviz is installed: apt-get install graphviz"
                            )

                if st.session_state.discovery_img:
                    st.image(st.session_state.discovery_img, use_container_width=True)
            else:
                st.markdown(
                    """<div class="pm-card" style="text-align:center;padding:3rem;">
                    <div style="font-size:3rem;margin-bottom:1rem;">⬡</div>
                    <div style="color:#4a6278;font-size:0.9rem;">Click "Generate Heuristic Net" to visualize the process model</div>
                </div>""",
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────────────────────
    # TAB 2: CONFORMANCE CHECKING
    # ─────────────────────────────────────────────────────────
    with main_tab2:
        st.markdown("### Conformance Checking")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Compare actual process (event log) against reference model (BPMN). Upload your BPMN file to run this analysis.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        bpmn_file = st.file_uploader(
            "Upload BPMN Reference Model (.bpmn)", type=["bpmn", "xml"], key="bpmn_up"
        )

        if bpmn_file:
            bpmn_bytes = bpmn_file.read()
            col_conf1, _ = st.columns([1, 2])
            with col_conf1:
                if st.button("▶  Run Conformance Checking", use_container_width=True):
                    with st.spinner(
                        "Running Token-Based Replay & Alignment Analysis..."
                    ):
                        try:
                            fitness, precision, deviations = run_conformance(
                                df, bpmn_bytes
                            )
                            st.session_state.fitness = fitness
                            st.session_state.precision = precision
                            st.session_state.deviations = deviations
                            st.rerun()
                        except Exception as e:
                            st.error(f"Conformance error: {e}")
                            st.code(traceback.format_exc())

        if st.session_state.fitness is not None:
            fitness = st.session_state.fitness
            precision = st.session_state.precision
            deviations = st.session_state.deviations

            fit_val = fitness.get("average_trace_fitness", 0)
            prec_val = precision if isinstance(precision, float) else 0.0

            # FIX: Ambil perc_fit_traces dengan fallback, lalu normalize ke 0–1
            fit_pct_raw = (
                fitness.get("perc_fit_traces")
                or fitness.get("percentage_of_fitting_traces")
                or fitness.get("percFitTraces")
                or 0
            )
            fit_pct_normalized = fit_pct_raw / 100 if fit_pct_raw > 1 else fit_pct_raw

            # Gauges
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                st.plotly_chart(
                    fitness_gauge(fit_val, "Average Trace Fitness"),
                    use_container_width=True,
                )
            with col_g2:
                st.plotly_chart(
                    fitness_gauge(prec_val, "Precision"), use_container_width=True
                )
            with col_g3:
                st.plotly_chart(
                    fitness_gauge(fit_pct_normalized, "% Fit Traces"),
                    use_container_width=True,
                )

            # Metrics detail
            with st.container():
                if deviations:
                    st.markdown("#### Top Deviations")
                    dev_df = pd.DataFrame(
                        deviations[:15], columns=["Deviation", "Frequency"]
                    )
                    dev_df["Deviation"] = dev_df["Deviation"].str[:60]
                    st.dataframe(dev_df, use_container_width=True, height=300)

                    total_log_moves = sum(
                        v for k, v in deviations if ">>" in k.split("|")[0]
                    )
                    total_model_moves = sum(
                        v for k, v in deviations if ">>" in k.split("|")[1] if "|" in k
                    )
                    st.markdown(
                        f"""<div class="pm-card">
                        <div style="display:flex;gap:2rem;">
                            <div><div class="metric-label">LOG MOVES</div><div class="metric-value" style="font-size:1.4rem;color:#ff4757;">{total_log_moves}</div></div>
                            <div><div class="metric-label">MODEL MOVES</div><div class="metric-value" style="font-size:1.4rem;color:#ffb800;">{total_model_moves}</div></div>
                        </div>
                    </div>""",
                        unsafe_allow_html=True,
                    )
        else:
            st.info(
                "Upload a BPMN file and click 'Run Conformance Checking' to see results here."
            )

    # ─────────────────────────────────────────────────────────
    # TAB 3: BOTTLENECK ANALYSIS
    # ─────────────────────────────────────────────────────────
    with main_tab3:
        st.markdown("### Bottleneck Analysis")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Multi-dimensional performance analysis based on inter-event time (duration_ms). Each metric reveals a different aspect of system performance.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if bn_df is not None and not bn_df.empty:
            sub1, sub2, sub3, sub4 = st.tabs(
                [
                    " Total Time Ranking",
                    " Frequency Ranking",
                    " Mean Duration Ranking",
                    " Transition Delays",
                ]
            )

            with sub1:
                st.markdown(
                    "**Activities ranked by cumulative total time — highest contributors to system load**"
                )
                col_b1, col_b2 = st.columns([1, 1])
                with col_b1:
                    display_cols = [
                        "concept:name",
                        "frekuensi",
                        "total_waktu",
                        "rata_rata",
                        "median",
                        "p95",
                        "maks",
                        "pct_total",
                        "variasi",
                    ]
                    st.dataframe(
                        bn_df[display_cols]
                        .head(15)
                        .rename(
                            columns={
                                "concept:name": "Activity",
                                "frekuensi": "Freq",
                                "total_waktu": "Total (ms)",
                                "rata_rata": "Mean (ms)",
                                "median": "Median (ms)",
                                "p95": "P95 (ms)",
                                "maks": "Max (ms)",
                                "pct_total": "% Total",
                                "variasi": "Volatility",
                            }
                        ),
                        use_container_width=True,
                        height=400,
                    )
                with col_b2:
                    fig_bn = make_plotly_bar(
                        bn_df.head(10),
                        "total_waktu",
                        "concept:name",
                        "Top Bottleneck — Total Time (ms)",
                        h=400,
                    )
                    st.plotly_chart(fig_bn, use_container_width=True)

            with sub2:
                top_freq = bn_df.sort_values("frekuensi", ascending=False)
                col_f1, col_f2 = st.columns([1, 1])
                with col_f1:
                    st.dataframe(
                        top_freq[
                            ["concept:name", "frekuensi", "rata_rata", "pct_total"]
                        ]
                        .head(10)
                        .rename(
                            columns={
                                "concept:name": "Activity",
                                "frekuensi": "Frequency",
                                "rata_rata": "Mean (ms)",
                                "pct_total": "% Total Time",
                            }
                        ),
                        use_container_width=True,
                        height=350,
                    )
                with col_f2:
                    fig_fr = make_plotly_bar(
                        top_freq.head(10),
                        "frekuensi",
                        "concept:name",
                        "Top Activities by Execution Frequency",
                        h=350,
                    )
                    st.plotly_chart(fig_fr, use_container_width=True)

            with sub3:
                top_dur = bn_df.sort_values("rata_rata", ascending=False)
                col_d1, col_d2 = st.columns([1, 1])
                with col_d1:
                    st.dataframe(
                        top_dur[
                            ["concept:name", "rata_rata", "median", "p95", "variasi"]
                        ]
                        .head(10)
                        .rename(
                            columns={
                                "concept:name": "Activity",
                                "rata_rata": "Mean (ms)",
                                "median": "Median (ms)",
                                "p95": "P95 (ms)",
                                "variasi": "Volatility",
                            }
                        ),
                        use_container_width=True,
                        height=350,
                    )
                with col_d2:
                    fig_dr = make_plotly_bar(
                        top_dur.head(10),
                        "rata_rata",
                        "concept:name",
                        "Top Activities by Mean Duration (ms)",
                        h=350,
                    )
                    st.plotly_chart(fig_dr, use_container_width=True)

            with sub4:
                if tr_df is not None and not tr_df.empty:
                    col_t1, col_t2 = st.columns([1, 1])
                    with col_t1:
                        st.dataframe(
                            tr_df[
                                [
                                    "transition",
                                    "frekuensi",
                                    "rata_rata",
                                    "median",
                                    "p95",
                                ]
                            ]
                            .head(15)
                            .rename(
                                columns={
                                    "transition": "Transition (A → B)",
                                    "frekuensi": "Freq",
                                    "rata_rata": "Mean Delay (ms)",
                                    "median": "Median (ms)",
                                    "p95": "P95 (ms)",
                                }
                            ),
                            use_container_width=True,
                            height=400,
                        )
                    with col_t2:
                        fig_tr = make_plotly_bar(
                            tr_df.head(10),
                            "rata_rata",
                            "transition",
                            "Top Transition Delays — Mean (ms)",
                            h=400,
                        )
                        st.plotly_chart(fig_tr, use_container_width=True)
                else:
                    st.info("No transition data available.")

            # Summary synthesis card
            if not bn_df.empty:
                top1 = bn_df.iloc[0]["concept:name"] if len(bn_df) > 0 else "-"
                top2 = bn_df.iloc[1]["concept:name"] if len(bn_df) > 1 else "-"
                top3 = bn_df.iloc[2]["concept:name"] if len(bn_df) > 2 else "-"
                st.markdown(
                    f"""<div class="pm-card" style="border-color:#2a3a50;margin-top:1rem;">
                    <div style="font-family:Space Mono;font-size:0.7rem;color:#4a6278;letter-spacing:0.1em;margin-bottom:0.8rem;">BOTTLENECK SYNTHESIS</div>
                    <div style="font-size:0.9rem;color:#5B4636;line-height:1.7;">
                    Based on total time analysis, the top 3 bottleneck activities are:<br>
                    <span class="pill pill-red">#{1} {top1}</span>&nbsp;
                    <span class="pill pill-yellow">#{2} {top2}</span>&nbsp;
                    <span class="pill pill-blue">#{3} {top3}</span>
                    </div>
                </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.warning(
                "No bottleneck data available. Ensure event log has valid timestamps."
            )

    # ─────────────────────────────────────────────────────────
    # TAB 4: BPI RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────
    with main_tab4:
        st.markdown("### Business Process Improvement Recommendations")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Auto-generated recommendations based on bottleneck analysis and conformance results. Both technical and business dimensions.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        bpi_df = generate_bpi_recommendations(
            bn_df if bn_df is not None else pd.DataFrame(),
            st.session_state.deviations,
            st.session_state.fitness,
        )
        st.session_state.bpi_df = bpi_df

        for _, row in bpi_df.iterrows():
            priority = row["Prioritas"]
            color = (
                "#ff4757"
                if "Tinggi" in priority
                else "#ffb800" if "Sedang" in priority else "#00ff9d"
            )
            st.markdown(
                f"""<div class="pm-card" style="border-left:3px solid {color};margin-bottom:0.8rem;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:0.6rem;">
                    <span style="font-family:Space Mono;font-size:0.75rem;color:{color};">{row['Prioritas']}</span>
                    <span style="font-size:0.95rem;font-weight:600;color:#e2eaf4;">{row['Aktivitas / Area']}</span>
                    <span style="font-family:Space Mono;font-size:0.68rem;color:#4a6278;border:1px solid #1e2a38;padding:1px 8px;border-radius:10px;">{row['Dimensi']}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                    <div>
                        <div style="font-size:0.7rem;color:#4a6278;letter-spacing:0.08em;font-family:Space Mono;margin-bottom:0.3rem;">⚙ TECHNICAL</div>
                        <div style="font-size:0.83rem;color:#8fa3bc;line-height:1.6;">{row['Rekomendasi Teknis']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;color:#4a6278;letter-spacing:0.08em;font-family:Space Mono;margin-bottom:0.3rem;">📋 BUSINESS</div>
                        <div style="font-size:0.83rem;color:#8fa3bc;line-height:1.6;">{row['Rekomendasi Bisnis']}</div>
                    </div>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────
    # TAB 5: EXPORT
    # ─────────────────────────────────────────────────────────
    with main_tab5:
        st.markdown("### Export Analysis Report")
        st.markdown(
            '<div style="font-size:0.85rem;color:#8fa3bc;">Download analysis results in various formats.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        col_e1, col_e2, col_e3 = st.columns(3)

        with col_e1:
            st.markdown(
                """<div class="pm-card" style="text-align:center;padding:2rem;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📊</div>
                <div style="font-weight:600;color:#e2eaf4;margin-bottom:0.5rem;">Bottleneck Report</div>
                <div style="font-size:0.8rem;color:#4a6278;margin-bottom:1rem;">Complete bottleneck table as CSV</div>
            </div>""",
                unsafe_allow_html=True,
            )
            if bn_df is not None:
                csv_bn = bn_df.to_csv(index=True).encode()
                st.download_button(
                    "⬇  Download Bottleneck CSV",
                    csv_bn,
                    f"bottleneck_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True,
                )

        with col_e2:
            st.markdown(
                """<div class="pm-card" style="text-align:center;padding:2rem;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">💡</div>
                <div style="font-weight:600;color:#e2eaf4;margin-bottom:0.5rem;">BPI Recommendations</div>
                <div style="font-size:0.8rem;color:#4a6278;margin-bottom:1rem;">All recommendations as CSV</div>
            </div>""",
                unsafe_allow_html=True,
            )
            if st.session_state.bpi_df is not None:
                csv_bpi = st.session_state.bpi_df.to_csv(index=False).encode()
                st.download_button(
                    "⬇  Download BPI CSV",
                    csv_bpi,
                    f"bpi_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True,
                )

        with col_e3:
            st.markdown(
                """<div class="pm-card" style="text-align:center;padding:2rem;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📋</div>
                <div style="font-weight:600;color:#e2eaf4;margin-bottom:0.5rem;">Full Summary Report</div>
                <div style="font-size:0.8rem;color:#4a6278;margin-bottom:1rem;">All results in one CSV file</div>
            </div>""",
                unsafe_allow_html=True,
            )
            stats = st.session_state.log_stats
            summary_csv = export_summary_csv(
                stats,
                bn_df if bn_df is not None else pd.DataFrame(),
                tr_df if tr_df is not None else pd.DataFrame(),
                (
                    st.session_state.bpi_df
                    if st.session_state.bpi_df is not None
                    else pd.DataFrame()
                ),
            )
            st.download_button(
                "⬇  Download Full Summary",
                summary_csv,
                f"processmine_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True,
            )

        # Event log export
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Export Parsed Event Log")
        if df is not None:
            csv_log = df.to_csv(index=False).encode()
            st.download_button(
                "⬇  Download Parsed Event Log (CSV)",
                csv_log,
                f"event_log_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
            )

        # Mapping export
        if st.session_state.mapping:
            st.markdown("#### Export Current Mapping Configuration")
            df_map = pd.DataFrame(st.session_state.mapping)
            csv_map = df_map.to_csv(index=False).encode()
            st.download_button(
                "⬇  Download Mapping Config (CSV)",
                csv_map,
                "mapping_config.csv",
                "text/csv",
            )
