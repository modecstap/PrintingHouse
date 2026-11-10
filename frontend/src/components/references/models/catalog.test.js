import { toJsonInt } from "./catalog";
import { toPrinter, toPrinterList, toSheet, toFilm } from "../../../lib/catalog-parsers";

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
      }),
    ).toEqual({
      id: 1,
      startup: "10",
      cyan: "1",
      magenta: "2",
      yellow: "3",
      black: "4",
    });
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
});

describe("toFilm", () => {
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

describe("toJsonInt", () => {
  it("should coerce a decimal integer string to a number", () => {
    expect(toJsonInt(" 42 ")).toBe(42);
  });

  it("should return trimmed string when not an integer pattern", () => {
    expect(toJsonInt("12.5")).toBe("12.5");
  });
});
