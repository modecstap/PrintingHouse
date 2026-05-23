import { useState } from "react";
import { BackendIP } from "../../../constants/BackendIP";

export const useAsyncAction = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const execute = async (
    endpoint,
    body,
    {
      method = "POST", 
      isBlob = false,
    } = {}
  ) => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const options = {
        method,
        headers: {
          "Content-Type": "application/json",
        },
      };

      if (body !== undefined && method !== "GET" && method !== "HEAD") {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(`${BackendIP}${endpoint}`, options);

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        const message =
          data?.detail
            ? Array.isArray(data.detail)
              ? data.detail
                  .map((d) => `${d.loc?.join(" → ")}: ${d.msg}`)
                  .join("\n")
              : typeof data.detail === "string"
              ? data.detail
              : JSON.stringify(data.detail)
            : `Ошибка сервера (${response.status})`;
        throw new Error(message);
      }

      const result = isBlob
        ? await response.blob()
        : await response.json().catch(() => null);

      if (!isBlob && method !== "GET") {
        setSuccessMsg("✅ Успешно отправлено");
      }

      return result;
    } catch (err) {
      console.error(err);
      setError(
        err.name === "TypeError"
          ? "Не удалось подключиться к серверу. Проверьте соединение."
          : err.message || "Произошла неизвестная ошибка"
      );
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, successMsg, execute };
};
