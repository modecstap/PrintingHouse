import { formatMoney } from "../../../lib/format-money";
import styles from "../calculator.module.css";

export default function ReportView({ report }) {
  if (!report) {
    return null;
  }

  return (
    <section>
      <h2>Результаты</h2>
      <table className={styles.reportTable}>
        <tbody>
          <tr>
            <th scope="row">Цена изделия</th>
            <td>{formatMoney(report.product_price)}</td>
          </tr>
          <tr>
            <th scope="row">Цена тиража</th>
            <td>{formatMoney(report.order_price)}</td>
          </tr>
          <tr>
            <th scope="row">Прибыль от тиража</th>
            <td>{formatMoney(report.income)}</td>
          </tr>
          {report.impositions.map((count, index) => (
            <tr key={index}>
              <th scope="row">{`Блок ${index + 1}: изделий на листе`}</th>
              <td>{count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
