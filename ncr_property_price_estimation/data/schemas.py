from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid

# =============================================================================
# NCR INTELLIGENCE ENGINE (V16 - MASTERPIECE FINAL)
# =============================================================================

class ListingMetadata(BaseModel):
    """Universal metadata for auditability and leakage protection."""
    batch_id: str
    source_site: str
    ingestion_timestamp: datetime = Field(default_factory=datetime.now)
    schema_version: str = "v16.0"
    config_hash: Optional[str] = None
    git_commit: Optional[str] = None

class RawListing(BaseModel):
    """STAGE 1: Raw extraction data from Playwright."""
    metadata: ListingMetadata
    listing_id: str
    url: str
    price_text: str  # Original raw text for audit
    area_text: str
    bhk_text: str
    society_raw: Optional[str] = None
    locality_raw: str
    is_rent: bool = False
    raw_attributes: Dict[str, Any] = Field(default_factory=dict)

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
    society: Optional[str] = None
    locality: str
    city: str
    
    # Uncertainty Tracking
    area_uncertainty: float = 0.0  # 0: exact, >0: estimate variation
    price_was_imputed: bool = False
    extraction_confidence: float = 1.0
    
    # Status
    quality_tag: str = "clean"  # clean, degraded, incomplete
    yield_rate: float = 1.0     # For observability

class EnrichedListing(ValidatedListing):
    """STAGE 3: Spatially enriched data (H3 + Distances)."""
    # Geospatial
    lat: Optional[float] = None
    lng: Optional[float] = None
    h3_res8: Optional[str] = None
    h3_res9: Optional[str] = None
    geo_confidence: float = 0.0
    
    # Neighborhood Features (Leakage-Proofed)
    h3_median_price: Optional[float] = None
    h3_listings_count: int = 0
    dist_to_metro_km: Optional[float] = None
    dist_to_cbd_km: Optional[float] = None
    
    # Derived Features
    price_per_sqft: float
    local_zscore: Optional[float] = None
    is_luxury_skew: bool = False

class FusedListing(EnrichedListing):
    """STAGE 4: Final Deduplicated Product Record."""
    fusion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_listing_ids: List[str] = Field(default_factory=list)
    fusion_score: float = 1.0
    
    # Model Intelligence (The "Product" Layer)
    predicted_price: Optional[float] = None
    prediction_uncertainty: Optional[float] = None
    undervaluation_score: Optional[float] = None
    is_strong_deal: bool = False
    
    # Recommendation Context
    comparable_listing_ids: List[str] = Field(default_factory=list)
    diversity_tag: Optional[str] = None # For diversifying results
