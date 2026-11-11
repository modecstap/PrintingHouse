import {
  uniquePaperTypeOptionsFromSheets,
  uniquePaperDensityOptionsFromSheets,
  filterSheetsByPaperFilters,
  isSelectedPaperSheetInFilteredList,
} from "./sheet-paper-filters";

const SHEETS = [
  {
    id: 1,
    paper: { name: "офсет", density: 80, thickness: 1, price_per_kilo: "50" },
    format: { name: "SRA3", width: 320, height: 450 },
  },
  {
    id: 2,
    paper: { name: "офсет", density: 120, thickness: 1, price_per_kilo: "60" },
    format: { name: "SRA3", width: 320, height: 450 },
  },
  {
    id: 3,
    paper: {
      name: "мелованная",
      density: 150,
      thickness: 1,
      price_per_kilo: "80",
    },
    format: { name: "SRA3", width: 320, height: 450 },
  },
];

describe("sheet paper filters", () => {
  it("should return sorted unique paper type options", () => {
    expect(uniquePaperTypeOptionsFromSheets(SHEETS)).toEqual([
      { value: "мелованная", label: "мелованная" },
      { value: "офсет", label: "офсет" },
    ]);
  });

  it("should return sorted unique density options as strings", () => {
    expect(uniquePaperDensityOptionsFromSheets(SHEETS)).toEqual([
      { value: "80", label: "80" },
      { value: "120", label: "120" },
      { value: "150", label: "150" },
    ]);
  });

  it("should return all sheets when filters are empty", () => {
    expect(filterSheetsByPaperFilters(SHEETS, "", "")).toEqual(SHEETS);
  });

  it("should filter by paper type only", () => {
    expect(filterSheetsByPaperFilters(SHEETS, "офсет", "")).toEqual([
      SHEETS[0],
      SHEETS[1],
    ]);
  });

  it("should filter by density only", () => {
    expect(filterSheetsByPaperFilters(SHEETS, "", "120")).toEqual([SHEETS[1]]);
  });

  it("should filter by both type and density", () => {
    expect(filterSheetsByPaperFilters(SHEETS, "офсет", "80")).toEqual([
      SHEETS[0],
    ]);
  });

  it("should treat empty selection as in filtered list", () => {
    expect(
      isSelectedPaperSheetInFilteredList("", emptyPaper(), SHEETS, SHEETS),
    ).toBe(true);
  });

  it("should report false when selected sheet is outside filter", () => {
    expect(
      isSelectedPaperSheetInFilteredList(
        "3",
        emptyPaper(),
        SHEETS,
        filterSheetsByPaperFilters(SHEETS, "офсет", ""),
      ),
    ).toBe(false);
  });

  it("should report true when selected sheet matches filter", () => {
    expect(
      isSelectedPaperSheetInFilteredList(
        "1",
        emptyPaper(),
        SHEETS,
        filterSheetsByPaperFilters(SHEETS, "офсет", ""),
      ),
    ).toBe(true);
  });
});

function emptyPaper() {
  return { name: "", density: "", thickness: "", price_per_kilo: "" };
}
