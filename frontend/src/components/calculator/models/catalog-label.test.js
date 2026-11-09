import {
  toPrinter,
  toLaminator,
  toCutter,
  toOperator,
  printerLabel,
  laminatorLabel,
  cutterLabel,
  operatorLabel,
  toSheet,
  filmLabel,
  sheetLabel,
  toFilm,
} from "./catalog-label";

describe("catalog parsers", () => {
  it("should parse a printer with money strings", () => {
    expect(
      toPrinter({
        id: 1,
        startup: "10",
        cyan: "0.1",
        magenta: "0.2",
        yellow: "0.3",
        black: "0.4",
      }),
    ).toEqual({
      id: 1,
      startup: "10",
      cyan: "0.1",
      magenta: "0.2",
      yellow: "0.3",
      black: "0.4",
    });
  });

  it("should throw when printer id is not a number", () => {
    expect(() => toPrinter({ id: "1", startup: "10" })).toThrow(
      "printer: id must be a number",
    );
  });

  it("should parse a laminator", () => {
    expect(toLaminator({ id: 2, startup: "5" })).toEqual({ id: 2, startup: "5" });
  });

  it("should parse a cutter", () => {
    expect(toCutter({ id: 8, max_stack: 40 })).toEqual({ id: 8, max_stack: 40 });
  });

  it("should parse an operator", () => {
    expect(toOperator({ id: 4, salary_by_operation: "5" })).toEqual({
      id: 4,
      salary_by_operation: "5",
    });
  });

  it("should parse a sheet with paper and format", () => {
    expect(
      toSheet({
        id: 2,
        paper: {
          name: "Мелованная",
          density: 150,
          thickness: 1,
          price_per_kilo: "80.50",
        },
        format: { name: "SRA3", width: 320, height: 450 },
      }),
    ).toEqual({
      id: 2,
      paper: {
        name: "Мелованная",
        density: 150,
        thickness: 1,
        price_per_kilo: "80.50",
      },
      format: { name: "SRA3", width: 320, height: 450 },
    });
  });
});

describe("catalog labels", () => {
  it("should format printer label with money", () => {
    const printer = {
      id: 3,
      startup: "10",
      cyan: "0.1",
      magenta: "0.2",
      yellow: "0.3",
      black: "0.4",
    };
    expect(printerLabel(printer)).toBe(
      "№ 3, запуск 10.00 ₽, C 0.10 ₽, M 0.20 ₽, Y 0.30 ₽, K 0.40 ₽",
    );
  });

  it("should format operator label with money", () => {
    expect(operatorLabel({ id: 4, salary_by_operation: "5" })).toBe(
      "№ 4, зарплата 5.00 ₽",
    );
  });

  it("should format laminator label with money", () => {
    expect(laminatorLabel({ id: 2, startup: "5" })).toBe("№ 2, запуск 5.00 ₽");
  });

  it("should format cutter label without money on max stack", () => {
    expect(cutterLabel({ id: 8, max_stack: 40 })).toBe("№ 8, макс. стопа 40");
  });

  it("should format sheet label with paper properties", () => {
    expect(
      sheetLabel({
        id: 1,
        paper: {
          name: "Офсет",
          density: 80,
          thickness: 1,
          price_per_kilo: "50",
        },
      }),
    ).toBe("Офсет, 80 г/м², 1 мм, 50.00 ₽/кг");
  });

  it("should parse a film and format its label", () => {
    expect(toFilm({ id: 2, name: "Глянец", price: "3", density: 25 })).toEqual({
      id: 2,
      name: "Глянец",
      price: "3",
      density: 25,
    });
    expect(filmLabel({ name: "Глянец", price: "3", density: 25 })).toBe(
      "Глянец, 3.00 ₽, плотность 25",
    );
  });
});
