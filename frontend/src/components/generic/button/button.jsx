import styles from "./button.module.css";

export default function Button({ children, onClick, disabled, type = "button" }) {
  return (
    <button
      className={styles.button}
      type={type}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
