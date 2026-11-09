import { BackendIP } from "../constants/BackendIP";

function authHeaders(body) {
  const token = localStorage.getItem("access_token");
  const headers = {
    Authorization: `Bearer ${token ?? ""}`,
  };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

async function readFailureDetail(response) {
  const data = await response.json().catch(() => null);
  if (typeof data?.detail === "string") {
    return data.detail;
  }
  return `Ошибка сервера (${response.status})`;
}

export async function requestJson(path, { method = "GET", body, signal } = {}) {
  try {
    const response = await fetch(`${BackendIP}${path}`, {
      method,
      headers: authHeaders(body),
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    });

    if (response.ok) {
      if (response.status === 204) {
        return null;
      }
      return response.json();
    }

    throw new Error(await readFailureDetail(response));
  } catch (error) {
    if (error?.name === "AbortError") {
      throw error;
    }
    if (error?.name === "TypeError") {
      throw new Error("Не удалось подключиться к серверу. Проверьте соединение.");
    }
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Произошла неизвестная ошибка");
  }
}
