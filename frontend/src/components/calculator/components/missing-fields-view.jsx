import styles from "../calculator.module.css";

export default function MissingFieldsView({ fields }) {
  if (!fields?.length) {
    return null;
  }

  return (
    <section>
      <p className={styles.missingFieldsHeading}>Пропущено:</p>
      <ul className={styles.missingFieldsList}>
        {fields.map((label) => (
          <li key={label}>{label}</li>
        ))}
      </ul>
    </section>
  );
}
