import "./item-actions.css";

import PropTypes from "prop-types";
import { BackendIP } from "../../../constants/BackendIP";

const ItemActions = ({ itemId, onEdit, onDelete, onChangeStatus }) => {
  const handlePrintInstruction = async () => {
    try {
      const response = await fetch(`${BackendIP}/api/instruction/${itemId}`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("Не удалось получить инструкцию");
      }

      const blob = await response.blob();

      const disposition = response.headers.get("Content-Disposition");
      let fileName = "file";

      if (disposition) {
        const match = disposition.match(/filename="?(.+)"?/);
        if (match?.[1]) {
          fileName = match[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert("Ошибка при загрузке инструкции");
    }
  };

  return (
    <span className="item-field item-actions">
      <button className="print-button" onClick={handlePrintInstruction} title="Печать инструкции">
        🖨️
      </button>
      <button className="edit-button" onClick={onEdit} title="Редактировать">
        ✏️
      </button>
      <button className="status-button" onClick={onChangeStatus} title="Сменить статус">
        🔄
      </button>
      <button className="delete-button" onClick={() => onDelete(itemId)} title="Удалить">
        ❌
      </button>
    </span>
  );
};

ItemActions.propTypes = {
  itemId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onChangeStatus: PropTypes.func.isRequired,
};

export default ItemActions;
