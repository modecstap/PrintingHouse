import { useState, useEffect, useCallback } from "react";
import {
  fetchOrdersApi,
  updateOrderStatusApi,
  deleteOrderApi,
  downloadInstructionApi,
} from "../services/ordersApi";

export const useOrdersData = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async (signal) => {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchOrdersApi(signal);
      setOrders(data);
    } catch (e) {
      if (e.name !== "AbortError") {
        setError(e.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const updateStatus = async (id, status) => {
    const prev = orders;

    setOrders((o) =>
      o.map((item) => (item.id === id ? { ...item, status } : item))
    );

    try {
      await updateOrderStatusApi(id, status);
    } catch (e) {
      setOrders(prev);
      throw e;
    }
  };

  const remove = async (id) => {
    const prev = orders;

    setOrders((o) => o.filter((item) => item.id !== id));

    try {
      await deleteOrderApi(id);
    } catch (e) {
      setOrders(prev);
      throw e;
    }
  };

  const downloadInstruction = async (id) => {
    return downloadInstructionApi(id);
  };

  useEffect(() => {
    const controller = new AbortController();

    load(controller.signal);

    return () => controller.abort();
  }, [load]);

  return {
    orders,
    loading,
    error,
    reload: load,
    updateStatus,
    remove,
    downloadInstruction,
  };
};
