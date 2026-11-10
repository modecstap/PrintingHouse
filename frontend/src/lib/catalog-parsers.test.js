import {
  toPrinter,
  toLaminator,
  toCutter,
  toOperator,
  toSheet,
  toFilm,
  toPrinterList,
} from "./catalog-parsers";

describe("toPrinter", () => {
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

  it("should throw when id is not a number", () => {
    expect(() =>
      toPrinter({
        id: "1",
        startup: "10",
        cyan: "1",
        magenta: "2",
        yellow: "3",
        black: "4",
      }),
    ).toThrow("printer: id must be a number");
  });
});

describe("toLaminator", () => {
  it("should parse a laminator", () => {
    expect(toLaminator({ id: 2, startup: "5" })).toEqual({ id: 2, startup: "5" });
  });
});

describe("toCutter", () => {
  it("should parse a cutter", () => {
    expect(toCutter({ id: 8, max_stack: 40 })).toEqual({ id: 8, max_stack: 40 });
  });
});

describe("toOperator", () => {
  it("should parse an operator", () => {
    expect(toOperator({ id: 4, salary_by_operation: "5" })).toEqual({
      id: 4,
      salary_by_operation: "5",
    });
  });
});

describe("toSheet", () => {
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
      format: { name: "SRA3", height: 450, width: 320 },
    });
  });

  it("should return paper and format with height before width in object", () => {
    expect(
      toSheet({
        id: 2,
        paper: {
          name: "Мелованная",
          density: 300,
          thickness: 1,
          price_per_kilo: "120.50",
        },
        format: {
          name: "A4",
          height: 297,
          width: 210,
        },
      }),
    ).toEqual({
      id: 2,
      paper: {
        name: "Мелованная",
        density: 300,
        thickness: 1,
        price_per_kilo: "120.50",
      },
      format: {
        name: "A4",
        height: 297,
        width: 210,
      },
    });
  });

  it("should throw when format.name is missing", () => {
    expect(() =>
      toSheet({
        id: 1,
        paper: {
          name: "X",
          density: 1,
          thickness: 1,
          price_per_kilo: "1",
        },
        format: { height: 1, width: 1 },
      }),
    ).toThrow("sheet: format.name must be a string");
  });
});

describe("toFilm", () => {
  it("should parse a film", () => {
    expect(toFilm({ id: 2, name: "Глянец", price: "3", density: 25 })).toEqual({
      id: 2,
      name: "Глянец",
      price: "3",
      density: 25,
    });
  });

  it("should return id, name, price, and density", () => {
    expect(toFilm({ id: 3, name: "Глянец", price: "50", density: 75 })).toEqual({
      id: 3,
      name: "Глянец",
      price: "50",
      density: 75,
    });
  });
});

describe("toPrinterList", () => {
  it("should throw when payload is not an array", () => {
    expect(() => toPrinterList({})).toThrow("printer: list must be an array");
  });
});
