import { useState, useCallback } from 'react';
import api from '../lib/api';
import { Hotspot, PropertyListing } from '../types';

export function useHotspots() {
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [featured, setFeatured] = useState<PropertyListing[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHotspots = useCallback(async (listingType: 'buy' | 'rent' = 'buy', city?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.getHotspots(listingType, city);
      setHotspots(result.hotspots);
      setFeatured(result.featured);
      return result;
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } }, message?: string };
      const message = errorObj.response?.data?.detail || errorObj.message || 'Failed to fetch mapping data';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { hotspots, featured, isLoading, error, refetch: fetchHotspots };
}
