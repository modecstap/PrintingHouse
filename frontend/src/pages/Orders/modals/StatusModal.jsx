import PropTypes from "prop-types";
import { useState } from "react";
import Modal from "../../../features/Modal/Modal";

const StatusModal = ({ item, onClose, onSubmit }) => {
  const [selectedStatus, setSelectedStatus] = useState(item.status ?? "");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!selectedStatus) {
      alert("Выберите статус.");
      return;
    }

    onSubmit(item.id, selectedStatus);
  };

  return (
    <Modal onClose={onClose} size="small">
      <form onSubmit={handleSubmit}  className="calculator-container">
        <h3 className="page-title">Сменить статус для заказа #{item.id}</h3>

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

        <div className="button-row">
          <button type="button" className="btn-accent" onClick={onClose}>
            Отмена
          </button>
          <button type="submit" className="btn-primary">
            Сохранить
          </button>
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