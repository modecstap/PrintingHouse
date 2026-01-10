import React, { useState } from "react";


function ReportRow({ label, value }) {
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
    <div className="block">
      <h2 className="block-title">Результаты</h2>
      <div>
        <table className="report-table">
          <tbody>
            {rows.map((row) => (
              <ReportRow
                key={row.label}
                label={row.label}
                value={row.value(report)}
              />
            ))}
          </tbody>
        </table>
        {detail_rows.length != 0 &&(
        <button
          className="btn btn-more"
          onClick={() => setShowDetails((v) => !v)}
        >
          {showDetails ? "Скрыть" : "Подробнее"}
        </button>
        )}
      </div>
    </div>
  );
}
