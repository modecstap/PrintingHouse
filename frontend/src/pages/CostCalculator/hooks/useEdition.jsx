import { useState } from "react";
import { calculatorService } from "../services/calculatorService";
import { buildHiddenRows } from "../utils/reportBuilder";
import { formatPrice } from "../utils/formatters";

const formatError = (err) => {
  const detail = err?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail.map((e) => ({
      path: e.loc.join(" → "),
      message: e.msg,
    }));
  }

  return err?.message || "Неизвестная ошибка";
};

const readError = async (res) => {
  const text = await res.text();
  if (!text) return "Неизвестная ошибка";

  try {
    return formatError(JSON.parse(text));
  } catch {
    return text;
  }
};

export const useEdition = (formData, setFormData) => {
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
        setError(await readError(res));
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
    setError(null);

    try {
      const res = await calculatorService.delay(formData);

      if (!res.ok) {
        setError(await readError(res));
        return;
      }

      const data = await res.json();
      setFormData((prev) => ({ ...prev, id: data.id }));
    } catch {
      setError("Ошибка сети или сервера");
    }
  };

  const accept = async () => {
    setError(null);

    try {
      const res = await calculatorService.accept(formData);

      if (!res.ok) {
        setError(await readError(res));
        return;
      }

      const data = await res.json();
      setFormData((prev) => ({ ...prev, id: data.id }));
      setHiddenRows(buildHiddenRows(data.cost_report));
      setReport(data.cost_report);
    } catch {
      setError("Ошибка сети или сервера");
    }
  };

  const update = async () => {
    setError(null);

    try {
      const res = await calculatorService.update(formData);

      if (!res.ok) {
        setError(await readError(res));
      }
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
    update,
  };
};