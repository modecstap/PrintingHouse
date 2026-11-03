import styles from "./sheet.module.css";

function optionLabel(sheet) {
  return `${sheet.name} ${sheet.density}гр`;
}

export default function SheetSelect({ sheets, sheetId, onChange }) {
  return (
    <label className={`${styles.field} ${styles.select}`}>
      Печатный лист
      <select
        value={sheetId == null ? "" : String(sheetId)}
        onChange={(event) => {
          const raw = event.target.value;
          onChange(raw === "" ? null : Number(raw));
        }}
      >
        <option value="">Не выбран</option>
        {sheets.map((sheet) => (
          <option key={sheet.id} value={sheet.id}>
            {optionLabel(sheet)}
          </option>
        ))}
      </select>
    </label>
  );
}
