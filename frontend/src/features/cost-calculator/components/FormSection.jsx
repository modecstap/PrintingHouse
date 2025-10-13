import React from "react";
import VisibleForm from "./VisibleForm";

export default function FormSection({
  formData,
  onFormChange,
  onCalculate,
  onOpenModal,
  loading,
  error,
  showAdvanced,
  toggleAdvanced,
  hideActionButtons,
}) {
  return (
    <div className="advanced-content">
      <VisibleForm data={formData} onChange={onFormChange} />

      <div className="button-row">
        <button className="btn btn-primary" onClick={onCalculate} disabled={loading}>
          {loading ? "Вычисляем..." : "Рассчитать"}
        </button>

        {!hideActionButtons && (
          <>
            <button className="btn btn-primary" onClick={() => onOpenModal("delay")} disabled={loading}>
              Отложить
            </button>
            <button className="btn btn-primary" onClick={() => onOpenModal("accept")} disabled={loading}>
              В работу
            </button>
          </>
        )}

        <button className="btn btn-more" onClick={toggleAdvanced}>
          {showAdvanced ? "Скрыть" : "Подробнее"}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <h3>⚠️ Ошибка</h3>
          {error.split("\n").map((line, idx) => <div key={idx}>{line}</div>)}
        </div>
      )}
    </div>
  );
}
