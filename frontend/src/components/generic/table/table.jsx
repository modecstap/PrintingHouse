import styles from "./table.module.css";

export default function Table({ children, className }) {
  const tableClass = className
    ? `${styles.table} ${className}`
    : styles.table;

  return <table className={tableClass}>{children}</table>;
}
