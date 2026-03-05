"""
NCR Property Price Estimator — Streamlit Frontend

A modern UI for predicting property prices in the National Capital
Region (Delhi-NCR).  Calls the FastAPI backend at /predict to get
price-per-sqft and estimated total price.
"""

import os

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"

CITIES = ["Delhi", "Faridabad", "Ghaziabad", "Greater Noida", "Gurugram", "Noida"]
PROP_TYPES = ["Apartment", "Builder Floor", "Independent House"]
FURNISHED_OPTIONS = ["Unknown", "Fully-Furnished", "Semi-Furnished", "Unfurnished"]
FACING_OPTIONS = [
    "Unknown",
    "East",
    "North",
    "North-East",
    "North-West",
    "South",
    "South-East",
    "South-West",
    "West",
]

# Curated sector suggestions per city (most popular)
SECTOR_HINTS: dict[str, list[str]] = {
    "Delhi": [
        "Dwarka",
        "Rohini",
        "Saket",
        "Vasant Kunj",
        "Janakpuri",
        "Laxmi Nagar",
        "Uttam Nagar",
        "Greater Kailash",
        "Hauz Khas",
        "Pitampura",
        "Okhla",
    ],
    "Faridabad": [
        "Sector 14",
        "Sector 15",
        "Sector 16",
        "Sector 21",
        "Sector 37",
        "Sector 42",
        "Sector 43",
        "Sector 88",
        "Neharpar",
        "Green Fields",
    ],
    "Ghaziabad": [
        "Indirapuram",
        "Vaishali",
        "Vasundhara",
        "Raj Nagar Extension",
        "Crossings Republik",
        "Kaushambi",
        "Govindpuram",
        "Wave City",
    ],
    "Greater Noida": [
        "Sector Alpha",
        "Sector Beta",
        "Sector Gamma",
        "Sector Delta",
        "Sector Omega",
        "Sector Chi",
        "Pari Chowk",
        "Greater Noida West",
        "Knowledge Park",
    ],
    "Gurugram": [
        "Sector 49",
        "Sector 50",
        "Sector 54",
        "Sector 56",
        "Sector 57",
        "Sector 65",
        "Sector 67",
        "Sector 69",
        "Sector 82",
        "Golf Course Road",
        "Golf Course Extension",
        "Sohna Road",
        "DLF Phase 1",
        "DLF Phase 2",
        "DLF Phase 5",
    ],
    "Noida": [
        "Sector 15",
        "Sector 44",
        "Sector 50",
        "Sector 62",
        "Sector 74",
        "Sector 75",
        "Sector 76",
        "Sector 77",
        "Sector 78",
        "Sector 128",
        "Sector 137",
        "Sector 143",
        "Sector 150",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def format_inr(amount: float) -> str:
    """Format a number in Indian Rupee notation (lakhs / crores)."""
    if amount >= 1_00_00_000:
        return f"₹ {amount / 1_00_00_000:,.2f} Cr"
    if amount >= 1_00_000:
        return f"₹ {amount / 1_00_000:,.2f} L"
    return f"₹ {amount:,.0f}"


def format_inr_full(amount: float) -> str:
    """Full INR with commas (Indian grouping approximated)."""
    if amount >= 1_00_00_000:
        cr = amount / 1_00_00_000
        return f"₹ {cr:,.2f} Crore"
    if amount >= 1_00_000:
        lakh = amount / 1_00_000
        return f"₹ {lakh:,.2f} Lakh"
    return f"₹ {amount:,.0f}"


def check_api_health() -> bool:
    """Check if the FastAPI backend is reachable."""
    try:
        r = requests.get(HEALTH_URL, timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NCR Property Price Estimator",
    page_icon="https://em-content.zobj.net/source/twitter/408/house_1f3e0.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
    }

    .hero-header {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        color: #f9fafb;
    }
    .hero-header h1 {
        margin: 0 0 0.5rem 0;
        font-size: 1.75rem;
        font-weight: 600;
        color: #f9fafb;
        letter-spacing: -0.025em;
    }
    .hero-header p {
        margin: 0;
        font-size: 1rem;
        color: #9ca3af;
        font-weight: 400;
    }

    .result-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: left;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .result-card .label {
        font-size: 0.75rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .result-card .value {
        font-size: 1.875rem;
        font-weight: 600;
        color: #e5e7eb;
        line-height: 1.2;
    }
    .result-card .value-highlight {
        color: #3b82f6;
    }
    .result-card .sub {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid;
    }
    .status-online {
        background: transparent;
        color: #10b981;
        border-color: #10b981;
    }
    .status-offline {
        background: transparent;
        color: #ef4444;
        border-color: #ef4444;
    }

    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #9ca3af;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .soft-divider {
        border: none;
        height: 1px;
        background-color: #1f2937;
        margin: 1.5rem 0;
    }

    .amenity-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 0.5rem;
    }
    .amenity-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid;
    }
    .amenity-on {
        background-color: transparent;
        color: #e5e7eb;
        border-color: #374151;
    }
    .amenity-off {
        background-color: transparent;
        color: #4b5563;
        border-color: #1f2937;
    }

    /* Override dataframe table styles for uniform simple look */
    [data-testid="stMarkdownContainer"] table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
    }
    [data-testid="stMarkdownContainer"] th {
        text-align: left;
        border-bottom: 1px solid #374151;
        padding: 0.5rem;
        color: #9ca3af;
        font-weight: 500;
    }
    [data-testid="stMarkdownContainer"] td {
        border-bottom: 1px solid #1f2937;
        padding: 0.5rem;
        color: #e5e7eb;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="hero-header">
    <h1>NCR Property Price Estimator</h1>
    <p>Instant ML-powered price estimates for properties across Delhi-NCR</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# API health check
# ---------------------------------------------------------------------------
api_healthy = check_api_health()
if api_healthy:
    st.markdown(
        '<div class="status-badge status-online">&#9679; API Connected</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="status-badge status-offline">&#9679; API Offline</div>',
        unsafe_allow_html=True,
    )
    st.info(
        f"**API not reachable** at `{API_BASE_URL}`. "
        "Start it with: `uvicorn ncr_property_price_estimation.api:app --reload`"
    )

# ---------------------------------------------------------------------------
# Sidebar — Property Details
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Property Details")
    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

    # --- Location ---
    st.markdown("### Location")
    city = st.selectbox("City", CITIES, index=4, help="Select the NCR city")
    sector_hints = SECTOR_HINTS.get(city, ["Sector 50"])
    selected_sector = st.selectbox(
        "Sector / Locality",
        options=sector_hints + ["Other (Type manually)"],
        help="Type to search or scroll to select a locality",
    )
    if selected_sector == "Other (Type manually)":
        sector = st.text_input("Enter Sector Name", placeholder="e.g. Sector 12")
    else:
        sector = selected_sector

    # --- Property Type ---
    st.markdown("### Type & Configuration")
    prop_type = st.selectbox("Property Type", PROP_TYPES)
    col_bed, col_bath = st.columns(2)
    with col_bed:
        bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=3)
    with col_bath:
        bathrooms = st.number_input("Bathrooms", min_value=0, max_value=10, value=2)

    col_area, col_floor = st.columns(2)
    with col_area:
        area = st.number_input("Area (sqft)", min_value=100, max_value=50000, value=1200, step=50)
    with col_floor:
        floor = st.number_input("Floor", min_value=0, max_value=80, value=5)
    balcony = st.number_input("Balconies", min_value=0, max_value=10, value=2)

    # --- Furnishing & Facing ---
    st.markdown("### Furnishing & Facing")
    col_f, col_d = st.columns(2)
    with col_f:
        furnished = st.selectbox("Furnished", FURNISHED_OPTIONS)
    with col_d:
        facing = st.selectbox("Facing", FACING_OPTIONS)

    # --- Amenities ---
    st.markdown("### Amenities")
    amenity_cols = st.columns(2)
    with amenity_cols[0]:
        lift = st.checkbox("Lift", value=True)
        parking = st.checkbox("Parking", value=True)
        gym = st.checkbox("Gym", value=False)
        pool = st.checkbox("Pool", value=False)
    with amenity_cols[1]:
        pooja_room = st.checkbox("Pooja Room", value=False)
        servant_room = st.checkbox("Servant Room", value=False)
        store_room = st.checkbox("Store Room", value=False)
        vastu_compliant = st.checkbox("Vastu Compliant", value=False)

    st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

    predict_clicked = st.button(
        "Estimate Price",
        use_container_width=True,
        type="primary",
        disabled=not api_healthy,
    )


# ---------------------------------------------------------------------------
# Main Area — Results
# ---------------------------------------------------------------------------
if predict_clicked:
    if not sector.strip():
        st.warning("Please enter a **Sector / Locality** in the sidebar.")
        st.stop()

    payload = {
        "area": float(area),
        "bedrooms": int(bedrooms),
        "bathrooms": int(bathrooms),
        "balcony": int(balcony),
        "floor": int(floor),
        "prop_type": prop_type,
        "furnished": furnished,
        "facing": facing,
        "city": city,
        "sector": sector.strip(),
        "pooja_room": int(pooja_room),
        "servant_room": int(servant_room),
        "store_room": int(store_room),
        "pool": int(pool),
        "gym": int(gym),
        "lift": int(lift),
        "parking": int(parking),
        "vastu_compliant": int(vastu_compliant),
    }

    with st.spinner("Estimating price..."):
        try:
            resp = requests.post(PREDICT_URL, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            price_sqft = data["price_per_sqft"]
            total_price = data["estimated_total_price"]

            st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

            # --- Result cards ---
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(
                    f"""
                <div class="result-card">
                    <div class="label">Price per Sqft</div>
                    <div class="value">₹ {price_sqft:,.0f}</div>
                    <div class="sub">per square foot</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"""
                <div class="result-card">
                    <div class="label">Estimated Total</div>
                    <div class="value">{format_inr(total_price)}</div>
                    <div class="sub">{format_inr_full(total_price)}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown(
                    f"""
                <div class="result-card">
                    <div class="label">Property Area</div>
                    <div class="value">{area:,} sqft</div>
                    <div class="sub">{area * 0.0929:.0f} sq.m</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown('<hr class="soft-divider">', unsafe_allow_html=True)

            # --- Property summary ---
            st.markdown("#### Property Summary")
            summary_col1, summary_col2 = st.columns(2)
            with summary_col1:
                st.markdown(
                    f"""
                | Detail | Value |
                |--------|-------|
                | **City** | {city} |
                | **Sector** | {sector} |
                | **Type** | {prop_type} |
                | **BHK** | {bedrooms} BHK, {bathrooms} Bath |
                | **Floor** | {floor} |
                | **Balconies** | {balcony} |
                """
                )
            with summary_col2:
                st.markdown(
                    f"""
                | Detail | Value |
                |--------|-------|
                | **Furnished** | {furnished} |
                | **Facing** | {facing} |
                | **Area** | {area:,} sqft |
                | **Price/sqft** | ₹ {price_sqft:,.0f} |
                | **Total Price** | {format_inr_full(total_price)} |
                """
                )

            # --- Amenity chips ---
            amenities = {
                "Lift": lift,
                "Parking": parking,
                "Gym": gym,
                "Pool": pool,
                "Pooja Room": pooja_room,
                "Servant Room": servant_room,
                "Store Room": store_room,
                "Vastu": vastu_compliant,
            }
            chips_html = '<div class="amenity-grid">'
            for label, on in amenities.items():
                cls = "amenity-on" if on else "amenity-off"
                icon = "&#10003;" if on else "&#10007;"
                chips_html += f'<span class="amenity-chip {cls}">{icon} {label}</span>'
            chips_html += "</div>"
            st.markdown(chips_html, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error(
                f"Could not connect to the API at `{API_BASE_URL}`. "
                "Make sure the FastAPI server is running."
            )
        except requests.exceptions.HTTPError as e:
            st.error(f"API error: {e.response.status_code} — {e.response.text}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

else:
    # --- Landing state ---
    st.markdown(
        """
    <div style="text-align: center; padding: 4rem 2rem; color: #6B7280;">
        <h3 style="color: #9CA3AF; font-weight: 500;">Ready to estimate</h3>
        <p style="max-width: 500px; margin: 0 auto; line-height: 1.6;">
            Fill in the property details in the sidebar and click
            <strong style="color: #6C63FF;">Estimate Price</strong>
            to get an instant price prediction.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
