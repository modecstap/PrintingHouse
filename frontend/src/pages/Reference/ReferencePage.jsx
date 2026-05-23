import { useEffect, useState } from "react";
import { useAsyncAction } from "../CostCalculator/hooks/useAsyncAction";

const initialFormData = {
  tax_rate: "0.0000",
  black_ink_cost: "0.0000",
  ink_cost: "0.0000",
  printer_salary: "0.0000",
  lamination_cost: "0.0000",
  die_cutting_cost: "0.0000",
  paper_cost: "0.0000",
  press_sheet: {
    height: 0,
    width: 0,
    spacing: 0,
  },
  cutter: {
    stack_height: 0,
  },
  cutting_cost: "0.0000",
  sheet_by_fitting: 0,
  markup: "1.0000",
};

export default function ReferencePage() {
  const { loading, error, execute } = useAsyncAction();
  const [formData, setFormData] = useState(initialFormData);


  useEffect(() => {
    const load = async () => {
      const data = await execute("/api/reference/production", null, {
        method: "GET",
      });
      if (data) setFormData(data);
    };

    load();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numericValue = value === "" ? "" : Number(value);

    setFormData((prev) => {
      const updated = structuredClone(prev);

      if (name.includes(".")) {
        const keys = name.split(".");
        let obj = updated;

        for (let i = 0; i < keys.length - 1; i++) {
          obj = obj[keys[i]];
        }
        obj[keys[keys.length - 1]] = numericValue;
      } else {
        updated[name] = numericValue;
      }

      return updated;
    });
  };

  // ===== PUT сохранение =====
  const onConfirm = async () => {
    await execute("/api/reference/production", formData, {
      method: "PUT",
    });
  };

  return (
    <div className="calculator-container">
      <h1 className="page-title">Справочная система</h1>
      {error && <div className="error">{error}</div>}

      <div className="form-grid">

        <FormTile label="Стоимость чёрной краски (руб./лист)">
          <input
            type="number"
            step="0.01"
            name="black_ink_cost"
            value={formData.black_ink_cost}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Стоимость всех красок (руб./лист)">
          <input
            type="number"
            step="0.01"
            name="ink_cost"
            value={formData.ink_cost}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Зарплата печатнику (руб./лист)">
          <input
            type="number"
            step="0.01"
            name="printer_salary"
            value={formData.printer_salary}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Цена ламинации (руб./лист)">
          <input
            type="number"
            step="0.01"
            name="lamination_cost"
            value={formData.lamination_cost}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Стоимость высечки (руб./лист)">
          <input
            type="number"
            step="0.01"
            name="die_cutting_cost"
            value={formData.die_cutting_cost}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Стоимость бумаги (руб./кг)">
          <input
            type="number"
            step="0.01"
            name="paper_cost"
            value={formData.paper_cost}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Высота печатного листа (мм)">
          <input
            type="number"
            name="press_sheet.height"
            value={formData.press_sheet.height}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Ширина печатного листа (мм)">
          <input
            type="number"
            name="press_sheet.width"
            value={formData.press_sheet.width}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Поля печатного листа (мм)">
          <input
            type="number"
            name="press_sheet.spacing"
            value={formData.press_sheet.spacing}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Высота стопки резака (мм)">
          <input
            type="number"
            name="cutter.stack_height"
            value={formData.cutter.stack_height}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Листы на приладку (шт)">
          <input
            type="number"
            name="sheet_by_fitting"
            value={formData.sheet_by_fitting}
            onChange={handleChange}
          />
        </FormTile>

        <FormTile label="Цена 1 реза (руб.)">
          <input
            type="number"
            step="0.01"
            name="cutting_cost"
            value={formData.cutting_cost}
            onChange={handleChange}
          />
        </FormTile>
      </div>

      <div className="modal-buttons">
        <button
          className="btn btn-primary"
          onClick={onConfirm}
          disabled={loading}
        >
          {loading ? "Отправляем..." : "Сохранить"}
        </button>
      </div>
    </div>
  );
}

function FormTile({ label, children }) {
  return (
    <div className="form-tile">
      <label>{label}</label>
      {children}
    </div>
  );
}

