import { emptyAdditionalWork } from "../models/order";
import Button from "../../generic/button/button";
import { TextField } from "../../generic/text-field/text-field";
import styles from "../calculator.module.css";

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
      <h3>Доп. работы</h3>
      {works.map((work) => {
        const idPrefix = work.clientKey;
        return (
          <article key={work.clientKey} className={styles.operationCard}>
            <div className={styles.heading}>
              <TextField
                id={`${idPrefix}-name`}
                label="Работа"
                value={work.name}
                onChange={(v) => updateWork(work.clientKey, { name: v })}
              />
              <Button
                type="button"
                onClick={() => removeWork(work.clientKey)}
              >
                Удалить
              </Button>
            </div>
            <div className={styles.fieldRow}>
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
      <Button type="button" onClick={addWork}>
        + Работа
      </Button>
    </section>
  );
}
