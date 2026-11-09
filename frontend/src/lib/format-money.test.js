import { formatMoney } from "./format-money";

describe("formatMoney", () => {
  it("should show two decimals and ruble for a fractional string", () => {
    expect(formatMoney("10.5")).toBe("10.50 ₽");
  });

  it("should show two decimals when there is no fraction", () => {
    expect(formatMoney("2")).toBe("2.00 ₽");
  });

  it("should round half up away from zero on the third decimal digit", () => {
    expect(formatMoney("-1.235")).toBe("-1.24 ₽");
  });

  it("should show em dash for null", () => {
    expect(formatMoney(null)).toBe("—");
  });

  it("should show em dash for empty string", () => {
    expect(formatMoney("")).toBe("—");
  });
});
