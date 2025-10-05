import { useState, useEffect } from 'react';

export function useMatrixData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/get_map');

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();

        if (!result.data || !result.layers) {
          throw new Error('Invalid response format');
        }

        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load matrix data');
        console.error('Matrix data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
}
