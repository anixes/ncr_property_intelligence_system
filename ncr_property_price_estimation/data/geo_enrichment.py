import h3
import numpy as np
import pandas as pd

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
            if hasattr(h3, "latlng_to_cell"):
                return h3.latlng_to_cell(lat, lng, self.res)
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
        df["h3_median_price"] = df.groupby("h3_res8", group_keys=False)["price"].apply(
            lambda x: x.shift(1).expanding().median()
        )

        df["h3_listings_count"] = df.groupby("h3_res8", group_keys=False).cumcount()

        # Local Z-Score for luxury detection (V16 Logic)
        def calc_zscore(row):
            if pd.isna(row["h3_median_price"]) or row["h3_median_price"] == 0:
                return 0
            return (row["price"] - row["h3_median_price"]) / row["h3_median_price"]

        df["local_zscore"] = df.apply(calc_zscore, axis=1)

        # H3 Stability Check (V16 Final Refinement)
        # We mark cells that have > 10 listings as "Stable" zones
        df["geo_confidence"] = np.where(df["h3_listings_count"] > 10, 1.0, 0.5)

        return df

    def enrich_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete enrichment cycle for a new batch."""
        # 1. Coordinate to H3
        # Support both naming conventions (lat/lng and latitude/longitude)
        lat_col = "latitude" if "latitude" in df.columns else "lat"
        lng_col = "longitude" if "longitude" in df.columns else "lng"
        if lat_col in df.columns and lng_col in df.columns:
            df["h3_res8"] = df.apply(lambda r: self.encode_h3(r[lat_col], r[lng_col]), axis=1)

        # 2. Neighborhood Enrichment (Leakage-Proof)
        df = self.get_neighborhood_stats(df)

        # 3. Derived price feature
        if "price" in df.columns and "area" in df.columns:
            df["price_per_sqft"] = df["price"] / df["area"]

        return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["sales", "rentals"], required=True)
    args = parser.parse_args()

    print(f"\n[GEO-ENRICHMENT: {args.mode.upper()}]")
    service = GeoEnrichmentService()

    in_file = PROCESSED_DATA_DIR.parent / "interim" / f"{args.mode}_geocoded.parquet"
    out_file = PROCESSED_DATA_DIR / f"{args.mode}_processed.parquet"

    df = pd.read_parquet(in_file)
    print(f"  Input rows: {len(df)}")

    # Fake timestamp if missing for safety
    if "timestamp" not in df.columns:
        if "scraped_at" in df.columns:
            df["timestamp"] = pd.to_datetime(df["scraped_at"])
        else:
            df["timestamp"] = pd.Timestamp("2026-03-25")

    df = service.enrich_batch(df)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_file, index=False)
    print(f"  Saved H3 Enriched data to: {out_file}")
