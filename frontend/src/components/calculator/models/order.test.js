import {
  applyCatalogDefaultsToForm,
  emptyBlock,
  emptyCalculatorForm,
  emptyPrintOperation,
  calculatorFormMissingFieldLabels,
  isCalculatorFormReadyForQuote,
  toOrderWrite,
  toCalculatorForm,
  toOrderReport,
  formatOrderCreatedDate,
  toOrderSummary,
} from "./order";

const sampleWriteJson = {
  count: 10,
  description: "Визитки",
  product: {
    blocks: [
      {
        count: 2,
        markup: 30,
        imposition: {
          target: { name: "", width: 90, height: 50 },
          sheet_id: 1,
          bleeds: 2,
          spacing: 5,
        },
        operations: [
          { kind: "print", printer_id: 1, operator_id: 4, chroma: "FOUR_ZERO" },
          {
            kind: "laminate",
            laminator_id: 2,
            operator_id: 5,
            lamination: "ONE_ZERO",
            film_id: 2,
          },
          { kind: "cut", cutter_id: 3, operator_id: 6 },
          { kind: "die_cut", operator_id: 7 },
        ],
      },
    ],
    operations: [
      { name: "Сборка", price: "10.00", description: "Вручную", markup: 15 },
    ],
  },
};

function sampleForm() {
  return {
    count: "10",
    description: "Визитки",
    blocks: [
      {
        clientKey: "block-key",
        count: "2",
        markup: "30",
        target: { name: "Визитка", width: "90", height: "50" },
        paperSheetId: "1",
        paper: {
          name: "Мелованная",
          density: "150",
          thickness: "1",
          price_per_kilo: "80.50",
        },
        sheetFormat: { name: "SRA3", width: "320", height: "450" },
        bleeds: "2",
        spacing: "5",
        operations: [
          {
            clientKey: "print-key",
            kind: "print",
            printerId: "1",
            operatorId: "4",
            chroma: "FOUR_ZERO",
          },
          {
            clientKey: "laminate-key",
            kind: "laminate",
            laminatorId: "2",
            operatorId: "5",
            lamination: "ONE_ZERO",
            filmId: "2",
            film: { name: "Глянец", price: "3.00", density: "25" },
          },
          {
            clientKey: "cut-key",
            kind: "cut",
            cutterId: "3",
            operatorId: "6",
          },
          {
            clientKey: "die-cut-key",
            kind: "die_cut",
            operatorId: "7",
          },
        ],
      },
    ],
    additionalWorks: [
      {
        clientKey: "work-key",
        name: "Сборка",
        price: "10.00",
        description: "Вручную",
        markup: "15",
      },
    ],
  };
}

describe("applyCatalogDefaultsToForm", () => {
  it("should pick the first catalog entry for empty dropdown fields", () => {
    const form = {
      ...emptyCalculatorForm(),
      blocks: [
        {
          ...emptyBlock(),
          operations: [emptyPrintOperation()],
        },
      ],
    };
    const catalogs = {
      printers: [{ id: 7 }],
      pressOperators: [{ id: 3 }],
      laminators: [],
      cutters: [],
      laminatorOperators: [],
      cutterOperators: [],
      dieCutOperators: [],
      sheets: [{ id: 2, paper: { name: "A", density: 1, thickness: 1, price_per_kilo: "1" }, format: null }],
      films: [],
    };
    const next = applyCatalogDefaultsToForm(form, catalogs);
    expect(next.blocks[0].paperSheetId).toBe("2");
    expect(next.blocks[0].operations[0].printerId).toBe("7");
    expect(next.blocks[0].operations[0].operatorId).toBe("3");
  });
});

describe("emptyCalculatorForm", () => {
  it("should return the default starting values from conventions", () => {
    const form = emptyCalculatorForm();
    expect(form.count).toBe("0");
    expect(form.description).toBe("");
    expect(form.additionalWorks).toEqual([]);
    expect(form.blocks).toHaveLength(1);
    const block = form.blocks[0];
    expect(block.count).toBe("0");
    expect(block.markup).toBe("0");
    expect(block.target).toEqual({ name: "", width: "0", height: "0" });
    expect(block.paperSheetId).toBe("");
    expect(block.paper).toEqual({
      name: "",
      density: "",
      thickness: "",
      price_per_kilo: "0",
    });
    expect(block.sheetFormat).toEqual({ name: "", width: "0", height: "0" });
    expect(block.bleeds).toBe("0");
    expect(block.spacing).toBe("0");
    expect(block.operations.map((op) => op.kind)).toEqual(["print", "cut"]);
    expect(typeof block.clientKey).toBe("string");
    expect(block.clientKey.length).toBeGreaterThan(0);
  });
});

describe("calculatorFormMissingFieldLabels", () => {
  it("should list order and block fields for the empty default form", () => {
    const missing = calculatorFormMissingFieldLabels(emptyCalculatorForm());
    expect(missing).toContain("Тираж");
    expect(missing).toContain("Листов");
    expect(missing).toContain("Ширина");
    expect(missing).toContain("Высота");
    expect(missing).toContain("Бумага");
    expect(missing).toContain("Печать: Цветность");
  });

  it("should be empty for a fully filled sample form", () => {
    expect(calculatorFormMissingFieldLabels(sampleForm())).toEqual([]);
  });
});

describe("isCalculatorFormReadyForQuote", () => {
  it("should be false for the empty default form", () => {
    expect(isCalculatorFormReadyForQuote(emptyCalculatorForm())).toBe(false);
  });

  it("should be true for a fully filled sample form", () => {
    expect(isCalculatorFormReadyForQuote(sampleForm())).toBe(true);
  });

  it("should be false when an additional work name is empty", () => {
    const form = {
      ...sampleForm(),
      additionalWorks: [
        {
          clientKey: "work-key",
          name: "",
          price: "10.00",
          description: "x",
          markup: "0",
        },
      ],
    };
    expect(isCalculatorFormReadyForQuote(form)).toBe(false);
  });
});

describe("toOrderWrite", () => {
  it("should map the sample form to OrderWriteDto without client keys", () => {
    expect(toOrderWrite(sampleForm())).toEqual(sampleWriteJson);
  });

  it("should map zeros and empty additional works", () => {
    const form = emptyCalculatorForm();
    expect(toOrderWrite(form)).toEqual({
      count: 0,
      description: "",
      product: {
        blocks: [
          {
            count: 0,
            markup: 0,
            imposition: {
              target: { name: "", width: 0, height: 0 },
              sheet_id: "",
              bleeds: 0,
              spacing: 0,
            },
            operations: [
              {
                kind: "print",
                printer_id: "",
                operator_id: "",
                chroma: "",
              },
              { kind: "cut", cutter_id: "", operator_id: "" },
            ],
          },
        ],
        operations: [],
      },
    });
  });

  it("should send an empty printer id as an empty string", () => {
    const form = emptyCalculatorForm();
    const printOp = form.blocks[0].operations.find((op) => op.kind === "print");
    printOp.printerId = "";
    const body = toOrderWrite(form);
    expect(body.product.blocks[0].operations[0].printer_id).toBe("");
  });
});

describe("toCalculatorForm", () => {
  it("should map OrderDto to string form fields and new client keys", () => {
    const order = { id: 99, created_at: "2026-06-15T12:00:00Z", ...sampleWriteJson };
    const form = toCalculatorForm(order);
    expect(form.count).toBe("10");
    expect(form.description).toBe("Визитки");
    expect(form.blocks[0].count).toBe("2");
    expect(form.blocks[0].markup).toBe("30");
    expect(form.blocks[0].target.width).toBe("90");
    expect(form.blocks[0].paperSheetId).toBe("1");
    expect(form.blocks[0].operations[0].printerId).toBe("1");
    expect(form.blocks[0].operations[0].chroma).toBe("FOUR_ZERO");
    expect(form.blocks[0].operations[1].filmId).toBe("2");
    expect(form.additionalWorks[0].price).toBe("10.00");
    expect(form.blocks[0].clientKey).toMatch(/\S/);
    expect(form.blocks[0].operations[0].clientKey).toMatch(/\S/);
    expect(form.additionalWorks[0].clientKey).toMatch(/\S/);
    expect(toOrderWrite(form)).toEqual(sampleWriteJson);
  });

  it("should throw when product has zero blocks", () => {
    expect(() =>
      toCalculatorForm({ id: 1, count: 1, product: { blocks: [], operations: [] } }),
    ).toThrow("order: product.blocks must not be empty");
  });
});

describe("toOrderReport", () => {
  it("should return report fields when prices and impositions are valid", () => {
    expect(
      toOrderReport({
        product_price: "12.5",
        order_price: "125",
        income: "50.00",
        impositions: [4, 2],
      }),
    ).toEqual({
      product_price: "12.5",
      order_price: "125",
      income: "50.00",
      impositions: [4, 2],
    });
  });

  it("should throw when a price field is missing", () => {
    expect(() =>
      toOrderReport({
        order_price: "1",
        income: "0",
        impositions: [],
      }),
    ).toThrow("order report: product_price");
  });
});

describe("formatOrderCreatedDate", () => {
  it("should format an ISO date for ru-RU locale", () => {
    expect(formatOrderCreatedDate("2026-06-15T12:00:00Z")).toBe("15.06.2026");
  });

  it("should throw when the string is not a valid date", () => {
    expect(() => formatOrderCreatedDate("not-a-date")).toThrow(
      "order: created_at is not a valid date",
    );
  });
});

describe("toOrderSummary", () => {
  it("should return id, count, description, and created_at", () => {
    expect(
      toOrderSummary({
        id: 3,
        count: 10,
        description: "Визитки",
        created_at: "2026-06-15T12:00:00Z",
      }),
    ).toEqual({
      id: 3,
      count: 10,
      description: "Визитки",
      created_at: "2026-06-15T12:00:00Z",
    });
  });

  it("should default description to an empty string", () => {
    expect(
      toOrderSummary({ id: 3, count: 10, created_at: "2026-06-15T12:00:00Z" }),
    ).toEqual({
      id: 3,
      count: 10,
      description: "",
      created_at: "2026-06-15T12:00:00Z",
    });
  });

  it("should throw when id is a string", () => {
    expect(() =>
      toOrderSummary({ id: "3", count: 10, created_at: "2026-06-15T12:00:00Z" }),
    ).toThrow("order: id must be a number");
  });

  it("should throw when created_at is missing", () => {
    expect(() => toOrderSummary({ id: 3, count: 10 })).toThrow(
      "order: created_at must be a non-empty string",
    );
  });
});
