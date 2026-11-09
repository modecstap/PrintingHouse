import { toReference, toReferenceList } from "./reference";

describe("toReference", () => {
  it("should return name, description, and order_id", () => {
    expect(toReference({ name: "r1", description: "d", order_id: 1 })).toEqual({
      name: "r1",
      description: "d",
      order_id: 1,
    });
  });

  it("should throw when order_id is a string", () => {
    expect(() =>
      toReference({ name: "r", description: "d", order_id: "1" })
    ).toThrow("reference: order_id must be a number");
  });

  it("should parse another valid reference row", () => {
    expect(
      toReference({ name: "Шаблон", description: "Визитки", order_id: 42 })
    ).toEqual({
      name: "Шаблон",
      description: "Визитки",
      order_id: 42,
    });
  });
});

describe("toReferenceList", () => {
  it("should map each element through toReference", () => {
    expect(
      toReferenceList([
        { name: "a", description: "b", order_id: 1 },
        { name: "Шаблон", description: "Визитки", order_id: 42 },
      ])
    ).toEqual([
      { name: "a", description: "b", order_id: 1 },
      { name: "Шаблон", description: "Визитки", order_id: 42 },
    ]);
  });
});
