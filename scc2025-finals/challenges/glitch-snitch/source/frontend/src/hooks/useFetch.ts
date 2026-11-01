import { useEffect, useState, useCallback } from "react";
import { fetchAPI } from "../func";

export default function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAndSetData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAPI<T>(url);
      setData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    fetchAndSetData();
  }, [fetchAndSetData]);

  return { data, loading, error, refetch: fetchAndSetData };
}
