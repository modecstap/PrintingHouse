import { useEffect, useRef, useState } from "react";
import { fetchReferences, saveReference } from "./api/references";
import styles from "./references.module.css";

const EMPTY_FORM = { name: "", description: "", orderId: "" };

export default function References() {
  const [listState, setListState] = useState({ status: "loading" });
  const [form, setForm] = useState(EMPTY_FORM);
  const [saveState, setSaveState] = useState({ status: "idle" });
  const listAbortRef = useRef(null);

  const startListLoad = () => {
    listAbortRef.current?.abort();
    const controller = new AbortController();
    listAbortRef.current = controller;
    setListState({ status: "loading" });

    fetchReferences(controller.signal)
      .then((references) => {
        if (controller.signal.aborted) {
          return;
        }
        setListState({ status: "success", references });
      })
      .catch((error) => {
        if (error?.name === "AbortError" || controller.signal.aborted) {
          return;
        }
        setListState({ status: "error", message: error.message });
      });
  };

  useEffect(() => {
    startListLoad();
    return () => {
      listAbortRef.current?.abort();
    };
  }, []);

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
    <div className={styles.calculatorContainer}>
      <div className={styles.pageTitle}>
        <h1 style={{ marginTop: 0 }}>Справочная система</h1>
      </div>

      {listState.status === "loading" && <div>Загрузка...</div>}

      {listState.status === "error" && (
        <div role="alert">{listState.message}</div>
      )}

      {listState.status === "success" && (
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">Имя</th>
              <th scope="col">Описание</th>
              <th scope="col">Номер заказа</th>
            </tr>
          </thead>
          <tbody>
            {listState.references.map((row) => (
              <tr key={`${row.name}-${row.order_id}`}>
                <td>{row.name}</td>
                <td>{row.description}</td>
                <td>{row.order_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className={styles.separator} />

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
            Номер заказа
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
          <button
            type="button"
            className={`${styles.btn} ${styles.btnPrimary}`}
            disabled={saveState.status === "loading"}
            onClick={handleSave}
          >
            Сохранить
          </button>
        </div>
        {saveError && <div role="alert">{saveError}</div>}
      </div>
    </div>
  );
}
