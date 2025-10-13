import { useState } from "react";
import "./ItemList.css";
import ItemRow from "../ItemRow/ItemRow";
import Modal from "../Modal/Modal";
import Pagination from "../Pagination/Pagination";
import CostCalculatorPage from "../../cost-calculator/CostCalculatorPage";
import "./ItemList.css";

const ITEMS_PER_PAGE = 10;

const ItemList = ({ data, visibleFields, disableAction, apiUrl }) => {
  const [items, setItems] = useState(data);
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(items.length / ITEMS_PER_PAGE);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const openModal = (item) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedItem(null);
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm("Удалить этот элемент?")) return;

    try {
      const response = await fetch(`${apiUrl}${itemId}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error(`Ошибка удаления: ${response.status}`);

      setItems((prev) => prev.filter((item) => item.id !== itemId));
    } catch (error) {
      console.error("Ошибка при удалении:", error);
      alert("Не удалось удалить элемент.");
    }
  };

  const fieldKeys =
    visibleFields && visibleFields.length > 0
      ? visibleFields
      : Object.keys(items[0] || {});

  const headers = fieldKeys.map((key) => key.replace(/_/g, " "));
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const currentItems = items.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  const gridColumns = disableAction
    ? `repeat(${fieldKeys.length}, 1fr)`
    : `repeat(${fieldKeys.length + 1}, 1fr)`; // +1 для ACTIONS

  return (
    <div className="item-list">
      {/* Заголовки таблицы */}
      <div className="item-row header" style={{ gridTemplateColumns: gridColumns }}>
        {headers.map((header) => (
          <span key={header} className="item-field">
            {header.toUpperCase()}
          </span>
        ))}
        {!disableAction && <span className="item-field">ACTIONS</span>}
      </div>

      {/* Список элементов */}
      {currentItems.map((item, index) => (
        <div
          key={index}
          className="item-row"
          style={{ gridTemplateColumns: gridColumns }}
        >
          {fieldKeys.map((key) => (
            <span key={key} className="item-field">
              {typeof item[key] === "object" && item[key] !== null
                ? JSON.stringify(item[key])
                : item[key]}
            </span>
          ))}

          {!disableAction && (
            <span className="item-field item-actions">
              <button
                className="edit-button"
                onClick={() => openModal(item)}
                title="Редактировать"
              >
                ✏️
              </button>
              <button
                className="delete-button"
                onClick={() => handleDelete(item.id)}
                title="Удалить"
              >
                ❌
              </button>
            </span>
          )}
        </div>
      ))}

      {/* Кнопка "Добавить" */}
      {!disableAction && (
        <button className="add-button" onClick={() => openModal({})}>
          +
        </button>
      )}

      {/* Модальное окно */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content large">
            <button className="modal-close" onClick={closeModal}>
              ✖
            </button>

            <CostCalculatorPage
              edition={selectedItem?.edition || {}}
              production={selectedItem?.production || {}}
            />
          </div>
        </div>
      )}

      {/* Пагинация */}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
};

export default ItemList;
