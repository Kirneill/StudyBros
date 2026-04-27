"use client";

import { useCallback, useEffect, useReducer, useState } from "react";

interface State<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

type Action<T> =
  | { type: "fetch" }
  | { type: "success"; data: T }
  | { type: "error"; error: string };

function reducer<T>(state: State<T>, action: Action<T>): State<T> {
  switch (action.type) {
    case "fetch":
      return { ...state, loading: true, error: null };
    case "success":
      return { data: action.data, error: null, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
  }
}

interface UseApiResult<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  refetch: () => void;
}

export function useApi<T>(fetcher: () => Promise<T>): UseApiResult<T> {
  const [state, dispatch] = useReducer(reducer<T>, {
    data: null,
    error: null,
    loading: true,
  });
  const [trigger, setTrigger] = useState(0);
  const refetch = useCallback(() => setTrigger((n) => n + 1), []);

  useEffect(() => {
    let cancelled = false;
    dispatch({ type: "fetch" });

    fetcher()
      .then((result) => {
        if (!cancelled) dispatch({ type: "success", data: result });
      })
      .catch((err: unknown) => {
        if (!cancelled)
          dispatch({
            type: "error",
            error: err instanceof Error ? err.message : String(err),
          });
      });

    return () => {
      cancelled = true;
    };
  }, [fetcher, trigger]);

  return { ...state, refetch };
}
