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
    chroma: "ZERO_ZERO",
  };
}

function emptyLaminateOperation() {
  return {
    clientKey: newClientKey(),
    kind: "laminate",
    laminatorId: "",
    operatorId: "",
    lamination: "DONT",
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

export function emptyBlock() {
  return {
    clientKey: newClientKey(),
    count: "0",
    markup: "0",
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
    operations: [],
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
      film: {
        name: operation.film.name,
        price: coerceMoneyField(operation.film.price),
        density: coerceIntegerField(operation.film.density),
      },
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
    markup: coerceIntegerField(block.markup),
    imposition: {
      target: {
        name: "",
        width: coerceIntegerField(block.target.width),
        height: coerceIntegerField(block.target.height),
      },
      press_sheet: {
        paper: {
          name: block.paper.name,
          density: coerceIntegerField(block.paper.density),
          thickness: coerceIntegerField(block.paper.thickness),
          price_per_kilo: coerceMoneyField(block.paper.price_per_kilo),
        },
        format: {
          name: block.sheetFormat.name,
          width: coerceIntegerField(block.sheetFormat.width),
          height: coerceIntegerField(block.sheetFormat.height),
        },
      },
      bleeds: coerceIntegerField(block.bleeds),
      spacing: coerceIntegerField(block.spacing),
    },
    operations: block.operations.map(mapOperationToWrite),
  };
}

export function toOrderWrite(form) {
  return {
    count: coerceIntegerField(form.count),
    product: {
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
      film: {
        name: operation.film.name,
        price: operation.film.price,
        density: numberToFormString(operation.film.density),
      },
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

function mapBlockFromDto(block) {
  const { imposition } = block;
  return {
    clientKey: newClientKey(),
    count: numberToFormString(block.count),
    markup: numberToFormString(block.markup),
    target: {
      name: imposition.target.name,
      width: numberToFormString(imposition.target.width),
      height: numberToFormString(imposition.target.height),
    },
    paperSheetId: "",
    paper: {
      name: imposition.press_sheet.paper.name,
      density: numberToFormString(imposition.press_sheet.paper.density),
      thickness: numberToFormString(imposition.press_sheet.paper.thickness),
      price_per_kilo: imposition.press_sheet.paper.price_per_kilo,
    },
    sheetFormat: {
      name: imposition.press_sheet.format.name,
      width: numberToFormString(imposition.press_sheet.format.width),
      height: numberToFormString(imposition.press_sheet.format.height),
    },
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

export function toOrderSummary(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("order: id must be a number");
  }
  if (typeof raw?.count !== "number") {
    throw new Error("order: count must be a number");
  }
  return { id: raw.id, count: raw.count };
}

export {
  emptyPrintOperation,
  emptyLaminateOperation,
  emptyCutOperation,
  emptyDieCutOperation,
};
