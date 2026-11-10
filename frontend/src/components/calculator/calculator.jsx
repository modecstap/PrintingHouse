import {
  calculatorFormMissingFieldLabels,
  emptyCalculatorForm,
} from "./models/order";
import AdditionalWorkSection from "./components/additional-work-section";
import BlockSection from "./components/block-section";
import MissingFieldsView from "./components/missing-fields-view";
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
    handleSave,
    updateBlock,
    removeBlock,
    addBlock,
    handlePresetChange,
  } = useCalculator({ initialForm, initialReport, onSaved });

  const missingFields = calculatorFormMissingFieldLabels(form);
  const formReady = missingFields.length === 0;

  return (
    <div className={styles.page}>
      <div>
          <div className={styles.heading}>
            <h2>Калькулятор</h2>
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
            <Button
              type="button"
              onClick={handleSave}
              disabled={actionBusy || presetBusy}
            >
              Сохранить
            </Button>
          </div>

          <NumberField
            id="order-count"
            label="Тираж"
            value={form.count}
            onChange={(v) => setForm({ ...form, count: v })}
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
      
      <div>
          {!formReady ? (
            <MissingFieldsView fields={missingFields} />
          ) : (
            <ReportView report={report} />
          )}

          {formReady && quoteState.status === "loading" && (
            <div className={styles.statusMessage} role="status">
              Счёт...
            </div>
          )}

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
    </div>
  );
}
