import { BackendIP } from "../../../constants/BackendIP";
import { toWorkplaceOrder } from "../../../lib/workplaceOrder";

function jsonHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function postOrder(path, formData) {
  return fetch(`${BackendIP}${path}`, {
    method: "POST",
    body: JSON.stringify(toWorkplaceOrder(formData)),
    headers: jsonHeaders(),
  });
}

export const calculatorService = {
  async getProductionReference(signal) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${BackendIP}/api/v2/reference/`, {
      signal,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    return res;
  },

  calculate(formData) {
    return postOrder("/api/v2/order/cost_report", formData);
  },

  delay(formData) {
    return postOrder("/api/v2/order/delay", formData);
  },

  accept(formData) {
    return postOrder("/api/v2/order/accept", formData);
  },

  update(formData) {
    return postOrder("/api/v2/order/", formData);
  },
};
