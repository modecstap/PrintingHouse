import { useEffect, useState } from "react";
import { fetchReferences } from "../references/api/references";
import { fetchOrderForm } from "../orders/api/orders";
import { loadCatalogs } from "./api/catalog";
import { quoteOrder, saveOrder } from "./api/order";
import {
  applyFilmsCatalogToForm,
  applySheetsCatalogToForm,
  emptyBlock,
  emptyCalculatorForm,
} from "./models/order";
import AdditionalWorkSection from "./components/additional-work-section";
import BlockSection from "./components/block-section";
import ReportView from "./components/report-view";
import Button from "../generic/button/button";
import styles from "./calculator.module.css";

const EMPTY_CATALOGS = {
  printers: [],
  laminators: [],
  cutters: [],
  pressOperators: [],
  laminatorOperators: [],
  cutterOperators: [],
  dieCutOperators: [],
  sheets: [],
  films: [],
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
  const [referencesState, setReferencesState] = useState({
    status: "loading",
    references: [],
    message: null,
  });
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [presetLoadState, setPresetLoadState] = useState({ status: "idle" });

  const applyCatalogsToForm = (formState, catalogs) => {
    let next = formState;
    if (catalogs.sheets.length > 0) {
      next = applySheetsCatalogToForm(next, catalogs.sheets);
    }
    if (catalogs.films.length > 0) {
      next = applyFilmsCatalogToForm(next, catalogs.films);
    }
    return next;
  };

  useEffect(() => {
    const controller = new AbortController();
    loadCatalogs(controller.signal).then(({ catalogs, error }) => {
      if (controller.signal.aborted) {
        return;
      }
      const merged = { ...EMPTY_CATALOGS, ...catalogs };
      setCatalogState({
        status: error ? "error" : "success",
        catalogs: merged,
        message: error,
      });
      if (!error) {
        setForm((prev) => applyCatalogsToForm(prev, merged));
      }
    });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchReferences(controller.signal)
      .then((references) => {
        if (controller.signal.aborted) {
          return;
        }
        setReferencesState({ status: "success", references, message: null });
      })
      .catch((error) => {
        if (error?.name === "AbortError" || controller.signal.aborted) {
          return;
        }
        setReferencesState({
          status: "error",
          references: [],
          message:
            error instanceof Error
              ? error.message
              : "Не удалось загрузить пресеты",
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
        : presetLoadState.status === "error"
          ? presetLoadState.message
          : catalogState.status === "error"
            ? catalogState.message
            : referencesState.status === "error"
              ? referencesState.message
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

  const handlePresetChange = async (event) => {
    const orderId = event.target.value;
    setSelectedPresetId(orderId);
    setPresetLoadState({ status: "idle" });
    setQuoteState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    setSaveState((prev) =>
      prev.status === "error" ? { status: "idle" } : prev,
    );
    if (orderId === "") {
      return;
    }

    setPresetLoadState({ status: "loading" });
    setReport(null);
    setSavedId(null);
    try {
      const loaded = await fetchOrderForm(Number(orderId));
      setForm(applyCatalogsToForm(loaded, catalogState.catalogs));
      setPresetLoadState({ status: "success" });
    } catch (error) {
      setPresetLoadState({
        status: "error",
        message:
          error instanceof Error ? error.message : "Не удалось загрузить пресет",
      });
    }
  };

  const presetBusy = presetLoadState.status === "loading";

  return (
    <div className={styles.page}>
      <div className={styles.fieldRow}>
        <h2 className={styles.pageTitle}>Калькулятор</h2>
      </div>

      {referencesState.status === "success" &&
        referencesState.references.length > 0 && (
          <div className={styles.fieldGroup}>
            <label htmlFor="calculator-preset">Пресет</label>
            <select
              id="calculator-preset"
              value={selectedPresetId}
              onChange={handlePresetChange}
              disabled={actionBusy || presetBusy}
            >
              <option value="">Нет</option>
              {referencesState.references.map((row) => (
                <option key={`${row.name}-${row.order_id}`} value={row.order_id}>
                  {row.description
                    ? `${row.name} (${row.description})`
                    : row.name}
                </option>
              ))}
            </select>
          </div>
        )}

      <div className={styles.fieldGroup}>
        <label htmlFor="order-count">Тираж</label>
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

      <Button type="button" onClick={addBlock}>
        + Блок
      </Button>

      <AdditionalWorkSection
        works={form.additionalWorks}
        onChange={(additionalWorks) => setForm({ ...form, additionalWorks })}
      />

      <ReportView report={report} />

      <div className={styles.buttonRow}>
        <Button
          type="button"
          onClick={handleQuote}
          disabled={actionBusy || presetBusy}
        >
          {quoteState.status === "loading" ? "Счёт..." : "Рассчитать"}
        </Button>
        <Button
          type="button"
          onClick={handleSave}
          disabled={actionBusy || presetBusy}
        >
          Сохранить
        </Button>
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
