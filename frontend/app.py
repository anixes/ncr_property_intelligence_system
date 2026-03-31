"""
NCR Property Intelligence — Streamlit Frontend (v2 — Compact Design).

Two main dashboards:
  1. Market Analyzer  — Investment Report
  2. Property Recommender — Discovery Engine
"""

import json
import math
import os
from pathlib import Path

import h3  # For spatial index decoding
import pydeck as pdk
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------
# Default to the internal docker-compose bridge if available, else localhost
DEFAULT_API_URL = "http://localhost:8000"
API_BASE_URL = os.getenv("API_BASE_URL", DEFAULT_API_URL)

PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"
DISCOVER_URL = f"{API_BASE_URL}/discover"
HOTSPOTS_URL = f"{API_BASE_URL}/intelligence/hotspots"

CITIES = ["Delhi", "Gurgaon", "Noida", "Greater Noida", "Ghaziabad", "Faridabad"]
BHK_OPTIONS = [1, 2, 3, 4, 5]
PROP_TYPES = ["Any", "Apartment", "Builder Floor", "Independent House"]

CITY_CENTERS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Gurgaon": {"lat": 28.4595, "lon": 77.0266},
    "Noida": {"lat": 28.5355, "lon": 77.3910},
    "Greater Noida": {"lat": 28.4744, "lon": 77.5040},
    "Ghaziabad": {"lat": 28.6692, "lon": 77.4538},
    "Faridabad": {"lat": 28.4089, "lon": 77.3178},
}

# The locality index uses different city key names in some cases
CITY_KEY_MAP = {
    "Gurgaon": "Gurugram",
    "Delhi": "Delhi",
    "Noida": "Noida",
    "Greater Noida": "Greater Noida",
    "Ghaziabad": "Ghaziabad",
    "Faridabad": "Faridabad",
}


# ---------------------------------------------------------------------------
# Page Config & Custom CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NCR Property Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Compact styling — override Streamlit's bloated defaults
css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>\n{f.read()}\n</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------
if "discovery_results" not in st.session_state:
    st.session_state.discovery_results = []
if "analyzer_results" not in st.session_state:
    st.session_state.analyzer_results = None
if "page" not in st.session_state:
    st.session_state.page = 0


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def fmt(number):
    """Format large numbers for Indian currency display."""
    if not number:
        return "0"
    if number >= 10000000:
        return f"₹{number / 10000000:.2f} Cr"
    elif number >= 100000:
        return f"₹{number / 100000:.1f} L"
    elif number >= 1000:
        return f"₹{number / 1000:.1f}K"
    return f"₹{number:,.0f}"


def score_class(s):
    if s >= 7:
        return "score-high"
    elif s >= 4:
        return "score-mid"
    return "score-low"


def render_property_card(item, intent="Buy"):
    """Compact HTML property card — no st.metric bloat."""
    society = item.get("society", "Unknown")
    loc = item.get("locality", item.get("sector", ""))
    city = item.get("city", "")
    price = item.get("price", 0)
    area = item.get("area", 0)
    psqft = item.get("price_per_sqft", 0)
    yld = item.get("yield_pct", 0)
    score = item.get("unified_score", 0)
    bhk = item.get("bhk", "–")
    furnishing = item.get("furnishing_status", "Unknown")

    # Adaptive metric labels and values
    price_label = "Rent" if intent == "Rent" else "Price"
    psqft_label = "₹/sqft (Rent)" if intent == "Rent" else "₹/sqft"
    
    # Second row adaptive metric (Yield for Buy, Furnishing for Rent)
    if intent == "Rent":
        secondary_metric_label = "Furnishing"
        secondary_metric_value = furnishing[:10] + ".." if len(furnishing) > 10 else furnishing
        score_label = "Value Score"
    else:
        secondary_metric_label = "Yield"
        secondary_metric_value = f"{yld}%"
        score_label = "Deal Score"

    st.markdown(
        f"""
    <div class="prop-card">
        <p class="card-title" title="{society}">{society}</p>
        <p class="card-loc">{loc}, {city}</p>
        <div class="card-row">
            <div class="card-kv"><p class="kv-label">{price_label}</p><p class="kv-value">{fmt(price)}</p></div>
            <div class="card-kv"><p class="kv-label">Area</p><p class="kv-value">{int(area)} sqft</p></div>
            <div class="card-kv"><p class="kv-label">BHK</p><p class="kv-value">{bhk}</p></div>
        </div>
        <div class="card-divider"></div>
        <div class="card-row">
            <div class="card-kv"><p class="kv-label">{psqft_label}</p><p class="kv-value">{psqft:,.0f}</p></div>
            <div class="card-kv"><p class="kv-label">{secondary_metric_label}</p><p class="kv-value">{secondary_metric_value}</p></div>
            <div class="card-kv"><p class="kv-label">{score_label}</p><p class="kv-value"><span class="score-badge {score_class(score)}">{score}/10</span></p></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_alternative_card(item, intent="Buy"):
    """Modern box UI for investment alternatives."""
    loc = item.get("locality", "Unknown")
    city = item.get("city", "")
    psqft = item.get("median_price_sqft", 0)
    yld = item.get("expected_yield_pct", 0)
    score = item.get("composite_score", 0)
    dist = item.get("distance_km")

    # Adaptive labels
    psqft_label = "Avg Rent/sqft" if intent == "Rent" else "Avg ₹/sqft"
    secondary_label = "Exp. Yield"
    secondary_value = f"{yld}%"
    
    listing_count = item.get("listing_count", None)
    if intent == "Rent":
        secondary_label = "Listings"
        secondary_value = str(listing_count) if listing_count is not None else "—"

    st.markdown(
        f"""
    <div class="prop-card">
        <p class="card-title" title="{loc}">{loc}</p>
        <p class="card-loc">{city}{f" · {dist}km away" if dist else ""}</p>
        <div class="card-divider"></div>
        <div class="card-row">
            <div class="card-kv"><p class="kv-label">{psqft_label}</p><p class="kv-value">{fmt(psqft)}</p></div>
            <div class="card-kv"><p class="kv-label">{secondary_label}</p><p class="kv-value">{secondary_value}</p></div>
            <div class="card-kv"><p class="kv-label">Sector Grade</p><p class="kv-value"><span class="score-badge {score_class(score)}">{score}/10</span></p></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def get_color_by_price(price_psf):
    """Dynamic color scale: Yellow -> Orange -> Red -> Dark Red."""
    if price_psf < 5000:
        return [255, 255, 0, 200]
    elif price_psf < 8000:
        return [255, 165, 0, 200]
    elif price_psf < 12000:
        return [255, 69, 0, 200]
    else:
        return [180, 0, 0, 200]


def render_hotspot_map(hotspots=None, listings=None, center_lat=None, center_lon=None, zoom=10):
    """Render 3D spatial visualization using HexagonLayer (Heatmap) or ColumnLayer (Points)."""
    if not hotspots and not listings:
        st.caption("No spatial data available.")
        return

    layers = []

    if listings:
        # ── Mode 2/3: Discovery & Comparables (3D Towers) ────────────
        # Limit to top 30 by score to prevent clutter
        display_data = sorted(listings, key=lambda x: x.get("unified_score", 0), reverse=True)[:30]

        # Pre-calculate fields for Pydeck (avoids complex expressions in JS)
        for item in display_data:
            psf = item.get("price_per_sqft", 0)
            score = item.get("unified_score", 0)
            item["color_val"] = get_color_by_price(psf)
            # score 0-10 -> height 80-480 (Elegant needle towers)
            item["elev_val"] = (score * 40) + 80

            # Resolve H3 index to coordinates if missing
            if ("latitude" not in item or "longitude" not in item) and "h3_res8" in item:
                try:
                    lat, lon = h3.cell_to_latlng(item["h3_res8"])
                    item["latitude"] = lat
                    item["longitude"] = lon
                except Exception:
                    pass

        column_layer = pdk.Layer(
            "ColumnLayer",
            data=display_data,
            get_position="[longitude, latitude]",
            get_elevation="elev_val",
            elevation_scale=1,
            radius=150,  # Precision radius for phone/desktop balance
            get_fill_color="color_val",
            pickable=True,
            auto_highlight=True,
            extrude=True,
        )
        layers.append(column_layer)
        tooltip = {
            "html": """
                <div style='font-family:sans-serif; padding:10px; background:#1a1a2e; border:1px solid #444; border-radius:4px;'>
                    <b style='font-size:14px;'>{society}</b><br/>
                    <i style='color:#aaa;'>{locality}, {city}</i><br/>
                    <hr style='margin:8px 0; border:0; border-top:1px solid rgba(255,255,255,0.1);'/>
                    Price: <b>Rs.{price:,.0f}</b><br/>
                    Rate: <b>Rs.{price_per_sqft}/sqft</b><br/>
                    Yield: <b style='color:#4caf50'>{yield_pct}%</b><br/>
                    Best Deal Score: <b style='color:#e05c5c'>{unified_score}/10</b>
                </div>
            """,
            "style": {"color": "white", "padding": "0"},
        }
    else:
        # ── Mode 1: Market Hotspots (3D Aggregate Towers) ─────────────
        # Convert aggregated hotspots to towers for visual consistency
        for h in hotspots:
            density = h.get("density", 0)
            h["color_val"] = get_color_by_price(h.get("median_price_sqft", 0))
            # Log-scaling: density 1 -> ~242, 10 -> ~839, 1000 -> ~2418
            h["elev_val"] = math.log1p(density) * 350

        column_layer = pdk.Layer(
            "ColumnLayer",
            data=hotspots,
            get_position="[longitude, latitude]",
            get_elevation="elev_val",
            elevation_scale=1,
            radius=300,  # Focused cluster size
            get_fill_color="color_val",
            pickable=True,
            auto_highlight=True,
            extrude=True,
        )
        layers.append(column_layer)
        tooltip = {
            "html": """
                <div style='font-family:sans-serif; padding:10px; background:#1a1a2e; border:1px solid #444; border-radius:4px;'>
                    <b>Market Cluster</b><br/>
                    City: <b>{city}</b><br/>
                    <hr style='margin:5px 0; border:0; border-top:1px solid rgba(255,255,255,0.1);'/>
                    Avg Rate: <b>Rs.{median_price_sqft:,.0f}/sqft</b><br/>
                    Listing Count: <b style='color:#ffa500'>{density}</b>
                </div>
            """,
            "style": {"color": "white", "padding": "0"},
        }

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=45,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="dark",  # High-contrast style matching dark mode theme
        height=450,
    )

    st.pydeck_chart(deck, use_container_width=True)


@st.cache_data
def load_society_map():
    try:
        root = Path(__file__).resolve().parents[1]
        index_path = root / "data" / "locality_intelligence_index.json"
        with open(index_path) as f:
            raw = json.load(f)
        # Map frontend city names to index keys
        result = {}
        for frontend_name, index_key in CITY_KEY_MAP.items():
            result[frontend_name] = raw.get(index_key, {})
        return result
    except Exception:
        return {}


SOCIETY_MAP = load_society_map()


# ---------------------------------------------------------------------------
# Shared Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("NCR Intelligence")
    st.caption("Spatial AI & Market Analytics")

    api_ok = False
    try:
        r = requests.get(HEALTH_URL, timeout=1)
        api_ok = r.status_code == 200
    except Exception:
        pass

    st.markdown(f":{'green' if api_ok else 'red'}[●] {'Online' if api_ok else 'Offline'}")

    mode = st.radio("Navigation", ["Market Analyzer", "Property Recommender"])
    intent = st.radio("Intent", ["Buy", "Rent"], horizontal=True)
    score_label = "Investment Score" if intent == "Buy" else "Value Score"


# ===========================================================================
# ===========================================================================
# MODE: MARKET ANALYZER
# ===========================================================================
if mode == "Market Analyzer":
    with st.sidebar:
        st.markdown("---")
        city = st.selectbox("NCR City", CITIES, index=1)
        city_data = SOCIETY_MAP.get(city, {})
        localities = sorted(list(city_data.keys()))
        sector = st.selectbox("Locality / Sector", options=localities if localities else ["Other"])

        # Reset results if city or sector changed
        if (
            "last_city" not in st.session_state
            or st.session_state.last_city != city
            or "last_sector" not in st.session_state
            or st.session_state.last_sector != sector
        ):
            st.session_state.analyzer_results = None
            st.session_state.last_city = city
            st.session_state.last_sector = sector

        st.markdown("---")
        prop_type = st.selectbox("Property Type", PROP_TYPES)

        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("Area (sqft)", min_value=100, max_value=20000, value=1500)
        with col2:
            bedrooms = st.selectbox("BHK", BHK_OPTIONS, index=2)

        with st.expander("Advanced Analytics Options"):
            st.caption("Location & Orientation")
            is_corner = st.checkbox("Corner Property")
            is_park_facing = st.checkbox("Park / Green Facing")
            is_vastu = st.checkbox("Vastu Compliant")

            st.markdown("---")
            st.caption("Extra Space")
            has_servant = st.checkbox("Servant Room")
            has_study = st.checkbox("Study Room")
            has_store = st.checkbox("Store Room")
            has_pooja = st.checkbox("Pooja / Prayer Room")

            st.markdown("---")
            st.caption("Amenities")
            has_pool = st.checkbox("Swimming Pool")
            has_lift = st.checkbox("Lift / Elevator")
            has_power = st.checkbox("Power Backup")
            has_gym = st.checkbox("Gym Access")

            st.markdown("---")
            st.caption("Property Details")
            bathrooms = st.selectbox("Number of Bathrooms", BHK_OPTIONS, index=1)
            is_luxury = st.checkbox("Luxury Segment Listing")
            furnishing = st.selectbox(
                "Furnishing Status", ["Semi-Furnished", "Fully-Furnished", "Unfurnished", "Unknown"]
            )
            legal = st.selectbox(
                "Legal Ownership Status", ["Unknown", "Freehold", "Leasehold", "Power of Attorney"]
            )

        predict_btn = st.button("Run Analytics", type="primary", use_container_width=True)

    if predict_btn:
        if city == "Delhi" and intent == "Buy":
            st.warning(
                "Buy listing data for Delhi is unavailable in our database. Showing valuation estimate only — no comparables."
            )

        payload = {
            "area": float(area),
            "bedrooms": int(bedrooms),
            "bathrooms": int(bathrooms),
            "prop_type": prop_type,
            "city": city,
            "sector": sector,
            "listing_type": intent.lower(),
            "amenities": {
                "has_gym": has_gym,
                "has_pool": has_pool,
                "has_lift": has_lift,
                "has_power_backup": has_power,
            },
            "location": {
                "is_near_metro": False,
                "is_corner_property": is_corner,
                "is_park_facing": is_park_facing,
                "is_vastu_compliant": is_vastu,
            },
            "features": {
                "is_luxury": is_luxury,
                "is_servant_room": has_servant,
                "is_study_room": has_study,
                "is_store_room": has_store,
                "is_pooja_room": has_pooja,
            },
            "furnishing_status": furnishing,
            "legal_status": legal,
        }

        with st.spinner("Calculating..."):
            try:
                res = requests.post(PREDICT_URL, json=payload, timeout=15)
                res.raise_for_status()
                st.session_state.analyzer_results = res.json()
            except Exception as e:
                st.error(f"Prediction Error: {e}")
                st.session_state.analyzer_results = None

    if st.session_state.analyzer_results:
        data = st.session_state.analyzer_results
        intel = data.get("intelligence_suite", {})
        score = intel.get("unified_score", 0)
        risk_data = intel.get("risk_analysis", {})

        if intent == "Rent":
            st.markdown(f"### Rental Market Analysis: {bedrooms} BHK {prop_type} in {sector}, {city}")
        else:
            st.markdown(f"### Investment Analysis: {bedrooms} BHK {prop_type} in {sector}, {city}")

        # ── 1. KPI Row (Adaptive) ────────────────────────
        if intent == "Rent":
            rent_sqft = data["predicted_monthly_rent"] / data["area"] if data["area"] > 0 else 0
            st.markdown(
                f"""
            <div class="kpi-row">
                <div class="kpi-box">
                    <p class="kpi-label">Predicted Rent</p>
                    <p class="kpi-value">{fmt(data["predicted_monthly_rent"])}</p>
                </div>
                <div class="kpi-box">
                    <p class="kpi-label">₹/sqft (Rent)</p>
                    <p class="kpi-value">₹{round(rent_sqft, 2)}</p>
                </div>
                <div class="kpi-box">
                    <p class="kpi-label">Value Score</p>
                    <p class="kpi-value"><span class="score-badge {score_class(score)}">{score}/10</span></p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="kpi-row">
                <div class="kpi-box">
                    <p class="kpi-label">Valuation</p>
                    <p class="kpi-value">{fmt(data["estimated_market_value"])}</p>
                </div>
                <div class="kpi-box">
                    <p class="kpi-label">Monthly Rent</p>
                    <p class="kpi-value">{fmt(data["predicted_monthly_rent"])}</p>
                </div>
                <div class="kpi-box">
                    <p class="kpi-label">Investment Score</p>
                    <p class="kpi-value"><span class="score-badge {score_class(score)}">{score}/10</span></p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # ── 2. ROI/Metric Breakdown (Adaptive) ──────────────
        metro_dist = data.get("dist_to_metro_km")
        if metro_dist is not None:
            if metro_dist <= 1.5:
                metro_color = "#4CAF50" # Green (Near)
            elif metro_dist <= 3.0:
                metro_color = "#FFC107" # Yellow (Moderate)
            else:
                metro_color = "#F44336" # Red (Far)
            metro_html = f'<p class="roi-value" style="color: {metro_color}">{metro_dist} km</p>'
            metro_box = f"<div class='roi-item'><p class='roi-label'>Metro Dist</p>{metro_html}</div>"
        else:
            metro_box = ""  # Plan: collapse entirely when null, don't show "Unknown"

        if intent == "Rent":
            roi_html = f"""
            <div class="roi-row">
                <div class="roi-item">
                    <p class="roi-label">Market Position</p>
                    <p class="roi-value">{intel.get("overvaluation_pct", 0)}%</p>
                </div>
            """ + metro_box + "</div>"
            st.markdown(roi_html, unsafe_allow_html=True)
        else:
            roi_html = f"""
            <div class="roi-row">
                <div class="roi-item">
                    <p class="roi-label">Rental Yield</p>
                    <p class="roi-value">{intel.get("yield_pct", 0)}%</p>
                </div>
                <div class="roi-item">
                    <p class="roi-label">Market Risk</p>
                    <p class="roi-value">{risk_data.get("label", "N/A")}</p>
                </div>
            """ + metro_box + f"""
                <div class="roi-item">
                    <p class="roi-label">Market Position</p>
                    <p class="roi-value">{intel.get("overvaluation_pct", 0)}%</p>
                </div>
            </div>"""
            st.markdown(roi_html, unsafe_allow_html=True)

        # ── 3. Score Bar ─────────────────────────────────────
        st.progress(max(0.0, min(1.0, score / 10.0)))

        # ── 4. Sector Map (Stable Toggle) ────────────────────
        st.markdown("---")
        show_map = st.checkbox("View 3D Intelligence Map", value=False, key="show_sector_map_chk")
        if show_map:
            similar = data.get("similar_listings", [])
            try:
                hotspot_res = requests.get(
                    HOTSPOTS_URL, params={"listing_type": intent.lower(), "city": city}, timeout=5
                )
                hotspot_data = hotspot_res.json().get("hotspots", [])
                loc_data = city_data.get(sector, {})
                center = CITY_CENTERS.get(city, {"lat": 28.5, "lon": 77.3})

                if similar:
                    # Mode 2: Show comparables as towers
                    st.caption(f"Visualizing {len(similar)} verified comparables in {sector}")
                    render_hotspot_map(
                        listings=similar,
                        center_lat=loc_data.get("lat", center["lat"]),
                        center_lon=loc_data.get("lon", center["lon"]),
                        zoom=12,
                    )
                else:
                    # Mode 1: Show general hotspots
                    render_hotspot_map(
                        hotspots=hotspot_data,
                        center_lat=center["lat"],
                        center_lon=center["lon"],
                        zoom=10,
                    )
            except Exception:
                st.caption("Map data unavailable.")

        # ── 5. Comparables ───────────────────────────────────
        similar = data.get("similar_listings", [])
        if similar:
            st.markdown("### Verified Comparables")
            st.caption(
                "**Micro Analysis**: Real listings from our database. 'Deal Score' measures how underpriced this specific unit is relative to its local market."
            )
            cols = st.columns(3)
            for i, item in enumerate(similar[:6]):
                with cols[i % 3]:
                    render_property_card(item, intent=intent)

        # ── 6. Alternatives ──────────────────────────────────
        recs = data.get("recommendations", [])
        if recs:
            st.markdown("### Better Investment Alternatives")
            st.caption(
                "**Macro Analysis**: Neighboring localities. 'Sector Grade' evaluates the overall investment health of the area against the entire NCR region."
            )
            grid_cols = st.columns(3)
            for i, rec in enumerate(recs[:6]):
                with grid_cols[i % 3]:
                    render_alternative_card(rec, intent=intent)
        elif not similar:
            st.caption("No comparables or alternatives found.")

    else:
        # Landing dashboard overview
        st.markdown(
            """
        <div class="landing-stat-row">
            <div class="landing-stat"><p class="ls-val">43,000+</p><p class="ls-lbl">Property Records</p></div>
            <div class="landing-stat"><p class="ls-val">6</p><p class="ls-lbl">NCR Cities</p></div>
            <div class="landing-stat"><p class="ls-val">H3</p><p class="ls-lbl">Spatial Indexing</p></div>
            <div class="landing-stat"><p class="ls-val">ML</p><p class="ls-lbl">Valuation Models</p></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        try:
            hotspot_res = requests.get(
                HOTSPOTS_URL,
                params={"listing_type": intent.lower(), "city": "Entire NCR"},
                timeout=5,
            )
            hotspot_data = hotspot_res.json().get("hotspots", [])

            st.markdown("---")
            show_map = st.checkbox(
                "View 3D Regional Hotspots Map", value=False, key="show_regional_map_chk"
            )
            if show_map:
                st.markdown("### Regional Overview")
                st.caption(
                    f"Visualizing active market hotspots for {intent} across the entire NCR."
                )
                render_hotspot_map(hotspots=hotspot_data, center_lat=28.5, center_lon=77.2, zoom=8)
                st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Intelligence Layer Unavailable: {e}")

        # Landing Page Alignment (Market Analyzer)
        st.markdown("""<h3 style="margin-bottom:12px;">How it works</h3>""", unsafe_allow_html=True)
        how_it_works_p2 = "predicts fair-market rent and value-for-money score" if intent == "Rent" else "predict market value, rental yield, and investment score"
        how_it_works_p3 = "rental market report: predicted rent, area benchmarks, and comparables." if intent == "Rent" else "full investment report: valuation, ROI breakdown, and verified comparables."

        st.markdown(
            f"""
        <div class="landing-grid">
            <div class="landing-card">
                <p class="lc-icon">01</p>
                <h4>Configure Property</h4>
                <p>Select city, locality, area, BHK, and property type. Adjust advanced options like corner property or luxury segment.</p>
            </div>
            <div class="landing-card">
                <p class="lc-icon">02</p>
                <h4>Run Analytics</h4>
                <p>Our ML models {how_it_works_p2} using spatial H3 indexing across the NCR region.</p>
            </div>
            <div class="landing-card">
                <p class="lc-icon">03</p>
                <h4>Review Intelligence</h4>
                <p>Get a {how_it_works_p3}</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("""<h3 style="margin-bottom:12px;">What you get</h3>""", unsafe_allow_html=True)
        val_p = "AI-predicted monthly rent and area benchmarking based on 43,000+ local NCR records." if intent == "Rent" else "AI-predicted market price per sqft and total value based on 43,000+ local NCR records."
        score_name = "Value Scores" if intent == "Rent" else "Deal Scores"
        score_desc = "rent-to-value scores for budget optimization" if intent == "Rent" else "bargain properties comparing list price to market median"

        st.markdown(
            f"""
        <div class="landing-grid">
            <div class="landing-card">
                <h4>{"Rent Benchmark" if intent == "Rent" else "Valuation Report"}</h4>
                <p>{val_p}</p>
            </div>
            <div class="landing-card">
                <h4>{score_name}</h4>
                <p>Specific <b>{score_name}</b> for {score_desc}.</p>
            </div>
            <div class="landing-card">
                <h4>Verified Proximity</h4>
                <p>Automated GPS-based distance to the nearest Metro station for accurate 'Transit Premium' valuations.</p>
            </div>
            <div class="landing-card">
                <h4>Dual Scoring</h4>
                <p>Specific <b>Deal Scores</b> for bargain properties and <b>Sector Grades</b> for overall neighborhood potential.</p>
            </div>
            <div class="landing-card">
                <h4>Verified Comparables</h4>
                <p>Up to 6 real historical listings similar to your property, sourced from real-world NCR transactions.</p>
            </div>
            <div class="landing-card">
                <h4>Spatial Intelligence</h4>
                <p>3D-tower visualization of market hotspots and results using H3 hexagonal spatial indexing.</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ===========================================================================
# MODE: PROPERTY RECOMMENDER
# ===========================================================================
elif mode == "Property Recommender":
    with st.sidebar:
        st.markdown("---")
        rec_city = st.selectbox("City", CITIES, index=1)
        selected_bhk = st.multiselect("BHK Type", BHK_OPTIONS, default=[2, 3])
        rec_prop_type = st.selectbox("Property Type", PROP_TYPES, key="rec_prop_type")

        if intent == "Buy":
            budget = st.slider("Budget (₹ Lakhs)", 10, 2000, (50, 300))
            budget_min = float(budget[0] * 100_000)
            budget_max = float(budget[1] * 100_000)
        else:  # Rent
            budget = st.slider("Monthly Rent (₹ /month)", 5000, 200000, (10000, 50000), step=5000)
            budget_min = float(budget[0])
            budget_max = float(budget[1])
        sort_options = {
            "score": "Deal Score (Best Value)",
            "yield": "Investment Yield (%)",
            "price_low": "Price: Low to High",
            "price_high": "Price: High to Low",
            "area": "Property Size (Area)",
        }
        sort_label = st.selectbox("Sort Priority", options=list(sort_options.values()))
        sort_by = [k for k, v in sort_options.items() if v == sort_label][0]

        with st.expander("Advanced Discovery Options"):
            st.caption("Location Preferences")
            corner_rec = st.checkbox("Corner Property", key="corner_rec")
            park_facing_rec = st.checkbox("Park / Green Facing", key="park_rec")
            vastu_rec = st.checkbox("Vastu Compliant", key="vastu_rec")

            st.markdown("---")
            st.caption("Room Requirements")
            servant_rec = st.checkbox("Servant Room", key="servant_rec")
            study_rec = st.checkbox("Study Room", key="study_rec")
            store_rec = st.checkbox("Store Room", key="store_rec")
            pooja_rec = st.checkbox("Pooja / Prayer Room", key="pooja_rec")

            st.markdown("---")
            st.caption("Amenities")
            pool_rec = st.checkbox("Swimming Pool", key="pool_rec")
            lift_rec = st.checkbox("Lift / Elevator", key="lift_rec")
            power_rec = st.checkbox("Power Backup", key="power_rec")
            gym_rec = st.checkbox("Gym Access", key="gym_rec")

            st.markdown("---")
            st.caption("Property Details")
            luxury_rec = st.checkbox("Luxury Segment Listing", key="luxury_rec")
            furnishing_rec = st.selectbox(
                "Furnishing Status",
                ["Unknown", "Semi-Furnished", "Fully-Furnished", "Unfurnished"],
                key="furn_rec",
            )
            legal_rec = st.selectbox(
                "Legal Ownership Status",
                ["Unknown", "Freehold", "Leasehold", "Power of Attorney"],
                key="legal_rec",
            )

        discover_btn = st.button("Discover Best Deals", type="primary", use_container_width=True)

    # ── 1. Search ─────────────────────────────────────────────
    if discover_btn:
        if rec_city == "Delhi" and intent == "Buy":
            st.warning(
                "Buy listing data for Delhi is currently zero. Please try Rent or another city."
            )

        payload = {
            "city": rec_city,
            "listing_type": intent.lower(),
            "bhk": selected_bhk,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "sort_by": sort_by,
            "amenities": {
                "has_gym": gym_rec,
                "has_pool": pool_rec,
                "has_lift": lift_rec,
                "has_power_backup": power_rec,
            },
            "location_score": {
                "is_near_metro": False,
                "is_corner_property": corner_rec,
                "is_park_facing": park_facing_rec,
                "is_vastu_compliant": vastu_rec,
            },
            "features": {
                "is_luxury": luxury_rec,
                "is_servant_room": servant_rec,
                "is_study_room": study_rec,
                "is_store_room": store_rec,
                "is_pooja_room": pooja_rec,
            },
            "prop_type": rec_prop_type,
            "furnishing_status": furnishing_rec,
            "legal_status": legal_rec if "legal_rec" in dir() else "Unknown",
        }
        with st.spinner("Scanning 43,000+ records..."):
            try:
                res = requests.post(DISCOVER_URL, json=payload, timeout=15)
                res.raise_for_status()
                st.session_state.discovery_results = res.json().get("listings", [])
                st.session_state.page = 0
            except Exception as e:
                st.error(f"Search failed: {e}")

    # ── 2. Map (Stable Toggle) ──────────────────────────
    st.markdown("---")
    show_discovery_map = st.checkbox(
        "View Market Intelligence Map", value=False, key="show_rec_map_chk"
    )
    if show_discovery_map:
        results_data = st.session_state.discovery_results
        try:
            map_city = rec_city if "rec_city" in dir() else CITIES[1]
            hotspot_res = requests.get(
                HOTSPOTS_URL, params={"listing_type": intent.lower(), "city": map_city}, timeout=5
            )
            hotspot_data = hotspot_res.json().get("hotspots", [])
            center = CITY_CENTERS.get(map_city, {"lat": 28.5, "lon": 77.3})

            if results_data:
                # Mode 3: Show discovery results as towers
                st.caption(
                    f"Visualizing top {min(30, len(results_data))} discovery results in {map_city}"
                )
                render_hotspot_map(
                    listings=results_data,
                    center_lat=center["lat"],
                    center_lon=center["lon"],
                    zoom=11,
                )
            else:
                # Mode 1: Show general hotspots
                render_hotspot_map(
                    hotspots=hotspot_data,
                    center_lat=center["lat"],
                    center_lon=center["lon"],
                    zoom=9,
                )
        except Exception:
            st.caption("Map data unavailable.")

    # ── 3. Featured ───────────────────────────────────────────
    featured = []
    try:
        featured_res = requests.get(
            HOTSPOTS_URL, params={"listing_type": intent.lower(), "city": rec_city}, timeout=5
        )
        featured = featured_res.json().get("featured", [])
    except Exception:
        pass

    # ── 4. Discovery Results or Landing Page ──────────────────
    results_data = st.session_state.discovery_results
    if not results_data:
        # Discovery Landing Page (Welcome State)
        st.markdown(f"### Discover Your Next Property in {rec_city}")
        st.caption("AI-powered search across 43,000+ real-world NCR property transaction records.")

        stat_1_val = "Budget-First" if intent == "Rent" else "Yield-First"
        stat_1_lbl = "Value Detection" if intent == "Rent" else "Arbitrage Detection"

        st.markdown(
            f"""
        <div class="landing-stat-row">
            <div class="landing-stat"><p class="ls-val">{stat_1_val}</p><p class="ls-lbl">{stat_1_lbl}</p></div>
            <div class="landing-stat"><p class="ls-val">30+</p><p class="ls-lbl">Strict UI Filters</p></div>
            <div class="landing-stat"><p class="ls-val">GPS</p><p class="ls-lbl">Verified Coordinates</p></div>
            <div class="landing-stat"><p class="ls-val">H3</p><p class="ls-lbl">Micro-Market Data</p></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """<h3 style="margin-bottom:12px;">How to Discover</h3>""", unsafe_allow_html=True
        )
        st.markdown(
            """
        <div class="landing-grid">
            <div class="landing-card">
                <p class="lc-icon">01</p>
                <h4>Configure Search</h4>
                <p>Select your target city and budget range. Choose whether you are looking to Buy or Rent your next investment.</p>
            </div>
            <div class="landing-card">
                <p class="lc-icon">02</p>
                <h4>AI Targeting</h4>
                <p>Apply strictly verified filters: <b>Vastu Compliant</b>, <b>Corner Property</b>, <b>Furnishing Status</b>, or <b>Luxury</b> segments.</p>
            </div>
            <div class="landing-card">
                <p class="lc-icon">03</p>
                <h4>Surface Deals</h4>
                <p>Click 'Discover' to scan 43,000+ records. The engine returns the top 30 matching deals sorted by price, yield, or score.</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """<h3 style="margin-bottom:12px;">Discovery Intelligence</h3>""",
            unsafe_allow_html=True,
        )
        intel_1_h = "Value Arbitrage" if intent == "Rent" else "Yield Arbitrage"
        intel_1_p = "Surface properties with best value for your budget before they reach the mass market." if intent == "Rent" else "Surface properties with the highest predicted rental returns before they reach the mass market."
        intel_4_p = "comparison of rent against sector averages." if intent == "Rent" else "comparing the listing to its specific sector median."

        st.markdown(
            f"""
        <div class="landing-grid">
            <div class="landing-card">
                <h4>{intel_1_h}</h4>
                <p>{intel_1_p}</p>
            </div>
            <div class="landing-card">
                <h4>High-Fidelity Filters</h4>
                <p>Filter by specific plot features (Park Facing, Corner Lot) with strictly verified metadata.</p>
            </div>
            <div class="landing-card">
                <h4>Verified H3 Mapping</h4>
                <p>All discovery results are mapped with high-precision spatial coordinates for 3D tower visualization.</p>
            </div>
            <div class="landing-card">
                <h4>Deal Benchmarking</h4>
                <p>Every discovery result includes a real-time 'Deal Score' comparing the listing to its specific sector median.</p>
            </div>
            <div class="landing-card">
                <h4>Smart Pagination</h4>
                <p>Easily browse through dozens of verified matches with our optimized grid view and pagination system.</p>
            </div>
            <div class="landing-card">
                <h4>Market Transparency</h4>
                <p>Access historical transaction data points to understand actual market pricing vs asking price premiums.</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    else:
        # ── 5. Discovery Grid ─────────────────────────────────────
        page_size = 9
        total_pages = math.ceil(len(results_data) / page_size)
        if st.session_state.page >= total_pages:
            st.session_state.page = 0

        start = st.session_state.page * page_size
        page_data = results_data[start : start + page_size]

        st.markdown(f"### Discovery Results ({len(results_data)} properties)")

        cols = st.columns(3)
        for i, item in enumerate(page_data):
            with cols[i % 3]:
                render_property_card(item, intent=intent)

        # Pagination
        st.markdown("---")
        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if st.button("← Previous") and st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()
        with p2:
            st.markdown(
                f"<center>Page {st.session_state.page + 1} of {total_pages}</center>",
                unsafe_allow_html=True,
            )
        with p3:
            if st.button("Next →") and st.session_state.page < total_pages - 1:
                st.session_state.page += 1
                st.rerun()
