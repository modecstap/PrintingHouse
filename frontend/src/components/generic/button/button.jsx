import styles from "./button.module.css";

export default function Button({
  children,
  onClick,
  disabled,
  type = "button",
  "aria-label": ariaLabel,
  "aria-pressed": ariaPressed,
}) {
  return (
    <button
      className={styles.button}
      type={type}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      aria-pressed={ariaPressed}
    >
      {children}
    </button>
  );
}
