import { useState, useMemo, useCallback } from "react";
import PropTypes from "prop-types";
import "./ItemList.css";
import ItemTable from "./ItemTable";
import ItemModal from "./ItemModal";
import StatusModal from "./StatusModal";
import Pagination from "../Pagination/Pagination";

const ITEMS_PER_PAGE = 10;

const ItemList = ({ data = [], visibleFields = [], disableAction = false, apiUrl }) => {
  const [items, setItems] = useState(data);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedItem, setSelectedItem] = useState(null);
  const [statusTarget, setStatusTarget] = useState(null); // 👈 новый стейт для статуса

  const totalPages = useMemo(() => Math.ceil(items.length / ITEMS_PER_PAGE), [items]);
  const start = (currentPage - 1) * ITEMS_PER_PAGE;
  const currentItems = useMemo(() => items.slice(start, start + ITEMS_PER_PAGE), [items, currentPage]);

  const fieldKeys = useMemo(() => (
    visibleFields.length > 0 ? visibleFields : Object.keys(items[0] || {})
  ), [visibleFields, items]);

  const handleDelete = useCallback(async (id) => {
    if (!window.confirm("Удалить этот элемент?")) return;
    try {
      const res = await fetch(`${apiUrl}${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`Ошибка: ${res.status}`);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      console.error(err);
      alert("Не удалось удалить элемент.");
    }
  }, [apiUrl]);

  const openModal = useCallback((item, showActions = false) => {
    setSelectedItem({ ...item, showActions });
  }, []);

  const closeModal = useCallback(() => setSelectedItem(null), []);

  /** === Новый метод: смена статуса === */
  const handleStatusChange = useCallback(async (orderId, status) => {
    try {
      const res = await fetch(`${apiUrl}status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId, new_status: status }),
      });

      if (!res.ok) throw new Error(`Ошибка: ${res.status}`);

      // обновляем локальные данные
      setItems((prev) =>
        prev.map((item) =>
          item.id === orderId ? { ...item, status } : item
        )
      );
    } catch (err) {
      console.error("Ошибка смены статуса:", err);
      alert("Не удалось сменить статус.");
    } finally {
      setStatusTarget(null);
    }
  }, [apiUrl]);

  return (
    <div className="item-list">
      <ItemTable
        items={currentItems}
        fieldKeys={fieldKeys}
        disableAction={disableAction}
        onEdit={openModal}
        onDelete={handleDelete}
        onChangeStatus={(item) => setStatusTarget(item)}
      />

      {!disableAction && (
        <button className="add-button" onClick={() => openModal({}, true)}>+</button>
      )}

      {selectedItem && (
        <ItemModal
          item={selectedItem}
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

      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      )}
    </div>
  );
};

ItemList.propTypes = {
  data: PropTypes.array.isRequired,
  visibleFields: PropTypes.array,
  disableAction: PropTypes.bool,
  apiUrl: PropTypes.string.isRequired,
};

export default ItemList;
