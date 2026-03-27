"""
🏙️ NCR Property Intelligence — Streamlit Frontend
V28: Active Intelligence Suite
"""

import os
import requests
import streamlit as st
import pandas as pd
import pydeck as pdk
import textwrap

# ---------------------------------------------------------------------------
# Page config (Must be the FIRST Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NCR Property Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        with open("societies_detailed_map_v2.json", "r") as f:
            data = json.load(f)
            # Map UI City names to JSON keys
            mapping = {
                "Gurugram": data.get("Gurgaon", {}),
                "Greater Noida": data.get("Greater_Noida", {}),
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
    "Greater Noida": ["Noida Extension", "Techzone IV Greater Noida West", "Sector 1", "Jalpura", "Vaidpura"],
    "Gurugram": ["Sector 89", "Sector 70A", "Sector 102", "Sector 57", "Sector 67", "Sector 92", "Sushant Lok Phase 1"],
    "Noida": ["Sector 137", "Sector 150", "Sector 104", "Amarpali Silicon City", "Sector 107"],
}


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* V30 Design System: Tokens & Variables */
    :root {
        --bg-card: rgba(255, 255, 255, 0.03);
        --bg-sidebar: #0b0f19;
        --border-subtle: rgba(255, 255, 255, 0.1);
        --text-primary: #f9fafb;
        --text-secondary: #9ca3af;
        --text-muted: #6b7280;
        --accent-blue: #63b3ed;
        --accent-green: #48bb78;
        --accent-orange: #ed8936;
        --primary: #2563eb;
    }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Hero Header - Responsive */
    .hero-header {
        background-color: #111827;
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: clamp(1.25rem, 4vw, 2.5rem);
        margin-bottom: 2rem;
        color: var(--text-primary);
    }
    .hero-header h1 { 
        font-size: clamp(1.5rem, 5vw, 2.25rem); 
        font-weight: 700; 
        color: var(--text-primary); 
        margin: 0; 
    }
    .hero-header p { 
        font-size: clamp(0.9rem, 2vw, 1.125rem); 
        color: var(--text-secondary); 
        margin-top: 0.5rem; 
    }

    /* Result Metric Cards (Market Analyzer) */
    .result-card {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }
    .result-card:hover { 
        border-color: var(--accent-blue); 
        box-shadow: 0 4px 12px rgba(99, 179, 237, 0.1);
        transform: translateY(-2px); 
    }
    .result-card .label { 
        font-size: 0.75rem; 
        color: var(--text-secondary); 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 0.75rem; 
        font-weight: 600; 
    }
    .result-card .value { 
        font-size: clamp(1.25rem, 3vw, 2rem); 
        font-weight: 700; 
        color: var(--text-primary); 
    }
    .result-card .value-highlight { color: var(--accent-blue); }

    /* Property Item Cards (Responsive Stack) */
    .property-item {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s;
        display: flex;
        justify-content: space-between;
        gap: 1rem;
    }
    .property-item:hover { border-color: rgba(99, 179, 237, 0.3); }
    
    .prop-info-main { flex: 1; }
    .prop-price-metrics { text-align: right; min-width: 120px; }
    
    .listing-tag {
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: inline-block;
    }
    .tag-buy { background: rgba(99, 179, 237, 0.2); color: var(--accent-blue); }
    .tag-rent { background: rgba(72, 187, 120, 0.2); color: var(--accent-green); }

    /* Mobile Adaptations */
    @media (max-width: 768px) {
        .property-item { flex-direction: column; gap: 0.5rem; }
        .prop-price-metrics { text-align: left; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem; min-width: unset; }
        .stMetric { margin-bottom: 1rem; }
    }

    .soft-divider { height: 1px; background-color: #2d3748; margin: 2rem 0; border: none; }
</style>
""", unsafe_allow_html=True)

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
    """Fetch pre-computed H3 hotspots for the selected listing type (V30)."""
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
    st.caption("V30.1: Spatial AI & Market Analytics")
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
            help="Type to search for sectors in this city."
        )

        loc_data = city_data.get(sector, {})
        sector_societies = loc_data.get("societies", [])
        total_discovery = loc_data.get("total_listings", 0)
        
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
            if any(x in n for x in ["independent", "standalone", "builder floor"]): return 100
            if any(x in n for x in ["block ", "phase ", "sector "]): return 50
            return 0 
            
        display_societies = sorted(raw_list, key=lambda x: (sort_score(x), x))

        prop_name = st.selectbox(
            f"Verified Property ({discovery_label})", 
            options=["Custom / None"] + display_societies, 
            index=0,
            help=f"Discovered {total_discovery} historical listings in this sector."
        )

        st.markdown("### Configuration")
        prop_type = st.selectbox("Property Type", PROP_TYPES)
        c1, c2 = st.columns(2)
        with c1: bedrooms = st.number_input("BHK", 1, 10, 3)
        with c2: bathrooms = st.number_input("Bathrooms", 0, 10, 2)
        
        c3, c4 = st.columns(2)
        with c3: area = st.number_input("Area (sqft)", 100, 50000, 1500)
        with c4: legal = st.selectbox("Legal", LEGAL_OPTIONS)
        
        furnished = st.selectbox("Furnished", FURNISHED_OPTIONS)

        st.markdown("### V28 Catalysts")
        is_luxury = st.checkbox("Luxury Segment")
        is_gated = st.checkbox("Gated Community", value=True)
        is_metro = st.checkbox("Near Metro (500m)", value=True)
        is_owner = st.checkbox("Owner Listing")
        is_rera = st.checkbox("RERA Registered", value=True)
        is_standalone = st.checkbox("Standalone Building")

        predict_btn = st.button("Generate Intelligence", type="primary", disabled=not api_healthy)

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
            if col.checkbox(f"{b} BHK", value=(b==3)):
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
                "area": "Largest Area"
            }
        else:
            sort_options = ["price_low", "price_high", "area"]
            sort_labels = {
                "price_low": "Lowest Rent",
                "price_high": "Highest Rent",
                "area": "Largest Area"
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
            "is_rera_registered": is_rera
        }

        with st.spinner("Analyzing Market Micro-Data..."):
            try:
                res = requests.post(PREDICT_URL, json=payload, timeout=10)
                res.raise_for_status()
                data = res.json()

                # Header
                header_title = f"{prop_name} • {sector}" if prop_name != "Custom / None" else f"{city} • {sector}"
                st.markdown(f"""
                <div class="hero-header">
                    <h1>{header_title}</h1>
                    <p>{bedrooms} BHK {prop_type} | {area:,} Sqft Intelligence Report</p>
                </div>
                """, unsafe_allow_html=True)

                # High-Level Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="label">Market Valuation</div>
                        <div class="value value-highlight">₹{data['estimated_market_value']:,.0f}</div>
                        <div class="sub">₹{data['price_per_sqft']:,.0f} / sqft</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="label">Rental Return</div>
                        <div class="value">₹{data['predicted_monthly_rent']:,.0f} <span style="font-size:1rem; color:#718096;">/mo</span></div>
                        <div class="sub">Yield: {data['intelligence_suite']['rental_yield_pct']}% p.a.</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    risk = data['intelligence_suite']['risk_analysis']
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="label">Active ROI Index</div>
                        <div class="value">{data['intelligence_suite']['investment_roi_index']} <span style="font-size:1rem; color:#718096;">/ 10</span></div>
                        <div class="sub">Risk Level: {risk['label']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("### Locality Risk Analysis")
                st.info(f"**Analysis**: {risk['label']}. This asset is currently performing at **{risk['score']}%** of the local spatial value peak (H3 Index).")
                
                # Recommender System (V29)
                if data.get("recommendations"):
                    st.write("---")
                    st.markdown("### Alternative Investment Opportunities")
                    st.caption(f"Top localities in {city} offering similar value with optimized yields.")
                    
                    # Compare current vs best alternative
                    best_alt = data["recommendations"][0]
                    current_y = data['intelligence_suite']['rental_yield_pct']
                    yield_diff = best_alt['expected_yield_pct'] - current_y
                    
                    if yield_diff > 0:
                        st.success(f"**Insight**: Switching to **{best_alt['locality']}** could increase your gross yield by **+{yield_diff:.2f}%**.")

                    # Display Recommendations in Cards
                    cols = st.columns(len(data["recommendations"]))
                    for idx, alt in enumerate(data["recommendations"]):
                        with cols[idx]:
                            st.markdown(f"""
                            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; height: 100%;">
                                <div style="font-weight: 600; color: #63b3ed; font-size: 0.9rem; margin-bottom: 8px;">{alt['locality']}</div>
                                <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 4px;">{alt['expected_yield_pct']}% <span style="font-size: 0.7rem; font-weight: 400; color: #a0aec0;">Yield</span></div>
                                <div style="font-size: 0.8rem; color: #cbd5e0; margin-bottom: 10px;">₹{alt['median_price_sqft']:,}/sqft</div>
                                <div style="font-size: 0.7rem; color: #718096; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
                                    <b>Top Projects:</b><br>{", ".join(alt['top_societies'][:2]) if alt['top_societies'] else "Various"}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    
                # Property Discovery (V30.1) - Real Listings
                if data.get("similar_listings"):
                    st.write("---")
                    st.markdown(f"### Local Market Evidence: Top Matches in {city}")
                    st.caption("Real historical listings found in our database matching your search profile.")
                    
                    # Display Listings in a Table or Cards
                    discovery_df = pd.DataFrame(data["similar_listings"])
                    sim_map_items = [d for d in data["similar_listings"] if d.get('latitude') and d.get('longitude')]
                    
                    # Airtight Selection & Value Audit (V30.3 - Hardened)
                    def get_pos(score):
                        try:
                            if pd.isna(score) or score == 0: return "🟡 Fair Value"
                            if score > 0.1: return "🟢 Great Value"
                            if score > 0.03: return "🟢 Good Deal"
                            if score < -0.1: return "🔴 Premium"
                            return "🟡 Fair Value"
                        except:
                            return "🟡 Pending Audit"
                    
                    cols_to_show = ["society", "locality", "price", "area", "bhk", "price_sqft"]
                    display_df = discovery_df[cols_to_show].copy()
                    
                    # Ensure value_score exists before applying logic
                    if "value_score" in discovery_df.columns:
                        display_df["Market Position"] = discovery_df["value_score"].apply(get_pos)
                    else:
                        display_df["Market Position"] = "🟡 Pending Audit"
                    
                    # Rename to professional headers
                    display_df.columns = ["Society", "Locality/Sector", "Price", "Area", "BHK", "Price/sqft", "Market Position"]
                    
                    # Format Price for readability
                    display_df["Price"] = display_df["Price"].apply(lambda x: f"₹{x:,.0f}")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                    )
                    
                    # Mini map for similar listings (V30.2: Unified UI)
                    if sim_map_items:
                        with st.expander("View Evidence Map", expanded=False):
                            st.info("These markers represent the exact locations of the historical matches listed above. Hover for society names and prices.")
                            sim_map_df = pd.DataFrame(sim_map_items)
                            st.pydeck_chart(pdk.Deck(
                                initial_view_state=pdk.ViewState(
                                    latitude=sim_map_df['latitude'].mean(),
                                    longitude=sim_map_df['longitude'].mean(),
                                    zoom=12,
                                    pitch=25,
                                ),
                                layers=[
                                    pdk.Layer(
                                        "ScatterplotLayer",
                                        data=sim_map_df,
                                        get_position=["longitude", "latitude"],
                                        get_radius=120,
                                        get_fill_color=[72, 187, 120, 200],
                                        pickable=True,
                                        auto_highlight=True,
                                    ),
                                ],
                                tooltip={
                                    "html": "<b>{society}</b><br/>{locality}<br/>₹{price:,.0f}",
                                    "style": {"backgroundColor": "#1a202c", "color": "#edf2f7", "fontSize": "13px", "padding": "8px", "borderRadius": "8px"}
                                }
                            ))
                    
                # Additional Insights
                st.write("---")
                st.markdown("#### Investment Catalysts")
                c1, c2, c3 = st.columns(3)
                c1.metric("Annualized Return", f"₹{data['intelligence_suite']['annual_rent_return']:,.0f}")
                c2.metric("Metro Premium", "Yes" if is_metro else "No", delta="+2.0 ROI Pts" if is_metro else None)
                c3.metric("Segment", "Luxury" if is_luxury else "Standard")

            except Exception as e:
                st.error(f"Intelligence failure: {e}")
            
elif mode == "Property Recommender":
    st.markdown("""
    <div class="hero-header">
        <h1>Property Discovery</h1>
        <p>Real historical listings filtered by your exact investment criteria.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- V30.1: Market Hotspots Heatmap ---
    with st.expander("Explore NCR Market Hotspots", expanded=False):
        st.info("Spatial Heatmap Guide: 3D column height represents Listing Density. Color gradient shows Pricing distribution (Warm = High Val, Cool = Budget).")
        hotspots = get_hotspots(listing_type)
        if not hotspots:
            st.info("No market data available for the current filters.")
        else:
            df_hotspots = pd.DataFrame(hotspots)
            
            # Dynamic scaling based on listing type
            elevation_scale = 50 if listing_type == "Buy" else 15
            
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v11',
                initial_view_state=pdk.ViewState(
                    latitude=28.5,
                    longitude=77.1,
                    zoom=9,
                    pitch=45,
                ),
                layers=[
                    pdk.Layer(
                        "H3HexagonLayer",
                        df_hotspots,
                        get_hexagon="h3_res8",
                        get_fill_color="[255, (1 - median_price_sqft / 20000) * 255, 0, 150]" if listing_type == "Buy" 
                                        else "[0, 255, (1 - median_price_sqft / 100) * 255, 150]",
                        get_elevation="density",
                        elevation_scale=elevation_scale,
                        elevation_range=[0, 1000],
                        pickable=True,
                        extruded=True,
                    ),
                ],
                tooltip={
                    "html": "<b>{city}</b><br/>Median Price: ₹{median_price_sqft:,.0f}/sqft<br/>Listings: {density}",
                    "style": {"backgroundColor": "#111827", "color": "#F3F4F6"}
                }
            ))
            st.caption(f"Currently viewing 3D density for **{listing_type}** listings across {len(df_hotspots)} NCR hotspots.")
    
    if 'discover_btn' in locals() and discover_btn:
        payload = {
            "city": rec_city,
            "listing_type": listing_type.lower(),
            "bhk": selected_bhk,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "sort_by": sort_by
        }
        with st.spinner("Searching Discovery Pool..."):
            try:
                res = requests.post(f"{API_BASE_URL}/discover", json=payload, timeout=10)
                res.raise_for_status()
                data = res.json().get("listings", [])
                
                if not data:
                    st.warning("No properties found matching your specific criteria.")
                else:
                    st.success(f"Found {len(data)} high-priority matches.")
                    
                    # --- Interactive Map (V30.2: Unified UI) ---
                    map_items = [d for d in data if d.get('latitude') and d.get('longitude')]
                    if map_items:
                        with st.expander("Explore Discovery Locations", expanded=False):
                            st.info("Visualizing the precise geographic footprint of the high-ROI properties identified by the recommender engine.")
                            map_df = pd.DataFrame(map_items)
                            avg_lat = map_df['latitude'].mean()
                            avg_lng = map_df['longitude'].mean()
                            
                            st.pydeck_chart(pdk.Deck(
                                initial_view_state=pdk.ViewState(
                                    latitude=avg_lat,
                                    longitude=avg_lng,
                                    zoom=11,
                                    pitch=35,
                                ),
                                layers=[
                                    pdk.Layer(
                                        "ScatterplotLayer",
                                        data=map_df,
                                        get_position=["longitude", "latitude"],
                                        get_radius=150,
                                        get_fill_color=[99, 179, 237, 180],
                                        pickable=True,
                                        auto_highlight=True,
                                    ),
                                ],
                                tooltip={
                                    "html": "<b>{society}</b><br/>{locality}<br/>{bhk} BHK • {area} sqft<br/>₹{price}",
                                    "style": {"backgroundColor": "#1a202c", "color": "#edf2f7", "fontSize": "13px", "padding": "8px", "borderRadius": "8px"}
                                }
                            ))
                    
                    st.write("---")
                    
                    # --- Result Cards (V30: Responsive Redesign) ---
                    for item in data:
                        is_buy = item['listing_type'] == 'buy'
                        tag_class = "tag-buy" if is_buy else "tag-rent"
                        
                        if is_buy:
                            if item['price'] >= 10000000:
                                price_fmt = f"₹{item['price']/10000000:.2f} Cr"
                            else:
                                price_fmt = f"₹{item['price']/100000:.2f} L"
                            price_sqft_str = f" • ₹{item['price_sqft']:,.0f}/sqft"
                        else:
                            price_fmt = f"₹{item['price']:,.0f}/mo"
                            price_sqft_str = ""
                        
                        # Audit Badge (V30.3)
                        val_score = item.get('value_score', 0)
                        if val_score > 0.1:
                            badge_html = f'<div style="background: rgba(72,187,120,0.2); color: #48bb78; border: 1px solid #48bb78; border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; width: fit-content; margin-bottom: 8px;">INVESTMENT GRADE ({(val_score*100):.1f}% Below Avg)</div>'
                        elif val_score > 0.03:
                            badge_html = f'<div style="background: rgba(72,187,120,0.1); color: #48bb78; border: 1px solid rgba(72,187,120,0.3); border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; width: fit-content; margin-bottom: 8px;">GOOD VALUE</div>'
                        elif val_score < -0.1:
                            badge_html = f'<div style="background: rgba(245,101,101,0.1); color: #f56565; border: 1px solid rgba(245,101,101,0.3); border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 700; width: fit-content; margin-bottom: 8px;">PREMIUM ASSET</div>'
                        else:
                            badge_html = ""

                        # Zero-Indentation Force (V30.5: NO LEADING NEWLINES)
                        card_html = f"""<div class="property-item">
<div class="prop-info-main">
{badge_html}
<span class="listing-tag {tag_class}">{item['listing_type']}</span>
<div style="font-weight: 700; color: var(--accent-blue); font-size: 1.15rem;">{item['society']}</div>
<div style="font-size: 0.95rem; color: var(--text-secondary);">{item['locality']}, {item['city']}</div>
<div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 6px;">
{item['bhk']} BHK • {item['area']:,.0f} sqft {price_sqft_str}
</div>
</div>
<div class="prop-price-metrics">
<div style="font-size: 1.6rem; font-weight: 700; color: var(--text-primary);">{price_fmt}</div>
<div style="font-size: 0.85rem; color: var(--accent-green); font-weight: 600; margin-top: 2px;">Yield: {item['rental_yield_pct']}%</div>
<div style="font-size: 0.85rem; color: var(--accent-orange); font-weight: 600;">ROI: {item['roi_index']}/10</div>
</div>
</div>"""
                        st.markdown(card_html.strip(), unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Discovery failure: {e}")

else:
    st.markdown("""
    <div style="text-align: center; padding: 10% 20%;">
        <h2 style="color: #4A5568;">Select a property to analyze</h2>
        <p style="color: #718096;">The V28 Intelligence Suite calculates spatial risk and rental yields across the National Capital Region.</p>
    </div>
    """, unsafe_allow_html=True)

