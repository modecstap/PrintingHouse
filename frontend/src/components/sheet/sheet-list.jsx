import styles from "./sheet.module.css";

export default function SheetList({ sheets, onDelete }) {
  if (sheets.length === 0) {
    return <p className={styles.row}>Нет листов</p>;
  }

  return (
    <ul className={styles.list}>
      <li className={styles.row}>
        <span>Имя</span>
        <span>Плотность</span>
        <span>Ставка</span>
        <span />
      </li>
      {sheets.map((sheet) => (
        <li key={sheet.id} className={styles.row}>
          <span>{sheet.name}</span>
          <span>{sheet.density}</span>
          <span>{sheet.cost}</span>
          <button
            className={styles.button}
            type="button"
            onClick={() => onDelete(sheet.id)}
          >
            Удалить
          </button>
        </li>
      ))}
    </ul>
  );
}
