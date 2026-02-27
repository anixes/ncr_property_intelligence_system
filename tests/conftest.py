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
    """Minimal DataFrame with every column the pipeline expects."""
    return pd.DataFrame(
        {
            "area": [1200.0, 850.0, 2400.0, 600.0, 1800.0],
            "bedrooms": [3, 2, 4, 1, 3],
            "bathrooms": [2.0, 1.0, np.nan, 1.0, 2.0],
            "balcony": [2, 1, 3, 0, 2],
            "floor": [5.0, np.nan, 12.0, 1.0, 8.0],
            "prop_type": ["Apartment", "Apartment", "Villa", "Studio Apartment", "Apartment"],
            "furnished": [
                "Semi-Furnished",
                "Unfurnished",
                "Furnished",
                "Unfurnished",
                "Semi-Furnished",
            ],
            "facing": ["East", "North", "South", "West", "East"],
            "city": ["Gurugram", "Noida", "Delhi", "Gurugram", "Noida"],
            "sector": ["Sector 50", "Sector 75", "Dwarka", "Sector 50", "Sector 75"],
            "pooja_room": [0, 0, 1, 0, 0],
            "servant_room": [0, 0, 1, 0, 0],
            "store_room": [0, 0, 1, 0, 0],
            "pool": [0, 0, 1, 0, 0],
            "gym": [1, 0, 1, 0, 1],
            "lift": [1, 1, 0, 1, 1],
            "parking": [1, 1, 1, 0, 1],
            "vastu_compliant": [1, 0, 1, 0, 1],
        }
    )


@pytest.fixture()
def sample_target():
    """Log-scale price_per_sqft target matching sample_df rows."""
    return pd.Series(
        np.log1p([8500, 6200, 12000, 5500, 7000]),
        name="log_price_per_sqft",
    )
