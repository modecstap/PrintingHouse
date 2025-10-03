import React, { useState, useEffect } from "react";

export default function VisibleForm({ data, onChange }) {
  // инициализация локального state один раз при монтировании
  const [formValues, setFormValues] = useState(() => ({
    count: data.edition.count,
    density: data.edition.density,
    width: data.edition.list_size.width,
    height: data.edition.list_size.height,
    chroma: data.edition.chroma,
    lamination: data.edition.lamination,
    die_cutting: data.edition.die_cutting,
  }));

  // обновляем локальный state только если data.edition реально меняется
  useEffect(() => {
    setFormValues({
      count: data.edition.count,
      density: data.edition.density,
      width: data.edition.list_size.width,
      height: data.edition.list_size.height,
      chroma: data.edition.chroma,
      lamination: data.edition.lamination,
      die_cutting: data.edition.die_cutting,
    });
  }, [data.edition, data.edition.list_size]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    let newValue = value;

    if (name === "die_cutting") {
      newValue = value === "true";
    } else if (["count", "density", "width", "height"].includes(name)) {
      newValue = value;
    } else if (name === "chroma" || name === "lamination") {
      newValue = Number(value); // преобразуем числа из select
    }

    const updated = { ...formValues, [name]: newValue };
    setFormValues(updated);

    // уведомляем родителя
    const updatedEdition = { ...data.edition, [name]: newValue };
    
    // если поле width или height, обновляем внутри list_size
    if (name === "width" || name === "height") {
      updatedEdition.list_size = { ...data.edition.list_size, [name]: newValue };
    }

    onChange("edition", updatedEdition);
  };

  return (
    <div className="form-grid">
      <div className="form-tile">
        <label>Кол-во изделий (шт.)</label>
        <input type="number" name="count" value={formValues.count} onChange={handleChange} />
      </div>

      <div className="form-tile">
        <label>Плотность бумаги (гр./м²)</label>
        <input type="number" name="density" value={formValues.density} onChange={handleChange} />
      </div>

      <div className="form-tile">
        <label>Ширина изделия</label>
        <input type="number" name="width" value={formValues.width} onChange={handleChange} />
      </div>

      <div className="form-tile">
        <label>Высота изделия</label>
        <input type="number" name="height" value={formValues.height} onChange={handleChange} />
      </div>

      <div className="form-tile">
        <label>Цветность</label>
        <select name="chroma" value={formValues.chroma} onChange={handleChange}>
          <option value="1">1+0</option>
          <option value="2">1+1</option>
          <option value="3">4+0</option>
          <option value="4">4+1</option>
          <option value="5">4+4</option>
        </select>
      </div>

      <div className="form-tile">
        <label>Ламинация</label>
        <select name="lamination" value={formValues.lamination} onChange={handleChange}>
          <option value="1">Без ламинации</option>
          <option value="2">1+0</option>
          <option value="3">1+1</option>
        </select>
      </div>

      <div className="form-tile">
        <label>Высечка</label>
        <select name="die_cutting" value={String(formValues.die_cutting)} onChange={handleChange}>
          <option value="false">Нет</option>
          <option value="true">Да</option>
        </select>
      </div>
    </div>
  );
}
