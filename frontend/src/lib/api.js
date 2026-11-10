import { BackendIP } from "../constants/BackendIP";

let unauthorizedHandler = null;

export function setUnauthorizedHandler(fn) {
  unauthorizedHandler = fn;
}

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

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc?.join(" → ")}: ${d.msg}`).join("\n");
  }
  if (typeof detail === "string") {
    return detail;
  }
  return JSON.stringify(detail);
}

async function readFailureDetail(response) {
  const data = await response.json().catch(() => null);
  if (data?.detail !== undefined && data?.detail !== null) {
    return formatDetail(data.detail);
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

    if (response.status === 401) {
      localStorage.removeItem("access_token");
      unauthorizedHandler?.();
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
