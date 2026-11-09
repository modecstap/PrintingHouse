import { requestJson } from "../../../lib/api";
import {
  toCutter,
  toFilm,
  toLaminator,
  toOperator,
  toPrinter,
  toSheet,
} from "../models/catalog-label";

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

export async function loadCatalogs(signal) {
  const settled = await Promise.allSettled(
    CATALOG_LOADERS.map(([, loader]) => loader(signal)),
  );

  const catalogs = {};
  let firstError = null;

  settled.forEach((result, index) => {
    const [key] = CATALOG_LOADERS[index];
    if (result.status === "fulfilled") {
      catalogs[key] = result.value;
    } else {
      catalogs[key] = [];
      if (!firstError) {
        firstError =
          result.reason instanceof Error
            ? result.reason.message
            : String(result.reason);
      }
    }
  });

  return { catalogs, error: firstError };
}
