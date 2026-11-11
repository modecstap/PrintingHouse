import { useEffect, useRef, useState } from "react";
import Calculator from "../calculator/calculator";
import Modal from "../generic/modal/modal";
import {
  fetchOrderForm,
  fetchOrderReport,
  fetchOrderSummaries,
} from "./api/orders";
import Button from "../generic/button/button";
import pageStyles from "../generic/page/page.module.css";
import Table from "../generic/table/table";
import { useAbortableLoad } from "../../hooks/useAbortableLoad";
import { formatOrderCreatedDate } from "../calculator/models/order";
import styles from "./orders.module.css";

export default function Orders({ catalogs, catalogLoadState }) {
  const {
    data: orders,
    status: listStatus,
    error: listError,
    reload: startListLoad,
  } = useAbortableLoad((signal) => fetchOrderSummaries(signal), []);
  const [selectedId, setSelectedId] = useState(null);
  const [modalState, setModalState] = useState(null);
  const modalAbortRef = useRef(null);

  useEffect(() => {
    if (selectedId == null) {
      return undefined;
    }

    modalAbortRef.current?.abort();
    const controller = new AbortController();
    modalAbortRef.current = controller;
    setModalState({ status: "loading" });

    Promise.allSettled([
      fetchOrderForm(selectedId, controller.signal),
      fetchOrderReport(selectedId, controller.signal),
    ]).then(([formResult, reportResult]) => {
      if (controller.signal.aborted) {
        return;
      }

      if (formResult.status === "rejected") {
        const message =
          formResult.reason instanceof Error
            ? formResult.reason.message
            : String(formResult.reason);
        setModalState({ status: "error", message });
        return;
      }

      const form = formResult.value;
      let report = null;
      let reportError = null;
      if (reportResult.status === "fulfilled") {
        report = reportResult.value;
      } else {
        reportError =
          reportResult.reason instanceof Error
            ? reportResult.reason.message
            : String(reportResult.reason);
      }

      setModalState({ status: "ready", form, report, reportError });
    });

    return () => {
      controller.abort();
    };
  }, [selectedId]);

  const closeModal = () => {
    modalAbortRef.current?.abort();
    modalAbortRef.current = null;
    setSelectedId(null);
    setModalState(null);
  };

  const handleSaved = () => {
    startListLoad();
  };

  return (
    <div className={pageStyles.page}>
      <div className={pageStyles.pageTitle}>
        <h1>Заказы</h1>
        <Button
          type="button"
          onClick={startListLoad}
          aria-label="Обновить"
        >
          &#10226;
        </Button>
      </div>

      {listStatus === "loading" && <div>Загрузка...</div>}

      {listStatus === "error" && <div role="alert">{listError}</div>}

      {listStatus === "success" && (
        <Table>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Количество</th>
              <th scope="col">Описание</th>
              <th scope="col">Дата создания</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td colSpan={4} style={{ padding: 0, border: "none" }}>
                  <button
                    type="button"
                    className={styles.rowButton}
                    onClick={() => setSelectedId(order.id)}
                  >
                    <span>{order.id}</span>
                    <span>{order.count}</span>
                    <span className={styles.descriptionCell}>
                      {order.description}
                    </span>
                    <span>{formatOrderCreatedDate(order.created_at)}</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {selectedId != null && (
        <Modal onClose={closeModal} size="large">
          {modalState?.status === "loading" && <div>Загрузка...</div>}

          {modalState?.status === "error" && (
            <div role="alert">{modalState.message}</div>
          )}

          {modalState?.status === "ready" && (
            <>
              {modalState.reportError && (
                <p className={styles.modalMessage} role="alert">
                  {modalState.reportError}
                </p>
              )}
              <Calculator
                key={selectedId}
                initialForm={modalState.form}
                initialReport={modalState.report}
                editingOrderId={selectedId}
                onSaved={handleSaved}
                catalogs={catalogs}
                catalogLoadState={catalogLoadState}
              />
            </>
          )}
        </Modal>
      )}
    </div>
  );
}
