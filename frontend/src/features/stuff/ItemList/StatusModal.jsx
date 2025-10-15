import PropTypes from "prop-types";
import { useState } from "react";
import Modal from "../Modal/Modal";

const StatusModal = ({ item, onClose, onSubmit }) => {
  const [selectedStatus, setSelectedStatus] = useState(item.new_status ?? "");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedStatus) return alert("Выберите статус.");
    onSubmit(item.id, selectedStatus);
  };

  return (
    <Modal onClose={onClose} size="small">
      <form onSubmit={handleSubmit} className="status-modal-form">
        <h3>Сменить статус для заказа #{item.id}</h3>

        <label>
          Статус:
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
          >
            <option value="">— Выберите —</option>
            <option value="Отложен">Отложен</option>
            <option value="В работе">В работе</option>
            <option value="Завершён">Завершён</option>
          </select>
        </label>

        <div className="modal-actions">
          <button type="button" onClick={onClose}>Отмена</button>
          <button type="submit" className="confirm-button">Сохранить</button>
        </div>
      </form>
    </Modal>
  );
};

StatusModal.propTypes = {
  item: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
};

export default StatusModal;
