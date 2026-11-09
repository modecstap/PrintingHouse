export function toReference(raw) {
  if (typeof raw?.name !== "string") {
    throw new Error("reference: name must be a string");
  }
  if (typeof raw?.description !== "string") {
    throw new Error("reference: description must be a string");
  }
  if (typeof raw?.order_id !== "number") {
    throw new Error("reference: order_id must be a number");
  }
  return {
    name: raw.name,
    description: raw.description,
    order_id: raw.order_id,
  };
}

export function toReferenceList(raw) {
  if (!Array.isArray(raw)) {
    throw new Error("reference: list must be an array");
  }
  return raw.map(toReference);
}
