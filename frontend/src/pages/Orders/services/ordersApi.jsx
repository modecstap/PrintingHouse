import { BackendIP } from "../../../constants/BackendIP";

const handleResponse = async (res) => {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Ошибка: ${res.status}`);
  }
  return res;
};

export const fetchOrdersApi = async (signal) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/order/`, { signal, headers: token ? { Authorization: `Bearer ${token}` } : {} });
  await handleResponse(res);
  return res.json();
};

export const updateOrderStatusApi = async (orderId, status) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/order/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: JSON.stringify({
      order_id: orderId,
      new_status: status,
    }),
  });

  await handleResponse(res);
};

export const deleteOrderApi = async (orderId) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/order/${orderId}`, {
    method: "DELETE",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  await handleResponse(res);
};

export const downloadInstructionApi = async (orderId) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${BackendIP}/api/instruction/${orderId}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  await handleResponse(res);

  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition");

  let fileName = "instruction";

  if (disposition) {
    const match = disposition.match(/filename="?(.+)"?/);
    if (match?.[1]) fileName = match[1];
  }

  return { blob, fileName };
};
