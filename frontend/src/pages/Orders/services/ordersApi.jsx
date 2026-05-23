import { BackendIP } from "../../../constants/BackendIP";

const handleResponse = async (res) => {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Ошибка: ${res.status}`);
  }
  return res;
};

export const fetchOrdersApi = async (signal) => {
  const res = await fetch(`${BackendIP}/api/order/`, { signal });
  await handleResponse(res);
  return res.json();
};

export const updateOrderStatusApi = async (orderId, status) => {
  const res = await fetch(`${BackendIP}/api/order/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      order_id: orderId,
      new_status: status,
    }),
  });

  await handleResponse(res);
};

export const deleteOrderApi = async (orderId) => {
  const res = await fetch(`${BackendIP}/api/order/${orderId}`, {
    method: "DELETE",
  });

  await handleResponse(res);
};

export const downloadInstructionApi = async (orderId) => {
  const res = await fetch(`${BackendIP}/api/instruction/${orderId}`);
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
