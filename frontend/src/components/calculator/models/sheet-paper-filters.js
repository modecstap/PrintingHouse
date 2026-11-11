export function resolvePaperSheetId(paperSheetId, paper, sheets) {
  if (paperSheetId) {
    return paperSheetId;
  }
  const match = sheets.find(
    (sheet) =>
      sheet.paper.name === paper.name &&
      String(sheet.paper.density) === String(paper.density) &&
      String(sheet.paper.thickness) === String(paper.thickness) &&
      sheet.paper.price_per_kilo === paper.price_per_kilo,
  );
  return match ? String(match.id) : "";
}

export function uniquePaperTypeOptionsFromSheets(sheets) {
  if (!sheets?.length) {
    return [];
  }
  return [...new Set(sheets.map((s) => s.paper.name))]
    .sort((a, b) => a.localeCompare(b))
    .map((name) => ({ value: name, label: name }));
}

export function uniquePaperDensityOptionsFromSheets(sheets) {
  if (!sheets?.length) {
    return [];
  }
  return [...new Set(sheets.map((s) => s.paper.density))]
    .sort((a, b) => a - b)
    .map((n) => ({ value: String(n), label: String(n) }));
}

export function filterSheetsByPaperFilters(
  sheets,
  paperTypeFilter,
  paperDensityFilter,
) {
  return sheets.filter((sheet) => {
    const typeOk =
      !paperTypeFilter || sheet.paper.name === paperTypeFilter;
    const densityOk =
      !paperDensityFilter ||
      String(sheet.paper.density) === String(paperDensityFilter);
    return typeOk && densityOk;
  });
}

export function isSelectedPaperSheetInFilteredList(
  paperSheetId,
  paper,
  allSheets,
  filteredSheets,
) {
  const resolvedId = resolvePaperSheetId(paperSheetId, paper, allSheets);
  if (resolvedId === "") {
    return true;
  }
  return filteredSheets.some((s) => String(s.id) === resolvedId);
}
