import {
  printerLabel,
  laminatorLabel,
  cutterLabel,
  operatorLabel,
  filmLabel,
  sheetLabel,
} from "./catalog-label";

describe("catalog labels", () => {
  it("should format printer label", () => {
    const printer = {
      id: 3,
      startup: "10",
      cyan: "0.1",
      magenta: "0.2",
      yellow: "0.3",
      black: "0.4",
    };
    expect(printerLabel(printer)).toBe("№ 3");
  });

  it("should format operator label with money", () => {
    expect(operatorLabel({ id: 4, salary_by_operation: "5" })).toBe(
      "№ 4, 5.00 ₽",
    );
  });

  it("should format laminator label", () => {
    expect(laminatorLabel({ id: 2, startup: "5" })).toBe("№ 2");
  });

  it("should format cutter label", () => {
    expect(cutterLabel({ id: 8, max_stack: 40 })).toBe("№ 8");
  });

  it("should format sheet label with format name", () => {
    expect(
      sheetLabel({
        id: 1,
        paper: {
          name: "офисная",
          density: 60,
          thickness: 1,
          price_per_kilo: "50",
        },
        format: { name: "А3", width: 297, height: 420 },
      }),
    ).toBe("офисная - 60 - А3");
  });

  it("should format sheet label with width x height when format name is empty", () => {
    expect(
      sheetLabel({
        id: 2,
        paper: {
          name: "офисная",
          density: 120,
          thickness: 1,
          price_per_kilo: "50",
        },
        format: { name: "", width: 470, height: 360 },
      }),
    ).toBe("офисная - 120 - 470x360");
  });

  it("should format film label", () => {
    expect(filmLabel({ name: "Глянец", price: "3", density: 25 })).toBe(
      "Глянец, 3.00 ₽, плотность 25",
    );
  });
});
