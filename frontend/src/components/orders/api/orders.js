import { requestJson } from "../../../lib/api";
import {
  toCalculatorForm,
  toOrderReport,
  toOrderSummary,
} from "../../calculator/models/order";

export async function fetchOrderSummaries(signal) {
  const data = await requestJson("/api/orders", { signal });
  return data.map(toOrderSummary);
}

export async function fetchOrderForm(id, signal) {
  const data = await requestJson(`/api/orders/${id}`, { signal });
  return toCalculatorForm(data);
}

export async function fetchOrderReport(id, signal) {
  const data = await requestJson(`/api/orders/${id}/report`, { signal });
  return toOrderReport(data);
}
