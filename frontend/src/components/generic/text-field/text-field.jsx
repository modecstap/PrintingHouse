import styles from "./text-field.module.css";

export function TextField({
  id,
  label,
  value,
  onChange,
  disabled,
  placeholder,
  type = "text",
  inputMode,
  step,
  min,
  max,
}) {
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>{label}</label>
      <input
        id={id}
        className={styles.input}
        type={type}
        inputMode={inputMode}
        step={step ?? (type === "number" ? "1" : undefined)}
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
      />
    </div>
  );
}
