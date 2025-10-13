import React from "react";
import CostReportView from "./CostReportView";

export default function ReportSection({ report }) {
  if (!report) return null;
  return (
    <div className="block">
      <h2 className="block-title">Результаты</h2>
      <CostReportView report={report} />
    </div>
  );
}
