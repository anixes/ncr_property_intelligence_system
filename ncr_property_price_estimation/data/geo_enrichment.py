import h3
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any
from pathlib import Path
from ncr_property_price_estimation.config import PROCESSED_DATA_DIR

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16) - GEO-ENRICHMENT SERVICE
# =============================================================================

class GeoEnrichmentService:
    """Handles Spatial Indexing (H3) and Leakage-Proof Neighborhood Features."""
    
    def __init__(self, h3_resolution: int = 8):
        self.res = h3_resolution

    def encode_h3(self, lat: float, lng: float) -> str:
        """Convert Lat/Long to H3 hexagonal index."""
        try:
            return h3.geo_to_h3(lat, lng, self.res)
        except Exception:
            return None

    def get_neighborhood_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute neighborhood-level statistics with zero look-ahead bias (V16).
        Ensures stats for row 'i' only use rows where t < t_i.
        """
        if "h3_res8" not in df.columns or "timestamp" not in df.columns:
            return df

        # Ensure temporal ordering for leakage protection
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        # We use a expanding window windowed by H3 cell to calculate historical medians
        # This is a key "Masterpiece" guard for a high-value portfolio.
        df['h3_median_price'] = df.groupby('h3_res8', group_keys=False)['price'].apply(
            lambda x: x.shift(1).expanding().median()
        )
        
        df['h3_listings_count'] = df.groupby('h3_res8', group_keys=False).cumcount()
        
        # Local Z-Score for luxury detection (V16 Logic)
        def calc_zscore(row):
            if pd.isna(row['h3_median_price']) or row['h3_median_price'] == 0:
                return 0
            return (row['price'] - row['h3_median_price']) / row['h3_median_price']

        df['local_zscore'] = df.apply(calc_zscore, axis=1)
        
        # H3 Stability Check (V16 Final Refinement)
        # We mark cells that have > 10 listings as "Stable" zones
        df['geo_confidence'] = np.where(df['h3_listings_count'] > 10, 1.0, 0.5)
        
        return df

    def enrich_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete enrichment cycle for a new batch."""
        # 1. Coordinate to H3
        if "lat" in df.columns and "lng" in df.columns:
            df['h3_res8'] = df.apply(lambda r: self.encode_h3(r['lat'], r['lng']), axis=1)
        
        # 2. Neighborhood Enrichment (Leakage-Proof)
        df = self.get_neighborhood_stats(df)
        
        # 3. Derived price feature
        if "price" in df.columns and "area" in df.columns:
            df['price_per_sqft'] = df['price'] / df['area']
            
        return df

if __name__ == "__main__":
    # Test Spatial Logic
    service = GeoEnrichmentService()
    print("GeoEnrichmentService Initialized.")
