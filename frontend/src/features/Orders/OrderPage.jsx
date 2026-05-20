import React, { useMemo, useState } from "react";
import DataTable from "../Table/dataTable";
import StatusModal from "./modals/StatusModal";
import ItemModal from "./modals/ItemModal";
import "./OrderPage.css"

import { useOrdersData } from "./hooks/useOrdersData";
import { useOrdersUI } from "./hooks/useOrdersUI";
import { downloadFile } from "./utils/downloadFile";

const OrderPage = () => {
  const {
    orders,
    loading,
    error,
    updateStatus,
    remove,
    downloadInstruction,
    reload,
  } = useOrdersData();

  const {
    selectedItem,
    openModal,
    closeModal,
    statusTarget,
    setStatusTarget,
  } = useOrdersUI();

  const [processingId, setProcessingId] = useState(null);

  const handleDelete = async (id) => {
    if (!window.confirm("Удалить этот заказ?")) return;

    try {
      setProcessingId(id);
      await remove(id);
    } catch (e) {
      alert(e.message);
    } finally {
      setProcessingId(null);
    }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await updateStatus(id, status);
    } catch (e) {
      alert(e.message);
    } finally {
      setStatusTarget(null);
    }
  };

  const handlePrint = async (id) => {
    try {
      const { blob, fileName } = await downloadInstruction(id);
      downloadFile(blob, fileName);
    } catch (e) {
      alert("Ошибка загрузки файла");
    }
  };

  const columns = [
    { key: "id", label: "ID" },
    { key: "creation_date", label: "Создан" },
    { key: "comment", label: "Комментарий" },
    { key: "status", label: "Статус" },
  ];

  const actions = useMemo(
    () => [
      {
        label: "🖨️",
        className: "print-button",
        onClick: (row) => handlePrint(row.id),
      },
      {
        label: "✏️",
        className: "edit-button",
        onClick: (row) => openModal(row, true),
      },
      {
        label: "🔄",
        className: "status-button",
        onClick: (row) => setStatusTarget(row),
      },
      {
        label: "❌",
        className: "delete-button",
        onClick: (row) => handleDelete(row.id),
        disabled: (row) => processingId === row.id,
      },
    ],
    [processingId]
  );

  if (loading) return <div className="loading">Загрузка...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <>
      <div className="calculator-container">
        <div className="page-title">
          <h1>Заказы</h1>
          <button className="refresh-button" onClick={() => reload()}>&#10226;</button>
        </div>
        <DataTable
          columns={columns}
          data={orders}
          actions={actions}
        />
      </div>

      {selectedItem && (
        <ItemModal
          item={selectedItem.item}
          onClose={closeModal}
          hideActionButtons={!selectedItem.showActions}
        />
      )}

      {statusTarget && (
        <StatusModal
          item={statusTarget}
          onClose={() => setStatusTarget(null)}
          onSubmit={handleStatusChange}
        />
      )}
    </>
  );
};

export default OrderPage;