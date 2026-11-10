import { requestJson } from "../../../lib/api";
import {
  CATALOG_LIST_LOADERS,
  fetchCatalogList,
} from "../../../lib/catalog-api";

export async function fetchCatalog(path, parseList, signal) {
  if (CATALOG_LIST_LOADERS[path]) {
    return fetchCatalogList(path, signal);
  }
  const data = await requestJson(path, { signal });
  return parseList(data);
}

export async function createCatalog(path, body) {
  return requestJson(path, { method: "POST", body });
}

export async function replaceCatalog(path, body) {
  return requestJson(path, { method: "PUT", body });
}

export async function deleteCatalog(path) {
  return requestJson(path, { method: "DELETE" });
}
