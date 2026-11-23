"""CIVITAS - an interactive Python Smart City Simulator (CP Lab CL1010).

Run: python -m streamlit run app.py
All calculations are performed in city_engine.py, not in JavaScript.
"""
from __future__ import annotations

import copy
import csv
from html import escape
import io
import json

import plotly.graph_objects as go
import streamlit as st

from city_engine import (
    DEMO, TRAFFIC_THRESHOLDS, WATER_LITRES_PER_PERSON,
    calculate_city, forecast_alerts, forecast_city, validate_city,
)
from reports import create_pdf_report

NAVY = "#22223B"
SLATE = "#4A4E69"
MAUVE = "#9A8C98"
ROSE = "#C9ADA7"
CREAM = "#F2E9E4"

st.set_page_config(page_title="CIVITAS | Smart City Simulator",
                   page_icon="🏙️", layout="wide",
                   initial_sidebar_state="expanded")

# These CSS overrides implement Ibrahim's exact five-colour theme.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family:'DM Sans',sans-serif; }
[data-testid="stAppViewContainer"] { background: #F2E9E4; }
[data-testid="stSidebar"] { background: #22223B !important; }
[data-testid="stSidebar"] * { color:#F2E9E4; }
[data-testid="stSidebar"] input {color:#22223B!important;-webkit-text-fill-color:#22223B!important;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {color:#F2E9E4!important;}
[data-testid="stSidebar"] [role="radiogroup"] label {background:rgba(242,233,228,.07); padding:10px 12px; border-radius:12px; margin:1px 0; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background:rgba(242,233,228,.17);}
[data-testid="stSidebar"] [data-testid="stFileUploader"] { border-radius:12px; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] * {color:#F2E9E4!important;}
section[data-testid="stMain"] > div { padding-top:1.8rem; }
.block-container {max-width:1340px; padding-top:1.1rem; padding-bottom:3rem;}
h1,h2,h3,h4,h5 {font-family:'Outfit','DM Sans',sans-serif!important; color:#22223B!important; letter-spacing:-.025em;}
h1 {font-weight:800!important;} p {color:#4A4E69;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e7dcd8; padding:18px 20px; border-radius:18px; box-shadow:0 7px 25px rgba(34,34,59,.035);}
[data-testid="stMetricLabel"] {color:#4A4E69!important; font-size:.9rem;}
[data-testid="stMetricValue"] {color:#22223B!important; font-family:'Outfit',sans-serif;font-size:clamp(1.1rem,1.7vw,1.7rem)!important;}
[data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px; }
[data-testid="stForm"], [data-testid="stExpander"] {background:#fff;border-radius:16px;border-color:#e5d7d3;}
[data-testid="stDataFrame"] {border-radius:14px;overflow:hidden;}
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] {background:#4A4E69!important;color:#fff!important;border:none!important;border-radius:12px!important;padding:10px 18px!important;}
.stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover{background:#22223B!important;}
.stButton button, .stDownloadButton button {border-radius:12px!important;}
.stTabs [data-baseweb="tab"] {font-family:'Outfit',sans-serif; font-weight:650;}
.hero {position:relative;overflow:hidden;min-height:245px; border-radius:23px; padding:30px 34px; background:linear-gradient(113deg,#22223B 3%,#4A4E69 80%); color:#F2E9E4; margin:8px 0 23px;}
.hero::after {content:"";position:absolute;bottom:-105px;right:-60px;width:480px;height:360px;border:1px solid rgba(242,233,228,.13);border-radius:50%;box-shadow:0 0 0 60px rgba(242,233,228,.025),0 0 0 130px rgba(242,233,228,.028);pointer-events:none;}
.hero .eyebrow {font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:800;color:#C9ADA7;}
.hero h1 {font-size:clamp(34px,4.2vw,56px);color:#F2E9E4!important;line-height:1.05;margin:11px 0 9px;}
.hero p {max-width:570px;color:#f2e9e4c9;font-size:15px;line-height:1.6;}
.hero .spot {display:inline-flex;border:1px solid #C9ADA7; color:#F2E9E4;border-radius:99px;padding:6px 13px;font-size:12px;margin-top:16px;}
.eyebrow {text-transform:uppercase;letter-spacing:2.4px;font-size:11px;color:#9A8C98;font-weight:800;}
.section-heading {font-size:21px;font-weight:800;margin:22px 0 13px;color:#22223B;font-family:'Outfit',sans-serif;letter-spacing:-.5px;}
.panel {background:#fff;padding:20px 23px;border-radius:17px;border:1px solid #e8dbd7;box-shadow:0 7px 25px rgba(34,34,59,.035);margin:6px 0 17px;}
.panel h3 {margin-top:0!important;}
.note {font-size:13px;color:#4A4E69;background:rgba(201,173,167,.24);padding:14px 16px;border-radius:12px;border-left:3px solid #9A8C98;margin-top:8px;margin-bottom:14px;}
.pill {display:inline-block;font-size:12px;font-weight:800;border-radius:99px;background:#F2E9E4;color:#4A4E69;padding:5px 13px;}
.footnote {font-size:12px;color:#9A8C98;margin-top:12px;}
.brand {font-family:'Outfit',sans-serif;font-size:28px;font-weight:800;letter-spacing:1px;color:#F2E9E4;margin-top:8px;}
.brand span {color:#C9ADA7;}
.brand-sub {font-size:11px;color:#C9ADA7;letter-spacing:2px;text-transform:uppercase;margin-bottom:25px;}
.side-caption {font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#C9ADA7!important;margin:15px 0 7px;}
[data-testid="stSidebar"] .stButton button {border:1px solid #9A8C98;background:#4A4E69;color:#F2E9E4;}
[data-testid="stSidebar"] .stDownloadButton button {border:1px solid #9A8C98;background:#4A4E69;color:#F2E9E4;}
@media(max-width:850px){.hero{padding:25px;min-height:210px}.hero h1{font-size:36px}}
</style>
""", unsafe_allow_html=True)


# Session state persists inputs even when the user navigates to other pages.
def start_session():
    # Apply changes before rendering widgets, avoiding Streamlit's restriction
    # on changing widget state after a widget has been instantiated.
    if "pending_scenario" in st.session_state:
        st.session_state.inputs = st.session_state.pop("pending_scenario")
        for key in list(st.session_state.keys()):
            if key.startswith("field_"):
                del st.session_state[key]
    if "inputs" not in st.session_state:
        st.session_state.inputs = copy.deepcopy(DEMO)
    if "page" not in st.session_state:
        st.session_state.page = "Overview"


def apply_scenario(new_values: dict):
    st.session_state.pending_scenario = validate_city(new_values)


def save_control(name):
    st.session_state.inputs[name] = st.session_state[f"field_{name}"]


def field(name, label, *, integer=False, minimum=0.0, maximum=None,
          step=None, help_text=None):
    key = f"field_{name}"
    if key not in st.session_state:
        st.session_state[key] = st.session_state.inputs[name]
    if integer:
        return st.number_input(label, min_value=int(minimum),
                               max_value=int(maximum) if maximum is not None else None,
                               step=int(step or 1), key=key, help=help_text,
                               on_change=save_control, args=(name,))
    return st.number_input(label, min_value=float(minimum) if minimum is not None else None,
                           max_value=float(maximum) if maximum is not None else None,
                           step=float(step or 1), key=key, help=help_text,
                           on_change=save_control, args=(name,))


def city_title(label, desc, eyebrow="CITY OPERATIONS"):
    st.markdown(f"<div class='eyebrow'>{escape(eyebrow)}</div>", unsafe_allow_html=True)
    st.title(label)
    st.caption(desc)


def note(message):
    st.markdown(f"<div class='note'>{escape(message)}</div>", unsafe_allow_html=True)


def section(label):
    st.markdown(f"<div class='section-heading'>{escape(label)}</div>", unsafe_allow_html=True)


def fmt(value, decimal=0):
    return f"{value:,.{decimal}f}"


def chart_layout(fig, height=310):
    fig.update_layout(height=height, margin=dict(l=10, r=15, t=20, b=15),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=SLATE, family="DM Sans"),
                      legend=dict(orientation="h", y=1.12),
                      hoverlabel=dict(bgcolor=CREAM, font_color=NAVY))
    fig.update_xaxes(showgrid=False, linecolor="#dfd1ce", zeroline=False)
    fig.update_yaxes(gridcolor="#e8deda", zeroline=False)
    return fig


def graph(fig):
    st.plotly_chart(chart_layout(fig), width="stretch",
                    config={"displayModeBar": False})


def quick_overview(result):
    t, w, b, r = result["traffic"], result["water"], result["construction"], result["waste"]
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: st.metric("🚗 Traffic density", f"{t['density']:,.1f} veh/km", t["condition"], delta_color="off")
    with c2: st.metric("💧 Water balance", f"{w['balance_lpd']/1e6:+,.2f}M L", w["status"], delta_color="off")
    with c3: st.metric("🏗️ Building budget", f"PKR {b['total_cost_pkr']/1e6:,.1f}M")
    with c4: st.metric("♻️ Daily waste", f"{r['total_kgpd']/1000:,.1f} tonnes")


def render_sidebar():
    st.sidebar.markdown("<div class='brand'>CIVI<span>TAS</span> /</div><div class='brand-sub'>Smart City Simulator • Python</div>",
                        unsafe_allow_html=True)
    pages = ["Overview", "Traffic Management", "Water Supply", "Construction Estimator",
             "Waste Management", "Future Planning", "Scenario Lab", "City Report"]
    icons = ["▦", "🚗", "💧", "🏗️", "♻️", "📈", "⚖️", "📋"]
    st.sidebar.markdown("<div class='side-caption'>Navigate</div>", unsafe_allow_html=True)
    page = st.sidebar.radio("Modules", pages, key="page",
                            format_func=lambda p: f"{icons[pages.index(p)]}  {p}",
                            label_visibility="collapsed")
    st.sidebar.markdown("<div class='side-caption'>City workspace</div>", unsafe_allow_html=True)
    if "field_city_name" not in st.session_state:
        st.session_state.field_city_name = st.session_state.inputs["city_name"]
    st.sidebar.text_input("City name", key="field_city_name", on_change=save_control,
                          args=("city_name",))
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Load demo", width="stretch"):
            apply_scenario(DEMO)
            st.rerun()
    with col2:
        if st.button("Reset city", width="stretch"):
            # A valid minimal blank slate; users can overwrite each field.
            blank = dict(DEMO, city_name="New City", vehicles=0, population=1,
                         available_water_lpd=0, recycling_percentage=0)
            apply_scenario(blank)
            st.rerun()
    st.sidebar.download_button("↓ Export scenario JSON",
        data=json.dumps(st.session_state.inputs, indent=2),
        file_name="civitas_city_scenario.json", mime="application/json",
        width="stretch")
    with st.sidebar.expander("Import a scenario"):
        uploaded = st.file_uploader("Upload saved .json", type=["json"])
        if uploaded is not None and st.button("Import file", width="stretch"):
            try:
                if uploaded.size > 1_000_000:
                    raise ValueError("File is too large.")
                imported = json.loads(uploaded.getvalue().decode("utf-8"))
                apply_scenario(imported)
                st.rerun()
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                st.error(f"Could not import scenario: {error}")
    st.sidebar.markdown("<div class='footnote' style='color:#C9ADA7'>CL1010 • CP Lab<br>Python functions • Validation • Decision logic</div>",
                        unsafe_allow_html=True)
    return page


def overview(result, rows):
    city = escape(result["inputs"]["city_name"])
    score = result["health"]
    st.markdown(f"""<div class="hero"><div class="eyebrow">COMMAND OVERVIEW / PYTHON SIMULATOR</div>
        <h1>A smarter future<br>for {city}.</h1>
        <p>One connected workspace for roads, water, construction, and recycling.
        Explore the numbers, test decisions, and build a more resilient city.</p>
        <div class="spot">◆ City health index&nbsp; <b>{score['score']:.1f} / 100</b> &nbsp;·&nbsp; {score['label']}</div>
        </div>""", unsafe_allow_html=True)
    quick_overview(result)
    section("CITY INTELLIGENCE")
    c1, c2 = st.columns([1.18, 1], gap="large")
    with c1:
        with st.container(border=True):
            st.markdown("**Infrastructure pressure · today vs year-end**")
            t = result["traffic"]
            w = result["water"]
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Current", x=["Traffic density", "Water coverage", "Recycling"],
                y=[min(t["density"], 130), min(w["coverage_pct"], 130), result["waste"]["recycling_percentage"]],
                marker_color=SLATE))
            fig.add_trace(go.Bar(name="Year-end", x=["Traffic density", "Water coverage", "Recycling"],
                y=[min(rows[-1]["traffic_density"], 130),
                   min(rows[-1]["water_supply_lpd"] / rows[-1]["water_demand_lpd"]*100, 130),
                   rows[-1]["recycling_pct"]], marker_color=ROSE))
            fig.update_layout(barmode="group", yaxis_title="Mixed indicators (see note)")
            graph(fig)
            st.caption("Comparative display only: traffic = vehicles/km; water coverage and recycling = %. Different units are not a combined score.")
    with c2:
        with st.container(border=True):
            st.markdown("**Priority actions**")
            for item in result["recommendations"]:
                st.markdown(f"- {item}")
            st.divider()
            st.markdown(f"**City status:** {score['label']} · {score['score']:.1f}/100")
            st.progress(min(1.0, score["score"] / 100))
            st.caption("The city health index is an illustrative educational score, not live sensor data.")
    section("EXPLORE THE WORKSPACE")
    st.markdown("Each module accepts editable inputs. Changes appear in the dashboard and final report automatically.")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("🚦 **Traffic:** calculate density, classify congestion, and recommend actions.")
    with c2: st.info("💦 **Water:** calculate 135 L/person demand and check the supply gap.")
    with c3: st.info("📑 **Reports:** get a formatted PDF and compare future scenarios.")


def traffic_page(result):
    city_title("Traffic management", "Make congestion measurable, understandable, and actionable.")
    l, r = st.columns([0.9, 1.1], gap="large")
    with l:
        with st.container(border=True):
            section("Road inputs")
            field("vehicles", "Number of vehicles", integer=True, maximum=10000000000, step=100,
                  help_text="Number of vehicles observed in the specified road section.")
            field("road_length_km", "Total road length (km)", minimum=0.001, step=1.0,
                  help_text="We define density as vehicles divided by kilometres of road.")
            note("Assumption: traffic density = number of vehicles / road length. The four category thresholds are user-defined classroom rules because the brief does not specify them.")
            st.markdown("**Classification boundaries**")
            st.markdown("Low ≤ 25 · Moderate 25–60 · High 60–100 · Critical > 100 vehicles/km")
    with r:
        with st.container(border=True):
            t = result["traffic"]
            st.metric("Measured density", f"{t['density']:,.2f} vehicles/km", t["condition"])
            gauge = go.Figure(go.Indicator(mode="gauge+number", value=min(t["density"], 150),
                number=dict(suffix=" veh/km"),
                gauge=dict(axis=dict(range=[0, 150], tickvals=[0, 25, 60, 100, 150]),
                           bar=dict(color=SLATE, thickness=.37),
                           steps=[dict(range=[0,25], color=CREAM),
                                  dict(range=[25,60], color="#e2d1cd"),
                                  dict(range=[60,100], color=ROSE),
                                  dict(range=[100,150], color=MAUVE)])))
            graph(gauge)
            st.markdown(f"**Traffic condition:** {t['condition']}")
            st.info(f"**Recommended action:** {t['action']}")


def water_page(result):
    city_title("Water supply management", "Balance human needs with the resources your city can deliver.")
    l, r = st.columns([.9,1.1], gap="large")
    with l:
        with st.container(border=True):
            section("Demand & supply inputs")
            field("population", "City population", integer=True, minimum=1, step=1000)
            field("available_water_lpd", "Available daily supply (litres)", step=100000.0,
                  maximum=1e15)
            note("Daily water demand is fixed by your teacher's rule: population × 135 litres per person per day.")
    with r:
        w = result["water"]
        c1, c2 = st.columns(2)
        with c1: st.metric("Daily demand", f"{w['demand_lpd']/1e6:,.2f}M L")
        with c2: st.metric("Supply gap", f"{w['balance_lpd']/1e6:+,.2f}M L", w["status"], delta_color="off")
        with st.container(border=True):
            fig = go.Figure(go.Bar(x=["Daily demand", "Daily supply"],
                                   y=[w["demand_lpd"], w["supply_lpd"]],
                                   marker_color=[MAUVE, SLATE], text=[fmt(w["demand_lpd"]), fmt(w["supply_lpd"])],
                                   textposition="auto"))
            fig.update_layout(yaxis_title="Litres per day", showlegend=False)
            graph(fig)
            st.markdown(f"**Result:** {w['status']} of {abs(w['balance_lpd']):,.0f} litres/day" if w['balance_lpd'] else "**Result:** Exact balance")
            st.progress(min(1.0, w["coverage_pct"] / 100))
            st.caption(f"Water demand coverage: {w['coverage_pct']:,.1f}%")


def construction_page(result):
    city_title("Construction cost estimator", "Estimate the size and financial requirements of a new building.")
    l, r = st.columns([.9,1.1], gap="large")
    with l:
        with st.container(border=True):
            section("Building inputs")
            field("building_length_m", "Building length (m)", minimum=.001, step=1.0)
            field("building_width_m", "Building width (m)", minimum=.001, step=1.0)
            field("floors", "Number of floors", integer=True, minimum=1, maximum=1000)
            field("cost_per_m2", "Construction cost (PKR/m²)", minimum=.01, step=1000.0)
            note("Model assumption: each floor has the same footprint; excludes land, taxes, financing and contingency unless included in your rate.")
    with r:
        b = result["construction"]
        c1,c2 = st.columns(2)
        with c1: st.metric("Total floor area", f"{b['total_floor_area_m2']:,.1f} m²")
        with c2: st.metric("Estimated budget", f"PKR {b['total_cost_pkr']/1e6:,.2f}M")
        with st.container(border=True):
            # A Python loop creates the floor-by-floor cost distribution.
            areas = list(range(1, result["inputs"]["floors"] + 1))
            # For very tall buildings show a compact summary rather than hundreds of bars.
            if len(areas) > 30:
                step = max(1, len(areas)//25)
                areas = areas[::step]
                if areas[-1] != result["inputs"]["floors"]: areas.append(result["inputs"]["floors"])
            cumulative = [i * b["cost_per_floor_pkr"] / 1e6 for i in areas]
            fig = go.Figure(go.Scatter(x=areas, y=cumulative, mode="lines+markers",
                                      fill="tozeroy", line=dict(color=SLATE, width=3),
                                      fillcolor="rgba(201,173,167,.30)"))
            fig.update_layout(xaxis_title="Completed floors", yaxis_title="Cumulative cost (PKR millions)")
            graph(fig)
            st.caption(f"Footprint: {b['footprint_m2']:,.2f} m² · Cost per floor: PKR {b['cost_per_floor_pkr']:,.0f}")


def waste_page(result):
    city_title("Waste management", "Turn city waste data into a realistic recycling target.")
    l, r = st.columns([.9,1.1], gap="large")
    with l:
        with st.container(border=True):
            section("Waste inputs")
            field("population", "City population", integer=True, minimum=1, step=1000)
            field("waste_kg_per_person", "Daily waste per person (kg)", minimum=.001, step=.05)
            field("recycling_percentage", "Recycling percentage (%)", minimum=0, maximum=100, step=1.0)
            note("Waste generation = population × waste per person. Recycled quantity = total daily waste × recycling percentage ÷ 100.")
    with r:
        w = result["waste"]
        c1,c2 = st.columns(2)
        with c1: st.metric("Total daily waste", f"{w['total_kgpd']/1000:,.1f} tonnes")
        with c2: st.metric("Recycled per day", f"{w['recycled_kgpd']/1000:,.1f} tonnes")
        with st.container(border=True):
            fig = go.Figure(go.Pie(values=[w["recycled_kgpd"], w["remaining_kgpd"]],
                                   labels=["To recycle", "For disposal"], hole=.69,
                                   marker=dict(colors=[SLATE, ROSE]),
                                   textinfo="percent+label", sort=False))
            graph(fig)
            st.markdown(f"**For disposal:** {w['remaining_kgpd']:,.2f} kg/day")
            st.progress(w["recycling_percentage"] / 100)
            st.caption(f"Recycling performance: {w['recycling_percentage']:,.0f}% of generated waste")


def forecast_page(result, rows):
    city_title("Future planning", "Explore the consequences of annual growth and infrastructure choices.",
               "OPTIONAL ADVANCED FEATURE")
    a,b,c,d,e = st.columns([1,1,1,1,1])
    with a: field("population_growth_pct", "Population growth %", minimum=-10, maximum=30, step=.5)
    with b: field("vehicle_growth_pct", "Vehicle growth %", minimum=-10, maximum=30, step=.5)
    with c: field("water_supply_growth_pct", "Water supply growth %", minimum=-10, maximum=30, step=.5)
    with d: field("recycling_target_pct", "Year-end recycling %", minimum=0, maximum=100, step=1.0)
    with e: field("forecast_years", "Forecast years", integer=True, minimum=1, maximum=30)
    rows = forecast_city(st.session_state.inputs)
    note("These are illustrative annual-growth projections, not forecasts based on real sensors. Road length and waste generated per person stay constant.")
    for alert in forecast_alerts(rows):
        st.info(alert)
    tab1, tab2, tab3 = st.tabs(["Water resilience", "Traffic pressure", "Waste & recycling"])
    years = [r["year"] for r in rows]
    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=[r["water_demand_lpd"]/1e6 for r in rows],
                                 name="Demand", line=dict(color=MAUVE, width=4)))
        fig.add_trace(go.Scatter(x=years, y=[r["water_supply_lpd"]/1e6 for r in rows],
                                 name="Supply", line=dict(color=SLATE, width=4)))
        fig.update_layout(xaxis_title="Year", yaxis_title="Million litres/day")
        graph(fig)
    with tab2:
        fig = go.Figure(go.Scatter(x=years, y=[r["traffic_density"] for r in rows],
                    mode="lines+markers", line=dict(color=SLATE, width=4)))
        fig.add_hline(y=TRAFFIC_THRESHOLDS[-1], line_dash="dash", line_color=MAUVE,
                      annotation_text="Critical threshold")
        fig.update_layout(xaxis_title="Year", yaxis_title="Vehicles per kilometre")
        graph(fig)
    with tab3:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=years, y=[r["waste_tonnes_pd"] for r in rows],
                             name="Waste generated", marker_color=ROSE))
        fig.add_trace(go.Bar(x=years, y=[r["recycled_tonnes_pd"] for r in rows],
                             name="To recycle", marker_color=SLATE))
        fig.update_layout(barmode="group", xaxis_title="Year", yaxis_title="Tonnes/day")
        graph(fig)
    with st.expander("View year-by-year projection data"):
        st.dataframe(rows, width="stretch", hide_index=True)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    st.download_button("↓ Download forecast CSV", buf.getvalue(), "civitas_forecast.csv", "text/csv")


def scenario_page(result):
    city_title("Scenario lab", "Compare today's city against a plan before committing resources.",
               "OPTIONAL DECISION SUPPORT")
    st.markdown("Try a mix of traffic reduction, water expansion, and recycling improvements. All maths is recalculated by the Python engine.")
    c1,c2,c3 = st.columns(3)
    with c1: traffic_change = st.slider("Reduce vehicles by (%)", 0, 60, 20, 5)
    with c2: water_change = st.slider("Increase daily water supply by (%)", 0, 60, 15, 5)
    with c3: recycling_change = st.slider("Increase recycling by (percentage points)", 0, 50, 15, 5)
    optimistic = copy.deepcopy(st.session_state.inputs)
    optimistic["vehicles"] = round(optimistic["vehicles"] * (1 - traffic_change/100))
    optimistic["available_water_lpd"] *= 1 + water_change/100
    optimistic["recycling_percentage"] = min(100, optimistic["recycling_percentage"] + recycling_change)
    try:
        planned = calculate_city(optimistic)
    except ValueError as error:
        st.warning(f"Please adjust the proposed changes: {error}")
        return
    c1,c2,c3 = st.columns(3)
    with c1:
        st.metric("Traffic density", f"{planned['traffic']['density']:,.1f} veh/km",
                  f"{planned['traffic']['density']-result['traffic']['density']:+,.1f} veh/km", delta_color="inverse")
    with c2:
        st.metric("Water balance", f"{planned['water']['balance_lpd']/1e6:+,.2f}M L",
                  f"{(planned['water']['balance_lpd']-result['water']['balance_lpd'])/1e6:+,.2f}M L", delta_color="normal")
    with c3:
        st.metric("City health index", f"{planned['health']['score']:,.1f}/100",
                  f"{planned['health']['score']-result['health']['score']:+,.1f} points", delta_color="normal")
    fig = go.Figure()
    categories = ["Traffic score", "Water coverage score", "Recycling score", "Overall health"]
    now = result["health"]
    after = planned["health"]
    fig.add_trace(go.Bar(name="Current city", x=categories,
                         y=[now["traffic_score"], now["water_score"], now["recycling_score"], now["score"]],
                         marker_color=MAUVE))
    fig.add_trace(go.Bar(name="Proposed plan", x=categories,
                         y=[after["traffic_score"], after["water_score"], after["recycling_score"], after["score"]],
                         marker_color=SLATE))
    fig.update_layout(barmode="group", yaxis=dict(range=[0,105]), yaxis_title="Illustrative points")
    graph(fig)
    if st.button("Apply proposed changes to my city", type="primary"):
        apply_scenario(optimistic)
        st.success("Scenario applied.")
        st.rerun()
    st.caption("This is a comparison of hypothetical policies, not a cost-benefit analysis or guarantee of real results.")


def report_page(result, rows):
    city_title("Smart city report", "One complete, formatted document combining every compulsory module.",
               "FINAL REQUIRED MODULE")
    d, t, w, b, z = (result[k] for k in ["inputs", "traffic", "water", "construction", "waste"])
    st.markdown(f"<div class='panel'><span class='eyebrow'>ANALYSIS COMPLETE / {escape(d['city_name'])}</span><h2 style='margin:8px 0 0'>City-wide management summary</h2><p>Prepared using validated Python calculations. Values reflect the latest inputs from all modules.</p></div>", unsafe_allow_html=True)
    quick_overview(result)
    with st.container(border=True):
        section("01 / Traffic management")
        st.write(f"**Road vehicles:** {d['vehicles']:,} &nbsp; | &nbsp; **Road length:** {d['road_length_km']:,.2f} km")
        st.write(f"**Density:** {t['density']:,.2f} vehicles/km &nbsp; | &nbsp; **Condition:** {t['condition']}")
        st.write(f"**Recommended action:** {t['action']}")
        st.divider()
        section("02 / Water supply management")
        st.write(f"**Population:** {d['population']:,} &nbsp; | &nbsp; **Daily demand:** {w['demand_lpd']:,.0f} L")
        st.write(f"**Available supply:** {w['supply_lpd']:,.0f} L &nbsp; | &nbsp; **Status:** {w['status']} ({abs(w['balance_lpd']):,.0f} L)")
        st.divider()
        section("03 / Construction cost estimator")
        st.write(f"**Building:** {d['building_length_m']:,.2f} m × {d['building_width_m']:,.2f} m × {d['floors']:,} floors")
        st.write(f"**Total floor area:** {b['total_floor_area_m2']:,.2f} m² &nbsp; | &nbsp; **Rate:** PKR {d['cost_per_m2']:,.2f}/m²")
        st.write(f"**Estimated budget:** PKR {b['total_cost_pkr']:,.2f}")
        st.divider()
        section("04 / Waste management")
        st.write(f"**Waste generated:** {z['total_kgpd']:,.2f} kg/day &nbsp; | &nbsp; **Recycling:** {z['recycling_percentage']:,.1f}%")
        st.write(f"**To recycle:** {z['recycled_kgpd']:,.2f} kg/day &nbsp; | &nbsp; **To dispose:** {z['remaining_kgpd']:,.2f} kg/day")
        st.divider()
        section("05 / Final city conditions")
        st.markdown(f"**Illustrative city health index:** {result['health']['score']:,.1f}/100 — {result['health']['label']}")
        for r in result["recommendations"]:
            st.markdown(f"- {r}")
    st.caption("Assumptions: traffic thresholds are classroom-defined; construction uses identical floor footprints; health index is illustrative; no live sensors are used.")
    c1,c2 = st.columns(2)
    with c1:
        try:
            pdf = create_pdf_report(result, rows)
            st.download_button("↓ Download professional PDF report", pdf,
                               file_name="civitas_smart_city_report.pdf",
                               mime="application/pdf", type="primary", width="stretch")
        except Exception as error:
            st.error(f"PDF export failed: {error}")
    with c2:
        lines = [f"SMART CITY REPORT — {d['city_name']}",
                 f"Traffic: {t['density']:.2f} veh/km ({t['condition']})",
                 f"Water: {w['status']}, balance {w['balance_lpd']:,.0f} L/day",
                 f"Construction: {b['total_floor_area_m2']:,.2f} m², PKR {b['total_cost_pkr']:,.2f}",
                 f"Waste: {z['total_kgpd']:,.2f} kg/day, recycle {z['recycled_kgpd']:,.2f} kg/day",
                 f"City health index: {result['health']['score']:.1f}/100", "", *result["recommendations"]]
        st.download_button("↓ Download text summary", "\n".join(lines),
                           file_name="civitas_smart_city_report.txt", mime="text/plain",
                           width="stretch")


def main():
    start_session()
    page = render_sidebar()
    try:
        result = calculate_city(st.session_state.inputs)
        rows = forecast_city(st.session_state.inputs)
    except ValueError as error:
        st.error(f"Please correct an input: {error}")
        return
    if page == "Overview": overview(result, rows)
    elif page == "Traffic Management": traffic_page(result)
    elif page == "Water Supply": water_page(result)
    elif page == "Construction Estimator": construction_page(result)
    elif page == "Waste Management": waste_page(result)
    elif page == "Future Planning": forecast_page(result, rows)
    elif page == "Scenario Lab": scenario_page(result)
    elif page == "City Report": report_page(result, rows)
    st.markdown("<div class='footnote'>CIVITAS / CP Lab CL1010 · Calculations performed by Python · Interface theme: #22223B / #4A4E69 / #9A8C98 / #C9ADA7 / #F2E9E4</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
