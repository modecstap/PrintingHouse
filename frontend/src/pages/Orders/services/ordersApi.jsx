import { BackendIP } from "../../../constants/BackendIP";
import { toCalculatorForm } from "../../../lib/workplaceOrder";

const handleResponse = async (res) => {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Ошибка: ${res.status}`);
  }
  return res;
};

export const fetchOrdersApi = async (signal) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/v2/order/`, {
    signal,
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  await handleResponse(res);
  const orders = await res.json();
  return orders.map(toCalculatorForm);
};

export const updateOrderStatusApi = async (orderId, status) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/v2/order/status`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      order_id: orderId,
      new_status: status,
    }),
  });

  await handleResponse(res);
};

export const deleteOrderApi = async (orderId) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/v2/order/${orderId}`, {
    method: "DELETE",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  await handleResponse(res);
};
