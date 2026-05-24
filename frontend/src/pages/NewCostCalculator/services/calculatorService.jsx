import { BackendIP } from "../../../constants/BackendIP";

export const calculatorService = {
  async getProductionReference() {
    const res = await fetch(`${BackendIP}/api/reference/production`);
    return res.json();
  },

  async calculate(formData) {
    const res = await fetch(`${BackendIP}/api/order/cost_report`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json" },
    });

    return res.json();
  },

  async delay(formData) {
    await fetch(`${BackendIP}/api/order/delay`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json" },
    });
  },

  async accept(formData) {
    const res = await fetch(`${BackendIP}/api/order/accept`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json" },
    });

    return res;
  },
};