export function toJsonInt(value) {
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (/^-?\d+$/.test(trimmed)) {
      return Number(trimmed);
    }
    return trimmed;
  }
  return value;
}

export function toPrinter(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("printer: id must be a number");
  }
  if (typeof raw?.startup !== "string") {
    throw new Error("printer: startup must be a string");
  }
  if (typeof raw?.cyan !== "string") {
    throw new Error("printer: cyan must be a string");
  }
  if (typeof raw?.magenta !== "string") {
    throw new Error("printer: magenta must be a string");
  }
  if (typeof raw?.yellow !== "string") {
    throw new Error("printer: yellow must be a string");
  }
  if (typeof raw?.black !== "string") {
    throw new Error("printer: black must be a string");
  }
  return {
    id: raw.id,
    startup: raw.startup,
    cyan: raw.cyan,
    magenta: raw.magenta,
    yellow: raw.yellow,
    black: raw.black,
  };
}

export function toLaminator(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("laminator: id must be a number");
  }
  if (typeof raw?.startup !== "string") {
    throw new Error("laminator: startup must be a string");
  }
  return { id: raw.id, startup: raw.startup };
}

export function toCutter(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("cutter: id must be a number");
  }
  if (typeof raw?.max_stack !== "number") {
    throw new Error("cutter: max_stack must be a number");
  }
  return { id: raw.id, max_stack: raw.max_stack };
}

export function toOperator(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("operator: id must be a number");
  }
  if (typeof raw?.salary_by_operation !== "string") {
    throw new Error("operator: salary_by_operation must be a string");
  }
  return { id: raw.id, salary_by_operation: raw.salary_by_operation };
}

export function toSheet(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("sheet: id must be a number");
  }
  const paper = raw?.paper;
  if (typeof paper?.name !== "string") {
    throw new Error("sheet: paper.name must be a string");
  }
  if (typeof paper?.density !== "number") {
    throw new Error("sheet: paper.density must be a number");
  }
  if (typeof paper?.thickness !== "number") {
    throw new Error("sheet: paper.thickness must be a number");
  }
  if (typeof paper?.price_per_kilo !== "string") {
    throw new Error("sheet: paper.price_per_kilo must be a string");
  }
  const format = raw?.format;
  if (typeof format?.name !== "string") {
    throw new Error("sheet: format.name must be a string");
  }
  if (typeof format?.height !== "number") {
    throw new Error("sheet: format.height must be a number");
  }
  if (typeof format?.width !== "number") {
    throw new Error("sheet: format.width must be a number");
  }
  return {
    id: raw.id,
    paper: {
      name: paper.name,
      density: paper.density,
      thickness: paper.thickness,
      price_per_kilo: paper.price_per_kilo,
    },
    format: {
      name: format.name,
      height: format.height,
      width: format.width,
    },
  };
}

export function toFilm(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("film: id must be a number");
  }
  if (typeof raw?.name !== "string") {
    throw new Error("film: name must be a string");
  }
  if (typeof raw?.price !== "string") {
    throw new Error("film: price must be a string");
  }
  if (typeof raw?.density !== "number") {
    throw new Error("film: density must be a number");
  }
  return {
    id: raw.id,
    name: raw.name,
    price: raw.price,
    density: raw.density,
  };
}

function toList(raw, itemParser, modelName) {
  if (!Array.isArray(raw)) {
    throw new Error(`${modelName}: list must be an array`);
  }
  return raw.map(itemParser);
}

export function toPrinterList(raw) {
  return toList(raw, toPrinter, "printer");
}

export function toLaminatorList(raw) {
  return toList(raw, toLaminator, "laminator");
}

export function toCutterList(raw) {
  return toList(raw, toCutter, "cutter");
}

export function toOperatorList(raw) {
  return toList(raw, toOperator, "operator");
}

export function toSheetList(raw) {
  return toList(raw, toSheet, "sheet");
}

export function toFilmList(raw) {
  return toList(raw, toFilm, "film");
}
