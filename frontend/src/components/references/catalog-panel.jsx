import { useId, useState } from "react";
import {
  createCatalog,
  deleteCatalog,
  fetchCatalog,
  replaceCatalog,
} from "./api/catalog";
import Button from "../generic/button/button";
import { useAbortableLoad } from "../../hooks/useAbortableLoad";
import styles from "./references.module.css";

function isFieldGroup(fieldDef) {
  return Array.isArray(fieldDef.fields);
}

export default function CatalogPanel({ def, onCatalogsInvalidated }) {
  const headingId = useId();
  const {
    data: rows,
    status: listStatus,
    error: listError,
    reload: reloadList,
  } = useAbortableLoad(
    (signal) => fetchCatalog(def.listPath, def.parseList, signal),
    [def.listPath, def.parseList],
  );
  const [form, setForm] = useState(def.emptyForm);
  const [saveState, setSaveState] = useState({ status: "idle" });
  const [deleteError, setDeleteError] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const handleFieldChange = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const renderInput = (field) => {
    const inputId = `${def.key}-${field.name}`;
    const common = {
      id: inputId,
      value: form[field.name] ?? "",
      onChange: (event) => handleFieldChange(field.name, event.target.value),
    };
    if (field.inputType === "number") {
      return <input type="number" step="1" {...common} />;
    }
    if (field.inputMode === "decimal") {
      return <input type="text" inputMode="decimal" {...common} />;
    }
    return <input type="text" {...common} />;
  };

  const handleSave = () => {
    setSaveState({ status: "loading" });
    setDeleteError(null);
    const body = def.toPayload(form);
    const request =
      editingId != null
        ? replaceCatalog(def.itemPath(editingId), body)
        : createCatalog(def.listPath, body);

    request
      .then(() => {
        setForm(def.emptyForm);
        setEditingId(null);
        setSaveState({ status: "idle" });
        reloadList();
        onCatalogsInvalidated?.();
      })
      .catch((error) => {
        setSaveState({ status: "error", message: error.message });
      });
  };

  const handleCancel = () => {
    setForm(def.emptyForm);
    setEditingId(null);
    setSaveState({ status: "idle" });
  };

  const handleEdit = (row) => {
    setForm(def.formFromRow(row));
    setEditingId(row.id);
    setSaveState({ status: "idle" });
    setDeleteError(null);
  };

  const handleDelete = (row) => {
    setDeleteError(null);
    setDeletingId(row.id);
    deleteCatalog(def.itemPath(row.id))
      .then(() => {
        reloadList();
        onCatalogsInvalidated?.();
        if (editingId === row.id) {
          setForm(def.emptyForm);
          setEditingId(null);
        }
      })
      .catch((error) => {
        setDeleteError(error.message);
      })
      .finally(() => {
        setDeletingId(null);
      });
  };

  const saveError = saveState.status === "error" ? saveState.message : null;

  return (
    <section aria-labelledby={headingId} className={styles.catalogPanel}>
      <h3 id={headingId}>{def.title}</h3>

      {listStatus === "loading" && <div>Загрузка...</div>}

      {listStatus === "error" && <div role="alert">{listError}</div>}

      {listStatus === "success" && (
        <table className={styles.table}>
          <thead>
            <tr>
              {def.columns.map((col, index) => (
                <th key={`${col.header}-${index}`} scope="col">
                  {col.header}
                </th>
              ))}
              <th scope="col" className={styles.actionsCol} />
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                {def.columns.map((col, index) => (
                  <td key={`${col.header}-${index}`}>{col.render(row)}</td>
                ))}
                <td className={styles.actionsCol}>
                  {def.canReplace && (
                    <Button type="button" onClick={() => handleEdit(row)}>
                      Изменить
                    </Button>
                  )}
                  <Button
                    type="button"
                    disabled={deletingId === row.id}
                    onClick={() => handleDelete(row)}
                  >
                    Удалить
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className={styles.calculatorBlock}>
        <div className={styles.formRow}>
          {def.fields.map((fieldDef) => {
            if (isFieldGroup(fieldDef)) {
              return (
                <fieldset key={fieldDef.legend} className={styles.fieldset}>
                  <legend>{fieldDef.legend}</legend>
                  <div className={styles.formRow}>
                    {fieldDef.fields.map((field) => (
                      <label key={field.name} className={styles.field} htmlFor={`${def.key}-${field.name}`}>
                        {field.label}
                        {renderInput(field)}
                      </label>
                    ))}
                  </div>
                </fieldset>
              );
            }
            return (
              <label key={fieldDef.name} className={styles.field} htmlFor={`${def.key}-${fieldDef.name}`}>
                {fieldDef.label}
                {renderInput(fieldDef)}
              </label>
            );
          })}
        </div>
        <div className={styles.buttonRow}>
          <Button
            type="button"
            disabled={saveState.status === "loading"}
            onClick={handleSave}
          >
            Сохранить
          </Button>
          {editingId != null && (
            <Button type="button" onClick={handleCancel}>
              Отмена
            </Button>
          )}
        </div>
        {saveError && <div role="alert">{saveError}</div>}
        {deleteError && <div role="alert">{deleteError}</div>}
      </div>
    </section>
  );
}
