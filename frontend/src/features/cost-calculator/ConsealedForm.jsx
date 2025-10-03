import React, { useState, useEffect } from "react";

export default function ConsealedForm({ data, onChange }) {
  const [formValues, setFormValues] = useState({
    ...data.production,
    bleeds: data.edition.list_size.bleeds,
  });

  useEffect(() => {
    setFormValues({
      ...data.production,
      bleeds: data.edition.list_size.bleeds,
    });
  }, [data]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numericValue = value === "" ? "" : Number(value);

    let updated = { ...formValues, [name]: numericValue };
    setFormValues(updated);

    if (name === "bleeds") {
      // обновляем edition
      onChange("edition", {
        ...data.edition,
        list_size: { ...data.edition.list_size, bleeds: numericValue },
      });
    } else if (name.includes(".")) {
      // обновляем вложенные production поля
      const keys = name.split(".");
      const newProduction = { ...data.production };
      let obj = newProduction;

      for (let i = 0; i < keys.length - 1; i++) {
        obj[keys[i]] = { ...obj[keys[i]] };
        obj = obj[keys[i]];
      }
      obj[keys[keys.length - 1]] = numericValue;

      onChange("production", newProduction);
    } else {
      // обычное production поле
      onChange("production", {
        ...data.production,
        [name]: numericValue,
      });
    }
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
        <input
          type="number"
          name="bleeds"
          value={formValues.bleeds}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Налоговая ставка</label>
        <input
          type="number"
          step="0.01"
          name="tax_rate"
          value={formValues.tax_rate}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Стоимость чёрной краски (руб./лист)</label>
        <input
          type="number"
          step="0.01"
          name="black_ink_cost"
          value={formValues.black_ink_cost}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Стоимость всех красок (руб./лист)</label>
        <input
          type="number"
          step="0.01"
          name="ink_cost"
          value={formValues.ink_cost}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Цена ламинации (руб./лист)</label>
        <input
          type="number"
          step="0.01"
          name="lamination_cost"
          value={formValues.lamination_cost}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Стоимость высечки (руб./лист)</label>
        <input
          type="number"
          step="0.01"
          name="die_cutting_cost"
          value={formValues.die_cutting_cost}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Стоимость бумаги (руб./кг)</label>
        <input
          type="number"
          step="0.01"
          name="paper_cost"
          value={formValues.paper_cost}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Высота печатного листа (мм)</label>
        <input
          type="number"
          name="press_sheet.height"
          value={formValues.press_sheet.height}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Ширина печатного листа (мм)</label>
        <input
          type="number"
          name="press_sheet.width"
          value={formValues.press_sheet.width}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Поля печатного листа (мм)</label>
        <input
          type="number"
          name="press_sheet.spacing"
          value={formValues.press_sheet.spacing}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Высота стопки резака (мм)</label>
        <input
          type="number"
          name="cutter.stack_height"
          value={formValues.cutter.stack_height}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Листы на приладку (шт)</label>
        <input
          type="number"
          name="sheet_by_fitting"
          value={formValues.sheet_by_fitting}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Цена 1 реза (руб.)</label>
        <input
          type="number"
          step="0.01"
          name="cutting_cost"
          value={formValues.cutting_cost}
          onChange={handleChange}
        />
      </div>

      <div className="form-tile">
        <label>Зарплата печатнику за 1 лист (руб.)</label>
        <input
          type="number"
          step="0.01"
          name="printer_salary"
          value={formValues.printer_salary}
          onChange={handleChange}
        />
      </div>
    </div>
  );
}
