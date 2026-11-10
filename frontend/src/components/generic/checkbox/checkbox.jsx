import styles from "./checkbox.module.css";

export function Checkbox({
  id,
  label,
  checked,
  onChange,
  disabled,
  className,
}) {
  return (
    <label className={className ?? styles.root} htmlFor={id}>
      <input
        id={id}
        className={styles.input}
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
      />
      <span className={styles.labelText}>{label}</span>
    </label>
  );
}
