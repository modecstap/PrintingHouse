import { BackendIP } from "../../../constants/BackendIP";

export const calculatorService = {
  async getProductionReference() {
    const res = await fetch(`${BackendIP}/api/reference/production`);
    return res;
  },

  async calculate(formData) {
    const res = await fetch(`${BackendIP}/api/order/cost_report`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json" },
    });

    return res;
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

  async update(formData) {
    const res = await fetch(`${BackendIP}/api/order/${formData.id}`, {
      method: "PUT",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json" },
    });

    return res;
  },
};