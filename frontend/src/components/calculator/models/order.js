function newClientKey() {
  return crypto.randomUUID();
}

function coerceIntegerField(value) {
  const raw = typeof value === "string" ? value.trim() : String(value ?? "");
  if (raw === "") {
    return "";
  }
  if (/^-?\d+$/.test(raw)) {
    return Number(raw);
  }
  return raw;
}

function coerceMoneyField(value) {
  return String(value ?? "").trim();
}

function coerceIdField(value) {
  if (value === "" || value === undefined || value === null) {
    return "";
  }
  const raw = String(value).trim();
  if (raw === "") {
    return "";
  }
  if (/^-?\d+$/.test(raw)) {
    return Number(raw);
  }
  return raw;
}

function numberToFormString(value) {
  return String(value);
}

function emptyPrintOperation() {
  return {
    clientKey: newClientKey(),
    kind: "print",
    printerId: "",
    operatorId: "",
    chroma: "",
  };
}

function emptyLaminateOperation() {
  return {
    clientKey: newClientKey(),
    kind: "laminate",
    laminatorId: "",
    operatorId: "",
    lamination: "",
    filmId: "",
    film: { name: "", price: "0", density: "0" },
  };
}

function emptyCutOperation() {
  return {
    clientKey: newClientKey(),
    kind: "cut",
    cutterId: "",
    operatorId: "",
  };
}

function emptyDieCutOperation() {
  return {
    clientKey: newClientKey(),
    kind: "die_cut",
    operatorId: "",
  };
}

const BLOCK_OPERATION_KIND_ORDER = ["print", "laminate", "cut", "die_cut"];

export function sortBlockOperationsByKind(operations) {
  return [...operations].sort(
    (a, b) =>
      BLOCK_OPERATION_KIND_ORDER.indexOf(a.kind) -
      BLOCK_OPERATION_KIND_ORDER.indexOf(b.kind),
  );
}

function ensureMandatoryBlockOperations(operations) {
  const next = [...operations];
  if (!next.some((op) => op.kind === "print")) {
    next.push(emptyPrintOperation());
  }
  if (!next.some((op) => op.kind === "cut")) {
    next.push(emptyCutOperation());
  }
  return sortBlockOperationsByKind(next);
}

export function emptyBlock() {
  return {
    clientKey: newClientKey(),
    count: "0",
    target: { name: "", width: "0", height: "0" },
    paperSheetId: "",
    paper: {
      name: "",
      density: "",
      thickness: "",
      price_per_kilo: "0",
    },
    sheetFormat: { name: "", width: "0", height: "0" },
    bleeds: "0",
    spacing: "0",
    operations: [emptyPrintOperation(), emptyCutOperation()],
  };
}

export function emptyAdditionalWork() {
  return {
    clientKey: newClientKey(),
    name: "",
    price: "0",
    description: "",
    markup: "0",
  };
}

export function emptyCalculatorForm() {
  return {
    count: "0",
    description: "",
    partsMarkup: "0",
    blocks: [emptyBlock()],
    additionalWorks: [],
  };
}

function mapOperationToWrite(operation) {
  if (operation.kind === "print") {
    return {
      kind: "print",
      printer_id: coerceIdField(operation.printerId),
      operator_id: coerceIdField(operation.operatorId),
      chroma: operation.chroma,
    };
  }
  if (operation.kind === "laminate") {
    return {
      kind: "laminate",
      laminator_id: coerceIdField(operation.laminatorId),
      operator_id: coerceIdField(operation.operatorId),
      lamination: operation.lamination,
      film_id: coerceIdField(operation.filmId),
    };
  }
  if (operation.kind === "cut") {
    return {
      kind: "cut",
      cutter_id: coerceIdField(operation.cutterId),
      operator_id: coerceIdField(operation.operatorId),
    };
  }
  if (operation.kind === "die_cut") {
    return {
      kind: "die_cut",
      operator_id: coerceIdField(operation.operatorId),
    };
  }
  throw new Error(`order: unknown operation kind ${operation.kind}`);
}

function mapBlockToWrite(block) {
  return {
    count: coerceIntegerField(block.count),
    imposition: {
      target: {
        name: "",
        width: coerceIntegerField(block.target.width),
        height: coerceIntegerField(block.target.height),
      },
      sheet_id: coerceIdField(block.paperSheetId),
      bleeds: coerceIntegerField(block.bleeds),
      spacing: coerceIntegerField(block.spacing),
    },
    operations: block.operations.map(mapOperationToWrite),
  };
}

export function toOrderWrite(form) {
  return {
    count: coerceIntegerField(form.count),
    description: String(form.description ?? ""),
    product: {
      parts_markup: coerceIntegerField(form.partsMarkup),
      blocks: form.blocks.map(mapBlockToWrite),
      operations: form.additionalWorks.map((work) => ({
        name: work.name,
        price: coerceMoneyField(work.price),
        description: work.description,
        markup: coerceIntegerField(work.markup),
      })),
    },
  };
}

function mapOperationFromDto(operation) {
  if (operation.kind === "print") {
    return {
      clientKey: newClientKey(),
      kind: "print",
      printerId: numberToFormString(operation.printer_id),
      operatorId: numberToFormString(operation.operator_id),
      chroma: operation.chroma,
    };
  }
  if (operation.kind === "laminate") {
    return {
      clientKey: newClientKey(),
      kind: "laminate",
      laminatorId: numberToFormString(operation.laminator_id),
      operatorId: numberToFormString(operation.operator_id),
      lamination: operation.lamination,
      filmId:
        operation.film_id != null
          ? numberToFormString(operation.film_id)
          : "",
      film: { name: "", price: "0", density: "0" },
    };
  }
  if (operation.kind === "cut") {
    return {
      clientKey: newClientKey(),
      kind: "cut",
      cutterId: numberToFormString(operation.cutter_id),
      operatorId: numberToFormString(operation.operator_id),
    };
  }
  if (operation.kind === "die_cut") {
    return {
      clientKey: newClientKey(),
      kind: "die_cut",
      operatorId: numberToFormString(operation.operator_id),
    };
  }
  throw new Error(`order: unknown operation kind ${operation.kind}`);
}

export function emptyPaperFields() {
  return {
    name: "",
    density: "",
    thickness: "",
    price_per_kilo: "0",
  };
}

export function paperFromSheet(sheet) {
  return {
    name: sheet.paper.name,
    density: String(sheet.paper.density),
    thickness: String(sheet.paper.thickness),
    price_per_kilo: sheet.paper.price_per_kilo,
  };
}

export function sheetFormatFromSheet(sheet) {
  if (!sheet.format) {
    return { name: "", width: "0", height: "0" };
  }
  return {
    name: sheet.format.name,
    width: String(sheet.format.width),
    height: String(sheet.format.height),
  };
}

export function emptyFilmFields() {
  return { name: "", price: "0", density: "0" };
}

export function filmOptionFromCatalog(film) {
  return {
    name: film.name,
    price: film.price,
    density: String(film.density),
  };
}

function applyFilmsToOperations(operations, films) {
  return operations.map((operation) => {
    if (operation.kind !== "laminate" || !operation.filmId) {
      return operation;
    }
    const film = films.find(
      (row) => String(row.id) === String(operation.filmId),
    );
    if (!film) {
      return operation;
    }
    return {
      ...operation,
      film: filmOptionFromCatalog(film),
    };
  });
}

export function applySheetsCatalogToForm(form, sheets) {
  return {
    ...form,
    blocks: form.blocks.map((block) => {
      if (!block.paperSheetId) {
        return block;
      }
      const sheet = sheets.find(
        (row) => String(row.id) === String(block.paperSheetId),
      );
      if (!sheet) {
        return block;
      }
      return {
        ...block,
        paper: paperFromSheet(sheet),
        sheetFormat: sheetFormatFromSheet(sheet),
      };
    }),
  };
}

export function applyFilmsCatalogToForm(form, films) {
  return {
    ...form,
    blocks: form.blocks.map((block) => ({
      ...block,
      operations: applyFilmsToOperations(block.operations, films),
    })),
  };
}

function catalogFirstId(items) {
  return items?.length > 0 ? String(items[0].id) : "";
}

export function applyOperationCatalogDefaults(operation, catalogs) {
  if (operation.kind === "print") {
    return {
      ...operation,
      printerId: operation.printerId || catalogFirstId(catalogs.printers),
      operatorId:
        operation.operatorId || catalogFirstId(catalogs.pressOperators),
    };
  }
  if (operation.kind === "laminate") {
    return {
      ...operation,
      laminatorId:
        operation.laminatorId || catalogFirstId(catalogs.laminators),
      operatorId:
        operation.operatorId || catalogFirstId(catalogs.laminatorOperators),
      filmId: operation.filmId || catalogFirstId(catalogs.films),
    };
  }
  if (operation.kind === "cut") {
    return {
      ...operation,
      cutterId: operation.cutterId || catalogFirstId(catalogs.cutters),
      operatorId:
        operation.operatorId || catalogFirstId(catalogs.cutterOperators),
    };
  }
  if (operation.kind === "die_cut") {
    return {
      ...operation,
      operatorId:
        operation.operatorId || catalogFirstId(catalogs.dieCutOperators),
    };
  }
  return operation;
}

export function applyBlockCatalogDefaults(block, catalogs) {
  let next = { ...block };
  if (next.paperSheetId === "" && catalogs.sheets?.length > 0) {
    const sheet = catalogs.sheets[0];
    next = {
      ...next,
      paperSheetId: String(sheet.id),
      paper: paperFromSheet(sheet),
      sheetFormat: sheetFormatFromSheet(sheet),
    };
  }
  return {
    ...next,
    operations: ensureMandatoryBlockOperations(next.operations).map((operation) =>
      applyOperationCatalogDefaults(operation, catalogs),
    ),
  };
}

export function applyCatalogDefaultsToForm(form, catalogs) {
  return {
    ...form,
    blocks: form.blocks.map((block) =>
      applyBlockCatalogDefaults(block, catalogs),
    ),
  };
}

function mapBlockFromDto(block) {
  const { imposition } = block;
  return {
    clientKey: newClientKey(),
    count: numberToFormString(block.count),
    target: {
      name: imposition.target.name,
      width: numberToFormString(imposition.target.width),
      height: numberToFormString(imposition.target.height),
    },
    paperSheetId:
      imposition.sheet_id != null
        ? numberToFormString(imposition.sheet_id)
        : "",
    paper: {
      name: "",
      density: "",
      thickness: "",
      price_per_kilo: "0",
    },
    sheetFormat: { name: "", width: "0", height: "0" },
    bleeds: numberToFormString(imposition.bleeds),
    spacing: numberToFormString(imposition.spacing),
    operations: block.operations.map(mapOperationFromDto),
  };
}

export function toCalculatorForm(order) {
  const blocks = order.product?.blocks;
  if (!Array.isArray(blocks) || blocks.length === 0) {
    throw new Error("order: product.blocks must not be empty");
  }
  return {
    count: numberToFormString(order.count),
    description: order.description ?? "",
    partsMarkup: numberToFormString(order.product.parts_markup),
    blocks: blocks.map(mapBlockFromDto),
    additionalWorks: (order.product.operations ?? []).map((work) => ({
      clientKey: newClientKey(),
      name: work.name,
      price: work.price,
      description: work.description,
      markup: numberToFormString(work.markup),
    })),
  };
}

const DECIMAL_STRING = /^-?\d+(\.\d+)?$/;
const SIGNED_INT_STRING = /^-?\d+$/;

function isCoercibleIntegerField(value) {
  const raw =
    typeof value === "string" ? value.trim() : String(value ?? "").trim();
  return raw !== "" && SIGNED_INT_STRING.test(raw);
}

function isCoercibleIdField(value) {
  if (value === "" || value === undefined || value === null) {
    return false;
  }
  const raw = String(value).trim();
  return raw !== "" && SIGNED_INT_STRING.test(raw);
}

function isNonEmptyStringField(value) {
  return String(value ?? "").trim() !== "";
}

function isCoercibleMoneyField(value) {
  const raw = String(value ?? "").trim();
  return raw !== "" && DECIMAL_STRING.test(raw);
}

function isPositiveIntegerField(value) {
  if (!isCoercibleIntegerField(value)) {
    return false;
  }
  return Number(String(value).trim()) > 0;
}

const OPERATION_KIND_LABEL = {
  print: "Печать",
  laminate: "Ламинация",
  cut: "Рез",
  die_cut: "Высечка",
};

function blockLabelPrefix(blockCount, index) {
  return blockCount > 1 ? `Блок ${index + 1}: ` : "";
}

function additionalWorkLabelPrefix(workCount, index) {
  return workCount > 1 ? `Доп. работа ${index + 1}: ` : "Доп. работа: ";
}

function pushWhenInvalid(missing, isValid, label) {
  if (!isValid) {
    missing.push(label);
  }
}

function collectOperationMissingLabels(operation, blockPrefix, missing) {
  const kindLabel = OPERATION_KIND_LABEL[operation.kind] ?? operation.kind;
  const labelPrefix = blockPrefix ? `${blockPrefix}${kindLabel}: ` : `${kindLabel}: `;

  if (operation.kind === "print") {
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.printerId),
      `${labelPrefix}Принтер`,
    );
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.operatorId),
      `${labelPrefix}Печатник`,
    );
    pushWhenInvalid(
      missing,
      isNonEmptyStringField(operation.chroma),
      `${labelPrefix}Цветность`,
    );
    return;
  }
  if (operation.kind === "laminate") {
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.laminatorId),
      `${labelPrefix}Ламинатор`,
    );
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.operatorId),
      `${labelPrefix}Оператор`,
    );
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.filmId),
      `${labelPrefix}Плёнка`,
    );
    pushWhenInvalid(
      missing,
      isNonEmptyStringField(operation.lamination),
      `${labelPrefix}Кратность`,
    );
    return;
  }
  if (operation.kind === "cut") {
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.cutterId),
      `${labelPrefix}Резак`,
    );
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.operatorId),
      `${labelPrefix}Оператор`,
    );
    return;
  }
  if (operation.kind === "die_cut") {
    pushWhenInvalid(
      missing,
      isCoercibleIdField(operation.operatorId),
      `${labelPrefix}Оператор`,
    );
  }
}

function collectBlockMissingLabels(block, blockCount, blockIndex, missing) {
  const prefix = blockLabelPrefix(blockCount, blockIndex);
  pushWhenInvalid(
    missing,
    isPositiveIntegerField(block.count),
    `${prefix}Листов`,
  );
  pushWhenInvalid(
    missing,
    isPositiveIntegerField(block.target.width),
    `${prefix}Ширина`,
  );
  pushWhenInvalid(
    missing,
    isPositiveIntegerField(block.target.height),
    `${prefix}Высота`,
  );
  pushWhenInvalid(
    missing,
    isCoercibleIdField(block.paperSheetId),
    `${prefix}Бумага`,
  );
  pushWhenInvalid(
    missing,
    isCoercibleIntegerField(block.bleeds),
    `${prefix}Вылеты`,
  );
  pushWhenInvalid(
    missing,
    isCoercibleIntegerField(block.spacing),
    `${prefix}Поля`,
  );
  for (const operation of block.operations) {
    collectOperationMissingLabels(operation, prefix, missing);
  }
}

function collectAdditionalWorkMissingLabels(work, workCount, workIndex, missing) {
  const prefix = additionalWorkLabelPrefix(workCount, workIndex);
  pushWhenInvalid(
    missing,
    String(work.name ?? "").trim() !== "",
    `${prefix}Работа`,
  );
  pushWhenInvalid(
    missing,
    isCoercibleMoneyField(work.price),
    `${prefix}Стоимость`,
  );
  pushWhenInvalid(
    missing,
    isCoercibleIntegerField(work.markup),
    `${prefix}Наценка`,
  );
}

export function calculatorFormMissingFieldLabels(form) {
  const missing = [];
  if (!form?.blocks?.length) {
    missing.push("Блок");
    return missing;
  }
  pushWhenInvalid(missing, isPositiveIntegerField(form.count), "Тираж");
  pushWhenInvalid(missing, isCoercibleIntegerField(form.partsMarkup), "Наценка");
  form.blocks.forEach((block, index) => {
    collectBlockMissingLabels(block, form.blocks.length, index, missing);
  });
  const works = form.additionalWorks ?? [];
  works.forEach((work, index) => {
    collectAdditionalWorkMissingLabels(work, works.length, index, missing);
  });
  return missing;
}

export function isCalculatorFormReadyForQuote(form) {
  return calculatorFormMissingFieldLabels(form).length === 0;
}

function requireDecimalString(raw, field) {
  if (typeof raw !== "string" || !DECIMAL_STRING.test(raw)) {
    throw new Error(`order report: ${field} must be a decimal string`);
  }
  return raw;
}

export function toOrderReport(raw) {
  return {
    product_price: requireDecimalString(raw?.product_price, "product_price"),
    order_price: requireDecimalString(raw?.order_price, "order_price"),
    income: requireDecimalString(raw?.income, "income"),
    impositions: (() => {
      if (!Array.isArray(raw?.impositions)) {
        throw new Error("order report: impositions must be an array");
      }
      return raw.impositions.map((value, index) => {
        if (typeof value !== "number" || !Number.isInteger(value)) {
          throw new Error(`order report: impositions[${index}] must be an integer`);
        }
        return value;
      });
    })(),
  };
}

export function formatOrderCreatedDate(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    throw new Error("order: created_at is not a valid date");
  }
  return date.toLocaleDateString("ru-RU");
}

export function toOrderSummary(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("order: id must be a number");
  }
  if (typeof raw?.count !== "number") {
    throw new Error("order: count must be a number");
  }
  if (typeof raw?.created_at !== "string" || raw.created_at.trim() === "") {
    throw new Error("order: created_at must be a non-empty string");
  }
  return {
    id: raw.id,
    count: raw.count,
    description: String(raw.description ?? ""),
    created_at: raw.created_at,
  };
}

export {
  emptyPrintOperation,
  emptyLaminateOperation,
  emptyCutOperation,
  emptyDieCutOperation,
};
