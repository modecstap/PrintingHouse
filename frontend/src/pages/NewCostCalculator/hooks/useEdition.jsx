import { useState } from "react";
import { calculatorService } from "../services/calculatorService";
import { buildHiddenRows } from "../utils/reportBuilder";
import { formatPrice } from "../utils/formatters";

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
      valueParser: Number,
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

  const calculate = async () => {
    setLoading(true);
    const data = await calculatorService.calculate(formData);
    setLoading(false);

    if (!data) return;

    setHiddenRows(buildHiddenRows(data));
    setReport(data);
  };

  const delay = () => calculatorService.delay(formData);

  const accept = async () => {
    const res = await calculatorService.accept(formData);
    if (!res.ok) return;

    const blob = await res.blob();
    return blob;
  };

  return {
    UNIT_FIELDS,
    BASE_ROWS,
    report,
    hiddenRows,
    loading,
    calculate,
    delay,
    accept,
  };
};