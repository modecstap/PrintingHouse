import React, { useState, useEffect } from "react";

export default function ProductionForm({ onChange }) {
  // Дефолтные значения
  const defaultValues = {
    tax_rate: 0.93,
    black_ink_cost: 2,
    ink_cost: 15.6,
    lamination_cost: 12,
    die_cutting_cost: 100,
    paper_cost: 165,
    press_sheet: {
      height: 450,
      width: 320,
      spacing: 5,
    },
    cutter: {
      stack_height: 30,
    },
    sheet_by_fitting: 2,
    cutting_cost: 10,
    printer_salary: 2,
  };


  const [formValues, setFormValues] = useState(defaultValues);

  useEffect(() => {
    onChange(formValues);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    // Проверяем, вложенное ли поле
    const keys = name.split(".");
    let newValues = { ...formValues };

    if (keys.length === 1) {
      newValues[keys[0]] = value;
    } else if (keys.length === 2) {
      newValues[keys[0]] = { ...newValues[keys[0]], [keys[1]]: value };
    }

    setFormValues(newValues);
    onChange(newValues);
  };

  return (
    <div className="form-grid">
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
