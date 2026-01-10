import React, { useState } from "react";
import ReportSection from "./sections/ReportSection";
import ActionModal from "./components/ActionModal";
import { useFormData } from "./hooks/useFormData";
import { useAsyncAction } from "./hooks/useAsyncAction";
import "./CostCalculator.css";
import FlexForm from "./components/FlexForm";
import { Hiddenfields, VisibleFields } from "./FormFields";
import AdvancedSection from "./components/AdvancedSection";


const formatPrice = (value) =>
  value == null ? "—" : `${Number(value).toFixed(2)} ₽`;


const BASE_ROWS = [
  {
    label: "Цена изделия",
    value: (r) => formatPrice(r.unit_cost),
  },
  {
    label: "Цена тиража",
    value: (r) => formatPrice(r.edition_cost),
  },
];


const DETAIL_ROWS = [
  {
    label: "Кол-во изделий на листе",
    value: (r) => r.items_per_sheet,
  },
  {
    label: "Кол-во печатных листов",
    value: (r) => r.sheet_count,
  },
  {
    label: "Себестоимость изделия",
    value: (r) => formatPrice(r.unit_cost_price),
  },
  {
    label: "Прибыль до налогов",
    value: (r) => formatPrice(r.profit_before_tax),
  },
  {
    label: "Прибыль после налогов",
    value: (r) => formatPrice(r.profit_after_tax),
  },
];


const ACTION_CONFIG = {
  delay: {
    title: "Отложить заказ",
    confirmText: "Отложить",
    fields: [
      {
        label: "Комментарий",
        path: "printings[0].comment",
        type: "textarea",
      },
    ],
  },
  accept: {
    title: "Принять в работу",
    confirmText: "Принять в работу",
    fields: [
      {
        label: "Комментарий",
        path: "printings[0].comment",
        type: "textarea",
      },
    ],
  },
};


export default function CostCalculatorPage({ edition = {}, production = {}, economy = {}, hideActionButtons = false }) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [actionType, setActionType] = useState(null);
  const [report, setReport] = useState(null);

  const [formData, setFormData] = useFormData(edition, production, economy);
  const { loading, error, execute } = useAsyncAction();

  const handleCalculate = async () => {
    const data = await execute("/api/printing/costs_report", {
      edition:{...formData.printings[0].edition},
      production:{...formData.printings[0].production},
      economy:{...formData.economy}
    });
    if (data) setReport(data);
  };

  const downloadPDF = async () => {
    const blob = await execute("/api/order/accept", { ...formData }, { isBlob: true });
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
    else await execute("/api/order/delay", {...formData });

    setShowModal(false);
    setActionType(null);
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Расчёт стоимости</h1>

      <div className="block">
        <FlexForm fields={VisibleFields} formData={formData} setFormData={setFormData} />
  
        <div className="button-row">
          <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
            {loading ? "Вычисляем..." : "Рассчитать"}
          </button>
  
          {!hideActionButtons && (
            <>
              <button className="btn btn-primary" onClick={() => { setActionType('delay'); setShowModal(true); }} disabled={loading}>
                Отложить
              </button>
              <button className="btn btn-primary" onClick={() => { setActionType('accept'); setShowModal(true); }} disabled={loading}>
                В работу
              </button>
            </>
          )}
  
          <button className="btn btn-more" onClick={() => setShowAdvanced(!showAdvanced)}>
            {showAdvanced ? "Скрыть" : "Подробнее"}
          </button>
          </div>
    
          {error && (
            <div className="error-message">
              <h3>⚠️ Ошибка</h3>
              {error.split("\n").map((line, idx) => <div key={idx}>{line}</div>)}
            </div>
          )}

        <AdvancedSection open={showAdvanced}>
          <div className="advanced-content">
            <FlexForm fields={Hiddenfields} formData={formData} setFormData={setFormData} />
          </div>
        </AdvancedSection>
      </div>

      <ReportSection report={report} base_rows={BASE_ROWS} detail_rows={DETAIL_ROWS}/>

      {showModal && (
        <ActionModal
          action={ACTION_CONFIG[actionType]}
          data={formData}
          setData={setFormData}
          onConfirm={handleModalConfirm}
          onClose={() => setShowModal(false)}
          loading={loading}
        />
      )}
    </div>
  );
}
