export interface PredictionInput {
  city: string;
  sector: string;
  property_name: string;
  bhk: number;
  area: number;
  age: string;
  facing: string;
}

export interface ValuationResponse {
  valuation: {
    predicted_price: number;
    price_per_sqft: number;
  };
  intelligence: {
    alpha_score: number;
    risk_label: string;
    financials: {
      gross_yield: number;
      estimated_monthly_rent: number;
    };
  };
}

export interface PropertyAsset {
  property_name: string;
  sector: string;
  type: string;
  intelligence: {
    alpha_score: number;
    risk_label: string;
    financials: {
      gross_yield: number;
      estimated_monthly_rent: number;
    };
  };
}

export type Intent = 'Buy' | 'Rent';

export interface DiscoveryResponse {
  summary: {
    processed_assets: number;
    scan_time: string;
  };
  featured_assets: PropertyAsset[];
}
