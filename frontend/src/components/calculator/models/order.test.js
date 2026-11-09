import {
  emptyCalculatorForm,
  toOrderWrite,
  toCalculatorForm,
  toOrderReport,
  toOrderSummary,
} from "./order";

const sampleWriteJson = {
  count: 10,
  product: {
    blocks: [
      {
        count: 2,
        markup: 30,
        imposition: {
          target: { name: "", width: 90, height: 50 },
          press_sheet: {
            paper: {
              name: "Мелованная",
              density: 150,
              thickness: 1,
              price_per_kilo: "80.50",
            },
            format: { name: "SRA3", width: 320, height: 450 },
          },
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
            film: { name: "Глянец", price: "3.00", density: 25 },
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
    blocks: [
      {
        clientKey: "block-key",
        count: "2",
        markup: "30",
        target: { name: "Визитка", width: "90", height: "50" },
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

describe("emptyCalculatorForm", () => {
  it("should return the default starting values from conventions", () => {
    const form = emptyCalculatorForm();
    expect(form.count).toBe("0");
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
    expect(block.operations).toEqual([]);
    expect(typeof block.clientKey).toBe("string");
    expect(block.clientKey.length).toBeGreaterThan(0);
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
      product: {
        blocks: [
          {
            count: 0,
            markup: 0,
            imposition: {
              target: { name: "", width: 0, height: 0 },
              press_sheet: {
                paper: {
                  name: "",
                  density: "",
                  thickness: "",
                  price_per_kilo: "0",
                },
                format: { name: "", width: 0, height: 0 },
              },
              bleeds: 0,
              spacing: 0,
            },
            operations: [],
          },
        ],
        operations: [],
      },
    });
  });

  it("should send an empty printer id as an empty string", () => {
    const form = emptyCalculatorForm();
    form.blocks[0].operations.push({
      clientKey: "p",
      kind: "print",
      printerId: "",
      operatorId: "",
      chroma: "ZERO_ZERO",
    });
    const body = toOrderWrite(form);
    expect(body.product.blocks[0].operations[0].printer_id).toBe("");
  });
});

describe("toCalculatorForm", () => {
  it("should map OrderDto to string form fields and new client keys", () => {
    const order = { id: 99, ...sampleWriteJson };
    const form = toCalculatorForm(order);
    expect(form.count).toBe("10");
    expect(form.blocks[0].count).toBe("2");
    expect(form.blocks[0].markup).toBe("30");
    expect(form.blocks[0].target.width).toBe("90");
    expect(form.blocks[0].paper.price_per_kilo).toBe("80.50");
    expect(form.blocks[0].operations[0].printerId).toBe("1");
    expect(form.blocks[0].operations[0].chroma).toBe("FOUR_ZERO");
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

describe("toOrderSummary", () => {
  it("should return id and count only", () => {
    expect(toOrderSummary({ id: 3, count: 10 })).toEqual({ id: 3, count: 10 });
  });

  it("should throw when id is a string", () => {
    expect(() => toOrderSummary({ id: "3", count: 10 })).toThrow(
      "order: id must be a number",
    );
  });
});
