import { emptyAdditionalWork } from "../models/order";
import Button from "../../../features/Button/Button";
import buttonStyles from "../../../features/Button/Button.module.css";
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

export default function AdditionalWorkSection({ works, onChange }) {
  const updateWork = (clientKey, partial) => {
    onChange(
      works.map((work) =>
        work.clientKey === clientKey ? { ...work, ...partial } : work,
      ),
    );
  };

  const removeWork = (clientKey) => {
    onChange(works.filter((work) => work.clientKey !== clientKey));
  };

  const addWork = () => {
    onChange([...works, emptyAdditionalWork()]);
  };

  return (
    <section className={styles.calculatorBlock}>
      <h3>Дополнительные работы</h3>
      {works.map((work) => {
        const idPrefix = work.clientKey;
        return (
          <article key={work.clientKey} className={styles.operationCard}>
            <div className={styles.operationHeading}>
              <span>{work.name || "Работа"}</span>
              <Button
                type="button"
                onClick={() => removeWork(work.clientKey)}
              >
                Удалить
              </Button>
            </div>
            <div className={styles.fieldRow}>
              <TextField
                id={`${idPrefix}-name`}
                label="Название операции"
                value={work.name}
                onChange={(v) => updateWork(work.clientKey, { name: v })}
              />
              <TextField
                id={`${idPrefix}-price`}
                label="Стоимость"
                value={work.price}
                inputMode="decimal"
                onChange={(v) => updateWork(work.clientKey, { price: v })}
              />
              <TextField
                id={`${idPrefix}-description`}
                label="Описание"
                value={work.description}
                onChange={(v) => updateWork(work.clientKey, { description: v })}
              />
              <TextField
                id={`${idPrefix}-work-markup`}
                label="Наценка (%)"
                value={work.markup}
                type="number"
                onChange={(v) => updateWork(work.clientKey, { markup: v })}
              />
            </div>
          </article>
        );
      })}
      <Button
        type="button"
        className={buttonStyles.standalone}
        onClick={addWork}
      >
        + Добавить работу
      </Button>
    </section>
  );
}
