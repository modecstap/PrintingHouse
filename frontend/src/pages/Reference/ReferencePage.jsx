import { useEffect, useState } from "react";
import { useAsyncAction } from "../../hooks/useAsyncAction";
import FlexForm from "../../features/Form/FlexForm";
import { deleteSheet, fetchSheets } from "../../components/sheet/api/sheet";
import SheetForm from "../../components/sheet/sheet-form";
import SheetList from "../../components/sheet/sheet-list";
import SheetSelect from "../../components/sheet/sheet-select";
import { toCalculatorForm, toWorkplaceOrder } from "../../lib/workplaceOrder";
import styles from "./ReferencePage.module.css"

const fields = [
  { label: "Стоимость голубой краски (руб./лист)", path: "printings[0].production.cyan", type: "number", step: "0.01" },
  { label: "Стоимость пурпурной краски (руб./лист)", path: "printings[0].production.magenta", type: "number", step: "0.01" },
  { label: "Стоимость жёлтой краски (руб./лист)", path: "printings[0].production.yellow", type: "number", step: "0.01" },
  { label: "Стоимость чёрной краски (руб./лист)", path: "printings[0].production.black_ink_cost", type: "number", step: "0.01" },
  { label: "Зарплата печатнику (руб./лист)", path: "printings[0].production.printer_salary", type: "number", step: "0.01" },
  { label: "Запуск ламинации (руб.)", path: "printings[0].production.lamination_startup", type: "number", step: "0.01" },
  { label: "Цена плёнки (руб.)", path: "printings[0].production.film_cost", type: "number", step: "0.01" },
  { label: "Зарплата за ламинацию (руб.)", path: "printings[0].production.lamination_salary", type: "number", step: "0.01" },
  { label: "Стоимость высечки (руб./лист)", path: "printings[0].production.die_cutting_cost", type: "number", step: "0.01" },
  { label: "Поля печатного листа (мм)", path: "printings[0].production.spacing", type: "number" },
  { label: "Высота стопки резака (мм)", path: "printings[0].production.cutter.stack_height", type: "number" },
  { label: "Листы на приладку (шт)", path: "printings[0].production.sheet_by_fitting", type: "number" },
  { label: "Цена 1 реза (руб.)", path: "printings[0].production.cutting_cost", type: "number", step: "0.01" },
];

function setTemplateSheet(setFormData, sheetId) {
  setFormData((prev) => {
    const printings = Array.isArray(prev.printings) ? [...prev.printings] : [{}];
    const printing = { ...(printings[0] ?? {}) };
    printings[0] = {
      ...printing,
      production: {
        ...(printing.production ?? {}),
        press_sheet: sheetId,
      },
    };
    return { ...prev, printings };
  });
}

export default function ReferencePage() {
  const { loading, error, execute } = useAsyncAction();
  const [formData, setFormData] = useState({});
  const [sheets, setSheets] = useState([]);
  const [sheetError, setSheetError] = useState(null);
  const templateSheetId = formData.printings?.[0]?.production?.press_sheet ?? null;

  useEffect(() => {
    const controller = new AbortController();
    let ignore = false;

    const load = async () => {
      const data = await execute("/api/v2/reference/", null, {
        method: "GET",
      });

      if (!ignore && data) setFormData(toCalculatorForm(data));
    };

    const loadSheets = async () => {
      try {
        const list = await fetchSheets(controller.signal);
        if (!ignore) setSheets(list);
      } catch (err) {
        if (err?.name === "AbortError" || ignore) return;
        setSheetError(err.message);
      }
    };

    load();
    loadSheets();
    return () => {
      ignore = true;
      controller.abort();
    };
  }, []);

  const reloadSheets = async () => {
    setSheets(await fetchSheets());
  };

  const onSheetSaved = async () => {
    setSheetError(null);
    try {
      await reloadSheets();
    } catch (err) {
      setSheetError(err.message);
    }
  };

  const onDeleteSheet = async (id) => {
    setSheetError(null);
    try {
      await deleteSheet(id);
      await reloadSheets();
    } catch (err) {
      setSheetError(err.message);
    }
  };

  const onConfirm = async () => {
    await execute("/api/v2/reference/", toWorkplaceOrder(formData), {
      method: "POST",
    });
  };

  const pageError = sheetError || error;

  return (
    <div className={styles.calculatorContainer}>
      <h1 className="page-title">Справочная система</h1>

      {pageError && <div className="error">{pageError}</div>}

      <h2>Печатные листы</h2>
      <SheetForm onSaved={onSheetSaved} onError={setSheetError} />
      <SheetList sheets={sheets} onDelete={onDeleteSheet} />

      <h2>Шаблон</h2>
      <SheetSelect
        sheets={sheets}
        sheetId={templateSheetId}
        onChange={(sheetId) => setTemplateSheet(setFormData, sheetId)}
      />
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
