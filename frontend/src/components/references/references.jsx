import { useState } from "react";
import {
  EQUIPMENT_CATALOGS,
  MATERIAL_CATALOGS,
  STAFF_CATALOGS,
} from "./catalog-defs";
import CatalogPanel from "./catalog-panel";
import { fetchReferences, saveReference } from "./api/references";
import Button from "../generic/button/button";
import { NumberField } from "../generic/number-field/number-field";
import pageStyles from "../generic/page/page.module.css";
import Table from "../generic/table/table";
import { TextField } from "../generic/text-field/text-field";
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
        <Table>
          <thead>
            <tr>
              <th scope="col">Имя</th>
              <th scope="col">Описание</th>
              <th scope="col">Заказ</th>
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
        </Table>
      )}

      <div className={styles.calculatorBlock}>
        <div className={styles.formRow}>
          <div className={styles.field}>
            <TextField
              id="references-template-name"
              label="Имя"
              value={form.name}
              onChange={(value) =>
                setForm((prev) => ({ ...prev, name: value }))
              }
            />
          </div>
          <div className={styles.field}>
            <TextField
              id="references-template-description"
              label="Описание"
              value={form.description}
              onChange={(value) =>
                setForm((prev) => ({ ...prev, description: value }))
              }
            />
          </div>
          <div className={styles.field}>
            <NumberField
              id="references-template-order-id"
              label="Заказ"
              value={form.orderId}
              onChange={(value) =>
                setForm((prev) => ({ ...prev, orderId: value }))
              }
            />
          </div>
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
