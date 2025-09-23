import React, { useState, useEffect } from "react";

export default function EditionForm({ initialValues, onChange }) {
  const [formValues, setFormValues] = useState({
    count: 0,
    density: 0,
    width: 0,
    height: 0,
    bleeds: 2,
    chroma: 1,
    lamination: 1,
    die_cutting: "false", // для select храним как строку
    markup: 80,            // в процентах!
    ...initialValues,     // если будут предустановки
  });

  // трансформируем в "edition" и отправляем наружу
  useEffect(() => {
    const edition = {
      count: Number(formValues.count),
      density: Number(formValues.density),
      list_size: {
        width: Number(formValues.width),
        height: Number(formValues.height),
        bleeds: Number(formValues.bleeds),
      },
      chroma: Number(formValues.chroma),
      lamination: Number(formValues.lamination),
      die_cutting: formValues.die_cutting === "true",
      markup: (parseFloat(formValues.markup) / 100) + 1, // преобразование
    };
    onChange(edition);
  }, [formValues, onChange]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormValues((prev) => ({ ...prev, [name]: value }));
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
        <select name="die_cutting" value={formValues.die_cutting} onChange={handleChange}>
          <option value="false">Нет</option>
          <option value="true">Да</option>
        </select>
      </div>
    </div>
  );
}
