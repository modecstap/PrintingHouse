import PropTypes from "prop-types";
import ItemRow from "./ItemRow";

const ItemTable = ({
  items,
  fieldKeys,
  disableAction,
  onEdit,
  onDelete,
  onChangeStatus, // 👈 новый проп
}) => {
  const gridColumns = `repeat(${fieldKeys.length + (disableAction ? 0 : 1)}, 1fr)`;
  const headers = fieldKeys.map((key) => key.replace(/_/g, " "));

  if (!items || items.length === 0) {
    return <div className="no-data">Нет данных для отображения</div>;
  }

  return (
    <>
      {/* Заголовки таблицы */}
      <div className="item-row header" style={{ gridTemplateColumns: gridColumns }}>
        {headers.map((header) => (
          <span key={header} className="item-field">
            {header.toUpperCase()}
          </span>
        ))}
        {!disableAction && <span className="item-field">ACTIONS</span>}
      </div>

      {/* Строки таблицы */}
      {items.map((item) => (
        <ItemRow
          key={item.id ?? JSON.stringify(item)}
          item={item}
          fieldKeys={fieldKeys}
          disableAction={disableAction}
          onEdit={onEdit}
          onDelete={onDelete}
          onChangeStatus={onChangeStatus} // 👈 передаём дальше
          gridColumns={gridColumns}
        />
      ))}
    </>
  );
};

ItemTable.propTypes = {
  items: PropTypes.array.isRequired,
  fieldKeys: PropTypes.array.isRequired,
  disableAction: PropTypes.bool,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  onChangeStatus: PropTypes.func, // 👈 добавлено
};

export default ItemTable;
