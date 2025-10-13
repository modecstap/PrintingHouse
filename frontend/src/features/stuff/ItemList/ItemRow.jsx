import PropTypes from "prop-types";
import ItemActions from "./ItemActions";

const ItemRow = ({ item, fieldKeys, disableAction, onEdit, onDelete, onChangeStatus, gridColumns }) => {
  const renderValue = (value) => {
    if (value === null || value === undefined) return "—";
    if (typeof value === "object") return JSON.stringify(value);
    return value;
  };

  return (
    <div className="item-row" style={{ gridTemplateColumns: gridColumns }}>
      {fieldKeys.map((key) => (
        <span key={key} className="item-field">
          {renderValue(item[key])}
        </span>
      ))}
      {!disableAction && (
        <ItemActions
          itemId={item.id}
          onEdit={() => onEdit(item)}
          onDelete={() => onDelete(item.id)}
          onChangeStatus={() => onChangeStatus(item)}
        />
      )}
    </div>
  );
};

ItemRow.propTypes = {
  item: PropTypes.object.isRequired,
  fieldKeys: PropTypes.array.isRequired,
  disableAction: PropTypes.bool,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  onChangeStatus: PropTypes.func,
  gridColumns: PropTypes.string.isRequired,
};

export default ItemRow;
