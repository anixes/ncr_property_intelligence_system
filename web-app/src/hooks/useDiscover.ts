import { useState } from 'react';
import api from '../lib/api';
import { DiscoverRequest, PropertyListing } from '../types';

export function useDiscover() {
  const [data, setData] = useState<PropertyListing[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const discover = async (request: DiscoverRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      // Unit Scale Isolation: Convert Lakhs/Thousands to raw numbers before API call
      const multiplier = request.listing_type === 'buy' ? 100000 : 1000;
      const rawRequest = {
        ...request,
        budget_min: request.budget_min * multiplier,
        budget_max: request.budget_max * multiplier
      };

      const result = await api.discover(rawRequest);
      setData(result);
      return result;
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } }, message?: string };
      const message = errorObj.response?.data?.detail || errorObj.message || 'Failed to search properties';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { data, isLoading, error, mutate: discover };
}
