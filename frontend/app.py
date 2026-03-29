"""
NCR Property Intelligence — Streamlit Frontend
Intelligence Suite
"""

import os
import requests
import streamlit as st
import pandas as pd
import pydeck as pdk
import textwrap
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# UI Helpers
# ---------------------------------------------------------------------------
def format_indian_number(n: float) -> str:
    """Format a number into the Indian Lakhs/Crores system (1,00,00,000)."""
    try:
        n = int(round(float(n), 0))
        s = str(n)
        if len(s) <= 3:
            return s
        last_three = s[-3:]
        remaining = s[:-3]
        parts = []
        while remaining:
            parts.append(remaining[-2:])
            remaining = remaining[:-2]
        return ",".join(reversed(parts)) + "," + last_three if parts else last_three
    except (ValueError, TypeError):
        return str(n)

def show_market_analyzer_dashboard():
    st.markdown("## Market Intelligence Hub")
    st.markdown("#### Real-time Asset Valuation across Delhi, Gurgaon, Noida, Faridabad & Ghaziabad")
    
    st.info("Spatial Awareness: Our AI tracks price movements across 1,200+ sectors in the NCR corridor.")

    # --- Pulse Metrics ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Avg. Gurgaon Rent (3 BHK)", "₹ 48,500", "+8.2% YoY", help="Based on 12k+ Gurgaon rental listings.")
    with c2:
        st.metric("Noida Appreciation", "14.4%", "Sector 150 Leader", help="Annual capital value growth across Noida micro-markets.")
    with c3:
        st.metric("Highest Rental Yield", "4.8%", "Cyber City Zone", delta_color="normal")

    st.markdown("---")
    
    # --- Market Strategy Chart ---
    st.subheader("Market Heatmap Preview")
    chart_data = pd.DataFrame({
        "Sector": ["Sector 150, Noida", "Golf Course Ext, GGN", "Sector 62, Noida", "Sector 37D, GGN", "Dwarka Expressway"],
        "Demand Score": [85, 92, 78, 65, 88],
        "Price Appr %": [12, 18, 9, 7, 22]
    })
    st.bar_chart(chart_data, x="Sector", y="Price Appr %", color="#3b82f6")
    
    st.markdown("""
    **How it works:**
    1. **Spatial AI**: We use H3 hexagonal indexing (Resolution 9) to analyze micro-market medians.
    2. **Comparables**: Our engine matches your criteria against 43,000+ real historical listings.
    3. **ROI Engine**: We calculate risk based on overvaluation vs. neighborhood medians.
    """)

def show_property_recommender_dashboard():
    st.markdown("## Investment Discovery Engine")
    st.markdown("#### Finding the 1% most profitable assets across the NCR corridor")
    
    st.info("Getting Started: Set your investment or rental criteria in the sidebar to discover high-priority targets.")

    # --- Investment Hotspots ---
    st.subheader("Current Hotspots (High ROI Corridor)")
    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown("""
        <div class="info-card">
            <div style="font-weight: 700; color: #f8fafc;">NCR Corridor North</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top:4px;">Sector 150 & 144, Noida</div>
            <div style="margin-top: 8px; color: #10b981; font-weight: 600;">Avg Yield: 4.4%</div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown("""
        <div class="info-card">
            <div style="font-weight: 700; color: #f8fafc;">Cyber-Life Zone</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top:4px;">Golf Course Ext, Gurgaon</div>
            <div style="margin-top: 8px; color: #10b981; font-weight: 600;">ROI Index: 8.4/10</div>
        </div>
        """, unsafe_allow_html=True)
    with h3:
        st.markdown("""
        <div class="info-card">
            <div style="font-weight: 700; color: #f8fafc;">The Next Frontier</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top:4px;">Dwarka Expressway (LRP)</div>
            <div style="margin-top: 8px; color: #3b82f6; font-weight: 600;">High Growth Area</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- Discovery Intelligence ---
    st.subheader("Discovery Intelligence")
    st.write("Our Discovery Engine continuously monitors **Gurgaon, Noida, Delhi, Faridabad, & Ghaziabad** to find hidden gems.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("- **Value Score**: Buy ONLY when price < neighborhood median.")
        st.markdown("- **Rental Velocity**: Projected days-to-rent stats.")
    with c2:
        st.markdown("- **Metro Affinity**: Proximity-aware yield calculation.")
        st.markdown("- **Historical Accuracy**: Backtested against NCR registry data.")

# ---------------------------------------------------------------------------
# CSS Foundation (Solid, Clean, Professional)
# ---------------------------------------------------------------------------
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #1e293b;
        }
        
        [data-testid="stMetricDelta"] {
            font-weight: 600 !important;
        }

        /* Modern Card styling (Dark Theme) */
        .info-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s, box-shadow 0.2s;
            color: #f8fafc;
        }
        
        .info-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border-color: #3b82f6;
        }

        /* Metric styling for Dark Mode */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #3b82f6 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
        }

        /* Responsive Grid for Results (Safe for Slim Phones) */
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            padding-top: 16px;
        }

        /* Mobile specific fixes (Ultra-Slim Support) */
        @media (max-width: 640px) {
            [data-testid="stMetricValue"] {
                font-size: 1.2rem !important;
            }
            .stHorizontalBlock {
                flex-direction: column !important;
                gap: 8px !important;
            }
            .info-card {
                padding: 12px;
                margin-bottom: 12px;
                width: 100%;
            }
            .main .block-container {
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }
            [data-testid="stSidebar"] {
                width: 80vw !important;
            }
        }

        /* Sidebar cleanup (Dark Theme) */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }

        /* Tabs (Dark Theme) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            color: #94a3b8;
        }

        .stTabs [aria-selected="true"] {
            color: #3b82f6 !important;
            font-weight: 700 !important;
            border-bottom-color: #3b82f6 !important;
        }

        /* Text colors */
        h1, h2, h3, h4, p, span, li {
            color: #f1f5f9 !important;
        }
        
        .stMarkdown div p {
            color: #cbd5e1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page config (Must be the FIRST Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NCR Property Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_custom_css()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

CITIES = ["Delhi", "Faridabad", "Ghaziabad", "Greater Noida", "Gurugram", "Noida"]
PROP_TYPES = ["Apartment", "Builder Floor", "Independent House"]
FURNISHED_OPTIONS = ["Unknown", "Fully-Furnished", "Semi-Furnished", "Unfurnished"]
LEGAL_OPTIONS = ["Unknown", "Freehold", "Leasehold", "Power of Attorney"]


# Load verified society names mapping (City -> Locality -> [Societies])
@st.cache_data
def load_society_map():
    try:
        import json
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        index_path = root / "data" / "locality_intelligence_index.json"

        with open(index_path, "r") as f:
            data = json.load(f)
            # Map UI City names to JSON keys (already normalized in build_locality_index.py)
            mapping = {
                "Gurugram": data.get("Gurugram", {}),
                "Greater Noida": data.get("Greater Noida", {}),
                "Delhi": data.get("Delhi", {}),
                "Faridabad": data.get("Faridabad", {}),
                "Ghaziabad": data.get("Ghaziabad", {}),
                "Noida": data.get("Noida", {}),
            }
            return mapping
    except:
        return {}


SOCIETY_MAP = load_society_map()

# Data-rich sector hints (mapped to societies_detailed_map.json)
SECTOR_HINTS = {
    "Delhi": ["West Patel Nagar", "Vasant Kunj", "Greater Kailash I", "Saket", "Janakpuri"],
    "Faridabad": ["Green Field Colony", "Sector 85", "Sector 89", "RPS City", "Sector 16"],
    "Ghaziabad": ["Vaishali", "Niti Khand", "Raj Nagar Extension", "Shakti Khand", "Ahinsa Khand"],
    "Greater Noida": [
        "Noida Extension",
        "Techzone IV Greater Noida West",
        "Sector 1",
        "Jalpura",
        "Vaidpura",
    ],
    "Gurugram": [
        "Sector 89",
        "Sector 70A",
        "Sector 102",
        "Sector 57",
        "Sector 67",
        "Sector 92",
        "Sushant Lok Phase 1",
    ],
    "Noida": ["Sector 137", "Sector 150", "Sector 104", "Amarpali Silicon City", "Sector 107"],
}


# ---------------------------------------------------------------------------
# API Health Check
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1)
def check_api():
    try:
        r = requests.get(HEALTH_URL, timeout=2)
        return r.status_code == 200, r.json()
    except:
        return False, {}


api_healthy, health_data = check_api()


@st.cache_data(ttl=60)
def get_hotspots(listing_type: str):
    """Fetch pre-computed H3 hotspots for the selected listing type."""
    try:
        url = f"{API_BASE_URL}/intelligence/hotspots?listing_type={listing_type.lower()}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("hotspots", [])
        return []
    except:
        return []


# ---------------------------------------------------------------------------
# Sidebar — Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("NCR Intelligence")
    st.caption("Spatial AI & Market Analytics")
    if not api_healthy:
        st.error("API Offline - Server requires restart.")

    mode = st.radio("Navigation", ["Market Analyzer", "Property Recommender"])

    if mode == "Market Analyzer":
        st.markdown("### Location")
        city = st.selectbox("NCR City", CITIES, index=4)
        hints = SECTOR_HINTS.get(city, ["Sector 1"])

        city_data = SOCIETY_MAP.get(city, {})
        all_city_localities = sorted(list(city_data.keys()))

        sector = st.selectbox(
            f"Locality / Sector ({len(all_city_localities)} found)",
            options=all_city_localities if all_city_localities else ["Other"],
            index=0,
            help="Type to search for sectors in this city.",
        )

        loc_data = city_data.get(sector, {})
        sector_societies = loc_data.get("top_societies", [])
        total_discovery = loc_data.get("listing_count", 0)

        if not sector_societies:
            all_city_societies = set()
            for l_data in city_data.values():
                all_city_societies.update(l_data.get("societies", []))
            raw_list = sorted(list(all_city_societies))
            scope_label = "all in city"
            discovery_label = f"city-wide fallback"
        else:
            raw_list = sorted(sector_societies)
            scope_label = f"in {sector}"
            discovery_label = f"{total_discovery} listings in {sector}"

        def sort_score(name):
            n = name.lower()
            if any(x in n for x in ["independent", "standalone", "builder floor"]):
                return 100
            if any(x in n for x in ["block ", "phase ", "sector "]):
                return 50
            return 0

        display_societies = sorted(raw_list, key=lambda x: (sort_score(x), x))

        prop_name = st.selectbox(
            f"Verified Property ({discovery_label})",
            options=["Custom / None"] + display_societies,
            index=0,
            help=f"Discovered {total_discovery} historical listings in this sector.",
        )

        st.markdown("### Configuration")
        prop_type = st.selectbox("Property Type", PROP_TYPES)
        c1, c2 = st.columns(2)
        with c1:
            bedrooms = st.number_input("BHK", 1, 10, 3)
        with c2:
            bathrooms = st.number_input("Bathrooms", 0, 10, 2)

        c3, c4 = st.columns(2)
        with c3:
            area = st.number_input("Area (sqft)", 100, 50000, 1500)
        with c4:
            legal = st.selectbox("Legal", LEGAL_OPTIONS)

        furnished = st.selectbox("Furnished", FURNISHED_OPTIONS)

        st.markdown("### Market Factors")
        c_cat, c_amen = st.columns(2)
        with c_cat:
            is_luxury = st.checkbox("Luxury Segment")
            is_gated = st.checkbox("Gated Community", value=True)
            is_metro = st.checkbox("Near Metro (500m)", value=True)
            is_owner = st.checkbox("Owner Listing")
            is_rera = st.checkbox("RERA Registered", value=True)
            is_standalone = st.checkbox("Standalone Building")
            no_brokerage = st.checkbox("No Brokerage")

        with c_amen:
            is_vastu = st.checkbox("Vastu Compliant")
            is_corner = st.checkbox("Corner Property")
            is_park = st.checkbox("Park Facing")
            has_pool = st.checkbox("Swimming Pool")
            has_gym = st.checkbox("Gymnasium")
            has_lift = st.checkbox("Lift Access", value=True)
            has_backup = st.checkbox("Power Backup", value=True)

        with st.expander("Additional Rooms"):
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                is_servant = st.checkbox("Servant Room")
                is_study = st.checkbox("Study Room")
            with c_r2:
                is_store = st.checkbox("Store Room")
                is_pooja = st.checkbox("Pooja Room")

        predict_btn = st.button("Generate Intelligence", type="primary", use_container_width=True, disabled=not api_healthy)

    elif mode == "Property Recommender":
        st.markdown("### Search Criteria")
        rec_city = st.selectbox("NCR City", CITIES, index=4, key="rec_city")
        listing_type = st.radio("Looking to", ["Buy", "Rent"], horizontal=True)

        st.markdown("### BHK Options")
        bhk_options = [1, 2, 3, 4, 5]
        selected_bhk = []
        c1, c2, c3 = st.columns(3)
        for i, b in enumerate(bhk_options):
            col = [c1, c2, c3][i % 3]
            if col.checkbox(f"{b} BHK", value=(b == 3)):
                selected_bhk.append(b)

        st.markdown("### Budget (Absolute)")
        if listing_type == "Buy":
            budget = st.slider("Budget (₹ Lakhs)", 10, 500, (50, 200), step=10)
            budget_min = budget[0] * 100000
            budget_max = budget[1] * 100000
        else:
            budget = st.slider("Monthly Rent (₹ Thousands)", 5, 200, (15, 60), step=5)
            budget_min = budget[0] * 1000
            budget_max = budget[1] * 1000

        if listing_type == "Buy":
            sort_options = ["yield", "roi", "price_low", "price_high", "area"]
            sort_labels = {
                "yield": "Highest Rental Yield",
                "roi": "Best ROI Index",
                "price_low": "Lowest Price",
                "price_high": "Highest Price",
                "area": "Largest Area",
            }
        else:
            sort_options = ["price_low", "price_high", "area"]
            sort_labels = {
                "price_low": "Lowest Rent",
                "price_high": "Highest Rent",
                "area": "Largest Area",
            }

        sort_by = st.selectbox("Sort By", sort_options, format_func=lambda x: sort_labels[x])
        discover_btn = st.button("Discover Properties", type="primary", disabled=not api_healthy)

# ---------------------------------------------------------------------------
# Results Display
# ---------------------------------------------------------------------------
if mode == "Market Analyzer":
    if predict_btn:
        payload = {
            "area": float(area),
            "bedrooms": int(bedrooms),
            "bathrooms": int(bathrooms),
            "prop_type": prop_type,
            "furnishing_status": furnished,
            "legal_status": legal,
            "city": city,
            "sector": sector,
            "property_name": prop_name if prop_name != "Custom / None" else None,
            "is_luxury": is_luxury,
            "is_gated_community": is_gated,
            "is_near_metro": is_metro,
            "is_owner_listing": is_owner,
            "is_standalone": is_standalone,
            "is_rera_registered": is_rera,
            "is_vastu_compliant": is_vastu,
            "is_corner_property": is_corner,
            "is_park_facing": is_park,
            "has_pool": has_pool,
            "has_gym": has_gym,
            "has_lift": has_lift,
            "has_power_backup": has_backup,
            "is_servant_room": is_servant,
            "is_study_room": is_study,
            "is_store_room": is_store,
            "is_pooja_room": is_pooja,
            "no_brokerage": no_brokerage
        }

        with st.spinner("Analyzing Market Micro-Data..."):
            try:
                res = requests.post(PREDICT_URL, json=payload, timeout=10)
                res.raise_for_status()
                data = res.json()

                header_title = f"{prop_name} • {sector}" if prop_name != "Custom / None" else f"{city} • {sector}"
                st.markdown(f"## {header_title}")
                
                # --- Metrics Grid ---
                m1, m2, m3 = st.columns(3)
                with m1:
                    val_fmt = f"₹ {format_indian_number(data['estimated_market_value'])}"
                    psq_fmt = f"₹ {format_indian_number(data['price_per_sqft'])} / sqft"
                    st.metric("Valuation Estimate", val_fmt, psq_fmt)
                
                with m2:
                    rent_fmt = f"₹ {format_indian_number(data['predicted_monthly_rent'])} / mo"
                    yield_fmt = f"Yield: {data['intelligence_suite']['rental_yield_pct']}%"
                    st.metric("Rental Benchmark", rent_fmt, yield_fmt)
                
                with m3:
                    risk = data['intelligence_suite']['risk_analysis']
                    st.metric("Investment ROI Index", f"{data['intelligence_suite']['investment_roi_index']} / 10", f"Risk: {risk['label']}")

                # --- Tabbed Details ---
                tab_overview, tab_market, tab_spatial = st.tabs(["📊 Market Data", "🏆 Comparison", "🗺️ Spatial Evidence"])
                
                with tab_overview:
                    st.markdown("### Intelligence Breakdown")
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.write("**Annual Rent Return:**")
                        st.subheader(f"₹ {format_indian_number(data['intelligence_suite']['annual_rent_return'])}")
                    with c2:
                        st.write("**Risk Analysis:**")
                        st.info(f"Property is currently categorized as **{risk['label']}** based on micro-market H3 medians.")

                with tab_market:
                    if data.get("similar_listings"):
                        st.markdown("### Comparable Properties")
                        comp_df = pd.DataFrame(data["similar_listings"])
                        # Format prices in DF
                        comp_df['price_display'] = comp_df['price'].apply(lambda x: f"₹ {format_indian_number(x)}")
                        comp_df['psqft_display'] = comp_df['price_sqft'].apply(lambda x: f"₹ {format_indian_number(x)}")
                        
                        st.dataframe(
                            comp_df[["society", "locality", "price_display", "area", "psqft_display"]], 
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("No comparable listings found in the immediate sector.")

                with tab_spatial:
                    with st.expander("Explore H3 Spatial Density", expanded=False):
                        if data.get("similar_listings"):
                            sim_map_items = [d for d in data["similar_listings"] if d.get('latitude') and d.get('longitude')]
                            if sim_map_items:
                                st.pydeck_chart(pdk.Deck(
                                    initial_view_state=pdk.ViewState(
                                        latitude=sum(d['latitude'] for d in sim_map_items)/len(sim_map_items),
                                        longitude=sum(d['longitude'] for d in sim_map_items)/len(sim_map_items),
                                        zoom=12.5, pitch=30,
                                    ),
                                    layers=[pdk.Layer("ScatterplotLayer", data=sim_map_items, get_position=["longitude", "latitude"],
                                                      get_radius=100, get_fill_color=[59, 130, 246, 180], pickable=True)],
                                    tooltip={"html": "<b>{society}</b><br/>₹{price}"}
                                ))
                            else:
                                st.info("Insufficient spatial data to render high-resolution H3 map.")
                        else:
                            st.info("Insufficient spatial data to render high-resolution H3 map.")

            except Exception as e:
                st.error(f"Intelligence failure: {e}")
    else:
        show_market_analyzer_dashboard()

elif mode == "Property Recommender":
    if discover_btn:
        payload = {
            "city": rec_city,
            "listing_type": listing_type.lower(),
            "bhk": selected_bhk,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "sort_by": sort_by,
        }
        with st.spinner("Searching Discovery Pool..."):
            try:
                res = requests.post(f"{API_BASE_URL}/discover", json=payload, timeout=10)
                res.raise_for_status()
                data = res.json().get("listings", [])

                if not data:
                    st.warning("No matches found within this budget across the NCR corridor.")
                else:
                    st.success(f"Discovered {len(data)} High-Priority Targets")

                    map_items = []
                    for d in data:
                        if d.get('latitude') and d.get('longitude'):
                            # Format for map
                            item = d.copy()
                            item['price_display'] = f"₹ {format_indian_number(item['price'])}"
                            
                            # Color coding [R, G, B, A]
                            score = item.get('roi_index', 5.0)
                            if score >= 7.5:
                                item['color'] = [16, 185, 129, 220] # Green
                            elif score >= 5.0:
                                item['color'] = [245, 158, 11, 220] # Amber
                            else:
                                item['color'] = [239, 68, 68, 220]  # Red
                            map_items.append(item)

                    with st.expander("Explore NCR Corridor (Heatmap)", expanded=False):
                        if map_items:
                            st.pydeck_chart(pdk.Deck(
                                initial_view_state=pdk.ViewState(latitude=28.61, longitude=77.23, zoom=10, pitch=40),
                                layers=[pdk.Layer("ScatterplotLayer", data=map_items, get_position=["longitude", "latitude"],
                                                  get_radius=180, get_fill_color="color", pickable=True)],
                                tooltip={"html": "<b>{society}</b><br/>{price_display}<br/>Score: {roi_index}/10"}
                            ))
                    
                    # --- ROI / Deal Explanation ---
                    if listing_type.lower() == "buy":
                        exp_title = "How is the ROI Index calculated?"
                        exp_text = """
                        The **Investment ROI Index** (0-10) is a composite score calculated as:
                        - **Base Score (5.0)**: The starting baseline.
                        - **Yield Bonus**: Up to **+5.0** based on annual rental yield (benchmarked at 2-6%).
                        - **Metro Bonus**: **+2.0** if the property is within 500m of a Metro station.
                        - **Risk Penalty**: Up to **-3.0** deducted if the property is overvalued vs. its H3 micro-market median.
                        """
                        section_title = "Top Investment Targets"
                    else:
                        exp_title = "How is the Deal Rating calculated?"
                        exp_text = """
                        The **Deal Rating** (0-10) is a value-metric for tenants calculated as:
                        - **Market Comparison**: Comparing current rent vs. the **H3 Spatial Median** for the exact neighborhood.
                        - **Savings Bonus**: Points added if the rent is significantly lower than similar properties.
                        - **Location Quality**: Includes proximity to transit and local amenities.
                        """
                        section_title = "Top Rental Picks"

                    with st.expander(exp_title, expanded=False):
                        st.markdown(exp_text)

                    # --- Result Cards Grid ---
                    st.markdown(f"### {section_title}")
                    
                    # Wrap cards in a div for CSS Grid control
                    cards_html = ""
                    for item in data:
                        # Logic for tenant-centric vs investor metrics
                        if listing_type.lower() == "buy":
                            metric_label = "Yield"
                            metric_val = f"{item['rental_yield_pct']}%"
                            score_label = f"ROI: {item['roi_index']}/10"
                            badge = "Great Value" if item['value_score'] > 0.05 else "Fair Value" if item['value_score'] > -0.05 else "Premium Price"
                        else:
                            h3_med = item.get('h3_median_price', 0)
                            if h3_med > 0:
                                savings = h3_med - item['price']
                                if savings > 0:
                                    metric_label = "Savings"
                                    metric_val = f"₹ {format_indian_number(savings)}"
                                else:
                                    metric_label = "Premium"
                                    metric_val = f"₹ {format_indian_number(abs(savings))}"
                            else:
                                metric_label = "Area"
                                metric_val = f"{item['area']} sqft"

                            score_label = f"Deal: {item['roi_index']}/10"
                            badge = "Budget Pick" if item['value_score'] > 0.05 else "Fair Deal" if item['value_score'] > -0.05 else "Luxury Living"

                        cards_html += f"""
                        <div class="info-card">
                            <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px;">{item['locality']}, {item['city']}</div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; line-height: 1.2;">{item['society']}</div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-weight: 600; color: #3b82f6;">{item['bhk']} BHK</span>
                                <span style="font-weight: 600; color: #10b981;">₹ {format_indian_number(item['price'])}</span>
                            </div>
                            <div style="font-size: 0.85rem; color: #94a3b8; display: flex; justify-content: space-between; border-top: 1px solid #334155; padding-top: 8px;">
                                <span>Area: {item['area']} sqft</span>
                                <span>{metric_label}: {metric_val}</span>
                            </div>
                            <div style="margin-top: 12px; display: flex; align-items: center; justify-content: space-between;">
                                <div style="background: #1e293b; color: #3b82f6; border: 1px solid #3b82f6; padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700;">
                                    {score_label}
                                </div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: {'#10b981' if item['value_score'] > 0 else '#ef4444'};">
                                    {badge}
                                </div>
                            </div>
                        </div>
                        """
                    
                    st.markdown(f'<div class="results-grid">{cards_html}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Discovery failure: {e}")
    else:
        show_property_recommender_dashboard()
