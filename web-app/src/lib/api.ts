import {
  PropertyInput,
  PredictionResponse,
  DiscoverRequest,
  PropertyAsset,
  DashboardSummary
} from '../types';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Health Check for the Intelligence Engine
 */
export async function fetchHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/intelligence/health`);
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === 'healthy' || data.model_loaded;
  } catch {
    return false;
  }
}

/**
 * Institutional Valuation Prediction
 */
export async function predictProperty(data: PropertyInput): Promise<PredictionResponse> {
  const res = await fetch('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Valuation failed');
  }
  return res.json();
}

/**
 * Property Discovery Engine
 */
export async function discoverProperties(request: DiscoverRequest): Promise<PropertyAsset[]> {
  const res = await fetch('/api/discovery', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Discovery failed');
  }
  return res.json();
}

/**
 * Market Dashboard Summary
 */
export async function getDashboardSummary(city: string = 'Gurgaon'): Promise<DashboardSummary> {
  const url = `/api/intelligence/dashboard-summary?city=${encodeURIComponent(city)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Dashboard summary failed: ${res.statusText}`);
  return res.json();
}

/**
 * Locality Autocomplete / Index
 */
export async function getLocalities(city: string): Promise<string[]> {
  const url = `/api/intelligence/localities?city=${encodeURIComponent(city)}`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const data = await res.json();
  return Array.isArray(data.localities) ? data.localities : [];
}
