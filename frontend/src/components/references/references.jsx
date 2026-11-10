import { useState } from "react";
import {
  EQUIPMENT_CATALOGS,
  MATERIAL_CATALOGS,
  STAFF_CATALOGS,
} from "./catalog-defs";
import CatalogPanel from "./catalog-panel";
import { fetchReferences, saveReference } from "./api/references";
import Button from "../generic/button/button";
import pageStyles from "../generic/page/page.module.css";
import { useAbortableLoad } from "../../hooks/useAbortableLoad";
import styles from "./references.module.css";

const EMPTY_FORM = { name: "", description: "", orderId: "" };

export default function References({
  catalogs: _catalogs,
  onCatalogsInvalidated,
}) {
  const {
    data: references,
    status: listStatus,
    error: listError,
    reload: startListLoad,
  } = useAbortableLoad((signal) => fetchReferences(signal), []);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saveState, setSaveState] = useState({ status: "idle" });

  const handleSave = () => {
    setSaveState({ status: "loading" });
    saveReference({
      name: form.name.trim(),
      description: form.description.trim(),
      order_id: form.orderId,
    })
      .then(() => {
        setForm(EMPTY_FORM);
        setSaveState({ status: "idle" });
        startListLoad();
      })
      .catch((error) => {
        setSaveState({ status: "error", message: error.message });
      });
  };

  const saveError =
    saveState.status === "error" ? saveState.message : null;

  return (
    <div className={pageStyles.page}>
      <div className={pageStyles.pageTitle}>
        <h1>Справочники</h1>
      </div>

      {listStatus === "loading" && <div>Загрузка...</div>}

      {listStatus === "error" && <div role="alert">{listError}</div>}

      {listStatus === "success" && (
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Имя</th>
              <th scope="col">Описание</th>
              <th scope="col">Заказ №</th>
            </tr>
          </thead>
          <tbody>
            {references.map((row) => (
              <tr key={`${row.name}-${row.order_id}`}>
                <td>{row.name}</td>
                <td>{row.description}</td>
                <td>{row.order_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className={styles.calculatorBlock}>
        <div className={styles.formRow}>
          <label className={styles.field}>
            Имя
            <input
              type="text"
              value={form.name}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, name: event.target.value }))
              }
            />
          </label>
          <label className={styles.field}>
            Описание
            <input
              type="text"
              value={form.description}
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  description: event.target.value,
                }))
              }
            />
          </label>
          <label className={styles.field}>
            Заказ №
            <input
              type="number"
              step="1"
              value={form.orderId}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, orderId: event.target.value }))
              }
            />
          </label>
        </div>
        <div className={styles.buttonRow}>
          <Button
            type="button"
            disabled={saveState.status === "loading"}
            onClick={handleSave}
          >
            Сохранить
          </Button>
        </div>
        {saveError && <div role="alert">{saveError}</div>}
      </div>

      <section aria-labelledby="references-equipment">
        <h2 id="references-equipment" className={styles.groupHeading}>
          Оборудование
        </h2>
        {EQUIPMENT_CATALOGS.map((def) => (
          <CatalogPanel
            key={def.key}
            def={def}
            onCatalogsInvalidated={onCatalogsInvalidated}
          />
        ))}
      </section>

      <section aria-labelledby="references-staff">
        <h2 id="references-staff" className={styles.groupHeading}>
          Персонал
        </h2>
        {STAFF_CATALOGS.map((def) => (
          <CatalogPanel
            key={def.key}
            def={def}
            onCatalogsInvalidated={onCatalogsInvalidated}
          />
        ))}
      </section>

      <section aria-labelledby="references-materials">
        <h2 id="references-materials" className={styles.groupHeading}>
          Материалы
        </h2>
        {MATERIAL_CATALOGS.map((def) => (
          <CatalogPanel
            key={def.key}
            def={def}
            onCatalogsInvalidated={onCatalogsInvalidated}
          />
        ))}
      </section>
    </div>
  );
}
