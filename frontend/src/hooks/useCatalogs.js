import { useCallback, useEffect, useRef, useState } from "react";
import { loadCatalogs } from "../lib/catalog-api";

export const EMPTY_CATALOGS = {
  printers: [],
  laminators: [],
  cutters: [],
  pressOperators: [],
  laminatorOperators: [],
  cutterOperators: [],
  dieCutOperators: [],
  sheets: [],
  films: [],
};

function toCatalogLoadState({ catalogs, error, errors }) {
  const merged = { ...EMPTY_CATALOGS, ...catalogs };
  return {
    status: error ? "error" : "success",
    catalogs: merged,
    errors: errors ?? {},
    message: error,
  };
}

export function useCatalogs() {
  const [catalogLoadState, setCatalogLoadState] = useState({
    status: "loading",
    catalogs: EMPTY_CATALOGS,
    errors: {},
    message: null,
  });
  const abortRef = useRef(null);

  const reloadCatalogs = useCallback(() => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setCatalogLoadState((prev) => ({
      ...prev,
      status: "loading",
    }));

    loadCatalogs(controller.signal)
      .then((result) => {
        if (controller.signal.aborted) {
          return;
        }
        setCatalogLoadState(toCatalogLoadState(result));
      })
      .catch((reason) => {
        if (controller.signal.aborted || reason?.name === "AbortError") {
          return;
        }
        const message =
          reason instanceof Error ? reason.message : String(reason);
        setCatalogLoadState({
          status: "error",
          catalogs: EMPTY_CATALOGS,
          errors: {},
          message,
        });
      });
  }, []);

  useEffect(() => {
    reloadCatalogs();
    return () => abortRef.current?.abort();
  }, [reloadCatalogs]);

  return { catalogLoadState, reloadCatalogs };
}
