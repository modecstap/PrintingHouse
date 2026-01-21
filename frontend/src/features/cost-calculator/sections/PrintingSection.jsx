import { useEffect, useState } from "react";
import { BackendIP } from "../../../constants/BackendIP";
import FlexForm from "../components/FlexForm";
import AdvancedSection from "../components/AdvancedSection";


const printingFields = (index) => [
  {
    label: "Кол-во листов",
    path: `printings[${index}].edition.count`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Комментарий",
    path: `printings[${index}].comment`,
    type: "text",
    valueParser: Number,
  },
  {
    label: "Ширина",
    path: `printings[${index}].edition.list_size.width`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Высота",
    path: `printings[${index}].edition.list_size.height`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Плотность",
    path: `printings[${index}].edition.density`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Цветность",
    path: `printings[${index}].edition.chroma`,
    type: "select",
    valueParser: Number,
    options: [
      { value: 0, label: "0+0" },
      { value: 1, label: "1+0" },
      { value: 2, label: "1+1" },
      { value: 3, label: "4+0" },
      { value: 4, label: "4+1" },
      { value: 5, label: "4+4" },
    ],
  },
  {
    label: "Ламинация",
    path: `printings[${index}].edition.lamination`,
    type: "select",
    valueParser: Number,
    options: [
      { value: 1, label: "Без ламинации" },
      { value: 2, label: "1+0" },
      { value: 3, label: "1+1" },
    ],
  },
  {
    label: "Высечка",
    path: `printings[${index}].edition.die_cutting`,
    type: "select",
    valueParser: (v) => v === "true",
    options: [
      { value: false, label: "Нет" },
      { value: true, label: "Да" },
    ],
  },
];

const printingHiddenFields = (index) => [
  {
    label: "Вылеты (мм)",
    path: `printings[${index}].edition.list_size.bleeds`,
  },
  {
    label: "Стоимость чёрной краски (руб./лист)",
    path: `printings[${index}].production.black_ink_cost`,
    step: 0.01,
  },
  {
    label: "Стоимость всех красок (руб./лист)",
    path: `printings[${index}].production.ink_cost`,
    step: 0.01,
  },
  {
    label: "Цена ламинации (руб./лист)",
    path: `printings[${index}].production.lamination_cost`,
    step: 0.01,
  },
  {
    label: "Стоимость высечки (руб./лист)",
    path: `printings[${index}].production.die_cutting_cost`,
    step: 0.01,
  },
  {
    label: "Стоимость бумаги (руб./кг)",
    path: `printings[${index}].production.paper_cost`,
    step: 0.01,
  },
  {
    label: "Высота печатного листа (мм)",
    path: `printings[${index}].production.press_sheet.height`,
  },
  {
    label: "Ширина печатного листа (мм)",
    path: `printings[${index}].production.press_sheet.width`,
  },
  {
    label: "Поля печатного листа (мм)",
    path: `printings[${index}].production.press_sheet.spacing`,
  },
  {
    label: "Высота стопки резака (мм)",
    path: `printings[${index}].production.cutter.stack_height`,
  },
  {
    label: "Листы на приладку (шт)",
    path: `printings[${index}].production.sheet_by_fitting`,
  },
  {
    label: "Цена 1 реза (руб.)",
    path: `printings[${index}].production.cutting_cost`,
    step: 0.01,
  },
  {
    label: "Зарплата печатнику за 1 лист (руб.)",
    path: `printings[${index}].production.printer_salary`,
    step: 0.01,
  },
]

const newPrinting = () => ({
    edition: {
      count: 0,
      list_size: { width: 420, height: 297, bleeds: 2 },
      density: 80,
      chroma: 1,
      lamination: 1,
      die_cutting: false,
    },
    production: {},
    comment: "",
});
  

export default function PrintingSection({formData, setFormData}){
    const [showAdvanced, setShowAdvanced] = useState(
        formData.printings.map(() => false)
    );

    
  useEffect(() => {
    fetch(`${BackendIP}/api/reference/production`)
      .then(res => res.json())
      .then(data => {
        setFormData(prev => ({
          ...prev,
          printings: prev.printings.map(p => ({ ...p, production: data })),
        }));
      });
  }, []);
    
    const addPrinting = () => {
        const newP = newPrinting();
        setFormData(d => ({
            ...d,
            printings: [...d.printings, newP],
        }));

        setShowAdvanced(prev => [...prev, false]);

        fetch(`${BackendIP}/api/reference/production`)
            .then(res => res.json())
            .then(data => {
            setFormData(d => {
                const updatedPrintings = [...d.printings];
                updatedPrintings[updatedPrintings.length - 1] = {
                ...updatedPrintings[updatedPrintings.length - 1],
                production: data,
                };
                return { ...d, printings: updatedPrintings };
            });
        });
    };


    const removePrinting = (index) => {
        setFormData(d => ({
            ...d,
            printings: d.printings.filter((_, i) => i !== index),
        }));

        setShowAdvanced(prev => prev.filter((_, i) => i !== index));
    };

    return(
        <section className="calculator-container" style={{marginTop: "0"}}>
            <h2>Параметры печати</h2>
            {formData.printings.map((_, i) => (
                <>
                <div key={i} className="sub-block">
                    <FlexForm
                    fields={printingFields(i)}
                    formData={formData}
                    setFormData={setFormData}
                    />
                    
                    <div className="button-row">
                    <button
                        className="btn btn-primary"
                        onClick={() => removePrinting(i)}
                    >
                        Удалить
                    </button>
                    <button
                        className="btn btn-more"
                        onClick={() =>
                        setShowAdvanced(prev =>
                            prev.map((val, idx) => (idx === i ? !val : val))
                        )
                        }
                    >
                        {showAdvanced[i] ? "Скрыть" : "Подробнее"}
                    </button>
                    </div>

                    
                    <AdvancedSection open={showAdvanced[i]}>
                    <div className="advanced-content">
                        <FlexForm
                        fields={printingHiddenFields(i)}
                        formData={formData}
                        setFormData={setFormData}
                        />
                    </div>
                    </AdvancedSection>
                </div>
                <div className="separator"></div>
                </>
            ))}
            <button className="btn btn-primary" onClick={addPrinting}>
                + Добавить печать
            </button>
        </section>
    )
}