import React, { useState } from "react";
import VisibleForm from "./VisibleForm";
import ConsealedForm from "./ConsealedForm";
import CostReportView from "./CostReportView";
import AdvancedSection from "./AdvancedSection";
import "./CostCalculator.css";
import { BackendIP } from "../../constants/BackendIP";

export default function CostCalculatorPage() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [formData, setFormData] = useState({
    edition: {
      count: 0,
      density: 0,
      list_size: { width: 0, height: 0, bleeds: 0 },
      chroma: 1,
      lamination: 1,
      die_cutting: false,
    },
    production: {
      tax_rate: 0.93,
      markup: 80,
      black_ink_cost: 2,
      ink_cost: 15.6,
      lamination_cost: 12,
      die_cutting_cost: 100,
      paper_cost: 165,
      press_sheet: {
        height: 450,
        width: 320,
        spacing: 5,
      },
      cutter: {
        stack_height: 30,
      },
      sheet_by_fitting: 2,
      cutting_cost: 10,
      printer_salary: 2,
    },
  });

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /** универсальное обновление edition / production */
  const handleFormChange = (section, newValues) => {
    setFormData((prev) => ({
      ...prev,
      [section]: { ...prev[section], ...newValues },
    }));
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(BackendIP + "/api/costs_report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        if (data?.detail) {
          if (Array.isArray(data.detail)) {
            throw new Error(
              data.detail
                .map(
                  (d) =>
                    `${d.loc ? d.loc.join(" → ") + ": " : ""}${d.msg || d}`
                )
                .join("\n")
            );
          } else {
            throw new Error(
              typeof data.detail === "string"
                ? data.detail
                : JSON.stringify(data.detail)
            );
          }
        }
        throw new Error(`Ошибка сервера (${response.status})`);
      }

      setReport(data);
    } catch (err) {
      console.error(err);
      if (err.name === "TypeError") {
        setError("Не удалось подключиться к серверу. Проверьте соединение.");
      } else {
        setError(err.message || "Произошла неизвестная ошибка");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Расчёт стоимости</h1>

      <div className="block">
        <div className="advanced-content">
          {/* Видимая форма — изменяет edition и production */}
          <VisibleForm
            data={formData}
            onChange={handleFormChange}
          />

          <div className="button-row">
            <button
              className="btn btn-primary"
              onClick={handleCalculate}
              disabled={loading}
            >
              {loading ? "Вычисляем..." : "Рассчитать"}
            </button>

            <button
              className="btn btn-more"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? "Скрыть" : "Подробнее"}
            </button>
          </div>

          {error && (
            <div className="error-message">
              <h3>⚠️ Ошибка</h3>
              {error.split("\n").map((line, idx) => (
                <div key={idx}>{line}</div>
              ))}
            </div>
          )}
        </div>

        <AdvancedSection open={showAdvanced}>
          <div className="advanced-content">
            {/* Скрытая форма — тоже изменяет edition и production */}
            <ConsealedForm
              data={formData}
              onChange={handleFormChange}
            />
          </div>
        </AdvancedSection>
      </div>

      {report && (
        <div className="block">
          <h2 className="block-title">Результаты</h2>
          <CostReportView report={report} />
        </div>
      )}
    </div>
  );
}
