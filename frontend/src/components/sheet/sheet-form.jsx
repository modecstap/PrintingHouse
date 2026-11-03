import { useState } from "react";
import { saveSheet } from "./api/sheet";
import styles from "./sheet.module.css";

const FORMATS = [
  { name: "А1", height: 594, width: 841 },
  { name: "А2", height: 420, width: 594 },
  { name: "А3", height: 297, width: 420 },
  { name: "А4", height: 210, width: 297 },
  { name: "А5", height: 148, width: 210 },
  { name: "А6", height: 105, width: 148 },
];

function formatLabel(format) {
  return `${format.name} (${format.height} x ${format.width})`;
}

function toInteger(value) {
  if (typeof value === "string" && /^-?\d+$/.test(value)) return Number(value);
  return value;
}

function toDecimalString(value) {
  if (typeof value === "number" && Number.isFinite(value)) return String(value);
  if (typeof value === "string") return value.trim();
  return value;
}

export default function SheetForm({ onSaved, onError }) {
  const [formatIndex, setFormatIndex] = useState("3");
  const [density, setDensity] = useState("");
  const [cost, setCost] = useState("");
  const [sending, setSending] = useState(false);
  const format = FORMATS[Number(formatIndex)];

  async function handleSubmit(event) {
    event.preventDefault();
    onError(null);
    setSending(true);
    try {
      await saveSheet({
        id: null,
        name: "",
        height: format.height,
        width: format.width,
        density: toInteger(density),
        cost: toDecimalString(cost),
      });
      onSaved();
    } catch (error) {
      onError(error.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className={styles.grid}>
        <label className={styles.field}>
          Формат
          <select
            value={formatIndex}
            onChange={(event) => setFormatIndex(event.target.value)}
          >
            {FORMATS.map((item, index) => (
              <option key={item.name} value={index}>
                {formatLabel(item)}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.field}>
          Плотность
          <input
            type="number"
            step="1"
            value={density}
            onChange={(event) => setDensity(event.target.value)}
          />
        </label>
        <label className={styles.field}>
          Стоимость бумаги (руб./кг)
          <input
            type="number"
            step="0.01"
            value={cost}
            onChange={(event) => setCost(event.target.value)}
          />
        </label>
      </div>
      <div className={styles.actions}>
        <button className={styles.button} type="submit" disabled={sending}>
          {sending ? "Отправляем..." : "Добавить лист"}
        </button>
      </div>
    </form>
  );
}
