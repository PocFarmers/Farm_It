import { useState, useEffect, useCallback } from 'react';

export function useMatrixData() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        try {
            console.log('🗺️ [useMatrixData] Fetching map from /get_map');
            setLoading(true);
            const response = await fetch('http://localhost:8000/get_map');
            console.log('🗺️ [useMatrixData] Response:', response);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const result = await response.json();

            if (!result.data || !result.layers) {
                throw new Error('Invalid response format');
            }

            console.log('🗺️ [useMatrixData] Map received:', {
                shape: result.shape,
                layers: result.layers,
                dataType: typeof result.data,
                dataIsArray: Array.isArray(result.data),
                dataLength: result.data?.length,
                firstRowLength: result.data?.[0]?.length,
                firstCellValue: result.data?.[0]?.[0]
            });

            setData(result);
            setError(null);
        } catch (err) {
            setError(err.message || 'Failed to load matrix data');
            console.error('❌ [useMatrixData] Error:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { data, loading, error, refreshMap: fetchData };
}
