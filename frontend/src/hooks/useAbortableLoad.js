import { useCallback, useEffect, useRef, useState } from "react";

/**
 * @param {(signal: AbortSignal) => Promise<unknown>} loader
 * @param {unknown[]} deps
 */
export function useAbortableLoad(loader, deps) {
  const [status, setStatus] = useState("loading");
  const [data, setData] = useState(undefined);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const reload = useCallback(() => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus("loading");
    setError(null);

    Promise.resolve(loaderRef.current(controller.signal))
      .then((result) => {
        if (controller.signal.aborted) {
          return;
        }
        setData(result);
        setStatus("success");
      })
      .catch((reason) => {
        if (reason?.name === "AbortError" || controller.signal.aborted) {
          return;
        }
        const message =
          reason instanceof Error ? reason.message : String(reason);
        setError(message);
        setStatus("error");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    reload();
    return () => {
      abortRef.current?.abort();
    };
  }, [reload]);

  return { data, status, error, reload };
}
