import { useEffect, useState } from "react";
import { useAsyncAction } from "../../hooks/useAsyncAction";
import FlexForm from "../../features/Form/FlexForm";
import styles from "./ReferencePage.module.css"

const initialFormData = {
  tax_rate: "0.0000",
  black_ink_cost: "0.0000",
  ink_cost: "0.0000",
  printer_salary: "0.0000",
  lamination_cost: "0.0000",
  die_cutting_cost: "0.0000",
  paper_cost: "0.0000",
  press_sheet: {
    height: 0,
    width: 0,
    spacing: 0,
  },
  cutter: {
    stack_height: 0,
  },
  cutting_cost: "0.0000",
  sheet_by_fitting: 0,
  markup: "1.0000",
};

const fields = [
  { label: "Стоимость чёрной краски (руб./лист)", path: "black_ink_cost", type: "number", step: "0.01" },
  { label: "Стоимость всех красок (руб./лист)", path: "ink_cost", type: "number", step: "0.01" },
  { label: "Зарплата печатнику (руб./лист)", path: "printer_salary", type: "number", step: "0.01" },
  { label: "Цена ламинации (руб./лист)", path: "lamination_cost", type: "number", step: "0.01" },
  { label: "Стоимость высечки (руб./лист)", path: "die_cutting_cost", type: "number", step: "0.01" },
  { label: "Стоимость бумаги (руб./кг)", path: "paper_cost", type: "number", step: "0.01" },

  { label: "Высота печатного листа (мм)", path: "press_sheet.height", type: "number" },
  { label: "Ширина печатного листа (мм)", path: "press_sheet.width", type: "number" },
  { label: "Поля печатного листа (мм)", path: "press_sheet.spacing", type: "number" },

  { label: "Высота стопки резака (мм)", path: "cutter.stack_height", type: "number" },

  { label: "Листы на приладку (шт)", path: "sheet_by_fitting", type: "number" },

  { label: "Цена 1 реза (руб.)", path: "cutting_cost", type: "number", step: "0.01" },
];

export default function ReferencePage() {
  const { loading, error, execute } = useAsyncAction();
  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    const load = async () => {
      const data = await execute("/api/reference/production", null, {
        method: "GET",
      });

      if (data) setFormData(data);
    };

    load();
  }, []);

  const onConfirm = async () => {
    await execute("/api/reference/production", formData, {
      method: "PUT",
    });
  };

  return (
    <div className={styles.calculatorContainer}>
      <h1 className="page-title">Справочная система</h1>

      {error && <div className="error">{error}</div>}

      <FlexForm
        fields={fields}
        formData={formData}
        setFormData={setFormData}
      />

      <div className={styles.buttonRow}>
        <button
          className={`${styles.btn} ${styles.btnPrimary}`}
          onClick={onConfirm}
          disabled={loading}
        >
          {loading ? "Отправляем..." : "Сохранить"}
        </button>
      </div>
    </div>
  );
}