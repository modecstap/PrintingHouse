import { useState } from "react";
import { BackendIP } from "../../../constants/BackendIP";

export const useAsyncAction = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const execute = async (endpoint, body, { isBlob = false } = {}) => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const response = await fetch(`${BackendIP}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        const message =
          data?.detail
            ? Array.isArray(data.detail)
              ? data.detail.map((d) => `${d.loc?.join(" → ")}: ${d.msg}`).join("\n")
              : typeof data.detail === "string"
              ? data.detail
              : JSON.stringify(data.detail)
            : `Ошибка сервера (${response.status})`;
        throw new Error(message);
      }

      const result = isBlob ? await response.blob() : await response.json().catch(() => null);
      if (!isBlob) setSuccessMsg("✅ Успешно отправлено");
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
