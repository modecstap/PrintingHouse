import { requestJson } from "../../../lib/api";
import { toOrderReport, toOrderWrite } from "../models/order";

export async function quoteOrder(form, signal) {
  const raw = await requestJson("/api/orders/quote", {
    method: "POST",
    body: toOrderWrite(form),
    signal,
  });
  return toOrderReport(raw);
}

export async function saveOrder(form) {
  const raw = await requestJson("/api/orders", {
    method: "POST",
    body: toOrderWrite(form),
  });
  if (typeof raw?.id !== "number") {
    throw new Error("order save: id must be a number");
  }
  return raw.id;
}

export async function replaceOrder(orderId, form) {
  const raw = await requestJson(`/api/orders/${orderId}`, {
    method: "PUT",
    body: toOrderWrite(form),
  });
  if (typeof raw?.id !== "number") {
    throw new Error("order replace: id must be a number");
  }
  return raw.id;
}
