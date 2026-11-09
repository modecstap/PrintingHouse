import {
  toFilm,
  toJsonInt,
  toPrinter,
  toPrinterList,
  toSheet,
} from "./catalog";

describe("toPrinter", () => {
  it("should return id and money fields", () => {
    expect(
      toPrinter({
        id: 1,
        startup: "10",
        cyan: "1",
        magenta: "2",
        yellow: "3",
        black: "4",
      })
    ).toEqual({
      id: 1,
      startup: "10",
      cyan: "1",
      magenta: "2",
      yellow: "3",
      black: "4",
    });
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
      })
    ).toThrow("printer: id must be a number");
  });
});

describe("toSheet", () => {
  it("should return paper and format", () => {
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
      })
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
      })
    ).toThrow("sheet: format.name must be a string");
  });
});

describe("toFilm", () => {
  it("should return id, name, price, and density", () => {
    expect(
      toFilm({ id: 3, name: "Глянец", price: "50", density: 75 })
    ).toEqual({
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

describe("toJsonInt", () => {
  it("should coerce a decimal integer string to a number", () => {
    expect(toJsonInt(" 42 ")).toBe(42);
  });

  it("should return trimmed string when not an integer pattern", () => {
    expect(toJsonInt("12.5")).toBe("12.5");
  });
});
