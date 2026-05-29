import { useState } from "react";
import { calculatorService } from "../services/calculatorService";
import { buildHiddenRows } from "../utils/reportBuilder";
import { formatPrice } from "../utils/formatters";

const formatError = (err) => {
  if (!err?.detail) {
    return [err?.message || "Неизвестная ошибка"];
  }

  return err.detail.map((e) => ({
    path: e.loc.join(" → "),
    message: e.msg,
  }));
};

export const useEdition = (formData) => {
  const UNIT_FIELDS = [
    {
      label: "Количество изделий",
      path: "unit_count",
      type: "number",
      valueParser: Number,
    },
    {
      label: "Комментарий",
      path: "comment",
      type: "text",
      valueParser: (v) => v,
    },
  ];

  const BASE_ROWS = [
    {
      label: "Цена изделия",
      value: (r) => formatPrice(r.unit_cost),
    },
    {
      label: "Себестоимость изделия",
      value: (r) => formatPrice(r.unit_cost_price),
    },
    {
      label: "Цена тиража",
      value: (r) => formatPrice(r.edition_cost),
    },
    {
      label: "Прибыль от тиража",
      value: (r) => formatPrice(r.profit_after_tax),
    },
  ];

  const [report, setReport] = useState(null);
  const [hiddenRows, setHiddenRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const calculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await calculatorService.calculate(formData);

      console.log(res);
      if (!res.ok) {
        const errData = await res.json();
        setError(formatError(errData));
        return;
      }

      const data = await res.json();

      setHiddenRows(buildHiddenRows(data));
      setReport(data);
    } catch (e) {
      setError("Ошибка сети или сервера");
    } finally {
      setLoading(false);
    }
  };

  const delay = async () => {
    try {
      const res = await calculatorService.delay(formData);

      if (!res.ok) {
        const errData = await res.json();
        setError(formatError(errData));
      }
    } catch {
      setError("Ошибка сети или сервера");
    }
  };

  const accept = async () => {
    try {
      const res = await calculatorService.accept(formData);

      if (!res.ok) {
        const errData = await res.json();
        setError(formatError(errData));
        return;
      }

      const blob = await res.blob();
      return blob;
    } catch {
      setError("Ошибка сети или сервера");
    }
  };

  return {
    UNIT_FIELDS,
    BASE_ROWS,
    report,
    hiddenRows,
    loading,
    error,
    calculate,
    delay,
    accept,
  };
};