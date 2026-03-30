import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16 - MASTERPIECE FINAL)
# =============================================================================


class ListingMetadata(BaseModel):
    """Universal metadata for auditability and leakage protection."""

    batch_id: str
    source_site: str
    ingestion_timestamp: datetime = Field(default_factory=datetime.now)
    schema_version: str = "v16.0"
    config_hash: str | None = None
    git_commit: str | None = None


class RawListing(BaseModel):
    """STAGE 1: Raw extraction data from Playwright."""

    metadata: ListingMetadata
    listing_id: str
    url: str
    price_text: str  # Original raw text for audit
    area_text: str
    bhk_text: str
    society_raw: str | None = None
    locality_raw: str
    is_rent: bool = False
    raw_attributes: dict[str, Any] = Field(default_factory=dict)


class ValidatedListing(BaseModel):
    """STAGE 2: Sanitized data after validator.py logic."""

    metadata: ListingMetadata
    listing_id: str

    # Core numerical fields (Sanitized)
    price: float
    area: float
    bhk: int
    is_rent: bool

    # Categorical
    society: str | None = None
    locality: str
    city: str

    # Uncertainty Tracking
    area_uncertainty: float = 0.0  # 0: exact, >0: estimate variation
    price_was_imputed: bool = False
    extraction_confidence: float = 1.0

    # Status
    quality_tag: str = "clean"  # clean, degraded, incomplete
    yield_rate: float = 1.0  # For observability


class EnrichedListing(ValidatedListing):
    """STAGE 3: Spatially enriched data (H3 + Distances)."""

    # Geospatial
    lat: float | None = None
    lng: float | None = None
    h3_res8: str | None = None
    h3_res9: str | None = None
    geo_confidence: float = 0.0

    # Neighborhood Features (Leakage-Proofed)
    h3_median_price: float | None = None
    h3_listings_count: int = 0
    dist_to_metro_km: float | None = None
    dist_to_cbd_km: float | None = None

    # Derived Features
    price_per_sqft: float
    local_zscore: float | None = None
    is_luxury_skew: bool = False


class FusedListing(EnrichedListing):
    """STAGE 4: Final Deduplicated Product Record."""

    fusion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_listing_ids: list[str] = Field(default_factory=list)
    fusion_score: float = 1.0

    # Model Intelligence (The "Product" Layer)
    predicted_price: float | None = None
    prediction_uncertainty: float | None = None
    undervaluation_score: float | None = None
    is_strong_deal: bool = False

    # Recommendation Context
    comparable_listing_ids: list[str] = Field(default_factory=list)
    diversity_tag: str | None = None  # For diversifying results
