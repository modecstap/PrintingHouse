import { useEffect, useState } from "react";
import FlexForm from "../../../features/Form/FlexForm";
import AdvancedSection from "../components/AdvancedSection";
import { referenceProduction } from "../../../lib/workplaceOrder";
import { calculatorService } from "../services/calculatorService";

import styles from "../CostCalculator.module.css";


// ✅ Пресеты форматов
const PAPER_PRESETS = {
  A3: { width: 420, height: 297 },
  A4: { width: 297, height: 210 },
  A5: { width: 210, height: 148 },
  A6: { width: 148, height: 105 },
  CARD: { width: 90, height: 50 },
};


const firstPrintingFields = (index) => [
  {
    label: "Кол-во листов",
    path: `printings[${index}].edition.count`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Комментарий",
    path: `printings[${index}].comment`,
    type: "text",
    valueParser: (v) => v,
  },
  {
    label: "Плотность",
    path: `printings[${index}].edition.density`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Цветность",
    path: `printings[${index}].edition.chroma`,
    type: "select",
    valueParser: Number,
    options: [
      { value: 0, label: "0+0" },
      { value: 1, label: "1+0" },
      { value: 2, label: "1+1" },
      { value: 3, label: "4+0" },
      { value: 4, label: "4+1" },
      { value: 5, label: "4+4" },
    ],
  },
  {
    label: "Ламинация",
    path: `printings[${index}].edition.lamination`,
    type: "select",
    valueParser: Number,
    options: [
      { value: 1, label: "Без ламинации" },
      { value: 2, label: "1+0" },
      { value: 3, label: "1+1" },
    ],
  },
  {
    label: "Высечка",
    path: `printings[${index}].edition.die_cutting`,
    type: "select",
    valueParser: (v) => v === "true" || v === true,
    options: [
      { value: false, label: "Нет" },
      { value: true, label: "Да" },
    ],
  },
];

const secondPrintingFields = (index) => [
  {
    label: "Ширина",
    path: `printings[${index}].edition.list_size.width`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Высота",
    path: `printings[${index}].edition.list_size.height`,
    type: "number",
    valueParser: Number,
  },
];

const printingHiddenFields = (index) => [
  { label: "Вылеты (мм)", path: `printings[${index}].edition.list_size.bleeds` },
  { label: "Стоимость голубой краски (руб./лист)", path: `printings[${index}].production.cyan`, step: 0.01 },
  { label: "Стоимость пурпурной краски (руб./лист)", path: `printings[${index}].production.magenta`, step: 0.01 },
  { label: "Стоимость жёлтой краски (руб./лист)", path: `printings[${index}].production.yellow`, step: 0.01 },
  { label: "Стоимость чёрной краски (руб./лист)", path: `printings[${index}].production.black_ink_cost`, step: 0.01 },
  { label: "Запуск ламинации (руб.)", path: `printings[${index}].production.lamination_startup`, step: 0.01 },
  { label: "Цена плёнки (руб.)", path: `printings[${index}].production.film_cost`, step: 0.01 },
  { label: "Зарплата за ламинацию (руб.)", path: `printings[${index}].production.lamination_salary`, step: 0.01 },
  { label: "Стоимость высечки (руб./лист)", path: `printings[${index}].production.die_cutting_cost`, step: 0.01 },
  { label: "Стоимость бумаги (руб./кг)", path: `printings[${index}].production.paper_cost`, step: 0.01 },
  { label: "Высота печатного листа (мм)", path: `printings[${index}].production.press_sheet.height` },
  { label: "Ширина печатного листа (мм)", path: `printings[${index}].production.press_sheet.width` },
  { label: "Поля печатного листа (мм)", path: `printings[${index}].production.press_sheet.spacing` },
  { label: "Высота стопки резака (мм)", path: `printings[${index}].production.cutter.stack_height` },
  { label: "Листы на приладку (шт)", path: `printings[${index}].production.sheet_by_fitting` },
  { label: "Цена 1 реза (руб.)", path: `printings[${index}].production.cutting_cost`, step: 0.01 },
  { label: "Зарплата печатнику за 1 лист (руб.)", path: `printings[${index}].production.printer_salary`, step: 0.01 },
];

function hasProduction(production) {
  return production != null && Object.keys(production).length > 0;
}

async function referenceFailureText(res) {
  const text = await res.text();
  if (!text) return "Не удалось загрузить справочник";

  try {
    const data = JSON.parse(text);
    if (typeof data?.detail === "string") return data.detail;
  } catch {
    return text;
  }

  return "Не удалось загрузить справочник";
}

const newPrinting = () => ({
  edition: {
    count: 0,
    list_size: { width: 420, height: 297, bleeds: 2 },
    density: 80,
    chroma: 1,
    lamination: 1,
    die_cutting: false,
  },
  production: {},
  comment: "",
});


export default function PrintingSection({ formData, setFormData }) {
  const [showAdvanced, setShowAdvanced] = useState(
    formData.printings.map(() => false)
  );

  const [referenceRates, setReferenceRates] = useState(null);
  const [referenceError, setReferenceError] = useState(null);

  // ✅ Установка формата листа
  const setPaperSize = (index, size) => {
    const preset = PAPER_PRESETS[size];

    setFormData(prev => {
      const updated = [...prev.printings];

      updated[index] = {
        ...updated[index],
        edition: {
          ...updated[index].edition,
          list_size: {
            ...updated[index].edition.list_size,
            width: preset.width,
            height: preset.height,
          },
        },
      };

      return { ...prev, printings: updated };
    });
  };

  useEffect(() => {
    const controller = new AbortController();

    calculatorService
      .getProductionReference(controller.signal)
      .then(async (res) => {
        if (controller.signal.aborted) return;

        if (!res.ok) {
          setReferenceError(await referenceFailureText(res));
          return;
        }

        const order = await res.json();
        if (controller.signal.aborted) return;

        const rates = referenceProduction(order);
        setReferenceRates(rates);
        setFormData((prev) => ({
          ...prev,
          printings: prev.printings.map((printing) => ({
            ...printing,
            production: hasProduction(printing.production)
              ? printing.production
              : rates,
          })),
        }));
      })
      .catch((error) => {
        if (error?.name === "AbortError") return;
        setReferenceError(error?.message || "Не удалось загрузить справочник");
      });

    return () => controller.abort();
  }, [setFormData]);

  const addPrinting = () => {
    const newP = newPrinting();
    if (referenceRates) {
      newP.production = referenceRates;
    }

    setFormData(d => ({
      ...d,
      printings: [...d.printings, newP],
    }));

    setShowAdvanced(prev => [...prev, false]);
  };

  const removePrinting = (index) => {
    setFormData(d => ({
      ...d,
      printings: d.printings.filter((_, i) => i !== index),
    }));

    setShowAdvanced(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <section className={styles.calculatorContainer} style={{ marginTop: 0 }}>
      <h2>Параметры печати</h2>

      {referenceError && <div className="error">{referenceError}</div>}

      {formData.printings.map((_, i) => (
        <div key={i}>
          <div>
            <FlexForm
              fields={firstPrintingFields(i)}
              formData={formData}
              setFormData={setFormData}
            />

            <div className={styles.buttonRow}>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={() => setPaperSize(i, "A3")}>A3</button>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={() => setPaperSize(i, "A4")}>A4</button>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={() => setPaperSize(i, "A5")}>A5</button>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={() => setPaperSize(i, "A6")}>A6</button>
              <button className={`${styles.btn} ${styles.btnSecondary}`} onClick={() => setPaperSize(i, "CARD")}>Визитка</button>
            </div>

            <FlexForm
              fields={secondPrintingFields(i)}
              formData={formData}
              setFormData={setFormData}
            />


            <div className={styles.buttonRow}>
              <button
                className={`${styles.btn} ${styles.btnPrimary}`}
                onClick={() => removePrinting(i)}
              >
                Удалить
              </button>

              <button
                className={`${styles.btn} ${styles.btnMore}`}
                onClick={() =>
                  setShowAdvanced(prev =>
                    prev.map((val, idx) =>
                      idx === i ? !val : val
                    )
                  )
                }
              >
                {showAdvanced[i] ? "Скрыть" : "Подробнее"}
              </button>
            </div>

            <AdvancedSection open={showAdvanced[i]}>
              <div className={styles.advancedContent}>
                <FlexForm
                  fields={printingHiddenFields(i)}
                  formData={formData}
                  setFormData={setFormData}
                />
              </div>
            </AdvancedSection>
          </div>

          <div className={styles.separator} />
        </div>
      ))}

      <button
        className={`${styles.btn} ${styles.btnPrimary}`}
        onClick={addPrinting}
      >
        + Добавить печать
      </button>
    </section>
  );
}