import styles from "./Button.module.css";

const VARIANTS = {
  primary: styles.primary,
  secondary: styles.secondary,
  accent: styles.accent,
  table: styles.table,
};

export default function Button({
  variant = "secondary",
  type = "button",
  className,
  children,
  ...rest
}) {
  const variantClass = VARIANTS[variant] ?? VARIANTS.secondary;

  return (
    <button
      type={type}
      className={[styles.btn, variantClass, className].filter(Boolean).join(" ")}
      {...rest}
    >
      {children}
    </button>
  );
}
