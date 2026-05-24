import React, { useState } from "react";

import styles from "../CostCalculator.module.css";


function ReportRow({ label, value, isGroup }) {
  if (isGroup) {
    return (
      <tr>
        <td colSpan={2}>
          <strong>{label}</strong>
        </td>
      </tr>
    );
  }

  return (
    <tr>
      <td>{label}</td>
      <td>{value}</td>
    </tr>
  );
}


export default function ReportSection({ report, base_rows, detail_rows = [] }) {
  const [showDetails, setShowDetails] = useState(false);

  const rows = showDetails
    ? [...base_rows, ...detail_rows]
    : base_rows;

  if (!report) return null;

  return (
    <div className={styles.calculatorBlock}>
      <h2>Результаты</h2>

      <table className={styles.reportTable}>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>
                {row.isGroup ? (
                  <strong>{row.label}</strong>
                ) : (
                  row.value(report)
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {detail_rows.length !== 0 && (
        <button
          className={`${styles.btn} ${styles.btnMore}`}
          onClick={() => setShowDetails((v) => !v)}
        >
          {showDetails ? "Скрыть" : "Подробнее"}
        </button>
      )}
    </div>
  );
}
