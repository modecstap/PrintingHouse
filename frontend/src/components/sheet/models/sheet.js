export function toSheet(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("sheet: id must be a number");
  }
  if (typeof raw?.name !== "string") {
    throw new Error("sheet: name must be a string");
  }
  if (typeof raw?.height !== "number") {
    throw new Error("sheet: height must be a number");
  }
  if (typeof raw?.width !== "number") {
    throw new Error("sheet: width must be a number");
  }
  if (typeof raw?.density !== "number") {
    throw new Error("sheet: density must be a number");
  }
  if (typeof raw?.cost !== "string") {
    throw new Error("sheet: cost must be a string");
  }
  return {
    id: raw.id,
    name: raw.name,
    height: raw.height,
    width: raw.width,
    density: raw.density,
    cost: raw.cost,
  };
}

export function toSheetList(raw) {
  if (!Array.isArray(raw)) {
    throw new Error("sheet: list must be an array");
  }
  return raw.map(toSheet);
}

export function toSavedSheet(raw) {
  if (typeof raw?.id !== "number") {
    throw new Error("sheet: id must be a number");
  }
  return { id: raw.id };
}
