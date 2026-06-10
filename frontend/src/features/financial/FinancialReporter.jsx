import React, { useState } from "react";
import "../cost-calculator/CostCalculator.css";
import FlexForm from "../cost-calculator/components/FlexForm";

const VisibleFields = [
  {
    label: "Начальная дата",
    path: "start",
    type: "datetime-local",
  },
  {
    label: "Конечная дата",
    path: "end",
    type: "datetime-local",
  },
];

export default function FinantialReporter() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    start: "2026-01-15T00:00",
    end: "2026-01-16T00:00",
  });

  const handleDownloadPdf = async () => {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams({
        start: new Date(formData.start).toISOString(),
        end: new Date(formData.end).toISOString(),
      });

      const response = await fetch(
        `http://localhost:8080/api/financial/?${params.toString()}`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const blob = await response.blob();

      const fileURL = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = fileURL;
      link.download = `financial_report.pdf`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(fileURL);
    } catch (err) {
      setError(err.message || "Ошибка загрузки файла");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Финансовый отчёт</h1>

      <div className="block">
        <FlexForm
          fields={VisibleFields}
          formData={formData}
          setFormData={setFormData}
        />

        <div className="button-row">
          <button
            className="btn btn-accent"
            onClick={handleDownloadPdf}
            disabled={loading}
          >
            {loading ? "Загрузка..." : "Скачать PDF"}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <h3>⚠️ Ошибка</h3>
            <div>{error}</div>
          </div>
        )}
      </div>
    </div>
  );
}