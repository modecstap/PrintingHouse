import { Dropdown } from "../dropdown/dropdown";
import styles from "./flex-form.module.css";

function parsePath(path) {
  return path
    .replace(/\[(\d+)\]/g, ".$1")
    .split(".")
    .filter(Boolean)
    .map((p) => (p.match(/^\d+$/) ? Number(p) : p));
}

function getByPath(obj, path) {
  const keys = Array.isArray(path) ? path : parsePath(path);

  return keys.reduce((acc, key) => {
    if (acc == null) return undefined;
    return acc[key];
  }, obj);
}

function updateByPath(obj, path, value) {
  const keys = parsePath(path);
  const result = structuredClone(obj);

  let current = result;

  keys.forEach((key, index) => {
    if (index === keys.length - 1) {
      current[key] = value;
      return;
    }

    if (current[key] == null) {
      current[key] = typeof keys[index + 1] === "number" ? [] : {};
    }

    current = current[key];
  });

  return result;
}

function FormField({
  label,
  path,
  data,
  setData,
  type = "text",
  step,
  options = {},
  valueParser,
  emptyOptionLabel,
}) {
  const value = getByPath(data, path);
  const fieldId = String(path);

  const handleChange = (e) => {
    let val = e.target.value;

    if (type === "select" && valueParser) {
      val = valueParser(val);
    }

    setData((prev) => updateByPath(prev, path, val));
  };

  const handleSelect = (val) => {
    let parsed = val;
    if (valueParser) {
      parsed = valueParser(val);
    }
    setData((prev) => updateByPath(prev, path, parsed));
  };

  return (
    <div className={styles.formTile}>
      {type === "select" ? (
        <Dropdown
          id={fieldId}
          label={label}
          value={value ?? ""}
          onChange={handleSelect}
          options={options}
          emptyOptionLabel={emptyOptionLabel}
        />
      ) : type === "textarea" ? (
        <>
          <label htmlFor={fieldId}>{label}</label>
          <textarea
            id={fieldId}
            className={styles.formInput}
            rows={options.rows ?? 3}
            value={value ?? ""}
            onChange={handleChange}
          />
        </>
      ) : (
        <>
          <label htmlFor={fieldId}>{label}</label>
          <input
            id={fieldId}
            className={styles.formInput}
            type={type}
            step={step}
            value={value ?? ""}
            onChange={handleChange}
          />
        </>
      )}
    </div>
  );
}

export default function FlexForm({ fields, formData, setFormData }) {
  return (
    <div className={styles.formGrid}>
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
          emptyOptionLabel={field.emptyOptionLabel}
        />
      ))}
    </div>
  );
}
