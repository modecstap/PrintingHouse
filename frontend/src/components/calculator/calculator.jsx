import { emptyCalculatorForm } from "./models/order";
import AdditionalWorkSection from "./components/additional-work-section";
import BlockSection from "./components/block-section";
import ReportView from "./components/report-view";
import Button from "../generic/button/button";
import { Dropdown } from "../generic/dropdown/dropdown";
import { NumberField } from "../generic/number-field/number-field";
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
          <Dropdown
            id="calculator-preset"
            label="Пресет"
            value={selectedPresetId}
            onChange={(v) =>
              handlePresetChange({ target: { value: v } })
            }
            disabled={actionBusy || presetBusy}
            emptyOptionLabel="Нет"
            options={referencesState.references.map((row) => ({
              value: row.order_id,
              label: row.description
                ? `${row.name} (${row.description})`
                : row.name,
            }))}
          />
        )}

      <NumberField
        id="order-count"
        label="Тираж"
        value={form.count}
        onChange={(v) => setForm({ ...form, count: v })}
      />

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
