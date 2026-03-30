/**
 * Горизонт — хук useApiData
 * Простой SWR-like хук для загрузки и мутации данных через api.ts
 * Использование:
 *   const { data, loading, error, refetch } = useApiData(() => trackerApi.list());
 */
"use client";

import { useEffect, useState, useCallback } from "react";

interface UseApiDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApiData<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
): UseApiDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const refetch = useCallback(() => setTick(t => t + 1), []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher()
      .then(result => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err?.detail ?? "Сетевая ошибка");
          setLoading(false);
        }
      });

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, ...deps]);

  return { data, loading, error, refetch };
}
