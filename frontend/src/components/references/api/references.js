import { requestJson } from "../../../lib/api";
import { toReferenceList } from "../models/reference";

export async function fetchReferences(signal) {
  const data = await requestJson("/api/references", { signal });
  return toReferenceList(data);
}

export async function saveReference({ name, description, order_id }) {
  const trimmedId = typeof order_id === "string" ? order_id.trim() : order_id;
  const payloadId =
    typeof trimmedId === "string" && /^-?\d+$/.test(trimmedId)
      ? Number(trimmedId)
      : trimmedId;

  await requestJson("/api/references", {
    method: "POST",
    body: { name, description, order_id: payloadId },
  });
}
