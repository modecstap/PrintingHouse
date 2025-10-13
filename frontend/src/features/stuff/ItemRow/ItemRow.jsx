import "./ItemRow.css";

const formatValue = (value) => {
  if (typeof value === "number") {
    return value;
  }

  if (typeof value === "string") {
    const date = new Date(value);
    if (!isNaN(date.getTime()) && value.includes("T")) {
      return value.replace("T", " ");
    }

    const num = parseFloat(value);
    if (!isNaN(num)) {
      return num.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
  }

  return value;
};


const ItemRow = ({ data, index, disableAction, onEdit }) => {
  return (
    <div className={`item-row ${index % 2 === 0 ? "even" : "odd"}`}>
      {Object.entries(data).map(([key, value]) => (
        <span key={key} className="item-field">
          {formatValue(value)}
        </span>
      ))}
      {!disableAction && <button className="update-button" onClick={onEdit}>Рассчитать</button>}
    </div>
  );
};
export default ItemRow;