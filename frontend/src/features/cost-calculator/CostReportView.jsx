// src/features/cost-calculator/CostReportView.tsx
import React from "react"

export default function CostReportView({ report }) {
  // Функция для форматирования чисел с максимум 2 знаками после запятой
  const formatPrice = (value) => Number(value).toFixed(2);

  return (
    <table className="report-table">
      <tbody>
        <tr>
          <td>Кол-во изделий на листе</td>
          <td>{report.items_per_sheet}</td>
        </tr>
        <tr>
          <td>Кол-во печатных листов</td>
          <td>{report.sheet_count}</td>
        </tr>
        <tr>
          <td>Себестоимость изделия</td>
          <td>{formatPrice(report.unit_cost_price)} ₽</td>
        </tr>
        <tr>
          <td>Цена изделия</td>
          <td>{formatPrice(report.unit_cost)} ₽</td>
        </tr>
        <tr>
          <td>Цена тиража</td>
          <td>{formatPrice(report.edition_cost)} ₽</td>
        </tr>
        <tr>
          <td>Прибыль до налогов</td>
          <td>{formatPrice(report.profit_before_tax)} ₽</td>
        </tr>
        <tr>
          <td>Прибыль после налогов</td>
          <td>{formatPrice(report.profit_after_tax)} ₽</td>
        </tr>
      </tbody>
    </table>
  )
}
