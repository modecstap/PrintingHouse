import { requestJson } from "./api";
import {
  toCutter,
  toFilm,
  toLaminator,
  toOperator,
  toPrinter,
  toSheet,
} from "./catalog-parsers";

export async function fetchPrinters(signal) {
  const data = await requestJson("/api/equipment/printers", { signal });
  return data.map(toPrinter);
}

export async function fetchLaminators(signal) {
  const data = await requestJson("/api/equipment/laminators", { signal });
  return data.map(toLaminator);
}

export async function fetchCutters(signal) {
  const data = await requestJson("/api/equipment/cutters", { signal });
  return data.map(toCutter);
}

export async function fetchPressOperators(signal) {
  const data = await requestJson("/api/staff/press-operators", { signal });
  return data.map(toOperator);
}

export async function fetchLaminatorOperators(signal) {
  const data = await requestJson("/api/staff/laminator-operators", { signal });
  return data.map(toOperator);
}

export async function fetchCutterOperators(signal) {
  const data = await requestJson("/api/staff/cutter-operators", { signal });
  return data.map(toOperator);
}

export async function fetchDieCutOperators(signal) {
  const data = await requestJson("/api/staff/die-cut-operators", { signal });
  return data.map(toOperator);
}

export async function fetchSheets(signal) {
  const data = await requestJson("/api/materials/sheets", { signal });
  return data.map(toSheet);
}

export async function fetchFilms(signal) {
  const data = await requestJson("/api/materials/films", { signal });
  return data.map(toFilm);
}

const CATALOG_LOADERS = [
  ["printers", fetchPrinters],
  ["laminators", fetchLaminators],
  ["cutters", fetchCutters],
  ["pressOperators", fetchPressOperators],
  ["laminatorOperators", fetchLaminatorOperators],
  ["cutterOperators", fetchCutterOperators],
  ["dieCutOperators", fetchDieCutOperators],
  ["sheets", fetchSheets],
  ["films", fetchFilms],
];

/** @type {Record<string, (signal?: AbortSignal) => Promise<unknown[]>>} */
export const CATALOG_LIST_LOADERS = {
  "/api/equipment/printers": fetchPrinters,
  "/api/equipment/laminators": fetchLaminators,
  "/api/equipment/cutters": fetchCutters,
  "/api/staff/press-operators": fetchPressOperators,
  "/api/staff/laminator-operators": fetchLaminatorOperators,
  "/api/staff/cutter-operators": fetchCutterOperators,
  "/api/staff/die-cut-operators": fetchDieCutOperators,
  "/api/materials/sheets": fetchSheets,
  "/api/materials/films": fetchFilms,
};

function failureMessage(reason) {
  return reason instanceof Error ? reason.message : String(reason);
}

export async function loadCatalogs(signal) {
  const settled = await Promise.allSettled(
    CATALOG_LOADERS.map(([, loader]) => loader(signal)),
  );

  const catalogs = {};
  const errors = {};
  let firstError = null;

  settled.forEach((result, index) => {
    const [key] = CATALOG_LOADERS[index];
    if (result.status === "fulfilled") {
      catalogs[key] = result.value;
    } else {
      catalogs[key] = [];
      const message = failureMessage(result.reason);
      errors[key] = message;
      if (!firstError) {
        firstError = message;
      }
    }
  });

  return { catalogs, error: firstError, errors };
}

export async function fetchCatalogList(path, signal) {
  const loader = CATALOG_LIST_LOADERS[path];
  if (!loader) {
    throw new Error(`Нет загрузчика каталога для пути: ${path}`);
  }
  return loader(signal);
}
