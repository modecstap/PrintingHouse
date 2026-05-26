import FormField from "./FormField";

export default function ActionModal({
  action,
  data,
  setData,
  onConfirm,
  onClose,
  loading,
}) {
  if (!action) return null;

  const { title, confirmText, fields } = action;

  return (
    <div className="modal-overlay">
      <div className="calculator-container">
        <h3>{title}</h3>

        {fields.map((field) => (
          <FormField
            key={field.path}
            label={field.label}
            path={field.path}
            data={data}
            setData={setData}
            type={field.type}
            valueParser={field.valueParser ?? ((v) => v)}
          />
        ))}

        <div className="modal-buttons">
          <button
            className="btn btn-primary"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Отправляем..." : confirmText}
          </button>

          <button className="btn btn-more" onClick={onClose}>
            Отмена
          </button>
        </div>
      </div>
    </div>
  );
}
