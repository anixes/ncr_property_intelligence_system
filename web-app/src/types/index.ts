export type ListingType = 'buy' | 'rent';

export interface AmenitiesSelection {
  has_pool: boolean;
  has_gym: boolean;
  has_lift: boolean;
  has_power_backup: boolean;
  is_gated_community?: boolean;
  has_clubhouse?: boolean;
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
  is_new_construction?: boolean;
}

export interface PropertyInput {
  area: number;
  bedrooms: number;
  bathrooms?: number;
  prop_type: 'Apartment' | 'Builder Floor' | 'Independent House' | 'Any';
  furnishing_status: 'Fully-Furnished' | 'Semi-Furnished' | 'Unfurnished' | 'Unknown';
  legal_status: 'Freehold' | 'Leasehold' | 'Power of Attorney' | 'Unknown';
  city: string;
  sector: string;
  property_name?: string;
  listing_type: ListingType;
  amenities: AmenitiesSelection;
  location_score: LocationSelection;
  features: PropertyFeatures;
}

export interface RiskAnalysis {
  score: number;
  label: string;
}

export interface IntelligenceSuite {
  yield_pct: number;
  unified_score: number;
  risk_analysis: RiskAnalysis;
  overvaluation_pct: number;
  annual_rent_return: number;
}

export interface PropertyListing {
  society: string;
  locality: string;
  city: string;
  price: number;
  area: number;
  bhk: number;
  price_per_sqft: number;
  yield_pct: number;
  unified_score: number;
  listing_type: string;
  latitude: number | null;
  longitude: number | null;
  dist_to_metro_km?: number;
  furnishing_status?: string;
}

export interface Recommendation {
  locality: string;
  city: string;
  distance_km: number;
  expected_yield_pct: number;
  composite_score: number;
  median_price_sqft: number;
}

export interface PredictionResponse {
  price_per_sqft: number;
  estimated_market_value: number;
  predicted_monthly_rent: number;
  property_name?: string;
  intelligence_suite: IntelligenceSuite;
  recommendations: Recommendation[];
  similar_listings: PropertyListing[];
  dist_to_metro_km?: number;
}

export interface DiscoverRequest {
  city: string;
  listing_type: ListingType;
  bhk: number[];
  budget_min: number;
  budget_max: number;
  area_min?: number;
  area_max?: number;
  prop_type?: string;
  sort_by?: 'yield' | 'price_low' | 'price_high' | 'score' | 'area';
  amenities?: AmenitiesSelection;
  location_score?: LocationSelection;
  features?: PropertyFeatures;
  furnishing_status?: string;
  legal_status?: string;
}

export interface Hotspot {
  h3_res8: string;
  city: string;
  median_price_sqft: number;
  density: number;
  latitude: number;
  longitude: number;
}
