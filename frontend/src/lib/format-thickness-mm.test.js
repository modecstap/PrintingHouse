import { formatThicknessMm } from "./format-thickness-mm";

describe("formatThicknessMm", () => {
  it("should show up to two decimals and trim trailing zeros", () => {
    expect(formatThicknessMm(1)).toBe("1");
    expect(formatThicknessMm(0.15)).toBe("0.15");
    expect(formatThicknessMm(1.5)).toBe("1.5");
  });
});
