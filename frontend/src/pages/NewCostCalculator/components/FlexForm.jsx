import FormField from "./FormField";


export default function FlexForm({ fields, formData, setFormData }) {
  return (
    <div className="form-grid">
      {fields.map((field) => (
        <FormField
          key={field.path}
          label={field.label}
          path={field.path}
          data={formData}
          setData={setFormData}
          type={field.type}
          step={field.step}
          options={field.options}
          valueParser={field.valueParser}
        />
      ))}
    </div>
  );
}
