import {
  cutterLabel,
  laminatorLabel,
  operatorLabel,
  printerLabel,
} from "../models/catalog-label";
import styles from "../calculator.module.css";

const CHROMA_OPTIONS = [
  { value: "ZERO_ZERO", label: "0+0" },
  { value: "ONE_ZERO", label: "1+0" },
  { value: "ONE_ONE", label: "1+1" },
  { value: "FOUR_ZERO", label: "4+0" },
  { value: "FOUR_ONE", label: "4+1" },
  { value: "FOUR_FOUR", label: "4+4" },
];

const LAMINATION_OPTIONS = [
  { value: "DONT", label: "Без ламинации" },
  { value: "ONE_ZERO", label: "1+0" },
  { value: "ONE_ONE", label: "1+1" },
];

export function CatalogSelect({ id, label, value, onChange, options }) {
  return (
    <div className={styles.fieldGroup}>
      <label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function TextField({ id, label, value, onChange, inputMode, type = "text" }) {
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

const KIND_HEADING = {
  print: "Печать",
  laminate: "Ламинация",
  cut: "Рез",
  die_cut: "Высечка",
};

export default function OperationFields({
  operation,
  catalogs,
  onChange,
  onRemove,
}) {
  const heading = KIND_HEADING[operation.kind] ?? operation.kind;
  const idPrefix = `${operation.clientKey}`;

  if (operation.kind === "print") {
    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <SectionHeading heading={heading} onRemove={onRemove} />
        <div className={styles.fieldRow}>
          <CatalogSelect
            id={`${idPrefix}-printer`}
            label="Принтер"
            value={operation.printerId}
            onChange={(v) => onChange({ ...operation, printerId: v })}
            options={catalogs.printers.map((p) => ({
              value: String(p.id),
              label: printerLabel(p),
            }))}
          />
          <CatalogSelect
            id={`${idPrefix}-press-operator`}
            label="Печатник"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            options={catalogs.pressOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
          <div className={styles.fieldGroup}>
            <label htmlFor={`${idPrefix}-chroma`}>Цветность</label>
            <select
              id={`${idPrefix}-chroma`}
              value={operation.chroma}
              onChange={(e) => onChange({ ...operation, chroma: e.target.value })}
            >
              {CHROMA_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </article>
    );
  }

  if (operation.kind === "laminate") {
    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <SectionHeading heading={heading} onRemove={onRemove} />
        <div className={styles.fieldRow}>
          <CatalogSelect
            id={`${idPrefix}-laminator`}
            label="Ламинатор"
            value={operation.laminatorId}
            onChange={(v) => onChange({ ...operation, laminatorId: v })}
            options={catalogs.laminators.map((l) => ({
              value: String(l.id),
              label: laminatorLabel(l),
            }))}
          />
          <CatalogSelect
            id={`${idPrefix}-laminate-operator`}
            label="Оператор ламинации"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            options={catalogs.laminatorOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
          <div className={styles.fieldGroup}>
            <label htmlFor={`${idPrefix}-lamination`}>Ламинация</label>
            <select
              id={`${idPrefix}-lamination`}
              value={operation.lamination}
              onChange={(e) =>
                onChange({ ...operation, lamination: e.target.value })
              }
            >
              {LAMINATION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <p className={styles.legend}>Плёнка</p>
        <div className={styles.fieldRow}>
          <TextField
            id={`${idPrefix}-film-name`}
            label="Название"
            value={operation.film.name}
            onChange={(v) =>
              onChange({
                ...operation,
                film: { ...operation.film, name: v },
              })
            }
          />
          <TextField
            id={`${idPrefix}-film-price`}
            label="Цена"
            value={operation.film.price}
            inputMode="decimal"
            onChange={(v) =>
              onChange({
                ...operation,
                film: { ...operation.film, price: v },
              })
            }
          />
          <TextField
            id={`${idPrefix}-film-density`}
            label="Плотность"
            value={operation.film.density}
            type="number"
            onChange={(v) =>
              onChange({
                ...operation,
                film: { ...operation.film, density: v },
              })
            }
          />
        </div>
      </article>
    );
  }

  if (operation.kind === "cut") {
    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <SectionHeading heading={heading} onRemove={onRemove} />
        <div className={styles.fieldRow}>
          <CatalogSelect
            id={`${idPrefix}-cutter`}
            label="Резак"
            value={operation.cutterId}
            onChange={(v) => onChange({ ...operation, cutterId: v })}
            options={catalogs.cutters.map((c) => ({
              value: String(c.id),
              label: cutterLabel(c),
            }))}
          />
          <CatalogSelect
            id={`${idPrefix}-cut-operator`}
            label="Оператор реза"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            options={catalogs.cutterOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
        </div>
      </article>
    );
  }

  if (operation.kind === "die_cut") {
    return (
      <article
        className={styles.operationCard}
        aria-label={heading}
        role="region"
      >
        <SectionHeading heading={heading} onRemove={onRemove} />
        <div className={styles.fieldRow}>
          <CatalogSelect
            id={`${idPrefix}-die-cut-operator`}
            label="Оператор высечки"
            value={operation.operatorId}
            onChange={(v) => onChange({ ...operation, operatorId: v })}
            options={catalogs.dieCutOperators.map((o) => ({
              value: String(o.id),
              label: operatorLabel(o),
            }))}
          />
        </div>
      </article>
    );
  }

  return null;
}

function SectionHeading({ heading, onRemove }) {
  return (
    <div className={styles.operationHeading}>
      <h4>{heading}</h4>
      <button type="button" className={styles.btnSecondary} onClick={onRemove}>
        Удалить
      </button>
    </div>
  );
}
