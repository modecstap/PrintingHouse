import { useEffect, useState } from "react";
import { useAsyncAction } from "../../hooks/useAsyncAction";
import FlexForm from "../../features/Form/FlexForm";
import { toCalculatorForm, toWorkplaceOrder } from "../../lib/workplaceOrder";
import styles from "./ReferencePage.module.css"

const fields = [
  { label: "Стоимость голубой краски (руб./лист)", path: "printings[0].production.cyan", type: "number", step: "0.01" },
  { label: "Стоимость пурпурной краски (руб./лист)", path: "printings[0].production.magenta", type: "number", step: "0.01" },
  { label: "Стоимость жёлтой краски (руб./лист)", path: "printings[0].production.yellow", type: "number", step: "0.01" },
  { label: "Стоимость чёрной краски (руб./лист)", path: "printings[0].production.black_ink_cost", type: "number", step: "0.01" },
  { label: "Стоимость бумаги (руб./кг)", path: "printings[0].production.paper_cost", type: "number", step: "0.01" },
  { label: "Зарплата печатнику (руб./лист)", path: "printings[0].production.printer_salary", type: "number", step: "0.01" },
  { label: "Запуск ламинации (руб.)", path: "printings[0].production.lamination_startup", type: "number", step: "0.01" },
  { label: "Цена плёнки (руб.)", path: "printings[0].production.film_cost", type: "number", step: "0.01" },
  { label: "Зарплата за ламинацию (руб.)", path: "printings[0].production.lamination_salary", type: "number", step: "0.01" },
  { label: "Стоимость высечки (руб./лист)", path: "printings[0].production.die_cutting_cost", type: "number", step: "0.01" },
  { label: "Высота печатного листа (мм)", path: "printings[0].production.press_sheet.height", type: "number" },
  { label: "Ширина печатного листа (мм)", path: "printings[0].production.press_sheet.width", type: "number" },
  { label: "Поля печатного листа (мм)", path: "printings[0].production.press_sheet.spacing", type: "number" },
  { label: "Высота стопки резака (мм)", path: "printings[0].production.cutter.stack_height", type: "number" },
  { label: "Листы на приладку (шт)", path: "printings[0].production.sheet_by_fitting", type: "number" },
  { label: "Цена 1 реза (руб.)", path: "printings[0].production.cutting_cost", type: "number", step: "0.01" },
];

export default function ReferencePage() {
  const { loading, error, execute } = useAsyncAction();
  const [formData, setFormData] = useState({});

  useEffect(() => {
    const load = async () => {
      const data = await execute("/api/v2/reference/", null, {
        method: "GET",
      });

      if (data) setFormData(toCalculatorForm(data));
    };

    load();
  }, []);

  const onConfirm = async () => {
    await execute("/api/v2/reference/", toWorkplaceOrder(formData), {
      method: "POST",
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
