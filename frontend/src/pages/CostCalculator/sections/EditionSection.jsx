import ReportSection from "./ReportSection";
import FlexForm from "../../../features/Form/FlexForm";
import { useEdition } from "../hooks/useEdition";

import styles from "../CostCalculator.module.css";

export default function EditionSection({
  formData,
  setFormData,
  hideAcceptButtons,
  hideUpdateButton,
}) {
  const {
    UNIT_FIELDS,
    BASE_ROWS,
    report,
    hiddenRows,
    loading,
    error,
    calculate,
    delay,
    accept,
    update,
  } = useEdition(formData);

  return (
    <section className={styles.calculatorContainer}>
      <h2>Тираж</h2>

      <FlexForm
        fields={UNIT_FIELDS}
        formData={formData}
        setFormData={setFormData}
      />
      
      <div className={styles.buttonRow}>
        <button
          className={`${styles.btn} ${styles.btnAccent}`}
          onClick={calculate}
          disabled={loading}
        >
          {loading ? "Вычисляем..." : "Рассчитать"}
        </button>

        {!hideAcceptButtons && (
          <>
            <button
              className={`${styles.btn} ${styles.btnPrimary}`}
              onClick={delay}
              disabled={loading}
            >
              Отложить
            </button>

            <button
              className={`${styles.btn} ${styles.btnPrimary}`}
              onClick={accept}
              disabled={loading}
            >
              В работу
            </button>
          </>
        )}
        {!hideUpdateButton && (
          <button
            className={`${styles.btn} ${styles.btnPrimary}`}
            onClick={update}
            disabled={loading}
          >
            Обновить
          </button>
        )}
      </div>

      {error && (
        <div className={styles.error}>
          {Array.isArray(error) ? (
            <ul>
              {error.map((e, i) => (
                <li key={i}>
                  <strong>{e.path}:</strong> {e.message}
                </li>
              ))}
            </ul>
          ) : (
            error
          )}
        </div>
      )}

      {report && (
        <ReportSection
          report={report}
          base_rows={BASE_ROWS}
          detail_rows={hiddenRows}
        />
      )}
    </section>
  );
}