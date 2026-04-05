from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AmenitiesSelection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    has_pool: bool = False
    has_gym: bool = False
    has_lift: bool = False
    has_power_backup: bool = False
    is_gated_community: bool = Field(False, alias="is_gated_community")
    has_clubhouse: bool = Field(False, alias="has_clubhouse")
    has_maintenance: bool = Field(False, alias="has_maintenance")
    has_wifi: bool = Field(False, alias="has_wifi")
    is_high_ceiling: bool = Field(False, alias="is_high_ceiling")


class LocationSelection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    is_near_metro: bool = False
    is_corner_property: bool = False
    is_park_facing: bool = False
    is_vastu_compliant: bool = False


class PropertyFeatures(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    is_luxury: bool = False
    is_servant_room: bool = False
    is_study_room: bool = False
    is_store_room: bool = False
    is_pooja_room: bool = False
    is_new_construction: bool = False


class PropertyInput(BaseModel):
    """Input schema for a single property prediction."""
    model_config = ConfigDict(populate_by_name=True)

    area: float = Field(..., gt=0, description="Built-up area in sqft")
    bedrooms: int = Field(..., ge=1, description="Number of bedrooms")
    bathrooms: int | None = Field(None, ge=0, description="Number of bathrooms")

    prop_type: Literal["Apartment", "Builder Floor", "Independent House", "Any"] = Field(
        ..., description="Property type"
    )
    furnishing_status: Literal["Fully-Furnished", "Semi-Furnished", "Unfurnished", "Unknown"] = (
        Field("Semi-Furnished", description="Furnishing status")
    )
    legal_status: Literal["Freehold", "Leasehold", "Power of Attorney", "Unknown"] = Field(
        "Unknown", description="Legal ownership status"
    )

    city: str = Field(..., description="NCR City (e.g., Gurgaon, Noida)")
    sector: str = Field(..., description="Sector or Locality Name")
    property_name: str | None = Field(None, description="Optional Project or Apartment name")
    listing_type: Literal["buy", "rent"] = Field("buy", description="Intent of the user")

    # Grouped High-Performance Catalyst Flags (V2 Schema)
    amenities: AmenitiesSelection = Field(default_factory=AmenitiesSelection)
    location: LocationSelection = Field(default_factory=LocationSelection, alias="location_score")
    property_features: PropertyFeatures = Field(default_factory=PropertyFeatures, alias="features")

    is_rera_registered: bool = False
    no_brokerage: bool = False
    bachelors_allowed: bool = False
    is_standalone: bool = False
    is_owner_listing: bool = False

    # Advanced Intelligence Metrics
    orientation: Literal["N", "S", "E", "W", "NE", "NW", "SE", "SW"] | None = Field(None, description="Property facing orientation")
    property_age: int | None = Field(None, ge=0, description="Property age in years")


class PredictionResponse(BaseModel):
    """Output schema for a single prediction."""

    price_per_sqft: float = Field(..., description="Predicted price in ₹/sqft")
    estimated_market_value: float = Field(
        ..., description="Estimated total price (price_per_sqft × area)"
    )
    predicted_monthly_rent: float = Field(..., description="Predicted monthly rent")
    property_name: str | None = Field(None, description="Project or Property name provided")
    intelligence_suite: dict[str, Any] = Field(..., description="ROI Intelligence analysis")
    recommendations: list[dict[str, Any]] = Field(
        default_factory=list, description="Top 5 alternative localities"
    )
    similar_listings: list[dict[str, Any]] = Field(
        default_factory=list, description="Top 5 real-world historical matches"
    )
    dist_to_metro_km: float | None = Field(None, description="Actual distance to nearest metro")
    asset: dict[str, Any] | None = Field(None, description="Full reconstructed asset for UI deep dive")


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_stage: str | None = None


class DiscoverRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    city: str
    listing_type: Literal["buy", "rent"]
    bhk: list[int]
    budget_min: float
    budget_max: float
    area_min: float | None = None
    area_max: float | None = None
    prop_type: str = "Any"
    sort_by: Literal["yield", "price_low", "price_high", "score", "area"] = "yield"

    # Advanced Filters
    amenities: AmenitiesSelection = Field(default_factory=AmenitiesSelection)
    location_features: LocationSelection = Field(
        default_factory=LocationSelection, alias="location_score"
    )
    property_features: PropertyFeatures = Field(default_factory=PropertyFeatures, alias="features")
    furnishing_status: str | None = "Unknown"
    legal_status: str | None = "Unknown"


class ModelInfoResponse(BaseModel):
    sales_version: str | None = None
    rentals_version: str | None = None
    experiment_name: str
