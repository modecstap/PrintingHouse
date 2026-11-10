import { emptyCalculatorForm } from "./models/order";
import AdditionalWorkSection from "./components/additional-work-section";
import BlockSection from "./components/block-section";
import ReportView from "./components/report-view";
import Button from "../generic/button/button";
import styles from "./calculator.module.css";
import { useCalculator } from "./hook";

export default function Calculator({
  initialForm = emptyCalculatorForm(),
  initialReport = null,
  onSaved,
}) {
  const {
    form,
    setForm,
    report,
    catalogState,
    quoteState,
    savedId,
    referencesState,
    selectedPresetId,
    actionBusy,
    actionError,
    presetBusy,
    handleQuote,
    handleSave,
    updateBlock,
    removeBlock,
    addBlock,
    handlePresetChange,
  } = useCalculator({ initialForm, initialReport, onSaved });

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
