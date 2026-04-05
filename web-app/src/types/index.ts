export interface AmenitiesSelection {
  has_pool: boolean;
  has_gym: boolean;
  has_lift: boolean;
  has_power_backup: boolean;
  is_gated_community: boolean;
  has_clubhouse: boolean;
  has_maintenance: boolean;
  has_wifi: boolean;
  is_high_ceiling: boolean;
}

export interface LocationSelection {
  is_near_metro: boolean;
  is_corner_property: boolean;
  is_park_facing: boolean;
  is_vastu_compliant: boolean;
}

export interface PropertyFeatures {
  is_luxury: boolean;
  is_servant_room: boolean;
  is_study_room: boolean;
  is_store_room: boolean;
  is_pooja_room: boolean;
  is_new_construction: boolean;
}

export interface PropertyInput {
  area: number;
  bedrooms: number;
  bhk?: number;
  bathrooms?: number;
  prop_type: "Apartment" | "Builder Floor" | "Independent House" | "Any";
  furnishing_status: "Fully-Furnished" | "Semi-Furnished" | "Unfurnished" | "Unknown";
  legal_status: "Freehold" | "Leasehold" | "Power of Attorney" | "Unknown";
  city: string;
  sector: string;
  property_name?: string;
  listing_type: "buy" | "rent";
  amenities: AmenitiesSelection;
  location: LocationSelection;
  property_features: PropertyFeatures;
  is_rera_registered: boolean;
  no_brokerage: boolean;
  bachelors_allowed: boolean;
  is_standalone: boolean;
  is_owner_listing: boolean;
  orientation?: "N" | "S" | "E" | "W" | "NE" | "NW" | "SE" | "SW";
  property_age?: number;
}

export interface PredictionResponse {
  price_per_sqft: number;
  estimated_market_value: number;
  predicted_monthly_rent: number;
  property_name?: string;
  intelligence_suite: {
    yield_pct: number;
    unified_score: number;
    risk_analysis: {
      label: string;
      score: number;
      confidence: string;
    };
    overvaluation_pct: number;
    annual_rent_return: number;
  };
  recommendations: Recommendation[];
  similar_listings: PropertyAsset[];
  dist_to_metro_km?: number;
  asset?: PropertyAsset;
}

export interface Recommendation {
  locality: string;
  city: string;
  median_price_sqft: number;
  expected_yield_pct: number;
  distance_km: number;
  listing_count: number;
  top_societies: string[];
  composite_score: number;
  latitude?: number;
  longitude?: number;
  h3_index?: string;
}

export interface PropertyAsset {
  society: string;
  locality: string;
  city: string;
  price: number;
  area: number;
  bhk: number;
  price_per_sqft: number;
  yield_pct: number;
  unified_score: number;
  listing_type: "buy" | "rent";
  latitude?: number;
  longitude?: number;
  h3_index?: string;
  dist_to_metro_km?: number;
  furnishing_status?: string;
  features?: {
    amenities: AmenitiesSelection;
    location: LocationSelection;
    property: PropertyFeatures;
  };
}

export interface DiscoverRequest {
  city: string;
  listing_type: "buy" | "rent";
  bhk: number[];
  budget_min: number;
  budget_max: number;
  area_min?: number;
  area_max?: number;
  prop_type?: string;
  sort_by: "yield" | "price_low" | "price_high" | "score" | "area";
  amenities: AmenitiesSelection;
  location_features: LocationSelection;
  property_features: PropertyFeatures;
  furnishing_status?: string;
  legal_status?: string;
}

export interface DashboardSummary {
  city: string;
  median_price_sqft: number;
  median_rent_sqft: number;
  listing_count: number;
  top_localities: string[];
}

export type Intent = 'buy' | 'rent';
