"""
CalTRANS Backtest Replay Dashboard

Run:
    streamlit run src/dashboard/backtest_demo.py
"""

from datetime import date
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────

_DATA_DIR = Path("data")

_TIER_COLOR = {
    "critical": "#e53935",
    "high":     "#FB8C00",
    "medium":   "#F9A825",
    "low":      "#43A047",
}
_TIER_RADIUS = {"critical": 10, "high": 8, "medium": 6, "low": 4}
_TIER_ORDER  = ["critical", "high", "medium", "low"]

# District display names — all 12 CalTRANS districts with zone counts
_DISTRICT_NAMES = {
    0:  "All California",
    1:  "D1 — North Coast",
    2:  "D2 — Shasta / Lassen",
    3:  "D3 — Sacramento Valley",
    4:  "D4 — Bay Area",
    5:  "D5 — Central Coast",
    6:  "D6 — Fresno / San Joaquin",
    7:  "D7 — Los Angeles",
    8:  "D8 — San Bernardino / Riverside",
    9:  "D9 — Eastern Sierra",
    10: "D10 — Stockton / Modesto",
    11: "D11 — San Diego",
    12: "D12 — Orange County",
}

# District fit_bounds: [[sw_lat, sw_lng], [ne_lat, ne_lng]] from GeoJSON
_DISTRICT_BOUNDS = {
    0:  [[32.53, -124.48], [42.00, -114.13]],  # All CA
    1:  [[38.67, -124.48], [42.00, -122.34]],
    2:  [[39.60, -123.72], [42.01, -120.00]],
    3:  [[38.02, -122.94], [40.15, -119.88]],
    4:  [[36.89, -123.63], [38.86, -121.21]],
    5:  [[34.33, -122.32], [37.29, -119.44]],
    6:  [[34.79, -120.92], [37.78, -117.98]],
    7:  [[33.66, -119.50], [34.90, -117.65]],
    8:  [[33.43, -117.80], [35.81, -114.13]],
    9:  [[34.82, -119.65], [38.71, -115.65]],
    10: [[36.74, -121.58], [38.93, -119.20]],
    11: [[32.53, -117.61], [33.51, -114.46]],
    12: [[33.33, -118.13], [33.95, -117.41]],
}

_AVAILABLE_DATES = sorted(
    p.stem.replace("CA_backtest_", "")
    for p in _DATA_DIR.glob("CA_backtest_2026-01-*.csv")
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _weekday_label(s: str) -> str:
    return date.fromisoformat(s).strftime("%A")

def _worst_tier(tiers) -> str:
    for t in _TIER_ORDER:
        if t in tiers.values:
            return t
    return "low"

# ──────────────────────────────────────────────────────────────────────────────
# Page
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CalTRANS Risk Forecast — Backtest Replay",
    page_icon="🚦",
    layout="wide",
)

st.markdown("""
<style>
    /* Hide default Streamlit top bar and reduce padding */
    [data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0.5rem !important; }
    [data-testid="metric-container"] { padding: 4px 0 !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: #888 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.72rem !important; }
    hr { margin: 0.35rem 0 !important; }
    .section-label { font-size:0.8rem; font-weight:600; color:#ccc;
                     text-transform:uppercase; letter-spacing:.05em; margin-bottom:2px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='font-size:1.7rem;font-weight:800;letter-spacing:.01em;"
        "color:#fff;line-height:1.1;padding:4px 0 2px'>RoadIQ</div>"
        "<div style='font-size:0.85rem;color:#aaa;margin-bottom:8px'>"
        "Crash Predictive System</div>",
        unsafe_allow_html=True,
    )
    st.title("Backtest Replay")
    st.caption("California — January 2026")
    st.divider()

    if not _AVAILABLE_DATES:
        st.error("No backtest files found in data/")
        st.stop()

    district_id = st.selectbox(
        "District",
        options=list(_DISTRICT_NAMES.keys()),
        index=0,
        format_func=lambda d: _DISTRICT_NAMES[d],
    )

    st.divider()

    selected_date_str = st.selectbox(
        "Select date (January 2026)",
        options=_AVAILABLE_DATES,
        index=9,
        format_func=lambda s: f"{s}  ({_weekday_label(s)})",
    )

    st.divider()

    view_mode = st.radio(
        "Map view",
        options=["Prediction", "Reality check"],
        index=0,
        help=(
            "**Prediction** — zones colored by model risk tier (what the model "
            "forecast that morning).\n\n"
            "**Reality check** — zones where crashes actually occurred keep their "
            "tier color; zones with no crashes turn grey."
        ),
    )

    st.divider()

    hour_filter = st.slider(
        "Filter by hour of day",
        min_value=0, max_value=23, value=(0, 23), step=1,
        format="%d:00",
    )

    st.divider()
    st.caption(
        "Data: CA crashes 2023–2025 (train) + Jan 2026 (holdout)."
    )

# ──────────────────────────────────────────────────────────────────────────────
# Load & filter
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_day(date_str: str) -> pd.DataFrame:
    path = _DATA_DIR / f"CA_backtest_{date_str}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["risk_tier"] = df["risk_tier"].fillna("low")
    return df


@st.cache_data(show_spinner=False)
def load_all_days() -> pd.DataFrame:
    """Load all 31 days from data/ — used for cross-day zone reliability stats."""
    frames = []
    for d in _AVAILABLE_DATES:
        path = _DATA_DIR / f"CA_backtest_{d}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df["risk_tier"] = df["risk_tier"].fillna("low")
            df["date"] = d
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(show_spinner=False)
def compute_zone_reliability(dist_id: int) -> pd.DataFrame:
    """
    Per zone: crash_days (any tier), hits (model in tier AND crash occurred).
    Sorted by hits descending.
    """
    all_days = load_all_days()
    filtered = all_days if dist_id == 0 else all_days[all_days["district_id"] == float(dist_id)]

    # Total crash days per zone across all tiers
    crash_days = (
        filtered.groupby(["hotspot_id", "primary_road", "date"])["crash_occurred"]
        .max().reset_index()
        .groupby(["hotspot_id", "primary_road"])["crash_occurred"]
        .sum().reset_index()
        .rename(columns={"crash_occurred": "crash_days"})
    )

    # Hits: zone was in critical/high/medium AND a crash occurred that day
    sub = filtered[filtered["risk_tier"].isin(["critical", "high", "medium"])]
    hits = (
        sub.groupby(["hotspot_id", "primary_road", "date"])["crash_occurred"]
        .max().reset_index()
        .groupby(["hotspot_id", "primary_road"])["crash_occurred"]
        .sum().reset_index()
        .rename(columns={"crash_occurred": "hits"})
    )

    stats = crash_days.merge(hits, on=["hotspot_id", "primary_road"], how="left")
    stats["hits"] = stats["hits"].fillna(0).astype(int)
    return stats.sort_values("hits", ascending=False)


df_all = load_day(selected_date_str)
if df_all.empty:
    st.error(f"No data for {selected_date_str}.")
    st.stop()

# Apply district filter
if district_id != 0:
    df_all = df_all[df_all["district_id"] == float(district_id)].copy()

df = df_all[
    (df_all["slot_hour"] >= hour_filter[0]) &
    (df_all["slot_hour"] <= hour_filter[1])
].copy()

df_map = df[df["risk_tier"] != "low"]

zone_summary = (
    df_map
    .groupby(["hotspot_id", "center_lat", "center_lng", "primary_road"], dropna=False)
    .agg(
        worst_tier=("risk_tier",      lambda s: _worst_tier(s)),
        max_score  =("risk_score",    "max"),
        any_crash  =("crash_occurred","max"),
        n_slots    =("slot_hour",     "count"),
        n_crashes  =("crash_occurred","sum"),
    )
    .reset_index()
)

# ──────────────────────────────────────────────────────────────────────────────
# Compute stats (used in header + right panel)
# ──────────────────────────────────────────────────────────────────────────────

n_pos       = int(df["crash_occurred"].sum())
n_slots     = len(df)
total_zones = df["hotspot_id"].nunique()
dow         = _weekday_label(selected_date_str)
hour_label  = ("All hours" if hour_filter == (0, 23)
               else f"{hour_filter[0]:02d}:00 – {hour_filter[1]:02d}:00")

# Zone-level stats: same unit as map (one zone = one point, worst tier wins)
# A zone "has crash" if any slot in the selected hour window had crash_occurred=1
zone_stats = (
    df[df["risk_tier"] != "low"]
    .groupby("hotspot_id")
    .agg(
        worst_tier    =("risk_tier",      lambda s: _worst_tier(s)),
        any_crash     =("crash_occurred", "max"),
    )
    .reset_index()
)
global_rate = zone_stats["any_crash"].mean() if len(zone_stats) > 0 else 0.045

# ──────────────────────────────────────────────────────────────────────────────
# Thin header bar — date + context only, no numbers (numbers are in right panel)
# ──────────────────────────────────────────────────────────────────────────────

district_label = _DISTRICT_NAMES.get(district_id, "California")
st.markdown(
    f"<div style='line-height:1.3;padding:2px 0 4px'>"
    f"<span style='font-size:1.15rem;font-weight:700'>{selected_date_str}</span>"
    f"&nbsp;&nbsp;<span style='color:#888;font-size:0.9rem'>{dow}</span>"
    f"&nbsp;&nbsp;·&nbsp;&nbsp;"
    f"<span style='color:#888;font-size:0.85rem'>{district_label}</span>"
    f"&nbsp;&nbsp;·&nbsp;&nbsp;"
    f"<span style='color:#888;font-size:0.85rem'>{hour_label}</span>"
    f"</div>",
    unsafe_allow_html=True,
)
st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Build Folium map — one layer, colors determined by current view_mode.
# view_mode IS part of the cache key so the map rebuilds when it changes,
# but NOT when unrelated widgets change.  The map HTML is embedded via
# components.html() so Streamlit does not recreate the iframe on every rerun —
# only when map_html itself changes (i.e. the cache key changes).
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _load_districts_geojson() -> dict:
    path = _DATA_DIR / "Caltrans_Districts.geojson"
    if not path.exists():
        return {}
    import json
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def _build_map_html(zone_rows: tuple, is_reality: bool, dist_id: int) -> str:
    bounds = _DISTRICT_BOUNDS.get(dist_id, _DISTRICT_BOUNDS[0])
    # Start with a rough center; fit_bounds JS will adjust after render
    center = [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2]
    m = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")
    m.fit_bounds(bounds)

    # District boundary overlay — no tooltip, no popup
    gj = _load_districts_geojson()
    if gj:
        if dist_id != 0:
            features = [f for f in gj["features"]
                        if int(f["properties"]["DISTRICT"]) == dist_id]
            gj_filtered = {**gj, "features": features}
        else:
            gj_filtered = gj

        folium.GeoJson(
            gj_filtered,
            style_function=lambda _: {
                "color":       "#2563eb",
                "weight":      2,
                "fillOpacity": 0.03,
                "fillColor":   "#2563eb",
            },
            highlight_function=lambda _: {
                "color":       "#2563eb",
                "weight":      2,
                "fillOpacity": 0.03,
            },
        ).add_to(m)

    for row in zone_rows:
        tier      = row["worst_tier"]
        has_crash = bool(row["any_crash"])
        lat, lng  = row["center_lat"], row["center_lng"]
        road      = row.get("primary_road") or "Unknown road"
        score     = row["max_score"]
        n_c, n_s  = int(row["n_crashes"]), int(row["n_slots"])
        prec_str  = f"{n_c}/{n_s} zone-hours had crashes" if n_s > 0 else "—"

        popup_html = (
            f"<b>{road}</b><br>"
            f"Zone {int(row['hotspot_id'])} · Tier: <b>{tier.upper()}</b><br>"
            f"Score: {score:.3f}<br>{prec_str}"
        )
        tooltip = f"{road} — {'CRASH ✓' if (is_reality and has_crash) else tier.upper()}"

        if not is_reality:
            fc, fo = _TIER_COLOR[tier], 0.78
            sc, wt = _TIER_COLOR[tier], 1
        else:
            if has_crash:
                fc, fo = _TIER_COLOR[tier], 0.92
                sc, wt = "#ffffff", 2
            else:
                fc, fo = "#aaaaaa", 0.20
                sc, wt = "#999999", 0.5

        folium.CircleMarker(
            location=[lat, lng],
            radius=_TIER_RADIUS[tier],
            color=sc, weight=wt,
            fill=True, fill_color=fc, fill_opacity=fo,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=tooltip,
        ).add_to(m)

    legend_rows = "".join(
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:4px">'
        f'<span style="display:inline-block;width:13px;height:13px;border-radius:50%;'
        f'flex-shrink:0;background:{_TIER_COLOR[t]}"></span>'
        f'<span style="color:#111;font-size:13px">{t.capitalize()}</span></div>'
        for t in ["critical", "high", "medium"]
    )
    if is_reality:
        legend_rows += (
            '<div style="border-top:1px solid #ccc;margin:6px 0 5px"></div>'
            '<div style="display:flex;align-items:center;gap:7px">'
            '<span style="display:inline-block;width:13px;height:13px;border-radius:50%;'
            'flex-shrink:0;background:#aaa;opacity:.45"></span>'
            '<span style="color:#111;font-size:13px">No crash</span></div>'
        )

    legend_js = f"""
    <script>
    (function waitForLeaflet() {{
        if (typeof L === 'undefined') {{ setTimeout(waitForLeaflet, 100); return; }}
        var legend = L.control({{position: 'bottomleft'}});
        legend.onAdd = function() {{
            var div = L.DomUtil.create('div');
            div.style.cssText = 'background:rgba(255,255,255,0.96);padding:10px 14px;'
                + 'border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.25);'
                + 'font-family:sans-serif;pointer-events:none';
            div.innerHTML = '<div style="font-weight:700;color:#111;font-size:13px;'
                + 'margin-bottom:7px">Risk tier</div>{legend_rows}';
            return div;
        }};
        var mapDivs = document.querySelectorAll('.folium-map');
        if (mapDivs.length) {{
            var mapId = mapDivs[0].id;
            if (window[mapId]) legend.addTo(window[mapId]);
        }}
    }})();
    </script>
    """
    m.get_root().html.add_child(folium.Element(legend_js))
    return m._repr_html_()


_zone_rows  = tuple(zone_summary.to_dict(orient="records"))
_is_reality = (view_mode == "Reality check")
map_html    = _build_map_html(_zone_rows, _is_reality, district_id)

# Pre-compute stats shared across panels

# Cross-day reliability: zones most consistently hit across all 31 days
_reliability = compute_zone_reliability(district_id)

# Today's crash status per zone (max over all hours of the day)
today_crash = (
    df_all.groupby("hotspot_id")["crash_occurred"].max().reset_index()
    .rename(columns={"crash_occurred": "today_crash"})
)
top10_reliability = (
    _reliability.head(10)
    .merge(today_crash, on="hotspot_id", how="left")
)
top10_reliability["today_crash"] = top10_reliability["today_crash"].fillna(0)
top10 = top10_reliability[["primary_road", "crash_days", "hits", "today_crash"]].rename(
    columns={
        "primary_road": "Road",
        "crash_days":   "Crash days",
        "hits":         "Hits",
        "today_crash":  "Today?",
    }
)
top10["Today?"] = top10["Today?"].map({1.0: "✅", 0.0: "—"})

hourly = (
    df_all
    .groupby("slot_hour")
    .agg(crash_rate=("crash_occurred", "mean"),
         avg_score  =("risk_score",    "mean"))
    .reset_index()
    .rename(columns={"crash_rate": "Actual crash rate",
                     "avg_score":  "Avg predicted score"})
)

# ──────────────────────────────────────────────────────────────────────────────
# Layout
#
#  ┌─────────────────────────────────┬──────────────────┐
#  │  map_col  (ratio 3.2)           │  right_col (1)   │
#  │  ┌─────────────────────────┐    │  Top-10 table    │
#  │  │  map  (650 px)          │    │                  │
#  │  └─────────────────────────┘    │  Hourly chart    │
#  │  ┌──────────────┬──────────┐    │                  │
#  │  │ Day summary  │ Legend   │    │                  │
#  │  └──────────────┴──────────┘    │                  │
#  └─────────────────────────────────┴──────────────────┘
#  ┌─────────────────────────────────────────────────────┐
#  │  Tier precision table  │  Crash capture table       │
#  └─────────────────────────────────────────────────────┘
# ──────────────────────────────────────────────────────────────────────────────

map_col, right_col = st.columns([3.2, 1])

# ── Left column: map + sub-row ────────────────────────────────────────────────
with map_col:
    mode_badge = (
        '<span style="background:#1565C0;color:#fff;border-radius:4px;'
        'padding:2px 8px;font-size:0.78rem;font-weight:600">🔮 Prediction</span>'
        if not _is_reality else
        '<span style="background:#2e7d32;color:#fff;border-radius:4px;'
        'padding:2px 8px;font-size:0.78rem;font-weight:600">✅ Reality check</span>'
    )
    st.markdown(mode_badge, unsafe_allow_html=True)
    components.html(map_html, height=620, scrolling=False)

    # Sub-row: Day summary (left) + Legend (right), both in two columns
    sub_left, sub_right = st.columns([2, 1])

    # ── Day summary ───────────────────────────────────────────────────────────
    with sub_left:
        st.markdown('<div class="section-label">Day summary</div>', unsafe_allow_html=True)

        def _chip(label, value, sub, color=None):
            c = f"color:{color};" if color else ""
            return (
                f"<div style='display:inline-block;margin:0 12px 8px 0;line-height:1.25'>"
                f"<span style='font-size:0.78rem;color:#888;text-transform:uppercase;"
                f"letter-spacing:.04em;display:block'>{label}</span>"
                f"<span style='font-size:1.25rem;font-weight:700;{c}'>{value}</span>"
                f"<span style='font-size:0.85rem;color:#aaa;display:block'>{sub}</span>"
                f"</div>"
            )

        html_chips = _chip(
            "Crashes recorded", f"{n_pos:,}",
            f"{n_slots:,} zone-hour slots",
        )
        for tier in ["critical", "high", "medium"]:
            tier_zones = zone_stats[zone_stats["worst_tier"] == tier]
            n    = len(tier_zones)
            c    = int(tier_zones["any_crash"].sum())
            prec = c / n if n > 0 else 0.0
            lift = prec / global_rate if global_rate > 0 else 0.0
            html_chips += _chip(
                f"{tier.capitalize()} zones",
                f"{n:,}",
                f"{prec*100:.1f}% hit · {lift:.1f}×",
                color=_TIER_COLOR[tier],
            )

        # Wrap in a flex row that wraps onto two lines naturally
        st.markdown(
            f"<div style='display:flex;flex-wrap:wrap;padding-top:6px'>{html_chips}</div>",
            unsafe_allow_html=True,
        )

    # ── Legend ────────────────────────────────────────────────────────────────
    with sub_right:
        st.markdown('<div class="section-label">Legend</div>', unsafe_allow_html=True)

        legend_chips = ""
        for t in ["critical", "high", "medium"]:
            legend_chips += (
                f"<div style='display:inline-flex;align-items:center;gap:5px;"
                f"margin:0 12px 6px 0'>"
                f"<span style='display:inline-block;width:13px;height:13px;"
                f"border-radius:50%;background:{_TIER_COLOR[t]};flex-shrink:0'></span>"
                f"<span style='font-size:0.85rem;color:#ddd'>{t.capitalize()}</span>"
                f"</div>"
            )
        if _is_reality:
            legend_chips += (
                "<div style='display:inline-flex;align-items:center;gap:5px;"
                "margin:0 12px 6px 0'>"
                "<span style='display:inline-block;width:13px;height:13px;"
                "border-radius:50%;background:#aaa;opacity:.5;flex-shrink:0'></span>"
                "<span style='font-size:0.85rem;color:#ddd'>No crash</span>"
                "</div>"
            )
        mode_desc = (
            "<span style='font-size:0.75rem;color:#aaa;display:block;margin-bottom:6px'>"
            + ("Zones colored by predicted risk tier (top 20%)." if not _is_reality
               else "Crash zones keep tier color. No-crash zones are grey.")
            + "</span>"
        )
        st.markdown(
            f"<div style='padding-top:6px'>{mode_desc}"
            f"<div style='display:flex;flex-wrap:wrap'>{legend_chips}</div></div>",
            unsafe_allow_html=True,
        )

# ── Right column: Top-10 + hourly chart ──────────────────────────────────────
with right_col:
    st.markdown('<div class="section-label">Top-10 most consistently hit zones (Jan 2026)</div>',
                unsafe_allow_html=True)
    st.dataframe(top10, hide_index=True, use_container_width=True, height=390)

    st.divider()

    st.markdown('<div class="section-label">Hourly: crash rate vs. score</div>',
                unsafe_allow_html=True)
    st.line_chart(
        hourly.set_index("slot_hour")[["Actual crash rate", "Avg predicted score"]],
        height=230,
        color=["#e53935", "#1565C0"],
    )

# ──────────────────────────────────────────────────────────────────────────────
# Bottom row: two metric tables
# ──────────────────────────────────────────────────────────────────────────────

st.divider()
tbl_left, tbl_right = st.columns(2)

with tbl_left:
    st.markdown(
        '<div class="section-label">Tier precision — how often predicted zones had crashes</div>',
        unsafe_allow_html=True,
    )
    prec_rows = []
    for tier in ["critical", "high", "medium"]:
        tier_zones = zone_stats[zone_stats["worst_tier"] == tier]
        n    = len(tier_zones)
        c    = int(tier_zones["any_crash"].sum())
        prec = c / n if n > 0 else 0.0
        lift = prec / global_rate if global_rate > 0 else 0.0
        prec_rows.append({
            "Tier":                 tier.capitalize(),
            "Predicted zones":      n,
            "Zones with crash":     c,
            "Precision (hit rate)": f"{prec*100:.1f}%",
            "Lift vs. baseline":    f"{lift:.1f}×",
        })
    st.dataframe(pd.DataFrame(prec_rows), hide_index=True, use_container_width=True)

with tbl_right:
    st.markdown(
        '<div class="section-label">Crash capture — share of real crashes caught per tier</div>',
        unsafe_allow_html=True,
    )
    # Total zones with crash (across all tiers, for denominator)
    total_crash_zones = int(zone_stats["any_crash"].sum()) + int(
        (df[df["risk_tier"] == "low"].groupby("hotspot_id")["crash_occurred"].max() == 1).sum()
    )
    cap_rows, cumul = [], 0
    for tier in ["critical", "high", "medium"]:
        tier_zones = zone_stats[zone_stats["worst_tier"] == tier]
        c      = int(tier_zones["any_crash"].sum())
        cumul += c
        denom   = total_crash_zones if total_crash_zones > 0 else 1
        pct     = c     / denom * 100
        cum_pct = cumul / denom * 100
        cap_rows.append({
            "Tier":                  tier.capitalize(),
            "Zones with crash":      c,
            "% of day's crashes":    f"{pct:.1f}%",
            "Cumulative (top→down)": f"{cum_pct:.1f}%",
        })
    st.dataframe(pd.DataFrame(cap_rows), hide_index=True, use_container_width=True)
