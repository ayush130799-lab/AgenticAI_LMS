"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api";

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

/** Runs `loader` on mount and exposes loading/error/retry, so each page section can fail independently. */
export function useAsync<T>(loader: () => Promise<T>, fallbackError = "Something went wrong."): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await loaderRef.current());
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : fallbackError);
    } finally {
      setLoading(false);
    }
  }, [fallbackError]);

  useEffect(() => {
    run();
  }, [run]);

  return { data, loading, error, reload: run };
}
