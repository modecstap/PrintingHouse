import React, { useState } from "react";
import "./Modal.css";

const Modal = ({ item, onClose, apiUrl, isAdd }) => {
  const initialData = isAdd ? {} : item || {};
  const [formData, setFormData] = useState(initialData);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    if (!apiUrl) return;

    try {
      const method = isAdd ? "POST" : "PUT";
      const url = isAdd ? apiUrl : `${apiUrl}/${formData.id}`;

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert(isAdd ? "Объект успешно добавлен!" : "Объект успешно обновлён!");
        onClose();
      } else {
        alert("Ошибка при сохранении!");
      }
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Ошибка сети!");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{isAdd ? "Добавить новую сущность" : formData.name || "Редактирование"}</h2>
        <div className="modal-content">
          {Object.keys(item || {}).map(
            (key) =>
              !(isAdd && key === "id") && ( // Пропускаем id при добавлении
                <div key={key} className="modal-row">
                  <span>{key}</span>
                  <input
                    type="text"
                    name={key}
                    value={formData[key] || ""}
                    onChange={handleChange}
                  />
                </div>
              )
          )}
        </div>
        <div className="modal-actions">
          <button className="save-button" onClick={handleSubmit}>
            {isAdd ? "Добавить" : "Изменить"}
          </button>
          <button className="cancel-button" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
};

export default Modal;
