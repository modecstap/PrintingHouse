const CHROMA_BY_NUMBER = {
  0: "ZERO_ZERO",
  1: "ONE_ZERO",
  2: "ONE_ONE",
  3: "FOUR_ZERO",
  4: "FOUR_ONE",
  5: "FOUR_FOUR",
};

const LAMINATION_BY_NUMBER = {
  1: "DONT",
  2: "ONE_ZERO",
  3: "ONE_ONE",
};

const CHROMA_BY_NAME = invert(CHROMA_BY_NUMBER);
const LAMINATION_BY_NAME = invert(LAMINATION_BY_NUMBER);

function invert(byNumber) {
  const byName = {};
  for (const [number, name] of Object.entries(byNumber)) {
    byName[name] = Number(number);
  }
  return byName;
}

function hasKey(object, key) {
  return Object.prototype.hasOwnProperty.call(object, key);
}

function toJsonInteger(value) {
  if (Number.isInteger(value)) return value;
  if (typeof value === "string" && /^-?\d+$/.test(value)) return Number(value);
  return value;
}

function toJsonDecimal(value) {
  if (typeof value === "number" && Number.isFinite(value)) return String(value);
  if (typeof value === "string") return value;
  return value;
}

function toOrderId(value) {
  const asInteger = toJsonInteger(value);
  return Number.isInteger(asInteger) ? asInteger : null;
}

function toText(value) {
  if (typeof value === "string") return value;
  if (value == null) return "";
  return value;
}

function toEnumName(value, byNumber) {
  const asInteger = toJsonInteger(value);
  if (Number.isInteger(asInteger) && hasKey(byNumber, asInteger)) {
    return byNumber[asInteger];
  }
  return value;
}

function enumNumber(value, byName) {
  if (typeof value === "string" && hasKey(byName, value)) return byName[value];
  return value;
}

function toDieCutting(value) {
  return value === true || value === "true";
}

function mapOutgoingList(value, mapper) {
  if (value == null) return [];
  if (!Array.isArray(value)) return value;
  return value.map(mapper);
}

function mapIncomingList(value, mapper) {
  if (!Array.isArray(value)) return [];
  return value.map(mapper);
}

function toOperation(operation) {
  const source = operation ?? {};
  return {
    name: toText(source.name),
    cost: toJsonDecimal(source.cost),
    description: toText(source.description),
  };
}

function toPrinting(printing) {
  const source = printing ?? {};
  const edition = source.edition ?? {};
  const production = source.production ?? {};
  const listSize = edition.list_size ?? {};
  const pressSheet = production.press_sheet ?? {};
  const cutter = production.cutter ?? {};

  return {
    count: toJsonInteger(edition.count),
    comment: toText(source.comment),
    chroma: toEnumName(edition.chroma, CHROMA_BY_NUMBER),
    lamination: toEnumName(edition.lamination, LAMINATION_BY_NUMBER),
    die_cutting: toDieCutting(edition.die_cutting),
    sheet_by_fitting: toJsonInteger(production.sheet_by_fitting),
    stack_height: toJsonInteger(cutter.stack_height),
    press_sheet: {
      density: toJsonInteger(edition.density),
      width: toJsonInteger(pressSheet.width),
      height: toJsonInteger(pressSheet.height),
      spacing: toJsonInteger(pressSheet.spacing),
    },
    list: {
      width: toJsonInteger(listSize.width),
      height: toJsonInteger(listSize.height),
      bleeds: toJsonInteger(listSize.bleeds),
    },
    press_pricing: {
      cyan: toJsonDecimal(production.cyan),
      magenta: toJsonDecimal(production.magenta),
      yellow: toJsonDecimal(production.yellow),
      black: toJsonDecimal(production.black_ink_cost),
      paper: toJsonDecimal(production.paper_cost),
      salary: toJsonDecimal(production.printer_salary),
    },
    cut_pricing: {
      salary: toJsonDecimal(production.cutting_cost),
    },
    lamination_pricing: {
      startup: toJsonDecimal(production.lamination_startup),
      film_cost: toJsonDecimal(production.film_cost),
      salary: toJsonDecimal(production.lamination_salary),
    },
    die_cut_pricing: {
      salary: toJsonDecimal(production.die_cutting_cost),
    },
  };
}

function productionFromPrinting(printing) {
  const source = printing ?? {};
  const pricing = source.press_pricing ?? {};
  const pressSheet = source.press_sheet ?? {};
  const lamination = source.lamination_pricing ?? {};

  return {
    cyan: pricing.cyan,
    magenta: pricing.magenta,
    yellow: pricing.yellow,
    black_ink_cost: pricing.black,
    paper_cost: pricing.paper,
    printer_salary: pricing.salary,
    lamination_startup: lamination.startup,
    film_cost: lamination.film_cost,
    lamination_salary: lamination.salary,
    die_cutting_cost: source.die_cut_pricing?.salary,
    press_sheet: {
      height: pressSheet.height,
      width: pressSheet.width,
      spacing: pressSheet.spacing,
    },
    cutter: {
      stack_height: source.stack_height,
    },
    sheet_by_fitting: source.sheet_by_fitting,
    cutting_cost: source.cut_pricing?.salary,
  };
}

function printingToForm(printing) {
  const source = printing ?? {};
  const pressSheet = source.press_sheet ?? {};
  const list = source.list ?? {};

  return {
    edition: {
      count: source.count,
      list_size: {
        width: list.width,
        height: list.height,
        bleeds: list.bleeds,
      },
      density: pressSheet.density,
      chroma: enumNumber(source.chroma, CHROMA_BY_NAME),
      lamination: enumNumber(source.lamination, LAMINATION_BY_NAME),
      die_cutting: source.die_cutting,
    },
    production: productionFromPrinting(source),
    comment: typeof source.comment === "string" ? source.comment : "",
  };
}

export function toWorkplaceOrder(form) {
  const source = form ?? {};
  const economy = source.economy ?? {};
  const body = {
    id: toOrderId(source.id),
    comment: toText(source.comment),
    unit_count: toJsonInteger(source.unit_count),
    tax_rate: toJsonDecimal(economy.tax_rate),
    markup: toJsonDecimal(economy.markup),
    operations: mapOutgoingList(source.operations, toOperation),
    printings: mapOutgoingList(source.printings, toPrinting),
  };

  if (typeof source.status === "string") {
    body.status = source.status;
  }

  return body;
}

export function toCalculatorForm(order) {
  const source = order ?? {};
  const form = {
    id: source.id ?? null,
    comment: typeof source.comment === "string" ? source.comment : "",
    unit_count: source.unit_count,
    economy: {
      tax_rate: source.tax_rate,
      markup: source.markup,
    },
    operations: mapIncomingList(source.operations, (item) => ({
      name: item?.name ?? "",
      cost: item?.cost,
      description: item?.description ?? "",
    })),
    printings: mapIncomingList(source.printings, printingToForm),
  };

  if (typeof source.status === "string") {
    form.status = source.status;
  }
  if (typeof source.creation_date === "string") {
    form.creation_date = source.creation_date;
  }

  return form;
}

export function referenceProduction(order) {
  return productionFromPrinting(order?.printings?.[0]);
}
