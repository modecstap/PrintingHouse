import { BackendIP } from "../../../constants/BackendIP";
import { toSavedSheet, toSheetList } from "../models/sheet";

function authHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function failureText(response) {
  const data = await response.json().catch(() => null);
  if (data?.detail) {
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item) => `${item.loc?.join(" → ")}: ${item.msg}`)
        .join("\n");
    }
    if (typeof data.detail === "string") return data.detail;
    return JSON.stringify(data.detail);
  }
  return `Ошибка сервера (${response.status})`;
}

function normalize(error) {
  if (error?.name === "AbortError") throw error;
  if (error?.name === "TypeError") {
    throw new Error("Не удалось подключиться к серверу. Проверьте соединение.");
  }
  if (error instanceof Error) throw error;
  throw new Error("Произошла неизвестная ошибка");
}

async function request(path, options) {
  try {
    const response = await fetch(`${BackendIP}${path}`, {
      ...options,
      headers: authHeaders(),
    });
    if (!response.ok) throw new Error(await failureText(response));
    return response;
  } catch (error) {
    normalize(error);
  }
}

export async function fetchSheets(signal) {
  const response = await request("/api/v2/sheet/", { method: "GET", signal });
  return toSheetList(await response.json());
}

export async function saveSheet(body) {
  const response = await request("/api/v2/sheet/", {
    method: "POST",
    body: JSON.stringify(body),
  });
  return toSavedSheet(await response.json());
}

export async function deleteSheet(id) {
  await request(`/api/v2/sheet/${id}`, { method: "DELETE" });
}
