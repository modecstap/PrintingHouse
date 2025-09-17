import React, { useState } from "react";
import EditionForm from "./EditionForm";
import ProductionForm from "./ProductionForm";
import CostReportView from "./CostReportView";
import AdvancedSection from "./AdvancedSection";
import "./CostCalculator.css";
import { BackendIP } from "../../constants/BackendIP";
import ConcealedParameters from "./ConcealedParameters";

export default function CostCalculatorPage() {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [edition, setEdition] = useState({
    count: 0,
    density: 0,
    list_size: { width: 0, height: 0, bleeds: 0 },
    chroma: 1,        // дефолт select
    lamination: 1,    // дефолт select
    die_cutting: false,
    markup: 0,
  });
  const [production, setProduction] = useState({});
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(BackendIP + "/api/costs_report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ edition, production }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Расчёт стоимости</h1>

      <div className="block">
        <div className="advanced-content">
          <EditionForm edition={edition} onChange={setEdition} />

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

          {error && <div className="error-message">{error}</div>}
        </div>

        <AdvancedSection open={showAdvanced}>
          <div className="advanced-content">
            <ConcealedParameters edition={edition} onChange={setEdition} />
            <ProductionForm onChange={setProduction} />
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
