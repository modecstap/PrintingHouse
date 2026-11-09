import {
  emptyCutOperation,
  emptyDieCutOperation,
  emptyLaminateOperation,
  emptyPrintOperation,
} from "../models/order";
import OperationFields from "./operation-fields";
import styles from "../calculator.module.css";

function TextField({ id, label, value, onChange, type = "text", inputMode }) {
  return (
    <div className={styles.fieldGroup}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type={type}
        inputMode={inputMode}
        step={type === "number" ? "1" : undefined}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function BlockSection({
  block,
  index,
  catalogs,
  soleBlock,
  onChange,
  onRemove,
}) {
  const idPrefix = block.clientKey;

  const update = (partial) => onChange({ ...block, ...partial });

  const updateOperation = (clientKey, next) => {
    update({
      operations: block.operations.map((op) =>
        op.clientKey === clientKey ? next : op,
      ),
    });
  };

  const removeOperation = (clientKey) => {
    update({
      operations: block.operations.filter((op) => op.clientKey !== clientKey),
    });
  };

  const addOperation = (factory) => {
    update({ operations: [...block.operations, factory()] });
  };

  return (
    <section className={styles.calculatorBlock}>
      <div className={styles.operationHeading}>
        <h3 className={styles.blockHeading}>{`Блок ${index + 1}`}</h3>
        <button
          type="button"
          className={styles.btnSecondary}
          onClick={onRemove}
          disabled={soleBlock}
        >
          Удалить
        </button>
      </div>

      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-block-count`}
          label="Количество копий"
          value={block.count}
          type="number"
          onChange={(v) => update({ count: v })}
        />
        <TextField
          id={`${idPrefix}-markup`}
          label="Наценка (%)"
          value={block.markup}
          type="number"
          onChange={(v) => update({ markup: v })}
        />
      </div>

      <p className={styles.legend}>Формат изделия</p>
      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-target-name`}
          label="Название"
          value={block.target.name}
          onChange={(v) => update({ target: { ...block.target, name: v } })}
        />
        <TextField
          id={`${idPrefix}-target-width`}
          label="Ширина (мм)"
          value={block.target.width}
          type="number"
          onChange={(v) => update({ target: { ...block.target, width: v } })}
        />
        <TextField
          id={`${idPrefix}-target-height`}
          label="Высота (мм)"
          value={block.target.height}
          type="number"
          onChange={(v) => update({ target: { ...block.target, height: v } })}
        />
      </div>

      <p className={styles.legend}>Бумага</p>
      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-paper-name`}
          label="Название бумаги"
          value={block.paper.name}
          onChange={(v) => update({ paper: { ...block.paper, name: v } })}
        />
        <TextField
          id={`${idPrefix}-paper-density`}
          label="Плотность (г/м²)"
          value={block.paper.density}
          type="number"
          onChange={(v) => update({ paper: { ...block.paper, density: v } })}
        />
        <TextField
          id={`${idPrefix}-paper-thickness`}
          label="Толщина (мм)"
          value={block.paper.thickness}
          type="number"
          onChange={(v) => update({ paper: { ...block.paper, thickness: v } })}
        />
        <TextField
          id={`${idPrefix}-paper-price`}
          label="Цена за кг"
          value={block.paper.price_per_kilo}
          inputMode="decimal"
          onChange={(v) =>
            update({ paper: { ...block.paper, price_per_kilo: v } })
          }
        />
      </div>

      <p className={styles.legend}>Формат листа</p>
      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-sheet-name`}
          label="Название"
          value={block.sheetFormat.name}
          onChange={(v) =>
            update({ sheetFormat: { ...block.sheetFormat, name: v } })
          }
        />
        <TextField
          id={`${idPrefix}-sheet-width`}
          label="Ширина (мм)"
          value={block.sheetFormat.width}
          type="number"
          onChange={(v) =>
            update({ sheetFormat: { ...block.sheetFormat, width: v } })
          }
        />
        <TextField
          id={`${idPrefix}-sheet-height`}
          label="Высота (мм)"
          value={block.sheetFormat.height}
          type="number"
          onChange={(v) =>
            update({ sheetFormat: { ...block.sheetFormat, height: v } })
          }
        />
      </div>

      <div className={styles.fieldRow}>
        <TextField
          id={`${idPrefix}-bleeds`}
          label="Вылеты (мм)"
          value={block.bleeds}
          type="number"
          onChange={(v) => update({ bleeds: v })}
        />
        <TextField
          id={`${idPrefix}-spacing`}
          label="Поля печатного листа (мм)"
          value={block.spacing}
          type="number"
          onChange={(v) => update({ spacing: v })}
        />
      </div>

      {block.operations.map((operation) => (
        <OperationFields
          key={operation.clientKey}
          operation={operation}
          catalogs={catalogs}
          onChange={(next) => updateOperation(operation.clientKey, next)}
          onRemove={() => removeOperation(operation.clientKey)}
        />
      ))}

      <EdgeButtonRow
        onPrint={() => addOperation(emptyPrintOperation)}
        onLaminate={() => addOperation(emptyLaminateOperation)}
        onCut={() => addOperation(emptyCutOperation)}
        onDieCut={() => addOperation(emptyDieCutOperation)}
      />
    </section>
  );
}

function EdgeButtonRow({ onPrint, onLaminate, onCut, onDieCut }) {
  return (
    <div className={styles.fieldRow}>
      <button type="button" className={styles.btnSecondary} onClick={onPrint}>
        + Печать
      </button>
      <button type="button" className={styles.btnSecondary} onClick={onLaminate}>
        + Ламинация
      </button>
      <button type="button" className={styles.btnSecondary} onClick={onCut}>
        + Рез
      </button>
      <button type="button" className={styles.btnSecondary} onClick={onDieCut}>
        + Высечка
      </button>
    </div>
  );
}
