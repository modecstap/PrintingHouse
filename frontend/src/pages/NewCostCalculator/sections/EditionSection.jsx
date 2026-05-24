import ReportSection from "../../CostCalculator/sections/ReportSection";
import FlexForm from "../components/FlexForm";
import { useEdition } from "../hooks/useEdition";

export default function EditionSection({
  formData,
  setFormData,
  hideActionButtons,
}) {
  const {
    UNIT_FIELDS,
    BASE_ROWS,
    report,
    hiddenRows,
    loading,
    calculate,
    delay,
    accept,
  } = useEdition(formData);

  return (
    <section className="calculator-container">
      <h2>Тираж</h2>

      <FlexForm
        fields={UNIT_FIELDS}
        formData={formData}
        setFormData={setFormData}
      />

      <div className="button-row">
        <button className="btn btn-accent" onClick={calculate} disabled={loading}>
          {loading ? "Вычисляем..." : "Рассчитать"}
        </button>

        {!hideActionButtons && (
          <>
            <button className="btn btn-primary" onClick={delay}>Отложить</button>
            <button className="btn btn-primary" onClick={accept}>В работу</button>
          </>
        )}
      </div>

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