"""
Shared pytest fixtures for NCR property price estimation tests.

All fixtures produce small synthetic data — no real data files or
trained models needed.  CI target: < 60 seconds total.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture()
def sample_df():
    """Realistic property DataFrame matching the 'Pure ML' schema."""
    return pd.DataFrame(
        {
            "area": [1200.0, 850.0, 4500.0, 600.0, 1800.0],
            "bedrooms": [3, 2, 5, 1, 3],
            "bathrooms": [2.0, 1.0, 5.0, 1.0, 2.0],
            "balcony": [2, 1, 3, 0, 2],
            "floor": [5.0, 2.0, 12.0, 1.0, 8.0],
            "prop_type": ["Apartment", "Apartment", "Villa", "Studio Apartment", "Apartment"],
            "city": ["Gurugram", "Noida", "Delhi", "Gurugram", "Noida"],
            "sector": ["Sector 50", "Sector 75", "Prithviraj Road", "Sector 50", "Sector 75"],
            "society": [
                "Emaar Palm Drive",
                "Supertech CapeTown",
                "Standalone",
                "Global Foyer",
                "Golf Estate",
            ],
            "furnishing_status": [
                "Semi-Furnished",
                "Unfurnished",
                "Furnished",
                "Unfurnished",
                "Semi-Furnished",
            ],
            "facing": ["East", "North", "South", "West", "East"],
            "legal_status": ["RERA", "RERA", "Freehold", "RERA", "RERA"],
            # Amenity / NLP Flags
            "is_rera_registered": [1, 1, 0, 1, 1],
            "is_luxury": [0, 0, 1, 0, 0],
            "is_gated_community": [1, 1, 0, 1, 1],
            "is_vastu_compliant": [1, 0, 1, 0, 1],
            "is_servant_room": [0, 0, 1, 0, 1],
            "is_study_room": [0, 0, 1, 0, 0],
            "is_store_room": [0, 0, 1, 0, 0],
            "is_pooja_room": [0, 0, 1, 0, 0],
            "has_pool": [1, 0, 1, 0, 1],
            "has_gym": [1, 0, 1, 0, 1],
            "has_lift": [1, 1, 0, 1, 1],
            "is_near_metro": [1, 1, 0, 1, 1],
            "has_power_backup": [1, 1, 0, 1, 1],
            "is_corner_property": [0, 0, 1, 0, 0],
            "is_park_facing": [0, 0, 1, 0, 1],
            "no_brokerage": [1, 0, 0, 1, 0],
            "bachelors_allowed": [1, 1, 0, 1, 1],
            "is_standalone": [0, 0, 1, 0, 0],
            "is_owner_listing": [1, 0, 0, 1, 0],
        }
    )


@pytest.fixture()
def sample_target():
    """Log-scale price_per_sqft target matching sample_df rows."""
    return pd.Series(
        np.log1p([8500, 6200, 85000, 5500, 12000]),
        name="log_price_per_sqft",
    )
