import { BackendIP } from "../../../constants/BackendIP";

export const calculatorService = {
  async getProductionReference() {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${BackendIP}/api/reference/production`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
    return res;
  },

  async calculate(formData) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${BackendIP}/api/order/cost_report`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    });

    return res;
  },

  async delay(formData) {
    const token = localStorage.getItem("access_token");
    await fetch(`${BackendIP}/api/order/delay`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    });
  },

  async accept(formData) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${BackendIP}/api/order/accept`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    });

    return res;
  },

  async update(formData) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${BackendIP}/api/order/${formData.id}`, {
      method: "PUT",
      body: JSON.stringify(formData),
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    });

    return res;
  },
};