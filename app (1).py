"""
Regulatory Performance Rating — States & UTs
Power Foundation of India & REC Ltd. | Ministry of Power, GoI
Charts rendered with pure HTML/CSS/SVG — no matplotlib, no plotly
Dependencies: streamlit, pandas, numpy only
"""

import streamlit as st
import pandas as pd
import numpy as np
import json, os
from datetime import datetime, date

st.set_page_config(
    page_title="Regulatory Performance — States & UTs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
html,body,[class*="css"]{font-family:sans-serif!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1b4b 0%,#1a3a7c 60%,#0f5499 100%)!important;}
[data-testid="stSidebar"] *{color:#fff!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,0.15)!important;}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-baseweb="popover"] *,
[data-testid="stSidebar"] [role="listbox"] *,
[data-testid="stSidebar"] [role="option"] *{color:#1a1a2e!important;}
[data-testid="stSidebar"] [data-baseweb="select"] > div{
    background:#fff!important;border-color:rgba(255,255,255,0.3)!important;}
.page-header{background:linear-gradient(135deg,#0d1b4b 0%,#1a3a7c 55%,#0f5499 100%);
  padding:1.25rem 1.5rem;border-radius:12px;margin-bottom:1rem;}
.page-header h1{font-size:1.3rem;font-weight:700;color:#fff;margin:0 0 4px 0;}
.page-header p{font-size:0.75rem;color:rgba(255,255,255,0.65);margin:0;}
.metric-card{background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;
  padding:1rem 1.2rem;text-align:center;margin-bottom:4px;}
.metric-val{font-size:2rem;font-weight:700;line-height:1;margin-bottom:4px;}
.metric-lbl{font-size:0.65rem;color:#64748b;text-transform:uppercase;letter-spacing:0.8px;}
.metric-sub{font-size:0.7rem;color:#94a3b8;margin-top:2px;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-weight:600;font-size:0.73rem;}
.badge-A{background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7;}
.badge-B{background:#e3f2fd;color:#0d47a1;border:1px solid #90caf9;}
.badge-C{background:#fff3e0;color:#bf360c;border:1px solid #ffcc80;}
.badge-D{background:#fce4ec;color:#880e4f;border:1px solid #f48fb1;}
.badge-E{background:#f3e5f5;color:#4a148c;border:1px solid #ce93d8;}
.rank-item{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;margin-bottom:2px;}
.rank-item:hover{background:#f8fafc;}
.rank-num{font-size:0.68rem;color:#94a3b8;width:22px;text-align:right;}
.rank-name{font-size:0.83rem;font-weight:500;flex:1;color:#1a1a2e;}
.rank-meta{font-size:0.65rem;color:#94a3b8;}
.section-title{font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;
  color:#64748b;padding-bottom:7px;border-bottom:1.5px solid #e2e8f0;margin-bottom:12px;}
.chart-box{background:#fff;border:0.5px solid #e2e8f0;border-radius:12px;padding:1rem;margin-bottom:0;}
#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
DATA_FILE   = "assessment_data.json"
GRADE_COLOR = {"A":"#1b5e20","B":"#0d47a1","C":"#bf360c","D":"#880e4f","E":"#4a148c"}
GRADE_BG    = {"A":"#e8f5e9","B":"#e3f2fd","C":"#fff3e0","D":"#fce4ec","E":"#f3e5f5"}
GRADE_BORDER= {"A":"#a5d6a7","B":"#90caf9","C":"#ffcc80","D":"#f48fb1","E":"#ce93d8"}
PARAM_META  = [
    {"key":"ra","label":"Resource Adequacy",    "max":32,"color":"#185FA5"},
    {"key":"fv","label":"Financial Viability",  "max":25,"color":"#1b5e20"},
    {"key":"el","label":"Ease of Living",       "max":23,"color":"#bf360c"},
    {"key":"et","label":"Energy Transition",    "max":15,"color":"#BA7517"},
    {"key":"rg","label":"Regulatory Governance","max":5, "color":"#4a148c"},
]
PALETTE = ["#185FA5","#1b5e20","#bf360c","#BA7517","#4a148c","#0F6E56","#D85A30","#4e342e"]

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

def gc_color(g): return GRADE_COLOR.get(g, "#555")
def gc_bg(g):    return GRADE_BG.get(g, "#f5f5f5")

def badge(g, label=None):
    txt = label or f"Grade {g}"
    return f'<span class="badge badge-{g}">{txt}</span>'

def bar_html(pct, color, height=7):
    pct = min(float(pct), 100)
    return (f'<div style="height:{height}px;background:#e2e8f0;border-radius:4px;overflow:hidden;margin-top:3px">'
            f'<div style="width:{pct:.1f}%;height:100%;background:{color};border-radius:4px"></div></div>')

# ── PERSISTENCE ───────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f: return json.load(f)
    scores = {s: {"ra":b["ra"],"fv":b["fv"],"el":b["el"],"et":b["et"],
                  "rg":b["rg"],"total":b["total"],"grade":b["grade"]}
              for s,b in BASELINE.items()}
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
        rows.append({"State/UT":state,"Region":b.get("region","—"),"Type":b.get("type","—"),
                     "Res. Adequacy":gv(s,"ra"),"Fin. Viability":gv(s,"fv"),
                     "Ease of Living":gv(s,"el"),"Energy Transition":gv(s,"et"),
                     "Reg. Governance":gv(s,"rg"),"Total":round(s.get("total",0),2),
                     "Grade":s.get("grade","E")})
    df = pd.DataFrame(rows).sort_values("Total",ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def make_csv_template():
    rows = [{"State/UT":s,"Resource Adequacy":b["ra"],"Financial Viability":b["fv"],
             "Ease of Living":b["el"],"Energy Transition":b["et"],"Regulatory Governance":b["rg"]}
            for s,b in BASELINE.items()]
    return pd.DataFrame(rows).to_csv(index=False).encode()

def parse_csv_upload(file):
    try:
        xdf = pd.read_csv(file); xdf.columns = xdf.columns.str.strip()
        col_map = {"Resource Adequacy":"ra","Financial Viability":"fv",
                   "Ease of Living":"el","Energy Transition":"et","Regulatory Governance":"rg"}
        sc = next((c for c in xdf.columns if "state" in c.lower() or "ut" in c.lower()), None)
        if sc is None: return None
        out = {}
        for _, row in xdf.iterrows():
            state = str(row[sc]).strip()
            if not state or state.lower()=="nan": continue
            rec = {}
            for full, short in col_map.items():
                m = next((c for c in xdf.columns if full.lower() in c.lower()), None)
                rec[short] = float(row[m]) if m and pd.notna(row[m]) else 0.0
            rec["total"] = round(sum(rec.values()),2); rec["grade"] = get_grade(rec["total"])
            out[state] = rec
        return out if out else None
    except Exception as e:
        st.error(f"Parse error: {e}"); return None

# ── SVG CHART FUNCTIONS ───────────────────────────────────────────────────────

def svg_hbar(df_sorted, width=700):
    n = len(df_sorted)
    row_h, pad_l, pad_r, pad_t, pad_b = 26, 160, 65, 28, 28
    chart_w = width - pad_l - pad_r
    h = n * row_h + pad_t + pad_b
    scale = chart_w / 100.0
    lines = [f'<svg width="{width}" height="{h}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for thr, g in [(85,"A"),(65,"B"),(50,"C"),(35,"D")]:
        x = pad_l + thr * scale
        lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h-pad_b}" stroke="{gc_color(g)}" stroke-width="1" stroke-dasharray="4,3" opacity="0.5"/>')
        lines.append(f'<text x="{x:.1f}" y="{pad_t-8}" text-anchor="middle" font-size="9" fill="{gc_color(g)}" font-weight="600">G{g}</text>')
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        y   = pad_t + i * row_h
        bw  = max(2, row["Total"] * scale)
        col = gc_color(row["Grade"])
        cy  = y + row_h * 0.5
        lines.append(f'<text x="{pad_l-6}" y="{cy+4:.1f}" text-anchor="end" font-size="10" fill="#334155">{row["State/UT"]}</text>')
        lines.append(f'<rect x="{pad_l}" y="{y+4:.1f}" width="{bw:.1f}" height="{row_h-8}" fill="{col}" opacity="0.82" rx="3"/>')
        lines.append(f'<text x="{pad_l+bw+4:.1f}" y="{cy+4:.1f}" font-size="9" fill="{col}" font-weight="600">{row["Total"]:.1f}</text>')
    for v in [0,20,40,60,80,100]:
        x = pad_l + v * scale
        lines.append(f'<text x="{x:.1f}" y="{h-pad_b+14}" text-anchor="middle" font-size="9" fill="#94a3b8">{v}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_donut(gc_series, size=280):
    grades = list(gc_series.index)
    vals   = list(gc_series.values)
    total  = sum(vals)
    cx = cy = size / 2
    R, r = size * 0.38, size * 0.22
    start = -np.pi / 2
    lines = [f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for g, v in zip(grades, vals):
        angle = 2 * np.pi * v / total
        end   = start + angle
        x1,y1 = cx+R*np.cos(start), cy+R*np.sin(start)
        x2,y2 = cx+R*np.cos(end),   cy+R*np.sin(end)
        ix1,iy1 = cx+r*np.cos(end),  cy+r*np.sin(end)
        ix2,iy2 = cx+r*np.cos(start),cy+r*np.sin(start)
        large = 1 if angle > np.pi else 0
        path  = (f"M {x1:.2f},{y1:.2f} A {R},{R} 0 {large},1 {x2:.2f},{y2:.2f} "
                 f"L {ix1:.2f},{iy1:.2f} A {r},{r} 0 {large},0 {ix2:.2f},{iy2:.2f} Z")
        lines.append(f'<path d="{path}" fill="{gc_bg(g)}" stroke="{gc_color(g)}" stroke-width="2"/>')
        mid = start + angle/2
        lx  = cx + (R+16)*np.cos(mid)
        ly  = cy + (R+16)*np.sin(mid)
        lines.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" font-size="11" font-weight="700" fill="{gc_color(g)}">G{g} {v}</text>')
        start = end
    lines.append(f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="14" font-weight="700" fill="#1a1a2e">{total}</text>')
    lines.append(f'<text x="{cx}" y="{cy+12}" text-anchor="middle" font-size="9" fill="#64748b">States/UTs</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_vbar(labels, values, colors, width=560, height=260, ylabel=""):
    n = len(labels)
    pad_l,pad_r,pad_t,pad_b = 44,16,20,56
    cw = width - pad_l - pad_r
    ch = height - pad_t - pad_b
    max_v = max(values) * 1.15 if values else 1
    bar_w = cw / n * 0.6
    gap   = cw / n
    lines = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for pct in [0,25,50,75,100]:
        v = max_v * pct / 100
        y = pad_t + ch - (v/max_v)*ch
        lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'<text x="{pad_l-4}" y="{y+4:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{v:.0f}</text>')
    for i, (lbl, val, col) in enumerate(zip(labels, values, colors)):
        x  = pad_l + i*gap + gap/2
        bh = (val/max_v)*ch
        by = pad_t + ch - bh
        lines.append(f'<rect x="{x-bar_w/2:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{col}" opacity="0.85" rx="4"/>')
        lines.append(f'<text x="{x:.1f}" y="{by-4:.1f}" text-anchor="middle" font-size="9" fill="{col}" font-weight="600">{val:.1f}</text>')
        words = lbl.replace("-"," ").split()
        for wi, w in enumerate(words[:2]):
            lines.append(f'<text x="{x:.1f}" y="{pad_t+ch+14+wi*13}" text-anchor="middle" font-size="9" fill="#475569">{w}</text>')
    if ylabel:
        lines.append(f'<text x="11" y="{pad_t+ch//2}" text-anchor="middle" font-size="9" fill="#64748b" transform="rotate(-90,11,{pad_t+ch//2})">{ylabel}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_radar(vals_pct, color, size=300):
    labels = [p["label"] for p in PARAM_META]
    N      = len(labels)
    cx = cy = size / 2
    R      = size * 0.36
    angles = [2*np.pi*i/N - np.pi/2 for i in range(N)]
    lines  = [f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for pct in [25,50,75,100]:
        pts = " ".join(f"{cx+R*(pct/100)*np.cos(a):.2f},{cy+R*(pct/100)*np.sin(a):.2f}" for a in angles)
        lines.append(f'<polygon points="{pts}" fill="none" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'<text x="{cx+4}" y="{cy-R*(pct/100)+4:.1f}" font-size="8" fill="#cbd5e1">{pct}%</text>')
    for a in angles:
        lines.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx+R*np.cos(a):.1f}" y2="{cy+R*np.sin(a):.1f}" stroke="#e2e8f0" stroke-width="1"/>')
    pts = " ".join(f"{cx+R*(v/100)*np.cos(a):.2f},{cy+R*(v/100)*np.sin(a):.2f}" for v,a in zip(vals_pct,angles))
    lines.append(f'<polygon points="{pts}" fill="{color}" fill-opacity="0.18" stroke="{color}" stroke-width="2"/>')
    for v,a in zip(vals_pct,angles):
        px = cx+R*(v/100)*np.cos(a); py = cy+R*(v/100)*np.sin(a)
        lines.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="4" fill="{color}"/>')
    for lbl, a in zip(labels, angles):
        lx = cx+(R+24)*np.cos(a); ly = cy+(R+24)*np.sin(a)
        anchor = "middle" if abs(np.cos(a))<0.3 else ("end" if np.cos(a)<0 else "start")
        words  = lbl.split()
        for wi, w in enumerate(words):
            lines.append(f'<text x="{lx:.1f}" y="{ly+wi*12:.1f}" text-anchor="{anchor}" font-size="9" fill="#475569">{w}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_compare_radar(sa, va, sb, vb, size=340):
    keys   = [p["key"] for p in PARAM_META]
    maxes  = [p["max"] for p in PARAM_META]
    labels = [p["label"] for p in PARAM_META]
    N  = len(labels)
    cx = cy = size / 2
    R  = size * 0.34
    angles = [2*np.pi*i/N - np.pi/2 for i in range(N)]
    lines  = [f'<svg width="{size}" height="{size+40}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for pct in [25,50,75,100]:
        pts = " ".join(f"{cx+R*(pct/100)*np.cos(a):.2f},{cy+R*(pct/100)*np.sin(a):.2f}" for a in angles)
        lines.append(f'<polygon points="{pts}" fill="none" stroke="#e2e8f0" stroke-width="1"/>')
    for a in angles:
        lines.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx+R*np.cos(a):.1f}" y2="{cy+R*np.sin(a):.1f}" stroke="#e2e8f0" stroke-width="1"/>')
    for name, v, color, dash in [(sa,va,"#185FA5","none"),(sb,vb,"#bf360c","5,3")]:
        pcts = [v[k]/m*100 for k,m in zip(keys,maxes)]
        pts  = " ".join(f"{cx+R*(p/100)*np.cos(a):.2f},{cy+R*(p/100)*np.sin(a):.2f}" for p,a in zip(pcts,angles))
        lines.append(f'<polygon points="{pts}" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width="2" stroke-dasharray="{dash}"/>')
        for p,a in zip(pcts,angles):
            lines.append(f'<circle cx="{cx+R*(p/100)*np.cos(a):.2f}" cy="{cy+R*(p/100)*np.sin(a):.2f}" r="3.5" fill="{color}"/>')
    for lbl, a in zip(labels, angles):
        lx = cx+(R+22)*np.cos(a); ly = cy+(R+22)*np.sin(a)
        anchor = "middle" if abs(np.cos(a))<0.3 else ("end" if np.cos(a)<0 else "start")
        lines.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="9" fill="#475569">{lbl}</text>')
    ly = size + 16
    lines.append(f'<rect x="30" y="{ly}" width="14" height="8" fill="#185FA5" rx="2"/>')
    lines.append(f'<text x="50" y="{ly+8}" font-size="10" fill="#185FA5" font-weight="600">{sa}</text>')
    lines.append(f'<rect x="{size//2+10}" y="{ly}" width="14" height="8" fill="#bf360c" rx="2"/>')
    lines.append(f'<text x="{size//2+30}" y="{ly+8}" font-size="10" fill="#bf360c" font-weight="600">{sb}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_heatmap(df, width=760):
    param_keys  = ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
    param_maxes = [32, 25, 23, 15, 5]
    states      = df["State/UT"].tolist()
    n_s, n_p    = len(states), len(param_keys)
    pad_l,pad_r,pad_t,pad_b = 145,20,55,10
    cell_w = (width - pad_l - pad_r) / n_p
    cell_h = 20
    h      = n_s * cell_h + pad_t + pad_b

    def heat_color(pct):
        if pct >= 75:   return "#a5d6a7","#1b5e20"
        elif pct >= 50: return "#b3d4f5","#0d47a1"
        elif pct >= 30: return "#ffcc80","#7c4a00"
        else:           return "#f48fb1","#880e4f"

    lines = [f'<svg width="{width}" height="{h}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for j, lbl in enumerate(param_keys):
        x = pad_l + j*cell_w + cell_w/2
        words = lbl.split()
        for wi, w in enumerate(words):
            lines.append(f'<text x="{x:.1f}" y="{10+wi*13}" text-anchor="middle" font-size="9" fill="#475569" font-weight="600">{w}</text>')
    for i, row in df.iterrows():
        y = pad_t + (i-1)*cell_h
        lines.append(f'<text x="{pad_l-5}" y="{y+14:.1f}" text-anchor="end" font-size="9" fill="#334155">{row["State/UT"]}</text>')
        for j, (col, mx) in enumerate(zip(param_keys, param_maxes)):
            val = row[col]
            pct = val/mx*100
            bg, fc = heat_color(pct)
            x = pad_l + j*cell_w
            lines.append(f'<rect x="{x+1:.1f}" y="{y+1:.1f}" width="{cell_w-2:.1f}" height="{cell_h-2}" fill="{bg}" rx="3"/>')
            lines.append(f'<text x="{x+cell_w/2:.1f}" y="{y+14:.1f}" text-anchor="middle" font-size="8" fill="{fc}" font-weight="600">{pct:.0f}%</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_scatter(df, width=520, height=400):
    pad_l,pad_r,pad_t,pad_b = 50,20,20,50
    cw = width-pad_l-pad_r; ch = height-pad_t-pad_b
    x_max, y_max = 26, 33
    lines = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for v in [0,5,10,15,20,25]:
        x = pad_l+v/x_max*cw
        lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{pad_t+ch}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'<text x="{x:.1f}" y="{pad_t+ch+14}" text-anchor="middle" font-size="9" fill="#94a3b8">{v}</text>')
    for v in [0,8,16,24,32]:
        y = pad_t+ch-v/y_max*ch
        lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+cw}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'<text x="{pad_l-4}" y="{y+4:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{v}</text>')
    lines.append(f'<text x="{pad_l+cw/2}" y="{height-4}" text-anchor="middle" font-size="9" fill="#64748b">Financial Viability</text>')
    lines.append(f'<text x="12" y="{pad_t+ch//2}" text-anchor="middle" font-size="9" fill="#64748b" transform="rotate(-90,12,{pad_t+ch//2})">Res. Adequacy</text>')
    for _, row in df.iterrows():
        cx = pad_l+row["Fin. Viability"]/x_max*cw
        cy = pad_t+ch-row["Res. Adequacy"]/y_max*ch
        r  = 4+row["Total"]/100*14
        col = gc_color(row["Grade"])
        lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" opacity="0.7" stroke="white" stroke-width="1"/>')
    lx, lbottom = pad_l+10, pad_t+ch-10
    for i,(g,color) in enumerate(GRADE_COLOR.items()):
        lines.append(f'<circle cx="{lx+i*48}" cy="{lbottom}" r="5" fill="{color}" opacity="0.8"/>')
        lines.append(f'<text x="{lx+i*48+8}" y="{lbottom+4}" font-size="9" fill="{color}" font-weight="600">G{g}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


def svg_trend(tdf, sel_states, dates_list, y_label):
    w,h = 700,300
    pad_l,pad_r,pad_t,pad_b = 50,20,20,70
    cw,ch = w-pad_l-pad_r, h-pad_t-pad_b
    vals_all = tdf["Value"].values.astype(float)
    y_min = float(vals_all.min())*0.88
    y_max = float(vals_all.max())*1.08
    if y_max == y_min: y_max = y_min + 1
    lines = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" style="font-family:sans-serif;background:#fff;border-radius:10px">']
    for yi in np.linspace(y_min,y_max,5):
        y = pad_t+ch-(yi-y_min)/(y_max-y_min)*ch
        lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+cw}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'<text x="{pad_l-4}" y="{y+4:.1f}" text-anchor="end" font-size="9" fill="#94a3b8">{yi:.1f}</text>')
    nd = max(len(dates_list)-1, 1)
    for di, d in enumerate(dates_list):
        x = pad_l + di/nd*cw
        lines.append(f'<text x="{x:.1f}" y="{h-10}" text-anchor="middle" font-size="8" fill="#475569" transform="rotate(-20,{x:.1f},{h-10})">{d}</text>')
    for si, stn in enumerate(sel_states):
        sub   = tdf[tdf["State/UT"]==stn].sort_values("Date")
        color = PALETTE[si % len(PALETTE)]
        pts   = []
        for _, r in sub.iterrows():
            if r["Date"] in dates_list:
                di = dates_list.index(r["Date"])
                x  = pad_l + di/nd*cw
                y  = pad_t + ch - (float(r["Value"])-y_min)/(y_max-y_min)*ch
                pts.append((x,y))
        if len(pts)>1:
            d_str = " ".join(f"{'M' if i==0 else 'L'}{px:.1f},{py:.1f}" for i,(px,py) in enumerate(pts))
            lines.append(f'<path d="{d_str}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for px,py in pts:
            lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{color}" stroke="white" stroke-width="1.5"/>')
        # legend
        leg_cols = max(len(sel_states), 1)
        lx = pad_l + (si % leg_cols) * (cw // leg_cols)
        ly = h - 42 + (si // leg_cols) * 14
        lines.append(f'<circle cx="{lx+6}" cy="{ly}" r="4" fill="{color}"/>')
        lines.append(f'<text x="{lx+14}" y="{ly+4}" font-size="9" fill="{color}" font-weight="600">{stn[:18]}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
data = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:1rem 0 0.5rem'>
      <div style='font-size:2rem'>⚡</div>
      <div style='font-size:1rem;font-weight:700;color:#fff;margin-top:4px'>Regulatory Performance</div>
      <div style='font-size:0.68rem;color:rgba(255,255,255,0.5);margin-top:2px'>States & Union Territories</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate",[
        "Overview","Rankings","State Profile","Compare",
        "Heatmap","Trends","Upload","New Assessment","History",
    ], label_visibility="collapsed")
    st.markdown("---")
    dates    = sorted(data["assessments"].keys(), reverse=True)
    sel_date = st.selectbox("Assessment Period", dates,
                            format_func=lambda d: data["assessments"][d]["label"])
    st.markdown("---")
    st.markdown("""<div style='font-size:0.63rem;color:rgba(255,255,255,0.38);text-align:center;line-height:1.7'>
      Power Foundation of India<br>REC Ltd. | Ministry of Power<br>Government of India</div>""", unsafe_allow_html=True)

snapshot   = data["assessments"][sel_date]
scores_raw = snapshot["scores"]
df         = build_df(scores_raw)
all_states = sorted(scores_raw.keys())

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown("""<div class="page-header">
  <h1>⚡ Regulatory Performance Rating — States &amp; UTs</h1>
  <p>Power Foundation of India &amp; REC Ltd. | Ministry of Power, Government of India</p>
</div>""", unsafe_allow_html=True)

# ── KPI STRIP ─────────────────────────────────────────────────────────────────
gc_counts = df["Grade"].value_counts()
avg_score = df["Total"].mean()
n_total   = len(df)
kc = st.columns(6)
kpi_data = [
    (str(n_total),      "#0d1b4b","States & UTs",""),
    (str(gc_counts.get("A",0)),GRADE_COLOR["A"],"Grade A","≥ 85 marks"),
    (str(gc_counts.get("B",0)),GRADE_COLOR["B"],"Grade B","65–84 marks"),
    (str(gc_counts.get("C",0)),GRADE_COLOR["C"],"Grade C","50–64 marks"),
    (str(gc_counts.get("D",0)+gc_counts.get("E",0)),GRADE_COLOR["D"],"Grade D/E","< 50 marks"),
    (f"{avg_score:.1f}","#64748b","National Avg","out of 100"),
]
for col,(val,color,lbl,sub) in zip(kc,kpi_data):
    with col:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-val' style='color:{color}'>{val}</div>"
            f"<div class='metric-lbl'>{lbl}</div>"
            f"{'<div class=metric-sub>'+sub+'</div>' if sub else ''}"
            f"</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    sorted_df = df.sort_values("Total", ascending=False)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='section-title'>Grade Distribution</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chart-box'>{svg_donut(gc_counts)}</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='section-title'>Average Score by Region</div>", unsafe_allow_html=True)
        rdf = df.groupby("Region")["Total"].mean().sort_values(ascending=False)
        st.markdown(f"<div class='chart-box'>{svg_vbar(list(rdf.index),list(rdf.values),PALETTE[:len(rdf)],ylabel='Avg Score')}</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-title'>Resource Adequacy vs Financial Viability</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chart-box'>{svg_scatter(df)}</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<div class='section-title'>States vs UTs — Summary</div>", unsafe_allow_html=True)
        for typ, color in [("State","#185FA5"),("UT","#bf360c")]:
            sub = df[df["Type"]==typ]["Total"]
            median_v = float(np.median(sub))
            mean_v   = float(np.mean(sub))
            min_v    = float(sub.min())
            max_v    = float(sub.max())
            dist     = df[df["Type"]==typ]["Grade"].value_counts()
            grade_badges = " ".join(f"{badge(g)} {dist.get(g,0)}" for g in ["A","B","C","D","E"])
            st.markdown(
                f"<div style='margin-bottom:12px;padding:12px 14px;background:#fff;"
                f"border:0.5px solid #e2e8f0;border-radius:10px'>"
                f"<div style='font-size:0.8rem;font-weight:600;color:{color};margin-bottom:6px'>{typ}s ({len(sub)})</div>"
                f"<div style='font-size:0.72rem;color:#64748b;margin-bottom:6px'>"
                f"Min <b>{min_v:.0f}</b> &nbsp;·&nbsp; Median <b>{median_v:.0f}</b> "
                f"&nbsp;·&nbsp; Mean <b>{mean_v:.1f}</b> &nbsp;·&nbsp; Max <b>{max_v:.0f}</b></div>"
                f"{bar_html(median_v,color,10)}"
                f"<div style='margin-top:8px;font-size:0.72rem'>{grade_badges}</div>"
                f"</div>", unsafe_allow_html=True)

    st.markdown("<br><div class='section-title'>Top 5 Performers</div>", unsafe_allow_html=True)
    for _, row in sorted_df.head(5).iterrows():
        color = gc_color(row["Grade"])
        st.markdown(
            f"<div class='rank-item'><span class='rank-num'>#{row.name}</span>"
            f"{badge(row['Grade'])}"
            f"<div style='flex:1'><div class='rank-name'>{row['State/UT']}</div>"
            f"<div class='rank-meta'>{row['Region']} · {row['Type']}</div></div>"
            f"<div style='min-width:120px'>{bar_html(row['Total'],color)}</div>"
            f"<span style='font-size:0.82rem;font-weight:600;color:{color};min-width:34px;text-align:right'>{row['Total']:.1f}</span>"
            f"</div>", unsafe_allow_html=True)

    st.markdown("<br><div class='section-title'>Bottom 5 Performers</div>", unsafe_allow_html=True)
    for _, row in sorted_df.tail(5).iterrows():
        color = gc_color(row["Grade"])
        st.markdown(
            f"<div class='rank-item'><span class='rank-num'>#{row.name}</span>"
            f"{badge(row['Grade'])}"
            f"<div style='flex:1'><div class='rank-name'>{row['State/UT']}</div>"
            f"<div class='rank-meta'>{row['Region']} · {row['Type']}</div></div>"
            f"<span style='font-size:0.82rem;font-weight:600;color:{color}'>{row['Total']:.1f}</span>"
            f"</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Rankings":
    fc1,fc2,fc3 = st.columns([3,1,1])
    search       = fc1.text_input("Search", placeholder="Filter by name…", label_visibility="collapsed")
    filter_type  = fc2.selectbox("Type",  ["All","State","UT"],        label_visibility="collapsed")
    filter_grade = fc3.selectbox("Grade", ["All","A","B","C","D","E"], label_visibility="collapsed")
    fdf = df.copy()
    if search:        fdf = fdf[fdf["State/UT"].str.contains(search, case=False)]
    if filter_type  != "All": fdf = fdf[fdf["Type"]  == filter_type]
    if filter_grade != "All": fdf = fdf[fdf["Grade"] == filter_grade]
    st.markdown(f"<div class='chart-box'>{svg_hbar(fdf.sort_values('Total',ascending=True))}</div>", unsafe_allow_html=True)
    st.markdown("<br><div class='section-title'>Detailed Table</div>", unsafe_allow_html=True)
    disp = fdf.copy(); disp.insert(0,"Rank",disp.index)
    st.dataframe(disp, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download CSV", fdf.to_csv(index=False).encode(),
                       "regulatory_rankings.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
#  STATE PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "State Profile":
    sel = st.selectbox("Select State / UT", sorted(scores_raw.keys()),
                       format_func=lambda s: f"{s}  ·  Grade {scores_raw[s].get('grade','?')}  ·  {scores_raw[s].get('total',0):.1f}")
    s_data = scores_raw[sel]
    b_data = BASELINE.get(sel, {})
    vals   = {p["key"]: gv(s_data, p["key"]) for p in PARAM_META}
    total  = s_data.get("total", 0)
    grade  = s_data.get("grade", get_grade(total))
    rank_r = df[df["State/UT"]==sel].index.tolist()
    rank_n = rank_r[0] if rank_r else "—"
    show_peers = st.checkbox("Show regional peers", value=False)

    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown(
            f"<div style='background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;padding:1.25rem;text-align:center'>"
            f"<div style='font-size:1.15rem;font-weight:700;color:#1a1a2e'>{sel}</div>"
            f"<div style='margin:8px 0'>{badge(grade)}</div>"
            f"<div style='font-size:0.7rem;color:#94a3b8;margin-bottom:6px'>Rank <b style='color:#1a1a2e'>#{rank_n}</b> of {len(df)}</div>"
            f"<div style='font-size:3rem;font-weight:700;line-height:1;color:{gc_color(grade)}'>{total:.1f}</div>"
            f"<div style='font-size:0.7rem;color:#64748b'>out of 100</div>"
            f"<hr style='border-color:#e2e8f0;margin:10px 0'>"
            f"<div style='font-size:0.72rem;color:#64748b'>{b_data.get('region','—')} | {b_data.get('type','—')}</div>"
            f"</div>", unsafe_allow_html=True)
        st.markdown("<br><div class='section-title'>Parameter Breakdown</div>", unsafe_allow_html=True)
        for p in PARAM_META:
            v   = vals[p["key"]]
            pct = v/p["max"]*100
            st.markdown(
                f"<div style='margin-bottom:10px'>"
                f"<div style='display:flex;justify-content:space-between;font-size:0.77rem'>"
                f"<span style='font-weight:500;color:#475569'>{p['label']}</span>"
                f"<span style='font-weight:600;color:#1a1a2e'>{v}/{p['max']} ({pct:.0f}%)</span></div>"
                f"{bar_html(pct,p['color'])}</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-title'>Parameter Radar</div>", unsafe_allow_html=True)
        vals_pct = [vals[p["key"]]/p["max"]*100 for p in PARAM_META]
        st.markdown(f"<div class='chart-box'>{svg_radar(vals_pct, gc_color(grade))}</div>", unsafe_allow_html=True)
        if show_peers:
            region = b_data.get("region","")
            peers  = df[df["Region"]==region].sort_values("Total",ascending=False)
            st.markdown(f"<br><div class='section-title'>Regional Peers — {region}</div>", unsafe_allow_html=True)
            for _, row in peers.iterrows():
                is_sel = row["State/UT"]==sel
                bg = "#eff6ff" if is_sel else "transparent"
                fw = "700" if is_sel else "400"
                pc = gc_color(row["Grade"])
                st.markdown(
                    f"<div class='rank-item' style='background:{bg}'>"
                    f"<span class='rank-num'>#{row.name}</span>{badge(row['Grade'])}"
                    f"<div class='rank-name' style='font-weight:{fw}'>{row['State/UT']}</div>"
                    f"<span style='font-size:0.8rem;font-weight:600;color:{pc}'>{row['Total']:.1f}</span>"
                    f"</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  COMPARE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Compare":
    cs1,cs2 = st.columns(2)
    with cs1:
        st.markdown("<div style='font-size:0.68rem;font-weight:600;color:#185FA5;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px'>State / UT A</div>", unsafe_allow_html=True)
        sa_name = st.selectbox("A", all_states, index=0, label_visibility="collapsed")
    with cs2:
        st.markdown("<div style='font-size:0.68rem;font-weight:600;color:#bf360c;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px'>State / UT B</div>", unsafe_allow_html=True)
        sb_name = st.selectbox("B", all_states, index=min(5,len(all_states)-1), label_visibility="collapsed")

    if sa_name == sb_name:
        st.warning("Please select two different States/UTs.")
    else:
        sa, sb = scores_raw[sa_name], scores_raw[sb_name]
        va = {p["key"]: gv(sa,p["key"]) for p in PARAM_META}
        vb = {p["key"]: gv(sb,p["key"]) for p in PARAM_META}
        va["total"] = sa.get("total",0); va["grade"] = sa.get("grade","E")
        vb["total"] = sb.get("total",0); vb["grade"] = sb.get("grade","E")
        a_wins = va["total"] > vb["total"]

        cc1,cc2 = st.columns(2)
        for col, name, v, color, wins in [(cc1,sa_name,va,"#185FA5",a_wins),(cc2,sb_name,vb,"#bf360c",not a_wins)]:
            with col:
                g = v["grade"]
                winner = "<div style='font-size:0.62rem;background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7;border-radius:10px;padding:2px 8px;display:inline-block;margin-bottom:4px'>Winner</div>" if wins else "<div style='height:22px'></div>"
                bc = color if wins else "#e2e8f0"
                st.markdown(
                    f"<div style='background:#fff;border:0.5px solid {bc};border-radius:12px;padding:1.1rem;text-align:center'>"
                    f"{winner}<div style='font-size:1rem;font-weight:700;margin-bottom:6px'>{name}</div>"
                    f"{badge(g)}<div style='font-size:2.5rem;font-weight:700;color:{gc_color(g)};margin:8px 0'>{v['total']:.1f}</div>"
                    f"<div style='font-size:0.7rem;color:#94a3b8'>out of 100</div></div>", unsafe_allow_html=True)

        col_rad, col_tbl = st.columns([3,2])
        with col_rad:
            st.markdown("<div class='section-title'>Radar Comparison</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chart-box'>{svg_compare_radar(sa_name,va,sb_name,vb)}</div>", unsafe_allow_html=True)
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
            st.markdown("<div class='section-title' style='margin-top:1rem'>Parameter Bars</div>", unsafe_allow_html=True)
            for p in PARAM_META:
                av,bv = va[p["key"]],vb[p["key"]]
                pa,pb = av/p["max"]*100, bv/p["max"]*100
                st.markdown(
                    f"<div style='margin-bottom:9px'>"
                    f"<div style='font-size:0.72rem;color:#64748b;margin-bottom:3px'>{p['label']}</div>"
                    f"<div style='display:flex;align-items:center;gap:5px'>"
                    f"<span style='min-width:24px;text-align:right;font-size:0.72rem;font-weight:600;color:#185FA5'>{av}</span>"
                    f"<div style='flex:1;height:6px;background:#e2e8f0;border-radius:3px;position:relative;overflow:hidden'>"
                    f"<div style='position:absolute;right:50%;width:{pa/2:.1f}%;height:100%;background:#185FA5;border-radius:3px 0 0 3px;top:0'></div>"
                    f"<div style='position:absolute;left:50%;width:{pb/2:.1f}%;height:100%;background:#bf360c;border-radius:0 3px 3px 0;top:0'></div>"
                    f"</div>"
                    f"<span style='min-width:24px;font-size:0.72rem;font-weight:600;color:#bf360c'>{bv}</span>"
                    f"</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Heatmap":
    st.markdown("<div class='section-title'>Parameter Achievement — % of Maximum Marks</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='chart-box' style='overflow-x:auto'>{svg_heatmap(df)}</div>", unsafe_allow_html=True)
    legend_html = "<div style='display:flex;flex-wrap:wrap;gap:16px;margin-top:10px'>"
    for bg,fc,lbl in [("#a5d6a7","#1b5e20","≥ 75% — Strong"),("#b3d4f5","#0d47a1","50–74% — Moderate"),
                      ("#ffcc80","#7c4a00","30–49% — Weak"),("#f48fb1","#880e4f","< 30% — Poor")]:
        legend_html += (f"<span style='display:flex;align-items:center;gap:5px;font-size:0.72rem'>"
                        f"<span style='width:14px;height:14px;border-radius:3px;background:{bg};display:inline-block'></span>"
                        f"<span style='color:#475569'>{lbl}</span></span>")
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Trends":
    if len(data["assessments"]) < 2:
        st.info("Add at least 2 assessments to see trends.")
    else:
        tc1,tc2 = st.columns([3,1])
        sel_states = tc1.multiselect("Select States/UTs", sorted(BASELINE.keys()),
                                     default=["Punjab","Karnataka","Uttar Pradesh","Delhi","Tripura"])
        param_opts = ["Total","ra","fv","el","et","rg"]
        param_lbls = ["Total Score","Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
        param_sel  = tc2.selectbox("Parameter", param_lbls)
        param_key  = param_opts[param_lbls.index(param_sel)]

        all_dates_sorted = sorted(data["assessments"].keys())
        rows = []
        for d_key in all_dates_sorted:
            snap = data["assessments"][d_key]
            for stn in sel_states:
                sc = snap["scores"].get(stn,{})
                if sc:
                    v = sc.get("total",0) if param_key=="Total" else gv(sc,param_key)
                    rows.append({"Date":d_key,"State/UT":stn,"Value":float(v)})
        if rows:
            tdf = pd.DataFrame(rows)
            dates_list = sorted(tdf["Date"].unique().tolist())
            st.markdown(f"<div class='chart-box'>{svg_trend(tdf,sel_states,dates_list,param_sel)}</div>", unsafe_allow_html=True)

            if len(all_dates_sorted)>=2:
                chg=[]
                for state in sorted(BASELINE.keys()):
                    s1=data["assessments"][all_dates_sorted[0]]["scores"].get(state,{})
                    s2=data["assessments"][all_dates_sorted[-1]]["scores"].get(state,{})
                    if s1 and s2:
                        delta=round(s2.get("total",0)-s1.get("total",0),2)
                        chg.append({"State/UT":state,
                                    f"Score ({all_dates_sorted[0]})":s1.get("total",0),
                                    f"Score ({all_dates_sorted[-1]})":s2.get("total",0),
                                    "Delta":delta,
                                    "Direction":"Improved" if delta>0 else ("Declined" if delta<0 else "Same")})
                if chg:
                    chg_df=pd.DataFrame(chg).sort_values("Delta",ascending=False)
                    st.markdown("<br><div class='section-title'>Score Change Table</div>", unsafe_allow_html=True)
                    st.dataframe(chg_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
#  UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Upload":
    st.info("Upload a CSV with columns: State/UT, Resource Adequacy, Financial Viability, Ease of Living, Energy Transition, Regulatory Governance")
    st.download_button("⬇️ Download CSV Template", make_csv_template(), "assessment_template.csv", mime="text/csv")
    st.markdown("---")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        parsed = parse_csv_upload(uploaded)
        if parsed is None:
            st.error("Could not parse file. Check column names match the template.")
        else:
            st.success(f"Parsed {len(parsed)} states/UTs successfully!")
            prev_rows=[{"State/UT":s,"RA":sc["ra"],"FV":sc["fv"],"EL":sc["el"],
                        "ET":sc["et"],"RG":sc["rg"],"Total":sc["total"],"Grade":sc["grade"]}
                       for s,sc in parsed.items()]
            st.dataframe(pd.DataFrame(prev_rows).sort_values("Total",ascending=False),
                         use_container_width=True, height=280)
            uc1,uc2 = st.columns(2)
            up_date  = uc1.date_input("Assessment Date", value=date.today())
            up_label = uc2.text_input("Assessment Label", placeholder="e.g. ARR FY 2026-27")
            up_notes = st.text_area("Notes", placeholder="Source, methodology…")
            if st.button("💾 Save Assessment", type="primary", use_container_width=True):
                if not up_label.strip(): st.error("Please provide a label.")
                else:
                    dk=str(up_date)
                    data["assessments"][dk]={"date":dk,"label":up_label,"scores":parsed,"notes":up_notes}
                    data["audit_log"].append({"action":"file_upload","date":dk,"label":up_label,
                                              "states":len(parsed),"timestamp":datetime.now().isoformat()})
                    save_data(data); st.success(f"Saved '{up_label}' with {len(parsed)} states!"); st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
#  NEW ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "New Assessment":
    st.info("Enter updated scores for each State/UT. Totals are auto-computed.")
    with st.form("new_assessment_form"):
        nc1,nc2 = st.columns(2)
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
                n_ra=i1.number_input("RA (0-32)",0.0,32.0,float(gv(p,"ra")),0.5,key=f"{state}_ra")
                n_fv=i2.number_input("FV (0-25)",0.0,25.0,float(gv(p,"fv")),0.5,key=f"{state}_fv")
                n_el=i3.number_input("EL (0-23)",0.0,23.0,float(gv(p,"el")),0.5,key=f"{state}_el")
                n_et=i4.number_input("ET (0-15)",0.0,15.0,float(gv(p,"et")),0.5,key=f"{state}_et")
                n_rg=i5.number_input("RG (0-5)", 0.0, 5.0,float(gv(p,"rg")),0.5,key=f"{state}_rg")
                n_tot=round(n_ra+n_fv+n_el+n_et+n_rg,2)
                g_col=GRADE_COLOR.get(get_grade(n_tot),"#555")
                st.markdown(f"<div style='font-weight:600;font-size:0.84rem;color:{g_col}'>Total: {n_tot} / 100 — Grade {get_grade(n_tot)}</div>", unsafe_allow_html=True)
                new_scores[state]={"ra":n_ra,"fv":n_fv,"el":n_el,"et":n_et,"rg":n_rg,"total":n_tot,"grade":get_grade(n_tot)}
        if st.form_submit_button("💾 Save Assessment", type="primary", use_container_width=True):
            if not alabel.strip(): st.error("Please enter a label.")
            else:
                dk=str(adate)
                data["assessments"][dk]={"date":dk,"label":alabel,"scores":new_scores,"notes":anotes}
                data["audit_log"].append({"action":"new_assessment","date":dk,"label":alabel,"timestamp":datetime.now().isoformat()})
                save_data(data); st.success(f"Saved '{alabel}'!"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "History":
    st.markdown("<div class='section-title'>Assessment History</div>", unsafe_allow_html=True)
    rows_h=[]
    for d_key, snap in sorted(data["assessments"].items(), reverse=True):
        sc=snap["scores"]
        avg_h=round(sum(v.get("total",0) for v in sc.values())/max(len(sc),1),2)
        rows_h.append({"Date":d_key,"Label":snap["label"],"States":len(sc),"Avg Score":avg_h,"Notes":snap.get("notes","")[:60]})
    st.dataframe(pd.DataFrame(rows_h), use_container_width=True, hide_index=True)
    if data["audit_log"]:
        st.markdown("<br><div class='section-title'>Audit Log</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(data["audit_log"]), use_container_width=True, hide_index=True)
    st.markdown("---")
    deletable=[d for d in sorted(data["assessments"].keys()) if d!="2025-03-31"]
    if deletable:
        del_sel=st.selectbox("Delete assessment (baseline protected)", deletable)
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
