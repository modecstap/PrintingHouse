import styles from "./dropdown.module.css";

export function Dropdown({
  id,
  label,
  value,
  onChange,
  options,
  disabled,
  emptyOptionLabel,
}) {
  return (
    <div className={styles.field}>
      <label htmlFor={id}>{label}</label>
      <select
        id={id}
        className={styles.input}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {emptyOptionLabel != null && (
          <option value="">{emptyOptionLabel}</option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
