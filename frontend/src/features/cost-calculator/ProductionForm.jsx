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
    markup: 80,
    bleeds: 0, // добавил, так как есть поле в форме
  };

  const [formValues, setFormValues] = useState(defaultValues);

  useEffect(() => {
    const normalized = {
      tax_rate: Number(formValues.tax_rate),
      black_ink_cost: Number(formValues.black_ink_cost),
      ink_cost: Number(formValues.ink_cost),
      lamination_cost: Number(formValues.lamination_cost),
      die_cutting_cost: Number(formValues.die_cutting_cost),
      paper_cost: Number(formValues.paper_cost),
      press_sheet: {
        height: Number(formValues.press_sheet.height),
        width: Number(formValues.press_sheet.width),
        spacing: Number(formValues.press_sheet.spacing),
      },
      cutter: {
        stack_height: Number(formValues.cutter.stack_height),
      },
      sheet_by_fitting: Number(formValues.sheet_by_fitting),
      cutting_cost: Number(formValues.cutting_cost),
      printer_salary: Number(formValues.printer_salary),
      bleeds: Number(formValues.bleeds),
      markup: (parseFloat(formValues.markup) / 100) + 1, // преобразование
    };

    onChange(normalized);
  }, [formValues, onChange]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const keys = name.split(".");
    let newValues = { ...formValues };

    if (keys.length === 1) {
      newValues[keys[0]] = value;
    } else if (keys.length === 2) {
      newValues[keys[0]] = { ...newValues[keys[0]], [keys[1]]: value };
    }

    setFormValues(newValues);
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
