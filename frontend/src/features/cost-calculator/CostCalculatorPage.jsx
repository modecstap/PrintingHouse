import React, { useState } from "react";
import FormSection from "./components/FormSection";
import AdvancedFormSection from "./components/AdvancedFormSection";
import ReportSection from "./components/ReportSection";
import ActionModal from "./components/ActionModal";
import { useFormData } from "./hooks/useFormData";
import { useAsyncAction } from "./hooks/useAsyncAction";
import "./CostCalculator.css";

export default function CostCalculatorPage({ edition = {}, production = {}, hideActionButtons = false }) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [actionType, setActionType] = useState(null);
  const [comment, setComment] = useState("");
  const [report, setReport] = useState(null);

  const [formData, handleFormChange] = useFormData(edition, production);
  const { loading, error, execute } = useAsyncAction();

  const handleCalculate = async () => {
    const data = await execute("/api/costs_report", formData);
    if (data) setReport(data);
  };

  const downloadPDF = async () => {
    const blob = await execute("/api/order/accept", { comment, ...formData }, { isBlob: true });
    if (!blob) return;

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "instruction.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleModalConfirm = async () => {
    if (!actionType) return;
    if (actionType === "accept") await downloadPDF();
    else await execute("/api/order/delay", { comment, ...formData });

    setShowModal(false);
    setComment("");
    setActionType(null);
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Расчёт стоимости</h1>

      <div className="block">
        <FormSection
          formData={formData}
          onFormChange={handleFormChange}
          onCalculate={handleCalculate}
          onOpenModal={(type) => { setActionType(type); setShowModal(true); }}
          loading={loading}
          error={error}
          showAdvanced={showAdvanced}
          toggleAdvanced={() => setShowAdvanced(!showAdvanced)}
          hideActionButtons = {hideActionButtons}
        />

        <AdvancedFormSection open={showAdvanced} formData={formData} onFormChange={handleFormChange} />
      </div>

      <ReportSection report={report} />

      {showModal && (
        <ActionModal
          actionType={actionType}
          comment={comment}
          setComment={setComment}
          onConfirm={handleModalConfirm}
          onClose={() => setShowModal(false)}
          loading={loading}
        />
      )}
    </div>
  );
}
