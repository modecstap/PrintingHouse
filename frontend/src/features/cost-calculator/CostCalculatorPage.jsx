import React, { useState } from "react";
import VisibleForm from "./VisibleForm";
import ConsealedForm from "./ConsealedForm";
import CostReportView from "./CostReportView";
import AdvancedSection from "./AdvancedSection";
import "./CostCalculator.css";
import { BackendIP } from "../../constants/BackendIP";

const defaultEdition = {
  count: 0,
  density: 0,
  list_size: { width: 0, height: 0, bleeds: 0 },
  chroma: 1,
  lamination: 1,
  die_cutting: false,
};

const defaultProduction = {
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
};

export default function CostCalculatorPage({ edition = {}, production = {} }) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [actionType, setActionType] = useState(null); // "delay" | "accept"
  const [comment, setComment] = useState("");

  const [formData, setFormData] = useState({
    edition: { ...defaultEdition, ...edition },
    production: { ...defaultProduction, ...production },
  });

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  /** Скачивание PDF-инструкции */
  const downloadInstruction = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${BackendIP}/api/order/accept`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          comment,
          edition: formData.edition,
          production: formData.production,
        }),
      });

      if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

      const blob = await response.blob(); // получаем PDF как blob
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "instruction.pdf"; // имя файла
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /** универсальное обновление edition / production */
  const handleFormChange = (section, newValues) => {
    setFormData((prev) => ({
      ...prev,
      [section]: { ...prev[section], ...newValues },
    }));
  };

  /** универсальная функция POST-запроса */
  const postAction = async (endpoint, body) => {
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const response = await fetch(`${BackendIP}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        throw new Error(
          data?.detail
            ? Array.isArray(data.detail)
              ? data.detail.map((d) => `${d.loc?.join(" → ")}: ${d.msg}`).join("\n")
              : typeof data.detail === "string"
              ? data.detail
              : JSON.stringify(data.detail)
            : `Ошибка сервера (${response.status})`
        );
      }

      setSuccessMsg("✅ Успешно отправлено");
      return data;
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

  const handleCalculate = async () => {
    const data = await postAction("/api/costs_report", formData);
    if (data) setReport(data);
  };

  /** подтверждение действия в модалке */
  const handleModalConfirm = async () => {
    if (!actionType) return;

    const endpoint = actionType === "delay" ? "/api/order/delay" : "/api/order/accept";

    if (actionType === "accept") {
      // при принятии в работу — скачиваем PDF
      await downloadInstruction();
    } else {
      // при откладывании — просто POST
      await postAction(endpoint, {
        comment,
        edition: formData.edition,
        production: formData.production,
      });
    }

    setShowModal(false);
    setComment("");
    setActionType(null);
  };

  const openModal = (type) => {
    setActionType(type);
    setShowModal(true);
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Расчёт стоимости</h1>

      <div className="block">
        <div className="advanced-content">
          <VisibleForm data={formData} onChange={handleFormChange} />

          <div className="button-row">
            <button
              className="btn btn-primary"
              onClick={handleCalculate}
              disabled={loading}
            >
              {loading ? "Вычисляем..." : "Рассчитать"}
            </button>

            <button
              className="btn btn-primary"
              onClick={() => openModal("delay")}
              disabled={loading}
            >
              Отложить
            </button>

            <button
              className="btn btn-primary"
              onClick={() => openModal("accept")}
              disabled={loading}
            >
              В работу
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
            <ConsealedForm data={formData} onChange={handleFormChange} />
          </div>
        </AdvancedSection>
      </div>

      {report && (
        <div className="block">
          <h2 className="block-title">Результаты</h2>
          <CostReportView report={report} />
        </div>
      )}

      {/* ===== МОДАЛЬНОЕ ОКНО ===== */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>
              {actionType === "delay" ? "Отложить заказ" : "Принять в работу"}
            </h3>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Введите комментарий..."
              rows={4}
            />
            <div className="modal-buttons">
              <button
                className="btn btn-primary"
                onClick={handleModalConfirm}
                disabled={loading}
              >
                {loading
                  ? "Отправляем..."
                  : actionType === "delay"
                  ? "Отложить"
                  : "Принять в работу"}
              </button>
              <button
                className="btn btn-more"
                onClick={() => setShowModal(false)}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
