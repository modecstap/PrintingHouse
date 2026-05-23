import { useState, useEffect } from "react";
import { BackendIP } from "../../constants/BackendIP";

const useOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedItem, setSelectedItem] = useState(null);
  const [statusTarget, setStatusTarget] = useState(null);

  const fetchOrders = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${BackendIP}/api/order/`);
      if (!response.ok) {
        throw new Error("Ошибка получения данных.");
      }
      const data = await response.json();
      setOrders(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId, status) => {
    try {
      const res = await fetch(`${BackendIP}/api/order/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          order_id: orderId,
          new_status: status,
        }),
      });

      if (!res.ok) throw new Error(`Ошибка: ${res.status}`);

      // оптимистичное обновление
      setOrders((prev) =>
        prev.map((item) =>
          item.id === orderId ? { ...item, status } : item
        )
      );
    } catch (err) {
      console.error("Ошибка смены статуса:", err);
      alert("Не удалось сменить статус.");
    } finally {
      setStatusTarget(null);
    }
  };

  const handlePrintInstruction = async (orderId) => {
    try {
      const response = await fetch(
        `${BackendIP}/api/instruction/${orderId}`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error("Не удалось получить инструкцию");
      }

      const blob = await response.blob();

      const disposition = response.headers.get("Content-Disposition");
      let fileName = "instruction";

      if (disposition) {
        const match = disposition.match(/filename="?(.+)"?/);
        if (match?.[1]) {
          fileName = match[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Ошибка загрузки инструкции:", err);
      alert("Ошибка при загрузке инструкции");
    }
  };

  const handleDelete = async (orderId) => {
    if (!window.confirm("Удалить этот заказ?")) return;

    try {
      const res = await fetch(`${BackendIP}/api/order/${orderId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error(`Ошибка: ${res.status}`);

      // обновляем UI
      setOrders((prev) => prev.filter((item) => item.id !== orderId));
    } catch (err) {
      console.error("Ошибка удаления:", err);
      alert("Не удалось удалить заказ.");
    }
  };

  const openModal = (item, showActions = false) => {
    setSelectedItem({ ...item, showActions });
  };

  const closeModal = () => {
    setSelectedItem(null);
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  return {
    orders,
    loading,
    error,
    statusTarget,
    setStatusTarget,
    selectedItem,
    openModal,
    closeModal,
    handleStatusChange,
    handlePrintInstruction,
    handleDelete,
  };
};

export default useOrders;