import PropTypes from "prop-types";

const ItemActions = ({ itemId, onEdit, onDelete, onChangeStatus }) => (
  <span className="item-field item-actions">
    <button className="edit-button" onClick={onEdit} title="Редактировать">✏️</button>
    <button className="status-button" onClick={onChangeStatus} title="Сменить статус">🔄</button>
    <button className="delete-button" onClick={() => onDelete(itemId)} title="Удалить">❌</button>
  </span>
);

ItemActions.propTypes = {
  itemId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onChangeStatus: PropTypes.func.isRequired,
};

export default ItemActions;
