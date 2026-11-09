import { useEffect, useState } from "react";
import { loadCatalogs } from "./api/catalog";
import { quoteOrder, saveOrder } from "./api/order";
import {
  emptyBlock,
  emptyCalculatorForm,
} from "./models/order";
import AdditionalWorkSection from "./components/additional-work-section";
import BlockSection from "./components/block-section";
import ReportView from "./components/report-view";
import styles from "./calculator.module.css";

const EMPTY_CATALOGS = {
  printers: [],
  laminators: [],
  cutters: [],
  pressOperators: [],
  laminatorOperators: [],
  cutterOperators: [],
  dieCutOperators: [],
};

export default function Calculator({
  initialForm = emptyCalculatorForm(),
  initialReport = null,
  onSaved,
}) {
  const [form, setForm] = useState(initialForm);
  const [report, setReport] = useState(initialReport);
  const [catalogState, setCatalogState] = useState({
    status: "loading",
    catalogs: EMPTY_CATALOGS,
    message: null,
  });
  const [quoteState, setQuoteState] = useState({ status: "idle" });
  const [saveState, setSaveState] = useState({ status: "idle" });
  const [savedId, setSavedId] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    loadCatalogs(controller.signal).then(({ catalogs, error }) => {
      if (controller.signal.aborted) {
        return;
      }
      setCatalogState({
        status: error ? "error" : "success",
        catalogs: { ...EMPTY_CATALOGS, ...catalogs },
        message: error,
      });
    });
    return () => controller.abort();
  }, []);

  const actionBusy =
    quoteState.status === "loading" || saveState.status === "loading";

  const actionError =
    quoteState.status === "error"
      ? quoteState.message
      : saveState.status === "error"
        ? saveState.message
        : catalogState.status === "error"
          ? catalogState.message
          : null;

  const handleQuote = async () => {
    setQuoteState({ status: "loading" });
    setSaveState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    try {
      const nextReport = await quoteOrder(form);
      setReport(nextReport);
      setQuoteState({ status: "success" });
    } catch (error) {
      setQuoteState({
        status: "error",
        message:
          error instanceof Error ? error.message : "Произошла неизвестная ошибка",
      });
    }
  };

  const handleSave = async () => {
    setSaveState({ status: "loading" });
    setQuoteState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    setSavedId(null);
    try {
      const id = await saveOrder(form);
      setSavedId(id);
      setSaveState({ status: "success" });
      if (onSaved) {
        onSaved(id);
      }
    } catch (error) {
      setSaveState({
        status: "error",
        message:
          error instanceof Error ? error.message : "Произошла неизвестная ошибка",
      });
    }
  };

  const updateBlock = (clientKey, nextBlock) => {
    setForm({
      ...form,
      blocks: form.blocks.map((block) =>
        block.clientKey === clientKey ? nextBlock : block,
      ),
    });
  };

  const removeBlock = (clientKey) => {
    setForm({
      ...form,
      blocks: form.blocks.filter((block) => block.clientKey !== clientKey),
    });
  };

  const addBlock = () => {
    setForm({ ...form, blocks: [...form.blocks, emptyBlock()] });
  };

  return (
    <div className={styles.calculatorContainer}>
      <div className={styles.fieldRow}>
        <h2 className={styles.pageTitle}>Калькулятор</h2>
      </div>

      <div className={styles.fieldGroup}>
        <label htmlFor="order-count">Количество изделий</label>
        <input
          id="order-count"
          type="number"
          step="1"
          value={form.count}
          onChange={(e) => setForm({ ...form, count: e.target.value })}
        />
      </div>

      {form.blocks.map((block, index) => (
        <BlockSection
          key={block.clientKey}
          block={block}
          index={index}
          soleBlock={form.blocks.length === 1}
          catalogs={catalogState.catalogs}
          onChange={(next) => updateBlock(block.clientKey, next)}
          onRemove={() => removeBlock(block.clientKey)}
        />
      ))}

      <button type="button" className={styles.btnSecondary} onClick={addBlock}>
        + Добавить блок
      </button>

      <div className={styles.separator} />

      <AdditionalWorkSection
        works={form.additionalWorks}
        onChange={(additionalWorks) => setForm({ ...form, additionalWorks })}
      />

      <div className={styles.separator} />

      <ReportView report={report} />

      <div className={styles.buttonRow}>
        <button
          type="button"
          className={`${styles.btn} ${styles.btnAccent}`}
          onClick={handleQuote}
          disabled={actionBusy}
        >
          {quoteState.status === "loading" ? "Вычисляем..." : "Рассчитать"}
        </button>
        <button
          type="button"
          className={`${styles.btn} ${styles.btnPrimary}`}
          onClick={handleSave}
          disabled={actionBusy}
        >
          Сохранить
        </button>
      </div>

      {actionError && (
        <div className={styles.errorMessage} role="alert">
          {actionError}
        </div>
      )}

      {savedId !== null && (
        <div className={styles.statusMessage} role="status">
          {`Заказ сохранён: ${savedId}`}
        </div>
      )}
    </div>
  );
}
