import { act, renderHook, waitFor } from "@testing-library/react";
import { loadCatalogs } from "../lib/catalog-api";
import { EMPTY_CATALOGS, useCatalogs } from "./useCatalogs";

jest.mock("../lib/catalog-api", () => ({
  loadCatalogs: jest.fn(),
}));

describe("useCatalogs", () => {
  beforeEach(() => {
    loadCatalogs.mockReset();
  });

  it("should call loadCatalogs once on mount", async () => {
    loadCatalogs.mockResolvedValue({
      catalogs: { printers: [{ id: 1, name: "Принтер 1", startup: "0", cyan: "0", magenta: "0", yellow: "0", black: "0" }] },
      error: null,
      errors: {},
    });

    const { result } = renderHook(() => useCatalogs());

    expect(loadCatalogs).toHaveBeenCalledTimes(1);
    expect(result.current.catalogLoadState.status).toBe("loading");

    await waitFor(() => {
      expect(result.current.catalogLoadState.status).toBe("success");
    });

    expect(result.current.catalogLoadState.catalogs.printers).toEqual([
      { id: 1, name: "Принтер 1", startup: "0", cyan: "0", magenta: "0", yellow: "0", black: "0" },
    ]);
    expect(result.current.catalogLoadState.catalogs.laminators).toEqual(
      EMPTY_CATALOGS.laminators,
    );
  });

  it("should reload catalogs when reloadCatalogs is called", async () => {
    loadCatalogs.mockResolvedValue({
      catalogs: {},
      error: null,
      errors: {},
    });

    const { result } = renderHook(() => useCatalogs());

    await waitFor(() => {
      expect(result.current.catalogLoadState.status).toBe("success");
    });

    loadCatalogs.mockClear();
    loadCatalogs.mockResolvedValue({
      catalogs: { sheets: [{ id: 2, height: 1, width: 1, price: 1 }] },
      error: null,
      errors: {},
    });

    await act(async () => {
      result.current.reloadCatalogs();
    });

    await waitFor(() => {
      expect(result.current.catalogLoadState.catalogs.sheets).toHaveLength(1);
    });

    expect(loadCatalogs).toHaveBeenCalledTimes(1);
  });
});
