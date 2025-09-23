import React, { useState, useEffect } from "react";

export default function ConcealedParameters({ initialValues, onChange }) {
  const [formValues, setFormValues] = useState({
    count: 0,
    density: 0,
    width: 0,
    height: 0,
    bleeds: 2,
    chroma: 1,
    lamination: 1,
    die_cutting: "false",
    markup: 80,
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
        <label>Наценка (%)</label>
        <input
          type="number"
          step="0.01"
          name="markup"
          value={formValues.markup}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Вылеты (мм)</label>
        <input type="number" name="bleeds" value={formValues.bleeds} onChange={handleChange} />
      </div>
    </div>
  );
}
