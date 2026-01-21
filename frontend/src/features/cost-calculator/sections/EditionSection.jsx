import { useState } from "react";
import { BackendIP } from "../../../constants/BackendIP";
import FlexForm from "../components/FlexForm";
import { useAsyncAction } from "../hooks/useAsyncAction";
import ReportSection from "./ReportSection";


const formatPrice = (value) =>
  value == null ? "—" : `${Number(value).toFixed(2)} ₽`;


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

const PRINTING_COST_HIDDEN_TEMPLATE = (index) => [
  {
    label: `Цена изделия`,
    value: (r) => formatPrice(r.printing_cost_reports[index].unit_cost),
  },
  {
    label: `Цена тиража`,
    value: (r) =>
      formatPrice(r.printing_cost_reports[index].edition_cost),
  },
  {
    label: `Кол-во изделий на листе`,
    value: (r) => r.printing_cost_reports[index].items_per_sheet,
  },
  {
    label: `Кол-во печатных листов`,
    value: (r) => r.printing_cost_reports[index].sheet_count,
  },
  {
    label: `Себестоимость изделия`,
    value: (r) => formatPrice(r.printing_cost_reports[index].unit_cost_price),
  },
  {
    label: `Прибыль до налога`,
    value: (r) =>
      formatPrice(r.printing_cost_reports[index].profit_before_tax),
  },
  {
    label: `Прибыль после налога`,
    value: (r) =>
      formatPrice(r.printing_cost_reports[index].profit_after_tax),
  },
];

export default function EditionSection({
  formData,
  setFormData,
  hideActionButtons,
}) {
  const { loading, error, successMsg, execute } = useAsyncAction();
  const [report, setReport] = useState(null);
  const [hiddenRows, setHiddenRows] = useState([]);

  const buildHiddenRows = (data) => {
    if (!Array.isArray(data.printing_cost_reports)) {
      return [];
    }

    return data.printing_cost_reports.flatMap((_, index) => [
      {
        label: `Печать №${index + 1}`,
        isGroup: true,
      },
      ...PRINTING_COST_HIDDEN_TEMPLATE(index),
    ]);
  };

  const handleCalculate = async () => {
    const data = await execute(`/api/order/cost_report`, formData);

    if (!data) return;

    setHiddenRows(buildHiddenRows(data));
    setReport(data);
  };

  const handleDelay = async () => {
    await execute(`/api/order/delay`, formData);
  };

  const handleAccept = async () => {
    const response = await fetch(`${BackendIP}/api/order/accept`, {
      method: "POST",
      body: JSON.stringify(formData),
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) return;

    const blob = await response.blob();

    const disposition = response.headers.get("Content-Disposition");
    let fileName = "file";

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
  };

  return (
    <section className="calculator-container">
      <h2>Тираж</h2>

      <FlexForm
        fields={UNIT_FIELDS}
        formData={formData}
        setFormData={setFormData}
      />

      {error && (
        <div className="error-message">
          <h3>⚠️ Ошибка</h3>
          {error.split("\n").map((line, idx) => (
            <div key={idx}>{line}</div>
          ))}
        </div>
      )}

      <div className="button-row">
        <button
          className="btn btn-accent"
          onClick={handleCalculate}
          disabled={loading}
        >
          {loading ? "Вычисляем..." : "Рассчитать"}
        </button>

        {!hideActionButtons && (
          <>
            <button
              className="btn btn-primary"
              onClick={handleDelay}
              disabled={loading}
            >
              Отложить
            </button>

            <button
              className="btn btn-primary"
              onClick={handleAccept}
              disabled={loading}
            >
              В работу
            </button>
          </>
        )}
      </div>

      {report && (
        <ReportSection
          report={report}
          base_rows={BASE_ROWS}
          detail_rows={hiddenRows}
        />
      )}
    </section>
  );
}
