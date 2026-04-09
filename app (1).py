"""
Regulatory Performance Rating — States & UTs
Power Foundation of India & REC Ltd. | Ministry of Power, GoI
Uses only: pandas, numpy, matplotlib (no plotly)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import json, os
from datetime import datetime, date

st.set_page_config(
    page_title="Regulatory Performance — States & UTs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: sans-serif !important; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d1b4b 0%,#1a3a7c 60%,#0f5499 100%) !important;
}
[data-testid="stSidebar"] * { color:#fff !important; }
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.15) !important; }
.metric-card {
    background:#fff; border:0.5px solid #e2e8f0; border-radius:12px;
    padding:1rem 1.2rem; text-align:center; margin-bottom:4px;
}
.metric-val { font-size:2rem; font-weight:700; line-height:1; margin-bottom:4px; }
.metric-lbl { font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.8px; }
.metric-sub { font-size:0.7rem; color:#94a3b8; margin-top:2px; }
.page-header {
    background:linear-gradient(135deg,#0d1b4b 0%,#1a3a7c 55%,#0f5499 100%);
    padding:1.25rem 1.5rem; border-radius:12px; margin-bottom:1rem;
}
.page-header h1 { font-size:1.3rem; font-weight:700; color:#fff; margin:0 0 4px 0; }
.page-header p  { font-size:0.75rem; color:rgba(255,255,255,0.65); margin:0; }
.badge { display:inline-block; padding:3px 12px; border-radius:20px; font-weight:600; font-size:0.75rem; }
.badge-A { background:#e8f5e9; color:#1b5e20; border:1px solid #a5d6a7; }
.badge-B { background:#e3f2fd; color:#0d47a1; border:1px solid #90caf9; }
.badge-C { background:#fff3e0; color:#bf360c; border:1px solid #ffcc80; }
.badge-D { background:#fce4ec; color:#880e4f; border:1px solid #f48fb1; }
.badge-E { background:#f3e5f5; color:#4a148c; border:1px solid #ce93d8; }
.rank-item { display:flex; align-items:center; gap:10px; padding:8px 12px; border-radius:8px; margin-bottom:3px; }
.rank-item:hover { background:#f8fafc; }
.rank-num  { font-size:0.7rem; color:#94a3b8; width:22px; text-align:right; }
.rank-name { font-size:0.84rem; font-weight:500; flex:1; }
.rank-meta { font-size:0.67rem; color:#94a3b8; }
.param-track { height:7px; background:#e2e8f0; border-radius:4px; overflow:hidden; margin-top:4px; }
.section-title { font-size:0.67rem; font-weight:600; text-transform:uppercase; letter-spacing:1.5px;
    color:#64748b; padding-bottom:8px; border-bottom:1.5px solid #e2e8f0; margin-bottom:12px; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
DATA_FILE = "assessment_data.json"

GRADE_COLOR = {"A":"#1b5e20","B":"#0d47a1","C":"#bf360c","D":"#880e4f","E":"#4a148c"}
GRADE_BG    = {"A":"#e8f5e9","B":"#e3f2fd","C":"#fff3e0","D":"#fce4ec","E":"#f3e5f5"}

PARAM_META = [
    {"key":"ra","label":"Resource Adequacy",    "max":32,"color":"#185FA5"},
    {"key":"fv","label":"Financial Viability",  "max":25,"color":"#1b5e20"},
    {"key":"el","label":"Ease of Living",       "max":23,"color":"#bf360c"},
    {"key":"et","label":"Energy Transition",    "max":15,"color":"#BA7517"},
    {"key":"rg","label":"Regulatory Governance","max":5, "color":"#4a148c"},
]

BASELINE = {
    "Punjab":            {"ra":32,"fv":25,"el":23,"et":12,"rg":5,   "total":97.0, "grade":"A","region":"North",      "type":"State"},
    "Karnataka":         {"ra":32,"fv":23,"el":22,"et":14,"rg":5,   "total":96.0, "grade":"A","region":"South",      "type":"State"},
    "Maharashtra":       {"ra":30,"fv":22,"el":23,"et":14,"rg":5,   "total":94.0, "grade":"A","region":"West",       "type":"State"},
    "Assam":             {"ra":32,"fv":24,"el":20,"et":12,"rg":5,   "total":93.0, "grade":"A","region":"North-East", "type":"State"},
    "Arunachal Pradesh": {"ra":32,"fv":25,"el":21,"et":8, "rg":5,   "total":91.0, "grade":"A","region":"North-East", "type":"State"},
    "Madhya Pradesh":    {"ra":27,"fv":22,"el":21,"et":14,"rg":5,   "total":89.0, "grade":"A","region":"Central",    "type":"State"},
    "Meghalaya":         {"ra":32,"fv":19,"el":20,"et":13,"rg":5,   "total":89.0, "grade":"A","region":"North-East", "type":"State"},
    "Haryana":           {"ra":28,"fv":21,"el":20,"et":15,"rg":4.5, "total":88.5, "grade":"A","region":"North",      "type":"State"},
    "Himachal Pradesh":  {"ra":29,"fv":20,"el":22,"et":12,"rg":5,   "total":88.0, "grade":"A","region":"North",      "type":"State"},
    "Mizoram":           {"ra":32,"fv":18,"el":20,"et":12,"rg":5,   "total":87.0, "grade":"A","region":"North-East", "type":"State"},
    "Jharkhand":         {"ra":28,"fv":22,"el":19,"et":13,"rg":4.67,"total":86.67,"grade":"A","region":"East",       "type":"State"},
    "Sikkim":            {"ra":24,"fv":20,"el":18,"et":11,"rg":5,   "total":78.0, "grade":"B","region":"North-East", "type":"State"},
    "Odisha":            {"ra":24,"fv":18,"el":17,"et":12,"rg":4.5, "total":75.5, "grade":"B","region":"East",       "type":"State"},
    "Chandigarh":        {"ra":22,"fv":18,"el":19,"et":10,"rg":5,   "total":74.0, "grade":"B","region":"North",      "type":"UT"},
    "Dadra & NH and DD": {"ra":22,"fv":17,"el":19,"et":11,"rg":5,   "total":74.0, "grade":"B","region":"West",       "type":"UT"},
    "Andaman & Nicobar": {"ra":28,"fv":9, "el":16,"et":14,"rg":5,   "total":72.0, "grade":"B","region":"Island UT",  "type":"UT"},
    "Lakshadweep":       {"ra":26,"fv":14,"el":17,"et":10,"rg":5,   "total":72.0, "grade":"B","region":"Island UT",  "type":"UT"},
    "Gujarat":           {"ra":18,"fv":19,"el":18,"et":11,"rg":5,   "total":71.0, "grade":"B","region":"West",       "type":"State"},
    "Goa":               {"ra":20,"fv":17,"el":19,"et":10,"rg":5,   "total":71.0, "grade":"B","region":"West",       "type":"State"},
    "Puducherry":        {"ra":20,"fv":17,"el":18,"et":10,"rg":5,   "total":70.0, "grade":"B","region":"South",      "type":"UT"},
    "Uttarakhand":       {"ra":20,"fv":16,"el":17,"et":10,"rg":5,   "total":68.0, "grade":"B","region":"North",      "type":"State"},
    "Andhra Pradesh":    {"ra":10,"fv":20,"el":13,"et":15,"rg":5,   "total":63.0, "grade":"C","region":"South",      "type":"State"},
    "Ladakh":            {"ra":22,"fv":14,"el":15,"et":7, "rg":5,   "total":63.0, "grade":"C","region":"North",      "type":"UT"},
    "Manipur":           {"ra":20,"fv":15,"el":14,"et":8, "rg":5,   "total":62.0, "grade":"C","region":"North-East", "type":"State"},
    "Bihar":             {"ra":18,"fv":15,"el":14,"et":9, "rg":5,   "total":61.0, "grade":"C","region":"East",       "type":"State"},
    "Tamil Nadu":        {"ra":14,"fv":15,"el":16,"et":8, "rg":5,   "total":58.0, "grade":"C","region":"South",      "type":"State"},
    "Kerala":            {"ra":14,"fv":14,"el":15,"et":8, "rg":4.5, "total":55.5, "grade":"C","region":"South",      "type":"State"},
    "Nagaland":          {"ra":18,"fv":13,"el":13,"et":6, "rg":5,   "total":55.0, "grade":"C","region":"North-East", "type":"State"},
    "Chhattisgarh":      {"ra":10,"fv":14,"el":14,"et":9, "rg":5,   "total":52.0, "grade":"C","region":"Central",    "type":"State"},
    "Telangana":         {"ra":12,"fv":13,"el":13,"et":8, "rg":4.5, "total":50.5, "grade":"C","region":"South",      "type":"State"},
    "West Bengal":       {"ra":14,"fv":12,"el":12,"et":7, "rg":5,   "total":50.0, "grade":"C","region":"East",       "type":"State"},
    "Jammu & Kashmir":   {"ra":14,"fv":12,"el":13,"et":7, "rg":3,   "total":49.0, "grade":"D","region":"North",      "type":"UT"},
    "Uttar Pradesh":     {"ra":10,"fv":14,"el":13,"et":8, "rg":3,   "total":48.0, "grade":"D","region":"North",      "type":"State"},
    "Delhi":             {"ra":8, "fv":10,"el":12,"et":7, "rg":3.5, "total":40.5, "grade":"D","region":"North",      "type":"UT"},
    "Rajasthan":         {"ra":8, "fv":11,"el":11,"et":6, "rg":3,   "total":39.0, "grade":"D","region":"North",      "type":"State"},
    "Tripura":           {"ra":5, "fv":6, "el":6, "et":3, "rg":1.5, "total":21.5, "grade":"E","region":"North-East", "type":"State"},
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_grade(score):
    if score >= 85: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "E"

def gv(s, *keys):
    for k in keys:
        if k in s: return s[k]
    return 0

def badge_html(grade, label=None):
    txt = label or f"Grade {grade}"
    return f'<span class="badge badge-{grade}">{txt}</span>'

def grade_color(g):
    return GRADE_COLOR.get(g, "#555")

def score_bar_html(pct, color, height=7):
    return (f'<div class="param-track">'
            f'<div style="width:{min(pct,100):.1f}%;height:{height}px;background:{color};border-radius:4px"></div>'
            f'</div>')

# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    scores = {s: {"ra":b["ra"],"fv":b["fv"],"el":b["el"],"et":b["et"],
                  "rg":b["rg"],"total":b["total"],"grade":b["grade"]}
              for s, b in BASELINE.items()}
    data = {"assessments":{"2025-03-31":{"date":"2025-03-31",
            "label":"Baseline — Report FY 2024-25","scores":scores,
            "notes":"First Report: Rating Regulatory Performance of States & UTs"}},
            "audit_log":[]}
    save_data(data); return data

def save_data(data):
    with open(DATA_FILE,"w") as f: json.dump(data, f, indent=2)

def build_df(scores):
    rows = []
    for state, s in scores.items():
        b = BASELINE.get(state, {})
        rows.append({
            "State/UT": state, "Region": b.get("region","—"), "Type": b.get("type","—"),
            "Res. Adequacy": gv(s,"ra"), "Fin. Viability": gv(s,"fv"),
            "Ease of Living": gv(s,"el"), "Energy Transition": gv(s,"et"),
            "Reg. Governance": gv(s,"rg"), "Total": round(s.get("total",0),2),
            "Grade": s.get("grade","E"),
        })
    df = pd.DataFrame(rows).sort_values("Total",ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def make_csv_template():
    rows = [{"State/UT":st,"Resource Adequacy":b["ra"],"Financial Viability":b["fv"],
             "Ease of Living":b["el"],"Energy Transition":b["et"],"Regulatory Governance":b["rg"]}
            for st,b in BASELINE.items()]
    return pd.DataFrame(rows).to_csv(index=False).encode()

def parse_csv_upload(file):
    try:
        xdf = pd.read_csv(file); xdf.columns = xdf.columns.str.strip()
        col_map = {"Resource Adequacy":"ra","Financial Viability":"fv",
                   "Ease of Living":"el","Energy Transition":"et","Regulatory Governance":"rg"}
        sc = next((c for c in xdf.columns if "state" in c.lower() or "ut" in c.lower()), None)
        if sc is None: return None
        scores = {}
        for _, row in xdf.iterrows():
            state = str(row[sc]).strip()
            if not state or state.lower()=="nan": continue
            rec = {}
            for full, short in col_map.items():
                m = next((c for c in xdf.columns if full.lower() in c.lower()), None)
                rec[short] = float(row[m]) if m and pd.notna(row[m]) else 0.0
            rec["total"] = round(sum(rec.values()),2); rec["grade"] = get_grade(rec["total"])
            scores[state] = rec
        return scores if scores else None
    except Exception as e:
        st.error(f"Parse error: {e}"); return None

# ── MATPLOTLIB CHARTS ─────────────────────────────────────────────────────────
def fig_style(fig, ax=None):
    fig.patch.set_facecolor("white")
    if ax:
        ax.set_facecolor("white")
        ax.spines[["top","right"]].set_visible(False)
        ax.spines[["left","bottom"]].set_color("#e2e8f0")
        ax.tick_params(colors="#475569", labelsize=9)
        ax.yaxis.label.set_color("#475569")
        ax.xaxis.label.set_color("#475569")

def chart_rankings(df_sorted):
    n = len(df_sorted)
    fig, ax = plt.subplots(figsize=(9, max(5, n * 0.35)))
    fig_style(fig, ax)
    colors = [GRADE_COLOR[g] for g in df_sorted["Grade"]]
    bars = ax.barh(range(n), df_sorted["Total"].values, color=colors, height=0.65,
                   edgecolor="white", linewidth=0.5)
    for i, (v, g) in enumerate(zip(df_sorted["Total"], df_sorted["Grade"])):
        ax.text(v + 1, i, f"{v:.1f}", va="center", ha="left", fontsize=8,
                color=GRADE_COLOR[g], fontweight="bold")
    for thr, g in [(85,"A"),(65,"B"),(50,"C"),(35,"D")]:
        ax.axvline(thr, color=GRADE_COLOR[g], linestyle="--", linewidth=1, alpha=0.5)
    ax.set_yticks(range(n))
    ax.set_yticklabels(df_sorted["State/UT"].values, fontsize=8.5)
    ax.set_xlim(0, 115)
    ax.set_xlabel("Score (out of 100)", fontsize=9)
    ax.invert_yaxis()
    patches = [mpatches.Patch(color=GRADE_COLOR[g], label=f"Grade {g}") for g in ["A","B","C","D","E"]]
    ax.legend(handles=patches, fontsize=8, loc="lower right", framealpha=0.8)
    plt.tight_layout()
    return fig

def chart_grade_donut(gc):
    fig, ax = plt.subplots(figsize=(4, 4))
    fig_style(fig)
    grades = list(gc.index)
    colors_bg  = [GRADE_BG[g] for g in grades]
    colors_edge= [GRADE_COLOR[g] for g in grades]
    wedges, texts, autotexts = ax.pie(
        gc.values, labels=[f"Grade {g}\n({v})" for g, v in zip(grades, gc.values)],
        colors=colors_bg, autopct="", startangle=90,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=2))
    for t, g in zip(texts, grades):
        t.set_color(GRADE_COLOR[g]); t.set_fontsize(9); t.set_fontweight("bold")
    ax.set_aspect("equal")
    plt.tight_layout()
    return fig

def chart_region_bar(df):
    palette = ["#185FA5","#1b5e20","#bf360c","#BA7517","#4a148c","#0F6E56","#D85A30"]
    rdf = df.groupby("Region")["Total"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig_style(fig, ax)
    bars = ax.bar(range(len(rdf)), rdf.values, color=[palette[i%len(palette)] for i in range(len(rdf))],
                  edgecolor="white", linewidth=0.5, width=0.6)
    for i, v in enumerate(rdf.values):
        ax.text(i, v + 1, f"{v:.1f}", ha="center", fontsize=8.5, color="#475569", fontweight="bold")
    ax.set_xticks(range(len(rdf))); ax.set_xticklabels(rdf.index, fontsize=8, rotation=20, ha="right")
    ax.set_ylabel("Average Score", fontsize=9); ax.set_ylim(0, 110)
    plt.tight_layout(); return fig

def chart_scatter(df):
    fig, ax = plt.subplots(figsize=(6, 5))
    fig_style(fig, ax)
    for g, color in GRADE_COLOR.items():
        sub = df[df["Grade"]==g]
        if len(sub):
            ax.scatter(sub["Fin. Viability"], sub["Res. Adequacy"],
                       c=color, s=sub["Total"]*3, alpha=0.75, label=f"Grade {g}", edgecolors="white", linewidth=0.5)
    ax.set_xlabel("Financial Viability (out of 25)", fontsize=9)
    ax.set_ylabel("Resource Adequacy (out of 32)", fontsize=9)
    ax.legend(fontsize=8, framealpha=0.8)
    plt.tight_layout(); return fig

def chart_type_box(df):
    fig, ax = plt.subplots(figsize=(4, 4))
    fig_style(fig, ax)
    state_vals = df[df["Type"]=="State"]["Total"].values
    ut_vals    = df[df["Type"]=="UT"]["Total"].values
    bp = ax.boxplot([state_vals, ut_vals], labels=["States","UTs"],
                    patch_artist=True, widths=0.5,
                    medianprops=dict(color="white", linewidth=2))
    colors = ["#185FA5", "#bf360c"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c); patch.set_alpha(0.3)
    for i, (vals, c) in enumerate([(state_vals,"#185FA5"),(ut_vals,"#bf360c")], 1):
        jitter = np.random.uniform(-0.15, 0.15, len(vals))
        ax.scatter(i + jitter, vals, c=c, alpha=0.6, s=25, zorder=5)
    ax.set_ylabel("Total Score", fontsize=9); ax.set_ylim(0, 110)
    plt.tight_layout(); return fig

def chart_radar(state_name, vals, maxes, color):
    labels = [p["label"] for p in PARAM_META]
    pcts   = [v / m * 100 for v, m in zip(vals, maxes)]
    N = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]; pcts_plot = pcts + pcts[:1]
    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.plot(angles, pcts_plot, color=color, linewidth=2)
    ax.fill(angles, pcts_plot, color=color, alpha=0.15)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=8, color="#475569")
    ax.set_ylim(0, 100); ax.set_yticks([25,50,75,100]); ax.set_yticklabels(["25","50","75","100"], size=7, color="#94a3b8")
    ax.grid(color="#e2e8f0", linewidth=0.8); ax.spines["polar"].set_color("#e2e8f0")
    plt.tight_layout(); return fig

def chart_compare_radar(sa, va, sb, vb):
    keys   = [p["key"] for p in PARAM_META]
    maxes  = [p["max"] for p in PARAM_META]
    labels = [p["label"] for p in PARAM_META]
    N = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    for name, v, color, ls in [(sa, va, "#185FA5", "-"), (sb, vb, "#bf360c", "--")]:
        pcts = [v[k]/m*100 for k, m in zip(keys, maxes)] + [v[keys[0]]/maxes[0]*100]
        ax.plot(angles, pcts, color=color, linewidth=2, linestyle=ls, label=name)
        ax.fill(angles, pcts, color=color, alpha=0.1)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=8, color="#475569")
    ax.set_ylim(0, 100); ax.set_yticks([25,50,75,100]); ax.set_yticklabels(["25","50","75","100"], size=7, color="#94a3b8")
    ax.grid(color="#e2e8f0", linewidth=0.8); ax.spines["polar"].set_color("#e2e8f0")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
    plt.tight_layout(); return fig

def chart_heatmap(df):
    param_keys  = ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
    param_maxes = [32, 25, 23, 15, 5]
    heat = df.set_index("State/UT")[param_keys].copy()
    for col, mx in zip(param_keys, param_maxes):
        heat[col] = (heat[col] / mx * 100).round(1)
    data_np = heat.values.astype(float)
    n_states, n_params = data_np.shape
    fig, ax = plt.subplots(figsize=(8, max(8, n_states * 0.28)))
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    im = ax.imshow(data_np, aspect="auto", cmap="RdYlGn", vmin=0, vmax=100)
    ax.set_xticks(range(n_params)); ax.set_xticklabels(param_keys, fontsize=8, rotation=20, ha="right")
    ax.set_yticks(range(n_states)); ax.set_yticklabels(heat.index.tolist(), fontsize=7.5)
    for i in range(n_states):
        for j in range(n_params):
            val = data_np[i, j]
            tc = "white" if val < 40 or val > 80 else "#1a1a2e"
            ax.text(j, i, f"{val:.0f}%", ha="center", va="center", fontsize=7, color=tc)
    cbar = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
    cbar.set_label("% of max marks", fontsize=8, color="#475569")
    cbar.ax.tick_params(labelsize=7, colors="#475569")
    plt.tight_layout(); return fig

def chart_trend(tdf, param):
    palette = ["#185FA5","#1b5e20","#bf360c","#BA7517","#4a148c","#0F6E56","#D85A30","#4e342e"]
    fig, ax = plt.subplots(figsize=(8, 4))
    fig_style(fig, ax)
    for i, (state, grp) in enumerate(tdf.groupby("State/UT")):
        grp = grp.sort_values("Date")
        ax.plot(grp["Date"], grp[param], marker="o", linewidth=2,
                color=palette[i % len(palette)], label=state, markersize=6)
    ax.set_ylabel(param, fontsize=9); ax.legend(fontsize=8, framealpha=0.8)
    plt.xticks(rotation=20, ha="right", fontsize=8)
    plt.tight_layout(); return fig

def chart_delta(chg_df):
    chg_df = chg_df.sort_values("Δ")
    colors = [GRADE_COLOR["A"] if v >= 0 else GRADE_COLOR["D"] for v in chg_df["Δ"]]
    fig, ax = plt.subplots(figsize=(10, 4))
    fig_style(fig, ax)
    ax.bar(range(len(chg_df)), chg_df["Δ"].values, color=colors, edgecolor="white", linewidth=0.5)
    ax.axhline(0, color="#94a3b8", linewidth=1)
    ax.set_xticks(range(len(chg_df))); ax.set_xticklabels(chg_df["State/UT"].values, fontsize=7, rotation=45, ha="right")
    ax.set_ylabel("Δ Score", fontsize=9)
    plt.tight_layout(); return fig

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
data = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem'>
      <div style='font-size:2rem'>⚡</div>
      <div style='font-size:1rem;font-weight:700;color:#fff;margin-top:4px'>Regulatory Performance</div>
      <div style='font-size:0.7rem;color:rgba(255,255,255,0.55);margin-top:2px'>States & Union Territories</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Overview","🏆 Rankings","🔍 State Profile","⚖️ Compare",
        "🗺️ Heatmap","📈 Trends","📤 Upload","📝 New Assessment","📋 History",
    ], label_visibility="collapsed")
    st.markdown("---")
    dates    = sorted(data["assessments"].keys(), reverse=True)
    sel_date = st.selectbox("Assessment Period", dates,
                            format_func=lambda d: data["assessments"][d]["label"])
    st.markdown("---")
    st.markdown("""<div style='font-size:0.65rem;color:rgba(255,255,255,0.4);text-align:center;line-height:1.6'>
      Power Foundation of India<br>REC Ltd. | Ministry of Power<br>Government of India
    </div>""", unsafe_allow_html=True)

snapshot   = data["assessments"][sel_date]
scores     = snapshot["scores"]
df         = build_df(scores)
all_states = sorted(scores.keys())

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>⚡ Regulatory Performance Rating — States &amp; UTs</h1>
  <p>Power Foundation of India &amp; REC Ltd. | Ministry of Power, Government of India</p>
</div>""", unsafe_allow_html=True)

# ── KPI STRIP ─────────────────────────────────────────────────────────────────
gc  = df["Grade"].value_counts()
avg = df["Total"].mean()
n   = len(df)
kc = st.columns(6)
kpi_data = [
    (str(n),            "#0d1b4b","States & UTs",""),
    (str(gc.get("A",0)),GRADE_COLOR["A"],"Grade A","≥ 85 marks"),
    (str(gc.get("B",0)),GRADE_COLOR["B"],"Grade B","65–84 marks"),
    (str(gc.get("C",0)),GRADE_COLOR["C"],"Grade C","50–64 marks"),
    (str(gc.get("D",0)+gc.get("E",0)),GRADE_COLOR["D"],"Grade D/E","< 50 marks"),
    (f"{avg:.1f}","#64748b","National Avg","out of 100"),
]
for col, (val, color, lbl, sub) in zip(kc, kpi_data):
    with col:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-val' style='color:{color}'>{val}</div>"
            f"<div class='metric-lbl'>{lbl}</div>"
            f"{'<div class=metric-sub>'+sub+'</div>' if sub else ''}"
            f"</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    sorted_df = df.sort_values("Total", ascending=False)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='section-title'>Grade Distribution</div>", unsafe_allow_html=True)
        st.pyplot(chart_grade_donut(gc), use_container_width=True)
    with col_r:
        st.markdown("<div class='section-title'>Average Score by Region</div>", unsafe_allow_html=True)
        st.pyplot(chart_region_bar(df), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-title'>States vs Union Territories</div>", unsafe_allow_html=True)
        st.pyplot(chart_type_box(df), use_container_width=True)
    with col_b:
        st.markdown("<div class='section-title'>Resource Adequacy vs Financial Viability</div>", unsafe_allow_html=True)
        st.pyplot(chart_scatter(df), use_container_width=True)

    st.markdown("<div class='section-title'>Top 5 Performers</div>", unsafe_allow_html=True)
    for _, row in sorted_df.head(5).iterrows():
        gc_color = grade_color(row["Grade"])
        st.markdown(
            f"<div class='rank-item'><span class='rank-num'>#{row.name}</span>"
            f"{badge_html(row['Grade'])}"
            f"<div style='flex:1'><div class='rank-name'>{row['State/UT']}</div>"
            f"<div class='rank-meta'>{row['Region']} · {row['Type']}</div></div>"
            f"<div style='min-width:140px'>{score_bar_html(row['Total'],gc_color)}</div>"
            f"<span style='font-size:0.82rem;font-weight:600;color:{gc_color};min-width:36px'>{row['Total']:.1f}</span>"
            f"</div>", unsafe_allow_html=True)

    st.markdown("<br><div class='section-title'>Bottom 5 Performers</div>", unsafe_allow_html=True)
    for _, row in sorted_df.tail(5).iterrows():
        gc_color = grade_color(row["Grade"])
        st.markdown(
            f"<div class='rank-item'><span class='rank-num'>#{row.name}</span>"
            f"{badge_html(row['Grade'])}"
            f"<div style='flex:1'><div class='rank-name'>{row['State/UT']}</div>"
            f"<div class='rank-meta'>{row['Region']} · {row['Type']}</div></div>"
            f"<span style='font-size:0.82rem;font-weight:600;color:{gc_color}'>{row['Total']:.1f}</span>"
            f"</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Rankings":
    fc1, fc2, fc3 = st.columns([3,1,1])
    search       = fc1.text_input("Search", placeholder="Filter by name…", label_visibility="collapsed")
    filter_type  = fc2.selectbox("Type",  ["All","State","UT"],           label_visibility="collapsed")
    filter_grade = fc3.selectbox("Grade", ["All","A","B","C","D","E"],    label_visibility="collapsed")
    fdf = df.copy()
    if search:        fdf = fdf[fdf["State/UT"].str.contains(search, case=False)]
    if filter_type  != "All": fdf = fdf[fdf["Type"]  == filter_type]
    if filter_grade != "All": fdf = fdf[fdf["Grade"] == filter_grade]
    st.pyplot(chart_rankings(fdf.sort_values("Total", ascending=True)), use_container_width=True)
    st.markdown("<div class='section-title'>Detailed Table</div>", unsafe_allow_html=True)
    disp = fdf.copy(); disp.insert(0,"Rank",disp.index)
    st.dataframe(disp.style.background_gradient(subset=["Total"],cmap="RdYlGn",vmin=0,vmax=100),
                 use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download CSV", fdf.to_csv(index=False).encode(),
                       "regulatory_rankings.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 State Profile":
    sel = st.selectbox("Select State / UT", sorted(scores.keys()),
                       format_func=lambda s: f"{s}  ·  Grade {scores[s].get('grade','?')}  ·  {scores[s].get('total',0):.1f}")
    s_data = scores[sel]; b_data = BASELINE.get(sel,{})
    vals   = {p["key"]: gv(s_data, p["key"]) for p in PARAM_META}
    total  = s_data.get("total",0); grade = s_data.get("grade", get_grade(total))
    rank   = df[df["State/UT"]==sel].index.tolist(); rank = rank[0] if rank else "—"
    show_peers = st.checkbox("Show regional peers", value=False)

    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown(
            f"<div style='background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;"
            f"padding:1.25rem;text-align:center'>"
            f"<div style='font-size:1.15rem;font-weight:700;color:#1a1a2e'>{sel}</div>"
            f"<div style='margin:8px 0'>{badge_html(grade)}</div>"
            f"<div style='font-size:0.72rem;color:#94a3b8;margin-bottom:6px'>Rank <strong style='color:#1a1a2e'>#{rank}</strong> of {len(df)}</div>"
            f"<div style='font-size:3rem;font-weight:700;line-height:1;color:{grade_color(grade)}'>{total:.1f}</div>"
            f"<div style='font-size:0.72rem;color:#64748b'>out of 100</div>"
            f"<hr style='border-color:#e2e8f0;margin:10px 0'>"
            f"<div style='font-size:0.73rem;color:#64748b'>{b_data.get('region','—')} | {b_data.get('type','—')}</div>"
            f"</div>", unsafe_allow_html=True)
        st.markdown("<br><div class='section-title'>Parameter Breakdown</div>", unsafe_allow_html=True)
        for p in PARAM_META:
            v = vals[p["key"]]; pct = v / p["max"] * 100
            st.markdown(
                f"<div style='margin-bottom:10px'>"
                f"<div style='display:flex;justify-content:space-between;font-size:0.78rem'>"
                f"<span style='font-weight:500;color:#475569'>{p['label']}</span>"
                f"<span style='font-weight:600;color:#1a1a2e'>{v}/{p['max']} ({pct:.0f}%)</span></div>"
                f"{score_bar_html(pct, p['color'])}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-title'>Parameter Radar</div>", unsafe_allow_html=True)
        st.pyplot(chart_radar(sel,[vals[p["key"]] for p in PARAM_META],
                              [p["max"] for p in PARAM_META], grade_color(grade)), use_container_width=True)
        if show_peers:
            region = b_data.get("region","")
            peers  = df[df["Region"]==region].sort_values("Total",ascending=False)
            st.markdown(f"<div class='section-title'>Regional Peers — {region}</div>", unsafe_allow_html=True)
            for _, row in peers.iterrows():
                is_sel = row["State/UT"]==sel
                bg = "#eff6ff" if is_sel else "transparent"
                st.markdown(
                    f"<div class='rank-item' style='background:{bg}'><span class='rank-num'>#{row.name}</span>"
                    f"{badge_html(row['Grade'])}"
                    f"<div class='rank-name' style='font-weight:{600 if is_sel else 400}'>{row['State/UT']}</div>"
                    "<span style='font-size:0.8rem;font-weight:600;color:" + grade_color(row['Grade']) + f"'>{row['Total']:.1f}</span>"
                    f"</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Compare":
    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown("<div style='font-size:0.7rem;font-weight:600;color:#185FA5;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px'>State / UT A</div>", unsafe_allow_html=True)
        sa_name = st.selectbox("A", all_states, index=0, label_visibility="collapsed")
    with cs2:
        st.markdown("<div style='font-size:0.7rem;font-weight:600;color:#bf360c;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px'>State / UT B</div>", unsafe_allow_html=True)
        sb_name = st.selectbox("B", all_states, index=min(5,len(all_states)-1), label_visibility="collapsed")

    if sa_name == sb_name:
        st.warning("Please select two different States/UTs.")
    else:
        sa, sb = scores[sa_name], scores[sb_name]
        def gv_all(s):
            return {p["key"]: gv(s, p["key"]) for p in PARAM_META} | \
                   {"total": s.get("total",0), "grade": s.get("grade","E")}
        va, vb = gv_all(sa), gv_all(sb)
        a_wins = va["total"] > vb["total"]

        cc1, cc2 = st.columns(2)
        for col, name, v, color, wins in [(cc1,sa_name,va,"#185FA5",a_wins),(cc2,sb_name,vb,"#bf360c",not a_wins)]:
            with col:
                g = v["grade"]
                winner = "<div style='font-size:0.63rem;background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7;border-radius:10px;padding:2px 8px;display:inline-block;margin-bottom:4px'>Winner</div>" if wins else ""
                st.markdown(
                    f"<div style='background:#fff;border:0.5px solid {''+color if wins else '#e2e8f0'};border-radius:12px;padding:1.1rem;text-align:center'>"
                    f"{winner}<div style='font-size:1.05rem;font-weight:700;margin-bottom:6px'>{name}</div>"
                    f"{badge_html(g)}"
                    f"<div style='font-size:2.5rem;font-weight:700;color:{grade_color(g)};margin:8px 0'>{v['total']:.1f}</div>"
                    f"<div style='font-size:0.7rem;color:#94a3b8'>out of 100</div></div>", unsafe_allow_html=True)

        col_rad, col_tbl = st.columns([3,2])
        with col_rad:
            st.markdown("<div class='section-title'>Radar Comparison</div>", unsafe_allow_html=True)
            st.pyplot(chart_compare_radar(sa_name,va,sb_name,vb), use_container_width=True)
        with col_tbl:
            st.markdown("<div class='section-title'>Head-to-Head</div>", unsafe_allow_html=True)
            rows_cmp = []
            for p in PARAM_META:
                av,bv = va[p["key"]],vb[p["key"]]
                rows_cmp.append({"Parameter":p["label"],sa_name:f"{av}/{p['max']}",sb_name:f"{bv}/{p['max']}",
                                  "Better":sa_name if av>bv else (sb_name if bv>av else "Tied")})
            rows_cmp.append({"Parameter":"TOTAL",sa_name:f"{va['total']:.1f}",sb_name:f"{vb['total']:.1f}",
                              "Better":sa_name if a_wins else sb_name})
            st.dataframe(pd.DataFrame(rows_cmp), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Heatmap":
    st.markdown("<div class='section-title'>Parameter Achievement — % of Maximum Marks</div>", unsafe_allow_html=True)
    st.pyplot(chart_heatmap(df), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Trends":
    if len(data["assessments"]) < 2:
        st.info("Add at least 2 assessments to see trends.")
    else:
        tc1, tc2 = st.columns([3,1])
        sel_states = tc1.multiselect("Select States/UTs", sorted(BASELINE.keys()),
                                     default=["Punjab","Karnataka","Uttar Pradesh","Delhi","Tripura"])
        param_opts = ["Total Score","Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
        param = tc2.selectbox("Parameter", param_opts)
        rows = []
        for d_key, snap in sorted(data["assessments"].items()):
            for stn in sel_states:
                sc = snap["scores"].get(stn,{})
                if sc:
                    rows.append({"Date":d_key,"State/UT":stn,
                                 "Total Score":sc.get("total",0),
                                 "Res. Adequacy":gv(sc,"ra"),"Fin. Viability":gv(sc,"fv"),
                                 "Ease of Living":gv(sc,"el"),"Energy Transition":gv(sc,"et"),
                                 "Reg. Governance":gv(sc,"rg")})
        if rows:
            tdf = pd.DataFrame(rows)
            st.pyplot(chart_trend(tdf,param), use_container_width=True)
            all_d = sorted(data["assessments"].keys())
            if len(all_d)>=2:
                chg = []
                for state in sorted(BASELINE.keys()):
                    s1 = data["assessments"][all_d[0]]["scores"].get(state,{})
                    s2 = data["assessments"][all_d[-1]]["scores"].get(state,{})
                    if s1 and s2:
                        delta = round(s2.get("total",0)-s1.get("total",0),2)
                        chg.append({"State/UT":state,
                                    f"Score ({all_d[0]})":s1.get("total",0),
                                    f"Score ({all_d[-1]})":s2.get("total",0),"Δ":delta,
                                    "Direction":"▲ Improved" if delta>0 else ("▼ Declined" if delta<0 else "→ Same")})
                if chg:
                    chg_df = pd.DataFrame(chg).sort_values("Δ",ascending=False)
                    st.pyplot(chart_delta(chg_df), use_container_width=True)
                    st.dataframe(chg_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload":
    st.info("Upload a CSV with columns: State/UT, Resource Adequacy, Financial Viability, Ease of Living, Energy Transition, Regulatory Governance")
    st.download_button("⬇️ Download CSV Template", make_csv_template(), "assessment_template.csv", mime="text/csv")
    st.markdown("---")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        parsed = parse_csv_upload(uploaded)
        if parsed is None:
            st.error("Could not parse file. Check column names.")
        else:
            st.success(f"Parsed {len(parsed)} states/UTs successfully!")
            prev_rows = [{"State/UT":s,"RA":sc["ra"],"FV":sc["fv"],"EL":sc["el"],
                          "ET":sc["et"],"RG":sc["rg"],"Total":sc["total"],"Grade":sc["grade"]}
                         for s,sc in parsed.items()]
            st.dataframe(pd.DataFrame(prev_rows).sort_values("Total",ascending=False)
                         .style.background_gradient(subset=["Total"],cmap="RdYlGn",vmin=0,vmax=100),
                         use_container_width=True, height=300)
            uc1, uc2 = st.columns(2)
            up_date  = uc1.date_input("Assessment Date", value=date.today())
            up_label = uc2.text_input("Assessment Label", placeholder="e.g. ARR FY 2026-27")
            up_notes = st.text_area("Notes", placeholder="Source, methodology…")
            if st.button("💾 Save Assessment", type="primary", use_container_width=True):
                if not up_label.strip():
                    st.error("Please provide a label.")
                else:
                    dk = str(up_date)
                    data["assessments"][dk] = {"date":dk,"label":up_label,"scores":parsed,"notes":up_notes}
                    data["audit_log"].append({"action":"file_upload","date":dk,"label":up_label,
                                              "states":len(parsed),"timestamp":datetime.now().isoformat()})
                    save_data(data); st.success(f"Saved '{up_label}' with {len(parsed)} states!"); st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 New Assessment":
    st.info("Enter updated scores for each State/UT. Totals are auto-computed.")
    with st.form("new_assessment_form"):
        nc1, nc2 = st.columns(2)
        adate  = nc1.date_input("Assessment Date", value=date.today(), max_value=date.today())
        alabel = nc2.text_input("Label", placeholder="e.g. ARR FY 2026-27")
        anotes = st.text_area("Notes", placeholder="Key policy changes, data sources…")
        st.markdown("---")
        prev_sc    = snapshot["scores"]
        new_scores = {}
        for state in sorted(BASELINE.keys()):
            p = prev_sc.get(state,{})
            with st.expander(f"📍 {state}  ·  Last: {p.get('total',0):.1f}  ·  Grade {p.get('grade','—')}"):
                i1,i2,i3,i4,i5 = st.columns(5)
                n_ra = i1.number_input("RA (0-32)",  0.0,32.0,float(gv(p,"ra")),0.5,key=f"{state}_ra")
                n_fv = i2.number_input("FV (0-25)",  0.0,25.0,float(gv(p,"fv")),0.5,key=f"{state}_fv")
                n_el = i3.number_input("EL (0-23)",  0.0,23.0,float(gv(p,"el")),0.5,key=f"{state}_el")
                n_et = i4.number_input("ET (0-15)",  0.0,15.0,float(gv(p,"et")),0.5,key=f"{state}_et")
                n_rg = i5.number_input("RG (0-5)",   0.0, 5.0,float(gv(p,"rg")),0.5,key=f"{state}_rg")
                n_tot = round(n_ra+n_fv+n_el+n_et+n_rg, 2)
                _gc = GRADE_COLOR.get(get_grade(n_tot), "#555")
                st.markdown(f"<div style='font-weight:600;font-size:0.85rem;color:{_gc}'>"
                            f"Total: {n_tot} / 100 — Grade {get_grade(n_tot)}</div>", unsafe_allow_html=True)
                new_scores[state] = {"ra":n_ra,"fv":n_fv,"el":n_el,"et":n_et,"rg":n_rg,
                                     "total":n_tot,"grade":get_grade(n_tot)}
        if st.form_submit_button("💾 Save Assessment", type="primary", use_container_width=True):
            if not alabel.strip():
                st.error("Please enter a label.")
            else:
                dk = str(adate)
                data["assessments"][dk] = {"date":dk,"label":alabel,"scores":new_scores,"notes":anotes}
                data["audit_log"].append({"action":"new_assessment","date":dk,"label":alabel,
                                          "timestamp":datetime.now().isoformat()})
                save_data(data); st.success(f"Saved '{alabel}'!"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 History":
    st.markdown("<div class='section-title'>Assessment History</div>", unsafe_allow_html=True)
    rows_h = []
    for d_key, snap in sorted(data["assessments"].items(), reverse=True):
        sc = snap["scores"]
        avg_h = round(sum(v.get("total",0) for v in sc.values())/max(len(sc),1),2)
        rows_h.append({"Date":d_key,"Label":snap["label"],"States":len(sc),
                        "Avg Score":avg_h,"Notes":snap.get("notes","")[:60]})
    st.dataframe(pd.DataFrame(rows_h), use_container_width=True, hide_index=True)
    if data["audit_log"]:
        st.markdown("<br><div class='section-title'>Audit Log</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(data["audit_log"]), use_container_width=True, hide_index=True)
    st.markdown("---")
    deletable = [d for d in sorted(data["assessments"].keys()) if d != "2025-03-31"]
    if deletable:
        del_sel = st.selectbox("Delete assessment (baseline protected)", deletable)
        if st.button("🗑️ Delete", type="secondary"):
            del data["assessments"][del_sel]; save_data(data); st.success(f"Deleted {del_sel}"); st.rerun()
    else:
        st.info("Only the baseline exists. Add new assessments to manage them here.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div style='font-size:0.7rem;color:#94a3b8;text-align:center'>"
            "First Report: Rating Regulatory Performance of States & UTs &nbsp;|&nbsp; "
            "Power Foundation of India &amp; REC Ltd. &nbsp;|&nbsp; Ministry of Power, GoI"
            "</div>", unsafe_allow_html=True)
