import { useState } from 'react';
import api from '../lib/api';
import { PropertyInput, PredictionResponse } from '../types';

export function usePredict() {
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predict = async (input: PropertyInput) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.predict(input);
      setData(result);
      return result;
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } }, message?: string };
      const message = errorObj.response?.data?.detail || errorObj.message || 'Failed to fetch prediction';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { data, isLoading, error, mutate: predict };
}
